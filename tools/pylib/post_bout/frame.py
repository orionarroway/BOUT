import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
#from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.colors as colors


# try:
import matplotlib.artist as artist 
import matplotlib.ticker as ticker   
from matplotlib.ticker import FormatStrFormatter
import matplotlib.animation as animation  
from matplotlib.lines import Line2D
import mpl_toolkits.axisartist as axisartist
import pylab

import pylab
import matplotlib.axis as axis

# print dir(xtick)                
# exit()
# except:
#     print "Can't import what you need"


# generic frame object, derives from ndarray since at its core its basically
# data with some annotations,metadata and presentation parameters
# http://docs.scipy.org/doc/numpy/user/basics.subclassing.html

class Frame(np.ndarray):

    def __new__(cls, data,meta=None):
        print 'new frame'
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        #obj = np.asarray(data).view(cls)  
        obj = np.asarray(data).view(cls)
        # add the new attribute to the created instance
        
        if meta is not None:
            for k, v in meta.items():
                setattr(obj, k, v)
        
        defaults = {'dx':1,'x0':0,'dy':1,'y0':0,'stationary':False,
                    'yscale':'linear','title':'','xlabel':'','ylabel':'',
                    'style':'','fontsz':6,'ticksize':6,'contour_only':False,
                    'alpha':1,'cmap':'Blues','colors':'k','markersize':30,'raster':True,
                    'linewidth':.3}   
        

        for key,val in defaults.items():
            if not hasattr(obj,key):
                #print 'setting: ',key,val
                setattr(obj, key, val)

        #its more economical to set some defaults rather than have to re-enter for each array type
        

   
        if not obj.stationary:   
            if obj.ndim == 3:   
                obj.nt,obj.nx, obj.ny = obj.shape
                nt,nx,ny = obj.shape
                obj.amp = abs(obj).max(1).max(1)
                
                #for now limit ourselves to 0 or 1D dx dy arrays
                obj.x = obj.dx*np.arange(obj.nx)
                obj.x = np.repeat(obj.x,obj.ny)
                obj.x = obj.x.reshape(nx,ny)
                
                obj.y = obj.dy*np.arange(obj.ny)
                obj.y = np.repeat(obj.y,obj.nx)
                obj.y = np.transpose(obj.y.reshape(ny,nx))
        
                 
                
                #print obj.dx,obj.dy
            elif obj.ndim == 2:
                obj.nt, obj.nx = obj.shape
                obj.x = obj.x0+obj.dx*np.arange(obj.nx)
                obj.Lx = obj.x.max()
                
            elif obj.ndim == 1:
                obj.nt = obj.shape[0]
                obj.x = obj.x0+obj.dx*np.arange(obj.nt)
        else:
            if obj.ndim == 3:   
                obj.nx,obj.ny, obj.nz = obj.shape
                obj.amp = abs(obj).max()
            elif obj.ndim == 2:
                obj.nx, obj.ny = obj.shape
                obj.x = obj.x0+obj.dx*np.arange(obj.nx)
                obj.y = obj.y0+obj.dy*np.arange(obj.ny)
            elif obj.ndim == 1:
                obj.nx = obj.shape[0] 
                obj.x = obj.x0+obj.dx*np.arange(obj.nx)
            if not hasattr(obj,'nt'):
                obj.nt = 1
    
       # print 'nt: ', obj.nt  
      
        if hasattr(obj, 'center'):
            print nx,ny
            if obj.center==True:
                data = np.roll(data,nx/2,axis=1)
                data = np.roll(data,ny/2,axis=2)
        
    
        if hasattr(obj,'zoom'):
            data = data[:,obj.nx/2-obj.nx/16:obj.nx/2+obj.nx/16,
                          obj.ny/2-obj.ny/16:obj.ny/2+obj.ny/16]
     
        #obj = np.asarray(data).view(cls)  
        
        if meta is not None:
            for k, v in meta.items():
                setattr(obj, k, v)

             
        if not hasattr(obj,'data_c'):
        #     print 'no data_c'
            obj.data_c = data
      
       # print 'nt: ', obj.nt  
        

        #params for 2d (imshow)
        obj.interpolation='bilinear'
        obj.aspect = 'auto'
        obj.cmap= plt.get_cmap(obj.cmap,2000) 
        obj.t = 0
        
        
        #we can't expect pointer to work if we reissun
        
        #create a dummy figure,scence variable
        #fig = plt.figure()

        obj.img = None
        obj.ax = None
        obj.img_sig = None
        obj.mesh = None
        obj.ax_3d = None
        
        # imgrid.append(ax.imshow(data_n[0,:,:],aspect='auto',cmap=jet,
        #                         interpolation='bicubic'))
        # Finally, we must return the newly created object:
        return obj
    
    def array_finalize(self, obj):
        #print 'array_finalize'

        #copy all frame like attributes - not nd.array-like ones

        #see whats missing
        copyme = set(dir(obj)).difference(set(dir(self)))
        #print copyme
        
        
        for key in copyme:
            if not hasattr(self,key): #why 2x check?
                setattr(self, key, getattr(obj,key))

    # def __array_finalize__(self, obj):
    #     #print 'array_finalize'

    #     #copy all frame like attributes - not nd.array-like ones

    #     #see whats missing
    #     copyme = set(dir(obj)).difference(set(dir(self)))
    #     #print copyme
        
        
    #     for key in copyme:
    #         if not hasattr(self,key): #why 2x check?
    #             setattr(self, key, getattr(obj,key))
   
        
    def reset(self):
        self.ax = None
        self.img = None
        self.img_sig = None
        self.ax_3d = None
        self.t = 0

    def render(self,fig,rect,rasterized=False):
        
        #print 'render !'
        # def setup_axes(fig, rect):
        #     ax = axisartist.Subplot(fig, rect)
        #     fig.add_subplot(ax)
         
        # ax = setup_axes(fig,221)  
        axes = {'linewidth': .5}
        tickset ={'markeredgewidth': .25}
        
        # from matplotlib import rc

        # font = {'family' : 'normal',
        #         'weight' : 'normal'}

        # rc('font', **font)
        # rc('axes',**axes)
        # rc('lines',**tickset)
        
        
        
        #plt.tick_params(axis='both',direction='in',which='both')
        #once rendered self.ax is always a regural maptplot axis object

        if self.ax == None:
            self.ax = fig.add_subplot(rect,rasterized=rasterized)
        
