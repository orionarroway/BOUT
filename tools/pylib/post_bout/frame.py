import numpy as np
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.colors as colors
try:
    import matplotlib.artist as artist 
    import matplotlib.ticker as ticker
    import matplotlib.animation as animation  
    from matplotlib.lines import Line2D
    import mpl_toolkits.axisartist as axisartist
    import pylab

except:
    print "Can't import what you need"


# generic frame object, derives from ndarray since at its core its basically
# data with some annotations,metadata and presentation parameters
# http://docs.scipy.org/doc/numpy/user/basics.subclassing.html

class Frame(np.ndarray):

    def __new__(cls, data,meta=None):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        
        obj = np.asarray(data).view(cls)
        # add the new attribute to the created instance
        
        if meta is not None:
            for k, v in meta.items():
                setattr(obj, k, v)
    
        if data.ndim == 3:   
            obj.nt,obj.nx, obj.ny = obj.shape
            nt,nx,ny = data.shape
            

        elif obj.ndim == 2:
            obj.nt, obj.nx = obj.shape
        elif obj.ndim == 1:
            obj.nt = obj.shape[0]
            
        if hasattr(obj, 'center'):
            print nx,ny
            if obj.center==True:
                data = np.roll(data,nx/2,axis=1)
                data = np.roll(data,ny/2,axis=2)
        
    
        if hasattr(obj,'zoom'):
            data = data[:,obj.nx/2-obj.nx/16:obj.nx/2+obj.nx/16,
                          obj.ny/2-obj.ny/16:obj.ny/2+obj.ny/16]
     
        obj = np.asarray(data).view(cls)  
        
        if meta is not None:
            for k, v in meta.items():
                setattr(obj, k, v)

             
        if not hasattr(obj,'data_c'):
        #     print 'no data_c'
            obj.data_c = data
        
        #print meta.keys()
        #print obj.data_c.shape    
        # if meta is not None:
        #     for k, v in meta.items():
        #         setattr(obj, k, v)
                
        if obj.ndim == 3:   
            obj.nt,obj.nx, obj.ny = obj.shape
            obj.amp = abs(obj).max(1).max(1)
        elif obj.ndim == 2:
            obj.nt, obj.nx = obj.shape
            obj.x = np.arange(obj.nx)
        elif obj.ndim == 1:
            obj.nt = obj.shape[0]        
                
        
    
        print 'nt: ', obj.nt  
        

        #params for 2d (imshow)
        obj.interpolation='nearest'
        obj.aspect = 'auto'
        obj.cmap= plt.get_cmap('jet',2000) 
        obj.t = 0
        
        
        obj.img = None
        obj.ax = None
        obj.img_sig =None
        
        # imgrid.append(ax.imshow(data_n[0,:,:],aspect='auto',cmap=jet,
        #                         interpolation='bicubic'))
        # Finally, we must return the newly created object:
        return obj
    def render(self,fig,rect):
        
        # def setup_axes(fig, rect):
        #     ax = axisartist.Subplot(fig, rect)
        #     fig.add_subplot(ax)
         
        # ax = setup_axes(fig,221)  
       
        self.ax = fig.add_subplot(rect)
        t = self.t

        #print self.interpolation
        
        if self.ndim == 3:
            self.img = self.ax.imshow((self[t,:,:].real)/self.amp[t],aspect= self.aspect,cmap = self.cmap,
                                      interpolation=self.interpolation,origin='lower')
            # if hasattr(self,'mask'):
            #      thres = 1.05*np.min(self[self.t,:,:])
            #      masked_array=np.ma.masked_where(self[self.t,:,:]<thres,self[self.t,:,:])
            #      self.cmap = plt.get_cmap('jet',2000) 
            #      self.cmap.set_bad('w',1.)
            # else:
            #     masked_array = self[self.t,:,:]
            #     thres = None
            # print masked_array.shape
            # self.img = self.ax.imshow(masked_array.real,aspect=self.aspect,origin='lower',
            #                           cmap=self.cmap,
            #                           norm = colors.Normalize(vmin = thres, clip = False))
                
            nlevels = 7
            self.nlevels = nlevels
            # if len(self.shape)==2:
            #     wire = obj
            # else:
            print self.shape
            
            #if hasattr(self,'data_c'):
            wire = self.data_c[self.t,:,:]
        
            self.cset_levels = np.linspace(np.min(wire), 
                                           np.max(wire),nlevels)
            levels = self.cset_levels
            removeZero = True
            if removeZero:   
                levels = levels[np.where(np.min(np.abs(levels)) < np.abs(levels))]
            
            self.cset = self.ax.contour(wire,self.cset_levels,colors='k',alpha=.7,linewidth=.1)
            
        elif self.ndim == 1:
            #print 'ampdot: ', self.shape,self[self.t]
            self.ax.plot(self.real)
            self.img, = self.ax.plot(self.t,self[self.t].real,color='red',marker='o', markeredgecolor='r')
        elif self.ndim == 2:
           
            self.img, = self.ax.plot(self.x,self[t,:].real)
            if hasattr(self,'sigma'):
                print self.sigma.shape
                self.img_sig = [self.ax.fill_between(
                    self.x,self[t,:]+self.sigma[t,:], 
                    self[t,:]-self.sigma[t,:], 
                    facecolor='yellow', alpha=0.5)]
        
        if hasattr(self,'t_array'):
            try:
                #print t
                self.tcount = self.ax.annotate(str('%03f' % self.t_array[t]),(.1,.1),
                                 xycoords='figure fraction',fontsize = 15)
            except:
                self.tcount = self.ax.annotate(str('%03f' % t),(.1,.1),
                                 xycoords='figure fraction',fontsize = 15)
            

    def update(self):
        if self.t < self.nt:
            self.t +=1
            t = self.t

            #3D 
            if self.ndim ==3:
                (self.img).set_data((self[self.t,:,:].real)/self.amp[t])
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
                wire = self.data_c[self.t,:,:]
                nlevels = self.nlevels
                self.cset_levels = np.linspace(np.min(wire.real), 
                                               np.max(wire.real),nlevels)
                self.cset = self.ax.contour(wire.real,self.cset_levels,colors='k',alpha=.7,linewidths=.5)
            #2D
            elif self.ndim ==2:
                print self.shape,self.t
                t = self.t
                self.img.set_data(np.arange(self.nx),self[t,:])
                self.ax.set_ylim([np.min(self[t,:]),np.max(self[t,:])])

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

    
    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None: return
        self.info = getattr(obj, 'info', None)


