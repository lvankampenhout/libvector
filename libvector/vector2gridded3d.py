#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: L.vankampenhout@uu.nl
"""

from .VectorMecVariable import VectorMecVariable, GLC_NEC, rtnnam
import netCDF4
import time
from netCDF4 import Dataset, default_fillvals

def vector2gridded3d(vmv, fname_target, custom_levs=None):
   """
   Wrapper function for converting a VectorMecVariable into a 3D variable
   and writing the output to NetCDF.

   :param vmv:             VectorMecVariable instance
   :param fname_target:    filename of output file (netCDF)
   :param custom_levs:     custom levels of elevation (m)
   :type vmv:              VectorMecVariable
   :type fname_target:     string
   :type custom_levs:      python list
   """
   print('INFO: %s: number of vectors = %d' % (rtnnam(), vmv.nvec))

   if (custom_levs == None):
      print("INFO: custom levels are NOT used")
      var3d = vmv.getGridded3d()
      nlev = GLC_NEC
   else:
      print("INFO: custom levels are used")
      var3d = vmv.getGridded3dCustomLevels(custom_levs)
      nlev = len(custom_levs)

   # Open a new NetCDF file to write the data to. For format, you can choose from
   # 'NETCDF3_CLASSIC', 'NETCDF3_64BIT', 'NETCDF4_CLASSIC', and 'NETCDF4'
   ncfile = Dataset(fname_target, 'w', format='NETCDF4')
   ncfile.title = 'CESM/CLM glacier elevation class output regridded to 3-dimensional mesh'
   ncfile.model = "CESM / Community Land Model"

   ncfile.institute = "NCAR / Utrecht University"
   ncfile.contact = "L.vankampenhout@uu.nl"

   ncfile.history = rtnnam() + " was applied to "+ vmv.fname_vector + " on " +time.strftime("%a %b %d %Y %H:%M:%S")
   ncfile.softwareURL = "https://github.com/lvankampenhout/libvector"
   ncfile.netcdf = netCDF4.__netcdf4libversion__

   ncfile.creation_date = time.strftime('%Y-%m-%d %X')
   #ncfile.frequency = "mon" 

   # Create dimensions
   ncfile.createDimension('longitude', vmv.nlon)
   ncfile.createDimension('latitude', vmv.nlat)
   ncfile.createDimension('time', None)
   ncfile.createDimension('lev',nlev)

   # Define the coordinate var
   lons   = ncfile.createVariable('longitude', 'f4', ('longitude',))
   lats   = ncfile.createVariable('latitude', 'f4', ('latitude',))
   times    = ncfile.createVariable('time', 'f8', ('time',))
   levs   = ncfile.createVariable('lev', 'i4', ('lev',))

   # Assign units attributes to coordinate var data
   lons.units   = "degrees_east"
   lons.axis = "Y"
   lats.units   = "degrees_north"
   lats.axis = "X"
   #times.units    = "days since 1-01-01 00:00:00"
   times.units = vmv.time_units
   
   levs.units   = "MEC level number"

   
   # Write data to coordinate var
   lons[:]    = vmv.lons
   lats[:]    = vmv.lats
   #times[:]   = times_
   times[:] = vmv.time
   levs[:]    = range(0,nlev)

   # Write custom elevations, if any
   if (custom_levs == None):
      ncfile.vertical_levels = "no vertical interpolation was applied; MEC elevation is variable across grid cells"
   else:
      ncfile.vertical_levels = "interpolated to user-specified heights"
      elevation  = ncfile.createVariable('elevation', 'f4', ('lev',))
      elevation.units = "m"
      elevation[:]    = custom_levs
      
   
   # Write data

   #print(var3d.shape) #(12, 192, 288, 10)
   var3d = var3d.transpose((0,3,1,2)) # permute columns
   #print(var3d.shape) #(12, 10, 192, 288)
   
   # Create output variable of correct dimensions
   # 'f4' stands for floating point 4 bytes, i.e. single precision
   # change to 'f8' for double precision
   var            = ncfile.createVariable(vmv.varname,'f4',('time','lev','latitude','longitude',), fill_value=default_fillvals['f4'])
   var.units      = vmv.units
   var.long_name  = vmv.long_name

   var[:,:,:,:]   = default_fillvals['f4'] # Initialise with missing value everywhere (will be replaced later)
   
   var[:] = var3d[:]
   
   ncfile.close()