# except:
#     print "Can't import what you need"


# generic frame object, derives from ndarray since at its core its basically
# data with some annotations,metadata and presentation parameters
# http://docs.scipy.org/doc/numpy/user/basics.subclassing.html

class Frame(np.ndarray):

    def __new__(cls, data,meta=None):
        print 'new frame'
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        #obj = np.asarray(data).view(cls)  
        obj = np.asarray(data).view(cls)
        # add the new attribute to the created instance
        
        if meta is not None:
            for k, v in meta.items():
                setattr(obj, k, v)
        
        defaults = {'dx':1,'x0':0,'dy':1,'y0':0,'stationary':False,
                    'yscale':'linear','title':'','xlabel':'','ylabel':'',
                    'style':'','fontsz':6,'ticksize':6,'contour_only':False,
                    'alpha':1,'cmap':'Blues','colors':'k','markersize':30,'raster':True,
                    'linewidth':.3}   
        

        for key,val in defaults.items():
            if not hasattr(obj,key):
                #print 'setting: ',key,val
                setattr(obj, key, val)

        #its more economical to set some defaults rather than have to re-enter for each array type
        

   
        if not obj.stationary:   
            if obj.ndim == 3:   
                obj.nt,obj.nx, obj.ny = obj.shape
                nt,nx,ny = obj.shape
                obj.amp = abs(obj).max(1).max(1)
                
                #for now limit ourselves to 0 or 1D dx dy arrays
                obj.x = obj.dx*np.arange(obj.nx)
                obj.x = np.repeat(obj.x,obj.ny)
                obj.x = obj.x.reshape(nx,ny)
                
                obj.y = obj.dy*np.arange(obj.ny)
                obj.y = np.repeat(obj.y,obj.nx)
                obj.y = np.transpose(obj.y.reshape(ny,nx))
        
                 
                
                #print obj.dx,obj.dy
            elif obj.ndim == 2:
                obj.nt, obj.nx = obj.shape
                obj.x = obj.x0+obj.dx*np.arange(obj.nx)
                obj.Lx = obj.x.max()
                
            elif obj.ndim == 1:
                obj.nt = obj.shape[0]
                obj.x = obj.x0+obj.dx*np.arange(obj.nt)
        else:
            if obj.ndim == 3:   
                obj.nx,obj.ny, obj.nz = obj.shape
                obj.amp = abs(obj).max()
            elif obj.ndim == 2:
                obj.nx, obj.ny = obj.shape
                obj.x = obj.x0+obj.dx*np.arange(obj.nx)
                obj.y = obj.y0+obj.dy*np.arange(obj.ny)
            elif obj.ndim == 1:
                obj.nx = obj.shape[0] 
                obj.x = obj.x0+obj.dx*np.arange(obj.nx)
            if not hasattr(obj,'nt'):
                obj.nt = 1
    
        print 'nt: ', obj.nt  
      
        if hasattr(obj, 'center'):
            print nx,ny
            if obj.center==True:
                data = np.roll(data,nx/2,axis=1)
                data = np.roll(data,ny/2,axis=2)
        
    
        if hasattr(obj,'zoom'):
            data = data[:,obj.nx/2-obj.nx/16:obj.nx/2+obj.nx/16,
                          obj.ny/2-obj.ny/16:obj.ny/2+obj.ny/16]
     
        #obj = np.asarray(data).view(cls)  
        
        if meta is not None:
            for k, v in meta.items():
                setattr(obj, k, v)

             
        if not hasattr(obj,'data_c'):
        #     print 'no data_c'
            obj.data_c = data
      
        print 'nt: ', obj.nt  
        

        #params for 2d (imshow)
        obj.interpolation='bilinear'
        obj.aspect = 'auto'
        obj.cmap= plt.get_cmap(obj.cmap,2000) 
        obj.t = 0
        
        
        #we can't expect pointer to work if we reissun
        
        #create a dummy figure,scence variable
        #fig = plt.figure()

        obj.img = None
        obj.ax = None
        obj.img_sig = None
        obj.mesh = None
        obj.ax_3d = None
        
        # imgrid.append(ax.imshow(data_n[0,:,:],aspect='auto',cmap=jet,
        #                         interpolation='bicubic'))
        # Finally, we must return the newly created object:
        return obj
    
    def array_finalize(self, obj):
        #print 'array_finalize'

        #copy all frame like attributes - not nd.array-like ones

        #see whats missing
        copyme = set(dir(obj)).difference(set(dir(self)))
        #print copyme
        
        
        for key in copyme:
            if not hasattr(self,key): #why 2x check?
                setattr(self, key, getattr(obj,key))

    # def __array_finalize__(self, obj):
    #     #print 'array_finalize'

    #     #copy all frame like attributes - not nd.array-like ones

    #     #see whats missing
    #     copyme = set(dir(obj)).difference(set(dir(self)))
    #     #print copyme
        
        
    #     for key in copyme:
    #         if not hasattr(self,key): #why 2x check?
    #             setattr(self, key, getattr(obj,key))
   
        
    def reset(self):
        self.ax = None
        self.img = None
        self.img_sig = None
        self.ax_3d = None
        self.t = 0

    def render(self,fig,rect,rasterized=False):
        
        #print 'render !'
        # def setup_axes(fig, rect):
        #     ax = axisartist.Subplot(fig, rect)
        #     fig.add_subplot(ax)
         
        # ax = setup_axes(fig,221)  
        axes = {'linewidth': .5}
        tickset ={'markeredgewidth': .25}
        
        # from matplotlib import rc

        # font = {'family' : 'normal',
        #         'weight' : 'normal'}

        # rc('font', **font)
        # rc('axes',**axes)
        # rc('lines',**tickset)
        
        
        
        #plt.tick_params(axis='both',direction='in',which='both')
        #once rendered self.ax is always a regural maptplot axis object

        if self.ax == None:
            self.ax = fig.add_subplot(rect,rasterized=rasterized)
        #xtick = matplotlib.axis.XTick
       
        #print self.ax,self.ndim  
        
        # if type(self.ax) is list:  
        #     self.ax = self.ax[0]
            
        print self.ax
            
        t = self.t

        #print self.interpolation
        
        if self.ndim == 3:
            
            if self.stationary:
                #need vtk to to do good volume renderign here
                self.img = self.ax.imshow((self[t,:,:].real)/self.amp[t],
                                          aspect= self.aspect,cmap = self.cmap,
                                          interpolation=self.interpolation,
                                          origin='lower')
                
            else:  
                print np.min(self.x)
                
                if self.contour_only is False:
                    self.img = self.ax.imshow(
                        ((self[t,:,:].real)/self.amp[t]).transpose(),
                        aspect= self.aspect,cmap = self.cmap,
                        interpolation=self.interpolation,
                        extent=[self.x.min(),self.x.max(),
                                self.y.min(),self.y.max()],
                        origin='lower',rasterized = self.raster,
                        linewidths=self.linewidth)
                    #self.ax_3d = fig.gca(projection='3d')
                    # X, Y = np.meshgrid(self.x, self.y)
                    # self.mesh = self.ax_3d.plot_surface(X,Y,((self[t,:,:].real)/self.amp[t]).transpose())

                    
                
                print self.x.shape, self.y.shape
            
            nlevels = 7
            self.nlevels = nlevels
            # if len(self.shape)==2:
            #     wire = obj
            # else: 
            print self.shape
            
            #if hasattr(self,'data_c'):
            
            print 'data_c: ',self.data_c.shape
            if self.data_c.ndim == 3: 
                wire = self.data_c[self.t,:,:]
            else:
                wire = self.data_c

            self.cset_levels = np.linspace(np.min(wire), 
                                           np.max(wire),nlevels)
            levels = self.cset_levels
            removeZero = True
            if removeZero:   
                levels = levels[np.where(np.min(np.abs(levels)) < np.abs(levels))]
            
            self.cset = self.ax.contour(self.x,self.y,wire,self.cset_levels,colors='k',alpha=1,linewidths=self.linewidth)
            
            if hasattr(self,'overplot'):
                if type(self.overplot) is list:
                     for subelem in self.overplot:
                         self.ax.plot(self.x,subelem[0:len(self.x)],alpha = self.alpha)
                else:
                    self.ax.plot(self.x,self.overplot[0:len(self.x)],alpha = self.alpha)
            
            #self.ax.set_ylim(self.y.min(),self.y.max())
      
        elif self.ndim == 1:
            
            #print 'ampdot: ', self.shape,self[self.t]
            if self.stationary:
                self.img, = self.ax.plot(self.x,self.real,self.style,linewidth=self.linewidth,
                                         markersize=self.markersize,
                                         alpha=self.alpha)
                #self.img, = self.ax.plot(self.x,self.real,'-',linewidth=50)
                if hasattr(self,'sigma'):
                    self.img_sig = [self.ax.fill_between(
                        self.x,self+self.sigma,self-self.sigma, 
                        facecolor='yellow', alpha=0.5)]
                  
            else:
                self.ax.plot(self.x,self.real,self.style)
                self.img, = self.ax.plot(self.x[self.t],self[self.t].real,color='red',marker='o', markeredgecolor='r',alpha=0)
                

            if hasattr(self,'overplot'):
                if type(self.overplot) is list:
                     for subelem in self.overplot:
                         self.ax.plot(self.x,subelem[0:len(self.x)],alpha = self.alpha)
                else:
                    self.ax.plot(self.x,self.overplot[0:len(self.x)],alpha = self.alpha)

            
        

        elif self.ndim == 2:
            #print 'render 2'
            if self.stationary:
                if self.contour_only:
                    self.cset = self.ax.contour(self.x,self.y,self.transpose(),alpha = self.alpha,
                                                colors=self.colors,linewidths=self.linewidth)
                    
                else:

                    #print yy.max()
                    self.img = self.ax.imshow(self.transpose(),aspect= self.aspect,cmap = self.cmap,
                                              interpolation=self.interpolation,
                                              extent=[self.x.min(),self.x.max(),
                                                      self.y.min(),self.y.max()],
                                              origin='lower',alpha = self.alpha, 
                                              rasterized=self.raster)
                    
                    # self.cset = self.ax.contour(self.x,self.y,self.transpose(),
                    #                             alpha=self.alpha,colors = self.colors)
                    print 'rendering . . ',self.x.min()
                    
            else:
                #print 'render 2img'
                self.img, = self.ax.plot(self.x,self[t,:].real,self.style,rasterized=self.raster)
                #print 'render 2img'
                #exit()
                if hasattr(self,'sigma'):
                    print self.sigma.shape
                    self.img_sig = [self.ax.fill_between(
                            self.x,self[t,:]+self.sigma[t,:], 
                            self[t,:]-self.sigma[t,:], 
                            facecolor='yellow', alpha=0.5,rasterized=self.raster)]

                if hasattr(self,'overplot'):
                    self.ax.plot(self.x,self.overplot,rasterized=self.raster)
                #print 'render 2sigs'
                #exit()
    
        if hasattr(self,'t_array'):
            try:
                #print t
                self.tcount = self.ax.annotate(str('%03f' % self.t_array[t]),(.1,.1),
                                               xycoords='figure fraction',fontsize = 15)
            except:
                self.tcount = self.ax.annotate(str('%03f' % t),(.1,.1),
                                               xycoords='figure fraction',fontsize = 15)
          
        self.ax.set_ylabel(self.ylabel,fontsize = self.fontsz,
                           rotation='horizontal')
        #self.ax.yaxis.set_label_coords(-0.050,.95)
        self.ax.set_xlabel(self.xlabel,fontsize =self.fontsz)
        
        #self.ax.xaxis.set_label_coords(1.05, -0.0250)
        self.ax.set_title(self.title,fontsize = self.fontsz)
        #self.ax.xaxis.set_label_coords(.7, -0.2)
        #self.ax.xaxis('tight')
        
        self.ax.set_yscale(self.yscale,linthreshy=1e-4)

        try:
            self.ax.grid(True,linestyle='-',color='.75',alpha=.5)
        except:
            self.ax.grid(True,linestyle='-',color='.75')
        self.ax.xaxis.set_label_coords(.7, -0.1)
        #self.ax.yaxis.set_label_coords(-.1, 0.50)
    

    def update(self):
       
        if self.t < self.nt:
            self.t +=1
            t = self.t

            #3D 
            if self.ndim ==3:
                if self.contour_only is False:
                    (self.img).set_data(((self[self.t,:,:].real)/self.amp[t]).transpose())
                # if hasattr(self,'mask'):
                #     thres = 1.1*np.min(self[self.t,:,:])
                #     masked_array=np.ma.masked_where(self[self.t,:,:] < thres,self[self.t,:,:])
                #     cmap = plt.get_cmap('jet',2000) 
                #     cmap.set_bad('w',1.)
                #     self.img.set_data(masked_array.real)
                try:    
                    for coll in self.cset.collections:
                        self.ax.collections.remove(coll)
                except:
                        'fail at removing cset'
                        
                        #print 'shape: ', self.ndim   
                        # if hasattr(self,'data_c'):
                if self.data_c.ndim ==3:
                    wire = self.data_c[self.t,:,:]
                else:
                    wire =  self.data_c
                   
                nlevels = self.nlevels
                self.cset_levels = np.linspace(np.min(wire.real), 
                                               np.max(wire.real),nlevels)
                self.cset = self.ax.contour(self.x,self.y,wire.real,self.cset_levels,colors='k',alpha=.7,linewidths=self.linewidth)
            #2D
            elif self.ndim ==2:
                if self.stationary:
                    pass
                else:
                    print self.shape,self.t
                    t = self.t
                    self.img.set_data(self.x,self[t,:])
                    #self.ax.axis('tight')
                    #self.ax.set_ylim[np.min(self[t,:]),np.max(self[t,:])])
                    
                    #print dir(self.img_sig)
                    #print 'collections', self.ax.collections #self.ax.collections.count()
                    if hasattr(self,'sigma'):
                        for coll in (self.ax.collections):
                            self.ax.collections.remove(coll)
                        self.ax.fill_between(
                            self.x,self[t,:]+self.sigma[t,:], 
                            self[t,:]-self.sigma[t,:], 
                            facecolor='yellow', alpha=0.5)

                # if hasattr(self,'sigma'):
                #     self.ax.fill_between(
                #         self.x,self[t,:]+self.sigma[t,:], 
                #         self[t,:]-self.sigma[t,:], 
                #         facecolor='yellow', alpha=0.5
                        
                
            elif self.ndim ==1:
                if self.stationary:
                    #self.ax.plot(self.x,self.real)
                    #self.ax.set_ylim([np.min(self),np.max(self)])
                    pass
                else:
                    self.img.set_data(self.t,self[self.t])

            if hasattr(self,'t_array'):
                self.ax.texts.remove(self.tcount) 
                
                try:
                #print t
                    self.tcount = self.ax.annotate(str('%g' % self.t_array[t]),(.1,.1),
                                     xycoords='figure fraction',fontsize = 20)
                except:
                    self.tcount = self.ax.annotate(str('%g' % t),(.1,.1),
                                 xycoords='figure fraction',fontsize = 20)    
