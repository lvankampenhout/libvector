#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
   Converting QICE from vector file into a 3d gridded variable using a wrapper script. 

   The result is a NetCDF file.
"""
import sys

# include libvector package (directory) in local directory tree
sys.path.insert(0, "..")

from libvector import VectorMecVariable, vector2gridded3d 

fname_vector='/glade2/scratch2/lvank/archive/f.e20.FHIST.f09_001/lnd/hist/f.e20.FHIST.f09_001.clm2.h2.1983-05.nc'
vmv = VectorMecVariable("QICE", fname_vector)

# convert to 3D output (no corrections for elevation) and export to file
vector2gridded3d(vmv, "qice_gridded3d.nc")
