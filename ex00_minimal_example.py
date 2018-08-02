#!/usr/bin/env python3

from libvector.VectorMecVariable import VectorMecVariable

filename='/glade2/scratch2/lvank/archive/f.e20.FHIST.f09_001/lnd/hist/f.e20.FHIST.f09_001.clm2.h2.1983-05.nc'

vmv = VectorMecVariable("QICE", filename)
foo = vmv.getGridded3d()
