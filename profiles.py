
#Former member function of VectorMecVariable
#should be converted into standalone function that takes VectorMecVariable as input

import matplotlib.pyplot as plt
import matplotlib


   def get_profiles(self, imonth, lat_bounds, lon_bounds):
      """
      Return monthly profile integrated over an area which given by the bounds
      """

      var_out = np.zeros((self.ntime,self.nlats,self.nlons,GLC_NEC))    
      
      # :ctype_landice = 3 ;
      # :ctype_landice_multiple_elevation_classes = "4*100+m, m=1,glcnec" ;
      for lev in range(GLC_NEC):
         mask = (self.coltype==(400+lev+1))
         idx, = np.where(mask)
         ix = self.ixy[idx]-1
         iy = self.jxy[idx]-1
         
         #print(tskin[:,idx].shape, var_out[:,iy,ix,lev].shape)
         var_out[:,iy,ix,lev] = self.data[:,idx]
            
      # Mask out all points without GLC_MEC
      var_out = np.ma.masked_less(var_out, 1e-4)
   
      # Mask out points with missing value
      var_out = np.ma.masked_greater(var_out, 1e34)
   
   
      # some region around Greenland   
      r1=range(158,186)
      r2=range(220,288)
      ind = np.ix_(r1,r2)
          
      # ---------------------------------------------------
      # Plotting TG on a single level
      # ---------------------------------------------------
      lev = 0 # fifth ICE level (lev=4) ranges (1000,1300)m
   
      #levels = np.linspace(260,290,11)
      levels = np.linspace(265,275,11)
      cmap=plt.get_cmap()
      norm=matplotlib.colors.BoundaryNorm(levels,ncolors=cmap.N,clip=False)
      
      Z = var_out[imonth,:,:,lev]
      
      # Mask away virtual cells (mec_frac = 0.0)
      # ICE LEVELS START AT 1; ZERO IS BARE LAND
      #print(mec_frac.shape)
      Z = np.ma.masked_where(self.mec_frac[lev+1] < 1e-3, Z) 
      
      if (False):
         plt.figure()   
         plt.pcolormesh(lon2d[ind],lat2d[ind],Z[ind],cmap=cmap,norm=norm) #,levels=levels,extend='both')
         plt.title('TG lev = %d'%lev)
         plt.colorbar()
      
      """
      Elevation class heights
      
      shr/glc_elevclass_mod.F90
          case(10)
             topomax = [0._r8,   200._r8,   400._r8,   700._r8,  1000._r8,  1300._r8,  &
                                1600._r8,  2000._r8,  2500._r8,  3000._r8, 10000._r8]
             
      """
      topomax = np.asarray([0.,   200.,   400.,   700.,  1000.,  1300., 1600.,  2000.,  2500.,  3000., 10000])
      bin_center = (topomax[1::] + topomax[:-1])*0.5
                            
      b1 = np.logical_and(lon_bounds[0] <= lon2d, lon2d <= lon_bounds[1])
      b2 = np.logical_and(lat_bounds[0] <= lat2d, lat2d <= lat_bounds[1])
      B = np.logical_and(b1,b2)
      Bind = np.where(B) # indices
      Bmask = np.where(B,1,0) # mask (0,1)
      
      if (False):
         plt.figure()
         plt.pcolormesh(lon2d[ind],lat2d[ind],(Z*Bmask)[ind],edgecolor='k', lw=0.01,antialiased=False)
         plt.title('Western greenland mask lev = %d'%lev)
         plt.colorbar()   
         print('number of cells in region', Z[Bind].count())
      
      # CALCULATE MEAN TEMPERATURE AT EACH ELEVATION CLASS IN THIS REGION
      zmeans = np.zeros(GLC_NEC)
      zstd = np.zeros(GLC_NEC)
      for lev in range(GLC_NEC):
         Z = var_out[imonth,:,:,lev]
      
         Z = np.ma.masked_where(self.mec_frac[lev+1] < 1e-3, Z)
         zmeans[lev] = Z[Bind].mean()
         zstd[lev] = Z[Bind].std()
         #print('lev=',lev,'number of cells in region', Z[Bind].count())
   
      return zmeans, bin_center,zstd