#class FrameArray(Frame):
def FrameMovie(frames,moviename='output',fast=True,bk=None,outline=True,
               t_array=None,encoder='mencoder',fps=5.0):
    
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
    from matplotlib import rc    

        
    lin_formatter = ticker.ScalarFormatter()
    lin_formatter.set_powerlimits((-2, 2))


    
    font = {'family' : 'normal',
            'weight' : 'normal',
            'size'   : 4}
    
    axes = {'linewidth': .5}
    tickset ={'markeredgewidth': .25}
    
    
    rc('font', **font)
    rc('axes',**axes)
    rc('lines',**tickset)
    
    plt.tick_params(axis='both',direction='in',which='both')
    
    jet = plt.get_cmap('jet',2000) 
    
    fig = plt.figure()
        
    nframes = len(frames)
    nrow = int(round(np.sqrt(nframes)))
    ncol = int(np.ceil(float(nframes)/nrow))

    
    def magic(numList):
        s = ''.join(map(str, numList))
        return int(s)

    for i,elem in enumerate(frames):
        print 'i: ',i
        elem.render(fig,magic([nrow,ncol,i+1]))

    def update_img(t):
        for elem in frames:
            elem.update()

    nt = frames[0].nt        
    ani = animation.FuncAnimation(fig,update_img,nt-2)    
    ani.save(moviename+'.mp4',writer=encoder,dpi=dpi,bitrate=20000,fps=5)
    
    plt.close(fig)
    
    return 0        
