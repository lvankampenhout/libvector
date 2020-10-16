#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module for reading and processing CLM vector output, specifically for multiple
elevation class (MEC) output over glaciated landunits

LIMITATIONS
Currently only files with single time steps are supported
Files with multiple time records may work, but are untested!!!

@author: L.vankampenhout@uu.nl
"""
import sys
import numpy as np
from netCDF4 import Dataset, default_fillvals
from scipy.interpolate import InterpolatedUnivariateSpline

GLC_NEC = 10 # maximum number of elevation classes present in input file
COLUNIT_GLCMEC = 4 # for landunit types and column types, land ice = 7 (older CLM) land ice = 4 (newer CLM)


rtnnam = lambda: sys._getframe(1).f_code.co_name # helper function that queries name of current routine


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
      self.fname_vector = fname_vector

      if (fname_vecinfo == None):
         self.fname_vecinfo = fname_vector # read grid info from vector file itself
      else:
         self.fname_vecinfo = fname_vecinfo # auxiliary file for grid info

      with Dataset(fname_vector,'r') as fid:
         self.time = fid.variables['time'][:]
         self.time_units = fid.variables['time'].units
         self.var_type = fid.variables[varname].dimensions[-1] # 'col' or 'pft' or 'lon'
         self.long_name = fid.variables[varname].long_name

         assert self.var_type in ("column", "pft", "lon"), "variable type <%s> not supported" % self.var_type

         try:
            self.units = fid.variables[varname].units
         except AttributeError:
            self.units = "-"

  
         if (varname[0:4] == "SNO_"):
            # special case for layered data (like SNO_T, SNO_GS) : use top layer only
            self.data = fid.variables[varname][:,0,:]
         #elif (varname[0:4] == "TSOI"):
         elif (varname.strip() == "TSOI"):
            #print(np.shape(fid.variables[varname][:])) # (1, 25, 97387)
            self.data = fid.variables[varname][:,0,:]
         else:
            self.data = fid.variables[varname][:]
      

      # WORKAROUND shift data by one month
      #self.data = self.data[[1,2,3,4,5,6,7,8,9,10,11,0]]
      
      print('INFO: %s: read variable %s, which is of type %s' %(rtnnam(), varname, self.var_type))
      
      self.ndim = self.data.ndim
      if (self.ndim == 1):
         # static variable
         self.ntime = 1
         self.nvec = len(self.data)
      elif (self.ndim == 2):
         # assume time indexed variable
         self.ntime, self.nvec = self.data.shape
      elif (self.ndim == 3 and self.var_type == "lon"):
         self.ntime, self.nlat, self.nlon = self.data.shape
         self.nvec = self.nlat * self.nlon
      else:
         raise NotImplementedError('Unexpected number of dimensions of input data, ndim = %d > 2' % self.ndim)

      # Read vector indices and grid information
      try: 
         self.readVectorInfo()
      except KeyError:
         msg = """
         Required vector information could not be read from file!
         This probably means that the file you supplied does not contain the right variables,
         which may happen for instance when you extracted a variable using ncks or CDO.
         Use optional argument \'fname_vecinfo\' in the constructor to point to a file that contains
         the vector information""" 
         raise RuntimeError(msg)

      print('INFO: %s: nlat = %d, nlon = %d' % (rtnnam(), self.nlat, self.nlon))


   def readVectorInfo(self):
      """
      Read vector information (col of pft based) for the variable at hand and store in memory. 
      Do the same for general grid information (lat, lon).
      Is called automatically during __init__()
      """
      with Dataset(self.fname_vecinfo,'r') as fid:
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
         elif (self.var_type == 'lon'):
            self.ixy, self.jxy, self.lunit, self.coltype = None, None, None, None
         else:
            raise NotImplementedError('Unknown variable type: '+self.var_type) 
      
      self.nlat = len(self.lats)
      self.nlon = len(self.lons)

     

   def applyFactor(self, fac, units=None):
      """
      Apply some scalar factor to variable in memory

      :param fac:         factor
      :param units:       new units (if applicable)
      :type fac:          int or float
      :type units:        string
      """
      self.data *= fac   
      if (units != None):
         self.units = units
         print("INFO: %s: converted units to: %s" % (rtnnam(), units))


   def setGlcFracCouplerFile(self, filename):
      """
      set glacier fraction from coupler history file

      variables read are named "x2lavg_Sg_ice_covered00" etc.

      :param filename:  filename of coupler history file
      """     
      self.mec_frac = np.zeros((GLC_NEC+1,self.nlat,self.nlon)) # One extra for tundra class
      with Dataset(filename,'r') as fid:
         #print(fid.variables)
         for i in range(0,GLC_NEC+1):
            #self.mec_frac[i,:,:] = fid.variables['x2lavg_Sg_ice_covered%02d' % i][:] # CESM 1.99
            self.mec_frac[i,:,:] = fid.variables['x2l_Sg_ice_covered%02d' % i][:] # CESM 2.0
            
      self.mec_frac = np.ma.masked_greater(self.mec_frac,2) # TODO: ugly, rewrite


   def setGlcFracSurfdat(self, filename):
      """
      set glacier fraction from a surfdat file

      variable read is named "PCT_GLC_MEC_ICESHEET(nglcec, lsmlat, lsmlon)"

      :param filename:  filename of surfdat file
      """
      self.mec_frac = np.zeros((GLC_NEC+1,self.nlat,self.nlon)) # One extra for tundra class
      with Dataset(filename,'r') as fid:
         #print(fid.variables)
         for i in range(1,GLC_NEC+1):
            self.mec_frac[i,:,:] = fid.variables['PCT_GLC_MEC_ICESHEET'][i-1,:,:]


   def setGlcTopoCouplerFile(self, fname_cpl_restart):
      """
      Set MEC topographic height from coupler restart file.
      Height is assumed constant in time (a single copy is stored)

      :param fname_cpl_restart:  filename of coupler restart file
      :type fname_cpl_restart:   string
      """
      self.mec_topo = np.ma.zeros((GLC_NEC+1,self.nlat,self.nlon)) # One extra for tundra class

      with Dataset(fname_cpl_restart,'r') as fid:
         for i in range(0,GLC_NEC+1):
            self.mec_topo[i,:,:] = fid.variables['l2gacc_lx_Sl_topo%02d' % i][:].reshape(self.nlat, self.nlon)# CESM 2.0

      #print(self.mec_topo[:,176,254]) # GrIS
      #print(self.mec_topo[:,164,250]) # GrIS
      #print(self.mec_topo[:,10,10]) # AIS
      #print(self.mec_topo[:,20,76]) # AIS
      #print(self.mec_topo[:,100,100]) # missing values


   def setGlcTopoHistfile(self, fname_vector):
      """
      Set MEC topographic height from TOPO_COL variable in (vector) history file.
      Height is assumed constant in time (a single copy is stored)

      :param fname_vector:    filename of CLM vector file (e.g. XXX.h2.YYY.nc)
      :type fname_vector:     string
      """
      # read TOPO_COL from vector file and convert to gridded
      vmv = VectorMecVariable("TOPO_COL", fname_vector, fname_vecinfo = self.fname_vecinfo) 
      tmp = vmv.getGridded3d()[0,:,:,:] # remove time dimension
      self.mec_topo = tmp.transpose(2,0,1) # nlev, nlat, nlon



   def getGridded3d(self):
      """
      Returns vector data as gridded (lat/lon) numpy array with levels (MEC).

      NOTE: This function does NOT take into account variable topographic height
      across MEC columns. It is recommended that for any variable that is 
      dynamically downscaled, e.g. temperature, the more elaborate getGridded3dCustomLevels()

      :returns:   numpy array (ntime,nlat,nlon,nlev)
      """
      lon2d,lat2d = np.meshgrid(self.lons,self.lats)
      var_out = np.ma.zeros((self.ntime,self.nlat,self.nlon,GLC_NEC))

      # Mask out all points without GLC_MEC
      var_out[:] = np.ma.masked

      if (self.var_type == "lon"): 
         """
         special case: this variable is in fact not unstructured
         """
         print(self.data.shape)
         for lev in range(GLC_NEC): 
            var_out[:,:,:,lev] = self.data[:]

      else: 
         """
         unstructured variable, type column or pft
         """
         for lev in range(GLC_NEC): 
            mask = (self.coltype==(400+lev+1)) # level 0 is tundra, omit this
            idx, = np.where(mask)
            ix = self.ixy[idx]-1
            iy = self.jxy[idx]-1
            
            #print(tskin[:,idx].shape, var_out[:,iy,ix,lev].shape)
            if (self.ndim == 1):
               var_out[:,iy,ix,lev] = self.data[idx]
            elif (self.ndim == 2):
               var_out[:,iy,ix,lev] = self.data[:,idx]
            else:
               raise NotImplementedError('Unexpected number of dimensions of input data, ndim = %d > 2' % self.ndim)
   
      # Mask out points with missing value
      var_out = np.ma.masked_greater(var_out, 1e34)

      # report number of non-missing points
      print('INFO: %s: number of non-zero points: %d' %  (rtnnam(), var_out.count() / self.ntime))
      return var_out
   

   def getGridded2d(self):
      """
      Returns vector data as gridded (lat/lon) numpy array.
      No levels, so weighted by ice_cover percentage.

      :returns:   numpy array (ntime,nlat,nlon)
      """
      var3d = self.getGridded3d() # dimensions (ntime, nlat, nlon, GLC_NEC)
      #print('DEBUG',var3d.shape)

      var_out = np.ma.zeros((self.ntime,self.nlat,self.nlon))

      try:
         frac = np.ma.filled(self.mec_frac, 0.0)
      except AttributeError:
         msg = """
         Glacier fraction has not been set in class VectorMecVariable! You must first set fraction 
         using class methods setGlcFracCouplerFile() or setGlcFracSurfdat()"""
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
           

   def getGridded3dCustomLevels(self, custom_levs):
      """
      Returns vector data as gridded (lat/lon) numpy array at user specified levels.
      A coupler restart file is required containing the topographic height of each MEC column.

      :param custom_levs:        custom levels
      :type custom_levs:         python list
      :returns:   numpy array (ntime,nlat,nlon,nlev)
      """
      lon2d,lat2d = np.meshgrid(self.lons,self.lats)
      nlev = len(custom_levs)

      var_out = np.ma.zeros((self.ntime,self.nlat,self.nlon,nlev))
      var_out[:] = np.ma.masked # mask out all points without GLC_MEC

      try:
         #topo = np.ma.filled(self.mec_topo, 0.0) # nlev, nlat, nlon
         mec_mask = np.any(self.mec_topo, axis=0)
         print('INFO: %s: using %d grid points out of a total %d' % (rtnnam(), mec_mask.sum(), self.nlat * self.nlon))
      except AttributeError:
         msg = """
         Glacier topography has not been set in class VectorMecVariable! You must first set topography
         using class methods setGlcTopoCouplerFile() or setGlcFracHistfile()"""
         raise AttributeError(msg)

      # get 3D view of variable
      var3d = self.getGridded3d() # dimensions (ntime, nlat, nlon, GLC_NEC)

      mec_topo2 = self.mec_topo

      # mask out all tundra columns
      mec_topo2[0,:,:] = np.ma.masked

      # mask out missing MEC columns (they have 0 height)
      mec_topo2 = np.ma.masked_less(mec_topo2, 1e-3)
      
      nvalid = np.ma.any(mec_topo2, axis=0).sum()
      print('INFO: %s: removing %d invalid grid points: they only contained tundra class (%d remaining)' % (rtnnam(), mec_mask.sum() - nvalid, nvalid))
      mec_mask = np.any(mec_topo2, axis=0)

      # loop grid points that contain at least 1 MEC column
      ix, iy = np.where(mec_mask)
      #print(ix.shape, iy.shape)
      for ii in range(len(ix)):
      #for ii in [10, 2000, 6000, 6500]: # testing with 2 AIS points and 2 GrIS points
         xx = mec_topo2[:,ix[ii], iy[ii]]
         exist, = np.ma.where(xx)
         kexist = len(exist)
         xp = xx[exist] # elevations of all MEC classes that exist

         # loop time steps
         for itime in range(self.ntime):
            # function values used in interpolation (= field values corresponding to heights xp)
            # indices are shifted by one due to presence of tundra class in mec_topo
            fp = var3d[itime, ix[ii], iy[ii], exist-1] 

            if (kexist > 1):
               # Interpolate to target levels using first order (= linear) splines from Scipy.
               # This way, we can linearly interpolate / extrapolate to any level, even sea level (z = 0).
               # Note: whether linear extrapolation makes sense really depends on the variable at hand.
               # Alternatively, numpy.interp() may be used, which extrapolates with constant value 
               # (i.e. repeating the boundary value).
               spl = InterpolatedUnivariateSpline(np.asarray(xp), np.asarray(fp), k=1)
               var_out[itime, ix[ii], iy[ii], :] = spl(custom_levs)

            else:
               # single MEC column at this grid point, can only be constantly extrapolated
               var_out[itime, ix[ii], iy[ii], :] = fp

      # Mask out points with missing value
      #var_out = np.ma.masked_greater(var_out, 1e34)

      # report number of non-missing points
      print('INFO: %s: number of non-zero points: %d' %  (rtnnam(), var_out.count() / self.ntime))
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
