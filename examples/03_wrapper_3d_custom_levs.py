#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
   3D output with custom output levels. 

   The result is a NetCDF file.
"""
import sys

# include libvector package (directory) in local directory tree
sys.path.insert(0, "..")

from libvector import VectorMecVariable, vector2gridded3d 

fname_vector ='/glade2/scratch2/lvank/archive/f.e20.FHIST.f09_001/lnd/hist/f.e20.FHIST.f09_001.clm2.h2.1983-05.nc'

vmv = VectorMecVariable("QICE", fname_vector )

# set topography
fname_cpl_restart = "/glade2/scratch2/lvank/archive/f.e20.FHIST.f09_001/rest/1994-01-01-00000/f.e20.FHIST.f09_001.cpl.r.1994-01-01-00000.nc"
vmv.setGlcTopoCouplerFile(fname_cpl_restart) # Option A: from coupler restart file
#vmv.setGlcTopoHistfile(fname_vector ) # Option B: from TOPO_COL in vector history output (TOPO_COL must be present)

# define custom levels
levs = [100.0, 300.0, 550.0, 850.0, 1150.0, 1450.0, 1800.0, 2250.0, 2750.0, 3500.0] # MEC default midpoints 

# convert
###fld = vmv.getGridded3dCustomLevels(levs) # without wrapper
vector2gridded3d(vmv, "qice_gridded3d_custom.nc", levs) # with wrapper
