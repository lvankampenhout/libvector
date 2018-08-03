#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
   example 02
   
   Read single vector file and convert variable "QICE" to 3d gridded variable
   using wrapper script. Store result in NetCDF.
"""
import sys

# import libvector package from local directory tree
sys.path.insert(0, "../libvector")

from VectorMecVariable import VectorMecVariable
from vector2gridded3d import vector2gridded3d

fname_vector='/glade2/scratch2/lvank/archive/f.e20.FHIST.f09_001/lnd/hist/f.e20.FHIST.f09_001.clm2.h2.1983-05.nc'
vmv = VectorMecVariable("QICE", fname_vector)

# apply unit scaling: mm/s to mm/year
fac = (86400. * 365)
vmv.applyFactor(fac)

# convert to 3D output (no corrections for elevation) and export to file
vector2gridded3d(vmv, "qice_gridded3d.nc")