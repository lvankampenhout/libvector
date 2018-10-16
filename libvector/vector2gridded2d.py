#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: L.vankampenhout@uu.nl
"""

from .VectorMecVariable import VectorMecVariable, GLC_NEC
from netCDF4 import Dataset, default_fillvals

def vector2gridded2d(vmv, fname_target):
   """
   Wrapper function for converting a VectorMecVariable into a 2D variable
   and writing the output to NetCDF

   :param vmv:             VectorMecVariable instance
   :param fname_target:    filename of output file (netCDF)
   """

   var2d = vmv.getGridded2d()

   # Open a new NetCDF file to write the data to. For format, you can choose from
   # 'NETCDF3_CLASSIC', 'NETCDF3_64BIT', 'NETCDF4_CLASSIC', and 'NETCDF4'
   ncfile = Dataset(fname_target, 'w', format='NETCDF4')
   ncfile.description = 'Gridded field from CLM vector output'

   # Create dimensions
   ncfile.createDimension('longitude', vmv.nlon)
   ncfile.createDimension('latitude', vmv.nlat)
   ncfile.createDimension('time', None)

   # Define the coordinate var
   lons   = ncfile.createVariable('longitude', 'f4', ('longitude',))
   lats   = ncfile.createVariable('latitude', 'f4', ('latitude',))
   times    = ncfile.createVariable('time', 'f8', ('time',))

   # Assign units attributes to coordinate var data
   lons.units   = "degrees_east"
   lons.axis = "Y"
   lats.units   = "degrees_north"
   lats.axis = "X"
   #times.units    = "days since 1-01-01 00:00:00"
   times.units = vmv.time_units

   #levs.units   = "MEC level number"

   # Write data to coordinate var
   lons[:]    = vmv.lons
   lats[:]    = vmv.lats
   #times[:]   = times_
   times[:] = vmv.time
   #levs[:]    = range(0,GLC_NEC)

   # Write data
   #print(sno_gs.shape) #(12, 192, 288, 10)
   #sno_gs = sno_gs.transpose((0,1,2)) # permute columns
   #print(sno_gs.shape) #(12, 192, 288, 10)

   # Create output variable of correct dimensions
   # 'f4' stands for floating point 4 bytes, i.e. single precision
   # change to 'f8' for double precision
   var = ncfile.createVariable(vmv.varname,'f4',('time','latitude','longitude',),fill_value=default_fillvals['f4'])
   var.units      = vmv.units
   var.long_name  = vmv.long_name

   #var[:,:,:] = default_fillvals['f4'] # Initialise with missing value everywhere (will be replaced later)
	
   var[:] = var2d[:]
   ncfile.close()
