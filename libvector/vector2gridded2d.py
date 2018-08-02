#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrapper function for converting a VectorMecVariable into a 2D variable
and writing the output to NetCDF

@author: L.vankampenhout@uu.nl
"""

import numpy as np
from netCDF4 import Dataset, default_fillvals
import matplotlib
import matplotlib.pyplot as plt
import os
import os.path

from string import Template
from DataReaderCesmVector import DataReaderCesmVector

def vector2gridded2d(varname, fname_vector, fname_target, fname_cpl_hist):
      """
      varname           CLM variable name
      fname_vector      filename of CLM vector output file
      fname_target      filename of output file (netCDF)
      fname_cpl_hist    filename of coupler history output file (needed for glacier fraction)
      """

      varname, units, vardesc, fac = x
      filename = S.substitute(varname=varname, case=case, period=period)
   
      datareader1 = DataReaderCesmVector(varname, filename, vector_info, ice_cover, fac)
      datareader1.setGlcFracSurfdat(ice_cover_including_ANT) # Antarctica missing in coupler ice frac

      sno_gs = datareader1.getGridded2d()
   
      # =====================================
      # Write NetCDF file with netcdf4-python
      # =====================================
      name = "gridded2d_%s_%s_%s_%s.nc" % (varname,case,period,filetype)
   
      # Open a new NetCDF file to write the data to. For format, you can choose from
      # 'NETCDF3_CLASSIC', 'NETCDF3_64BIT', 'NETCDF4_CLASSIC', and 'NETCDF4'
      ncfile = Dataset(name, 'w', format='NETCDF4')
      ncfile.description = 'Gridded field from CLM vector output'
   
      # Create dimensions
      ncfile.createDimension('longitude', nlon)
      ncfile.createDimension('latitude', nlat)
      ncfile.createDimension('time', None)
   
      # Define the coordinate var
      lons   = ncfile.createVariable('longitude', 'f4', ('longitude',))
      lats   = ncfile.createVariable('latitude', 'f4', ('latitude',))
      times    = ncfile.createVariable('time', 'f8', ('time',))
   
      # Assign units attributes to coordinate var data
      lons.units   = "degrees_east"
      lats.units   = "degrees_north"
      #times.units    = "days since 1-01-01 00:00:00"
      times.units = datareader1.time_units
   
      #levs.units   = "MEC level number"
   
      # Write data to coordinate var
      lons[:]    = lons_
      lats[:]    = lats_
      #times[:]   = times_
      times[:] = datareader1.time
      #levs[:]    = range(0,GLC_NEC)
   
   	# ----------
   	# WRITE DATA
   	# ----------
   
      print(sno_gs.shape) #(12, 192, 288, 10)
      #sno_gs = sno_gs.transpose((0,1,2)) # permute columns
      #print(sno_gs.shape) #(12, 192, 288, 10)
   
      # Create output variable of correct dimensions
      var = ncfile.createVariable(varname,'f4',('time','latitude','longitude',),fill_value=default_fillvals['f4'])
      var.units = "microns"
      var.long_name = vardesc 

#      var[:,:,:] = default_fillvals['f4'] # Initialise with missing value everywhere (will be replaced later)
   	
      var[:] = sno_gs[:]
   
   #   for imonth in range(0,12):
      ncfile.close()
   
   

