#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
   example 03
   
   Read single vector file and convert variable "QICE" to 3d gridded variable
   using custom levels. Store result in NetCDF.
"""
import sys

# import libvector package from local directory tree
sys.path.insert(0, "../libvector")

from VectorMecVariable import VectorMecVariable
from vector2gridded3d import vector2gridded3d

#fname_vector ='/glade2/scratch2/lvank/archive/f.e20.FHIST.f09_001/lnd/hist/f.e20.FHIST.f09_001.clm2.h2.1983-05.nc'
fname_vector='/glade2/scratch2/lvank/archive/avg2/f.e20.FHIST.f09_001/1979-1983/vector/QICE_f.e20.FHIST.f09_001_yearmean.nc'

vmv = VectorMecVariable("QICE", fname_vector )
#vector2gridded3d(vmv, "qice_gridded3d.nc")

fname_cpl_restart = "/glade2/scratch2/lvank/archive/f.e20.FHIST.f09_001/rest/1994-01-01-00000/f.e20.FHIST.f09_001.cpl.r.1994-01-01-00000.nc"
vmv.setGlcTopoCouplerFile(fname_cpl_restart)
#vmv.setGlcTopoHistfile(fname_vector )

# apply unit scaling: mm/s to mm/year
fac = (86400. * 365)
vmv.applyFactor(fac)

# define custom levels
#levs = (0, 100, 200, 500, 1000, 1500, 2000)
levs = [100.0, 300.0, 550.0, 850.0, 1150.0, 1450.0, 1800.0, 2250.0, 2750.0, 3500.0] # MEC default midpoints 

# convert 3D output to custom levels and export to file
#fld = vmv.getGridded3dCustomLevels(levs) # without wrapper
vector2gridded3d(vmv, "qice_gridded3d_custom.nc", levs) # with wrapper

