#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
   example 03
   
   Read single vector file and convert variable "QICE" to 3d gridded variable
   using custom levels. Store result in NetCDF.
"""

GLC_NEC = 10 # maximum number of elevation classes present in input file
COLUNIT_GLCMEC = 4 # for landunit types and column types, land ice = 7 (older CLM) land ice = 4 (newer CLM)

from netCDF4 import Dataset, default_fillvals

from libvector.VectorMecVariable import VectorMecVariable
from libvector.vector2gridded3d import vector2gridded3d

filename='/glade2/scratch2/lvank/archive/f.e20.FHIST.f09_001/lnd/hist/f.e20.FHIST.f09_001.clm2.h2.1983-05.nc'

vmv = VectorMecVariable("QICE", filename)
vector2gridded3d(vmv, "qice_gridded3d.nc")