#        if self.ndim ==1:

    
   


#class FrameAasray(Frame):
def FrameMovie(frames,moviename='output',fast=True,bk=None,outline=True,
               t_arraSy=None,encoder='ffmpeg',fps=5.0,fig=None):
    
    if fast:
        dpi = 100
    else:
        dpi = 240
    
    import matplotlib.artist as artist 
    import matplotlib.ticker as ticker
    import matplotlib.animation as animation  
    from matplotlib.lines import Line2D
    import mpl_toolkits.axisartist as axisartist
    import pylab
    from matplotlib import rc

        
    lin_formatter = ticker.ScalarFormatter()
    lin_formatter.set_powerlimits((1, 1))
    

    
    # font = {'family' : 'normal',
    #         'weight' : 'normal',
    #         'size'   : frames[0].ticksize}
    font = {'family' : 'normal',
            'weight' : 'normal'}
    
    
    axes = {'linewidth': .5}
    tickset ={'markeredgewidth': .25}
    
    
    rc('font', **font)
    rc('axes',**axes)
    rc('lines',**tickset)
    
    
    plt.tick_params(axis='both',direction='in',which='both')
    
    jet = plt.get_cmap('bone',2000) 
    
    if fig == None:
        fig = plt.figure()
        
    
    fig_ref =plt.figure()
    temp = fig_ref.add_subplot(111)
    axis_subplot = type(temp)

    nframes = len(frames) 

    shared = 0
    for elem in frames:
        if hasattr(elem,'shareax'):
            if elem.shareax ==True:
                shared = shared+1
                

    nframes = nframes - shared            

    nrow = int(round(np.sqrt(nframes)))
    ncol = int(np.ceil(float(nframes)/nrow))

    print nframes
    
    def magic(numList):
        s = ''.join(map(str, numList))
        return int(s)

    offset = 0
  
    for i,elem in enumerate(frames):
        #print 'elem',elem.title,elem.__class__,type(elem)
        
        print 'i: ',i,nrow,ncol,type(elem),nframes,nrow,ncol
        if type(elem) is list:
            print 'its a list'
            for subelem in elem:
               subelem.render(fig,magic([nrow,ncol,i+1-offset]))
               nt = subelem.nt
            #exit()
               
        else:
            print 'ndim: ',elem.ndim
            elem.render(fig,magic([nrow,ncol,i+1-offset]))
            #elem.render(fig2,magic([nrow,ncol,i+1-offset]))
            elem.ax.yaxis.set_major_formatter(lin_formatter)
            nt = elem.nt
            #exit()
            #elem.ax.yaxis.set_major_formatter(FormatStrFormatter('%1f'))
                #if hasattr(elem,'shareax'):
                #    if elem.shareax ==True:
                 #       offset = offset +1
 

    def flatten(l,flat_l):
        for el in l:
            if type(el) is list:
                flatten(el,flat_l)
            else:
                flat_l.append(el)
        
    flat_frames = []
    flatten(frames,flat_frames)



    print len(flat_frames), flat_frames[0].__class__


    
    def update_img(t):
        print 't: ' ,t
        for elem in flat_frames:
            print elem.shape,elem.stationary
            elem.update()

            #update_img(2)

    #let's draw a simple pdf

    #    update_img(0)
    
    try:
        ani = animation.FuncAnimation(fig,update_img,nt-2) 
    except:
        pass
    #ani = animation.FuncAnimation(fig,frames[0].update,nt-5) 
    ani.save(moviename+'.mp4',writer=encoder,dpi=dpi,bitrate=20000,fps=5)
    
    plt.close(fig)
    plt.close(fig_ref)

    for i,elem in enumerate(flat_frames):
        if hasattr(elem,'t'):
            elem.t = 0
    
    return 0        
