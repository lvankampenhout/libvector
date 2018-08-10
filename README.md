
Package for reading and processing Community Land Model (CLM) vector output, in particular useful for processing multiple elevation class (MEC) output over glaciated landunits.

## What is vector output? 
Normal CLM output is layed out on a latitude/longitude grid with each number representing the grid cell average value. 
However, internally CLM grid cells are made out of columns, for instance crop, lake and swamp. 
Each column has a type called a "landunit", we refer to the CLM User Guide for more details.
In order to retrieve the column output one can set

```
hist_dov2xy = .false. 
```

in the CLM namelist. 
Instead of a structured lat-lon grid, the output is now unstructured and each value represents a column.
This we call *column* or *vector* output. 

## Multiple elevation classes
Here, we are interested in the vertical distribution of energy and mass over glaciers.
CLM is capable of using "Multiple Elevation Classes" (ref Lipscomb 2013), a subgrid scale parameterization which basically boils down to the fact that we have a independent CLM glacier columns at different heights within a grid cell.
The values at different heights can be obtained from the vector output (see above). 

## This package
The goal of this package is to take the unstructured vector output and turn that into something more useable: a structured lat-lon 3d gridded field. 
The core of this package is the `VectorMecVariable` class which represents exactly one variable stored in one vector history file.

## Input
The package works on CLM vector history output. 
Standard CESM runs do not have this!
To generate vector output, add e.g. these lines to your `user_nl_clm`:

```
   hist_nhtfrq = 0,-24,0
   hist_mfilt = 1,1,1
   hist_dov2xy = .true., .true, .false.
   
   ! Daily output
   ! hist_fincl2 = 'QSNOMELT'
   
   ! monthly, vector
   hist_fincl3 = 'QICE`
```

which define three output streams. Stream one (`*.h0.*.nc`) contains the gridded monthly data, stream two (`*.h1.*.nc`) contains daily gridded data and stream three (`*.h2.*.nc`) contains unstructured monthly vector data. 


## Importing the package
Include package from a relative path:
```python
sys.path.insert(0, "..")
from libvector import VectorMecVariable
```

or from an absolute path:
```python
sys.path.insert(0, "/glade/u/home/lvank/github/libvector/")
from libvector import VectorMecVariable
```

## Examples
see the `examples` directory. 

## Usage notes
Some operations require additional information, for instance the ice cover or the topographic height of columns.
**Alas, the documentation about this still needs to be written.**
Luckily, the package will yield a somewhat helpful error message in case a requirement hasn't been met.

## Getting help
Create an Github issue at https://github.com/lvankampenhout/libvector or contact me at L.vankampenhout@uu.nl

