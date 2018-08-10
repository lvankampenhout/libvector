#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
   Converting QICE from vector file into a 2d gridded variable using a wrapper script. 

   The result is a NetCDF file.
"""
import sys

# include libvector package (directory) in local directory tree
sys.path.insert(0, "..")

from libvector import VectorMecVariable, vector2gridded2d 

filename='/glade2/scratch2/lvank/archive/f.e20.FHIST.f09_001/lnd/hist/f.e20.FHIST.f09_001.clm2.h2.1983-05.nc'

vmv = VectorMecVariable("QICE", filename)

# Set glacier fraction per MEC column using coupler history file
#vmv.setGlcFracCouplerFile("/glade2/scratch2/lvank/archive/f.e20.FHIST.f09_001/cpl/hist/f.e20.FHIST.f09_001.cpl.hi.1980-01-01-00000.nc")

# Set glacier fraction per MEC column using surfdata file
vmv.setGlcFracSurfdat("/glade/p/cesmdata/cseg/inputdata/lnd/clm2/surfdata_map/surfdata_0.9x1.25_16pfts_Irrig_CMIP6_simyr1850_c170824.nc")

# Convert 3D vector dataset to 2d gridded and store
vector2gridded2d(vmv, "qice_gridded2d.nc")
