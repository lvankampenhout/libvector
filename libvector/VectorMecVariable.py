#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module for reading and processing CLM vector output, specifically for multiple
elevation class (MEC) output over glaciated landunits

@author: L.vankampenhout@uu.nl
"""

import numpy as np
from netCDF4 import Dataset, default_fillvals

GLC_NEC = 10 # maximum number of elevation classes present in input file
COLUNIT_GLCMEC = 4 # for landunit types and column types, land ice = 7 (older CLM) land ice = 4 (newer CLM)


class VectorMecVariable(object):
   """
   This class represents a memory representation of a CLM variable which has been 
   computed on Multiple Elevation Classes (MEC). 
   
   Normally, these variables are aggregated  on the grid cell level, and the vertical
   or level information is lost.
   However, by setting hist_dov2xy = .false. in the CLM namelist all CLM columns are 
   output -- this is called "vector output". 
   
   MEC variables are used over ice sheets and glaciers and typically have 
   11 levels: level 0 representing tundra and the other 10 are different elevations
   of the glaciated part of the grid cell. 
   
   Some of these levels are "virtual", meaning that they don't have any area associated
   with them. Over Antarctica, virtual columns are usually disabled. This is controlled
   by the CLM namelist (see User Documentation for more details). 
   To find out which columns are virtual and which are not, coupler output can be used.
   This coupler information is required to e.g. downscale on a 2 D map.
   
   MEC column area and topographic height are determined by a high-resolution ice mask, 
   e.g. from CISM. This is typically done in the first time step of any simulation. 
   The topographic height of MEC levels is variable across grid cells. For example, 
   in one grid cell, level 6 may correspond to elevation 550 m, whereas in the next it 
   corresponds to elevation 570 m. This stems from the fact that MEC columns are associated 
   with *bins* and not *heights*. Within each elevation bin, the mean of the underlying 
   topography is assigned to topographic height (CLM: variable TOPO_COL).
   """

   def __init__(self, varname, fname_vector, fname_vecinfo = None):
      """
      init and read MEC variable into memory
      
      By default, the vector information is read from the vector file itself.
      In case this is not possible, e.g. when that file has been post-processed, an 
      auxiliary file can be given from which this data is retrieved.

      :param varname:         CLM variable name
      :param fname_vector:    filename of CLM vector file (e.g. XXX.h2.YYY.nc)
      :param fname_vecinfo:   filename of CLM vector grid info file (optional)
      :type varname:          string
      :type fname_vector:     string
      :type fname_vecinfo:    string
      :returns: nothing
      """
      self.varname = varname

      with Dataset(fname_vector,'r') as fid:
         self.time = fid.variables['time'][:]
         self.time_units = fid.variables['time'].units
         self.var_type = fid.variables[varname].dimensions[-1] # 'col' or 'pft'
         self.long_name = fid.variables[varname].long_name
         self.units = fid.variables[varname].units

         if (varname[0:4] == "SNO_"):
            # workaround layered data (like SNO_GS) : use top layer only
            self.data = fid.variables[varname][:,0,:]
         else:
            self.data = fid.variables[varname][:]
      

      # WORKAROUND shift data by one month
      #self.data = self.data[[1,2,3,4,5,6,7,8,9,10,11,0]]
      
      print('INFO: read variable %s, which is of type %s' %(varname, self.var_type))
      
      
      self.ntime, self.nvec = self.data.shape

      # ===============================================
      # Read vector indices and grid information
      # ===============================================
      if (fname_vecinfo == None):
         filename = fname_vector
      else:
         filename = fname_vecinfo

      with Dataset(filename,'r') as fid:
         self.lats = fid.variables['lat'][:]
         self.lons = fid.variables['lon'][:]           
         if (self.var_type == 'column'):
            self.ixy = fid.variables['cols1d_ixy'][:]
            self.jxy = fid.variables['cols1d_jxy'][:]
            self.lunit   = fid.variables['cols1d_itype_lunit'][:]   # col landunit type (vegetated,urban,lake,wetland,glacier or glacier_mec)
            self.coltype   = fid.variables['cols1d_itype_col'][:] 
         elif (self.var_type == 'pft'):
            self.ixy = fid.variables['pfts1d_ixy'][:]
            self.jxy = fid.variables['pfts1d_jxy'][:]
            self.lunit   = fid.variables['pfts1d_itype_lunit'][:]   # col landunit type (vegetated,urban,lake,wetland,glacier or glacier_mec)
            self.coltype   = fid.variables['pfts1d_itype_col'][:] 
         else:
            raise Exception('Unknown variable type: '+self.var_type)   
      
      self.nlat = len(self.lats)
      self.nlon = len(self.lons)

      print('INFO: nlat = %d, nlon = %d' % (self.nlat, self.nlon))
     

   def applyFactor(self, fac):
      """
      Apply some scalar factor to variable in memory

      :param fac:         factor
      """
      self.data *= fac   


   def setGlcFracCPL(self, filename):
      """
      set glacier fraction from coupler history file

      variables read are named "x2lavg_Sg_ice_covered00" etc.

      :param filename:  filename of coupler history file
      """     
      self.mec_frac = np.zeros((GLC_NEC+1,self.nlat,self.nlon)) # One extra for tundra class
      with Dataset(filename,'r') as fid:
         #print(fid.variables)
         for i in range(0,11):
            #self.mec_frac[i,:,:] = fid.variables['x2lavg_Sg_ice_covered%02d' % i][:] # CESM 1.99
            self.mec_frac[i,:,:] = fid.variables['x2l_Sg_ice_covered%02d' % i][:] # CESM 2.0
            
      self.mec_frac = np.ma.masked_greater(self.mec_frac,2)


   def setGlcFracSurfdat(self, filename):
      """
      set glacier fraction from a surfdat file

      variable read is named "PCT_GLC_MEC_ICESHEET(nglcec, lsmlat, lsmlon)"

      :param filename:  filename of surfdat file
      """
      self.mec_frac = np.zeros((GLC_NEC+1,self.nlat,self.nlon)) # One extra for tundra class
      with Dataset(filename,'r') as fid:
         #print(fid.variables)
         for i in range(1,11):
            self.mec_frac[i,:,:] = fid.variables['PCT_GLC_MEC_ICESHEET'][i-1,:,:]


   def getGridded3d(self):
      """
      Returns vector data as gridded (lat/lon) numpy array with levels (MEC).
      """
      lon2d,lat2d = np.meshgrid(self.lons,self.lats)
      var_out = np.ma.zeros((self.ntime,self.nlat,self.nlon,GLC_NEC))

      # Mask out all points without GLC_MEC
      var_out[:] = np.ma.masked
      
      for lev in range(GLC_NEC):
         mask = (self.coltype==(400+lev+1))
         idx, = np.where(mask)
         ix = self.ixy[idx]-1
         iy = self.jxy[idx]-1
         
         #print(tskin[:,idx].shape, var_out[:,iy,ix,lev].shape)
         var_out[:,iy,ix,lev] = self.data[:,idx]
   
      # Mask out points with missing value
      var_out = np.ma.masked_greater(var_out, 1e34)

      # report number of non-missing points
      print('number of non-zero points:', var_out.count() / self.ntime)
      return var_out
   

   def getGridded2d(self):
      """
      Returns vector data as gridded (lat/lon) numpy array.
      No levels, so weighted by ice_cover percentage.
      """
      var3d = self.getGridded3d() # dimensions (ntime, nlat, nlon, NGLC_NEC)
      #print('DEBUG',var3d.shape)

      var_out = np.ma.zeros((self.ntime,self.nlat,self.nlon))

      try:
         frac = np.ma.filled(self.mec_frac, 0.0)
      except AttributeError:
         msg = """
         USER ERROR: Glacier fraction has not been set in class VectorMecVariable! You must first set fraction 
         using class methods setGlcFracCPL() or setGlcFracSurfdat()"""
         raise AttributeError(msg)

      #print('DEBUG',np.max(frac))

      for lev in range(GLC_NEC):
         #var_out += self.mec_frac[lev+1,:,:] * var3d[:,:,:,lev]
         var_out += frac[lev+1,:,:] * np.ma.filled(var3d[:,:,:,lev], 0.0)


      var_out /= np.sum(frac[1:,:,:], axis=0) # normalize for total fraction ( /= 1.0 when tundra present)

      # Mask out all points without GLC_MEC
      #var_out = np.ma.masked_less(var_out, 1e-4) # TODO: this is quite crude!!

      # Mask out all points without GLC_MEC
      #invalid_mask = np.all(var3d.mask, axis=3)
      #var_out[invalid_mask] = np.ma.masked

      return var_out
           

   def getGridded3dCustomLevels(self, custom_levs, fname_cpl_restart):
      """
      Returns vector data as gridded (lat/lon) numpy array at user specified levels.
      A coupler restart file is required containing the topographic height of each MEC column.

      :param custom_levs:        custom levels
      :param fname_cpl_restart:  filename of coupler restart file
      :type custom_levs:         python list
      :type fname_cpl_restart:   string
      """
      lon2d,lat2d = np.meshgrid(self.lons,self.lats)
      var_out = np.ma.zeros((self.ntime,self.nlat,self.nlon,GLC_NEC))

      # Mask out all points without GLC_MEC
      var_out[:] = np.ma.masked
      
      for lev in range(GLC_NEC):
         mask = (self.coltype==(400+lev+1))
         idx, = np.where(mask)
         ix = self.ixy[idx]-1
         iy = self.jxy[idx]-1
         
         #print(tskin[:,idx].shape, var_out[:,iy,ix,lev].shape)
         var_out[:,iy,ix,lev] = self.data[:,idx]
   
      # Mask out points with missing value
      var_out = np.ma.masked_greater(var_out, 1e34)

      # report number of non-missing points
      print('number of non-zero points:', var_out.count() / self.ntime)
      return var_out
 

   def divideByGriddedField(self,gfield):
      """ 
      To calculate albedo, we need to divide FSR by a regular lat/lon field. 
      This routine implements the division by a gridded field. 

      :param gfield:  numpy array
      """
      print(self.nlat, self.nlon)
      print(gfield.shape)
      if(self.nlat != gfield.shape[0] or self.nlon != gfield.shape[1]):
         raise ValueError('grid dimensions do not match!')
      
      #print(self.ixy[0:10]-1)
      #print(self.jxy[0:10]-1)      


      #coords = list(zip(self.ixy-1 ,self.jxy-1))
      #print(coords)
      print(gfield[0,0])
      print(gfield[100,100])

      #print(gfield[self.jxy-1,self.ixy-1][1000:1010])
      fsds = gfield[self.jxy-1,self.ixy-1]
      print(self.data.shape)
      print(fsds.shape)
      self.data /= fsds
         #print(tskin[:,idx].shape, var_out[:,iy,ix,lev].shape)
         #var_out[:,iy,ix,lev] = self.data[:,idx]
