#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
   Converting QICE from vector file into a 3d gridded variable using the wrapper script,
   but now with custom output levels.

   The result is a NetCDF file.
"""
import sys

# include libvector package (directory) in local directory tree
sys.path.insert(0, "..")

from libvector import VectorMecVariable

fname_vector='/glade2/scratch2/lvank/archive/avg2/f.e20.FHIST.f09_001/1979-1983/vector/QICE_f.e20.FHIST.f09_001_yearmean.nc'
fname_vecinfo='/glade2/scratch2/lvank/archive/f.e20.FHIST.f09_001/lnd/hist/f.e20.FHIST.f09_001.clm2.h2.1983-05.nc'

vmv = VectorMecVariable("QICE", fname_vector, fname_vecinfo=fname_vecinfo) 

# apply unit scaling: mm/s to m
fac = (86400. * 365) / 1000.
vmv.applyFactor(fac, "m")
