#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
   Read single vector file and convert variable "QICE" to 3d gridded variable.

   The result is a numpy array.
"""
import sys

# include libvector package (directory) in local directory tree
sys.path.insert(0, "..")

from libvector import VectorMecVariable

filename='/glade2/scratch2/lvank/archive/f.e20.FHIST.f09_001/lnd/hist/f.e20.FHIST.f09_001.clm2.h2.1983-05.nc'

vmv = VectorMecVariable("QICE", filename)
foo = vmv.getGridded3d()
print(foo.shape)
