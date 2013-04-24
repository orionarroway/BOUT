# Display animations of data, similar to the IDL routine
# of the same name
#
# Ben Dudson, University of York, July 2009
#
#

#try:
try:

    import numpy as np
    import subprocess 
    import os
    from matplotlib.ticker import ScalarFormatter, FormatStrFormatter, MultipleLocator
    import matplotlib.ticker as ticker
    
except:
    print "ERROR: Showdata needs numpy, matplotlib and gobject modules"
    raise

try:
    import gobject
    widget = "gtk"
except:
    try:
        from wx import *
        widget = "wx"
    except:
        print "showdata: Couldn't import gobject or wx"
        #raise
    

try:
    import matplotlib
    if 'widget' in vars():
        if widget == "gtk":
            matplotlib.use('GTKAgg')
        else:
            matplotlib.use('Agg') # do this before importing pylab

    import matplotlib.pyplot as plt
    
except ImportError:
    print "ERROR: Showdata needs numpy, matplotlib and gobject modules"
    #raise
# try:
#     from wx import *
#     widget = "wx"
# except:
#     print "failed wx import"
    


def showdata(data, scale=True, loop=False,movie=False):
    try:
        print "Trying to import GTK..."
        import gobject
        widget = "gtk"
    except:
        print "failed\nTrying to import WX..."
   
    
   
    if widget == "gtk":
        matplotlib.use('GTKAgg')
    else:
        matplotlib.use('WXAgg') # do this before importing pylab

 


    """Animate a dataset, with time as first dimension
    
    2D - Show a line plot
    3D - Show a surface plot

    scale = True  Use the same scale for all times
    loop  = False Loop the dataset
    """

    if movie:
        return savemovie(data)

    size = data.shape
    ndims = len(size)
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    #ax.set_autoscale(true)
                        
    # w,h = fig.figaspect(1);
   
    if ndims == 2:
        # Animate a line plot
        
        if widget == "gtk":
            # GTK method (default)
            def animate():
                line, = ax.plot(data[0,:])
                if scale:
                    ax.set_ylim([np.min(data), np.max(data)])
                while True:
                    for i in np.arange(size[0]):
                        line.set_ydata(data[i,:])
                        if not scale:
                            ax.set_ylim([np.min(data[i,:]), np.max(data[i,:])])
                        fig.canvas.draw()
                        yield True
                    if not loop: break
            
            gobject.idle_add(lambda iter=animate(): iter.next())
        else:
            # WX widgets method
            line, = ax.plot(data[0,:])
            def animate(idleevent):
                if scale:
                    # Get data range
                    ax.set_ylim([np.min(data), np.max(data)])

                if animate.i == size[0]:
                    wx.GetApp().Bind(wx.EVT_IDLE, None)
                    return False
              
                line.set_ydata(data[animate.i,:])
                if not scale:
                    ax.set_ylim([np.min(data[i,:]), np.max(data[i,:])])
                fig.canvas.draw_idle()
                animate.i += 1
            animate.i = 0
            wx.GetApp().Bind(wx.EVT_IDLE, animate)
        
        plt.show()
        
    elif ndims == 3:
        # Animate a contour plot

        if widget == "gtk":
            def animate():
                cmap = None
                m = plt.imshow(data[0,:,:], interpolation='bilinear', cmap=cmap, animated=True,aspect='auto')
                #c = plt.contour(data[0,:,:],8,colors='k')
                while True:
                    for i in np.arange(size[0]):
                        m.set_data(data[i,:,:])
                        #c = plt.contour(data[0,:,:],8,colors='k')
                        fig.canvas.draw()
                        yield True
                    if not loop: break

            gobject.idle_add(lambda iter=animate(): iter.next())
        else:
            # WX widgets method
            cmap = None
            m = plt.imshow(data[0,:,:], interpolation='bilinear', cmap=cmap, animated=True,aspect='auto')
            def animateContour(idleevent):
                if animateContour.i == size[0]:
                    wx.GetApp().Bind(wx.EVT_IDLE, None)
                    return False

                m.set_data(data[animateContour.i,:,:])
                fig.canvas.draw_idle()
                animateContour.i += 1
            
            animateContour.i = 0

            wx.GetApp().Bind(wx.EVT_IDLE, animateContour)
        
        plt.show()
    else:
      print "Sorry can't handle this number of dimensions"


   
def new_save_movie(data,data2=None,dx=1,dy=1,xO=0,yO=0,
                   moviename='output',norm=False,
                   overcontour=True,aspect='auto',meta=None,mxg=2,
                   cache='/tmp/',hd=False,nlevels = 9,removeZero=True,
                   t_array=None,outline=True,bk=None,fps=5.0,fast=True):
    try:
        import matplotlib.animation as animation  
        from matplotlib.lines import Line2D
        import mpl_toolkits.axisartist as axisartist
        #from pylab import writer
    except:
        print "No animation submodule = no movie"
       

    size = data.shape
    ndims = len(size)
    nt,nx,nz = size  

    if norm: 
            data_n = normalize(data)
    else:
            data_n = data

    if data2 != None:
        data_c = data2
        if norm:
            data_c = normalize(data_c)
    else:
        data_c = data_n
    
    #put in a switch later    
    #os.system("rm "+cache+"*png")
    if fast:
        dpi = 100
    else:
        dpi = 400

    amp = abs(data).max(1).max(1)

    
    kx_max = nx/10.0
    kz_max = nz/10.0

    fft_data = np.fft.fft2(data)[:,0:kx_max,0:kz_max]
    power = fft_data.conj() * fft_data

    power.shape

    kz = (2.0*np.pi/(1.0*dy))*np.linspace(0,kz_max-1,kz_max)
    kz = np.repeat(kz,kx_max)
    kz = np.transpose(kz.reshape(kz_max,kx_max))

    kx =(2.0*np.pi/(1.0*dx))*np.linspace(0,kx_max-1,kx_max)
    kx = np.repeat(kx,kz_max)
    kx = kx.reshape(kx_max,kz_max)
    
    k = np.sqrt(kx**2 + kz**2)

    axhandle = []

    lin_formatter = ticker.ScalarFormatter()
    lin_formatter.set_powerlimits((-2, 2))

    font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 4}
    
    axes = {'linewidth': .5}
    tickset ={'markeredgewidth': .25}

    matplotlib.rc('font', **font)
    matplotlib.rc('axes',**axes)
    matplotlib.rc('lines',**tickset)

    #tickargs = {'which':'both','axis':'both','direction':'in'}
    matplotlib.pyplot.tick_params(axis='both',direction='in',which='both')
    #count = 0;
   
    def setup_axes(fig, rect):
        
        ax = axisartist.Subplot(fig, rect)
        fig.add_subplot(ax)
        
    # ax.set_yticks([0.2, 0.8])
    # ax.set_yticklabels(["short", "loooong"])
    # ax.set_xticks([0.2, 0.8])
    # ax.set_xticklabels([r"$\frac{1}{2}\pi$", r"$\pi$"])
        
        return ax
    
    def ani_frame():
        #count = 0;
        
        fig = plt.figure()
        fig.subplots_adjust(bottom=0.0)
        fig.subplots_adjust(top=1.0)
        fig.subplots_adjust(wspace=0.0)
        fig.subplots_adjust(hspace=0.0)
        #ax = fig.add_subplot(2,2,1)
        ax = setup_axes(fig,221)
        ax.set_aspect('equal')
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        
        t=0
        axhandle.append(ax)
        #1st image############
        imgrid = []
        
        imgrid.append(ax.imshow(data_n[0,:,:],aspect='auto',cmap='jet',
                                interpolation='bicubic'))
        
        #contour image overplots
        if len(data_c.shape)==2:
            wire = data_c
        else:
            wire = data_c[t,:,:]
        nlevels = 7
        levels = np.linspace(np.min(wire), 
                             np.max(wire),nlevels)
        # print np.where(np.min(np.abs(levels)) < np.abs(levels))
        removeZero = True
        if removeZero:   
            levels = levels[np.where(np.min(np.abs(levels)) < np.abs(levels))]
        
        ani_frame.cset = ax.contour(wire,levels,colors='k',alpha=.7,linewidth=.1)
        
        #2nd image ######################     
        #ax = fig.add_subplot(2,2,2)
        imgrid.append(fig.add_subplot(2,2,2))
        #imgrid.append(setup_axes(fig,222))

        t= np.linspace(0,nt-1,nt)
        ampline, = imgrid[1].plot(t,amp)
        ampdot, = imgrid[1].plot(t[0],amp[0],color='red',marker='o', markeredgecolor='r')
        #imgrid[-1].axis["left"].major_ticklabels.set_axis_direction("left")
        #imgrid[-1].axis["bottom"].major_ticklabels.set_va("bottom")
        
        imgrid[-1].yaxis.set_major_formatter(lin_formatter)
        imgrid[-1].tick_params(which='both',axis='both', direction='in')

        #rich fft info ###
       
        #imgrid.append(setup_axes(fig,223))
        imgrid.append(fig.add_subplot(2,2,3))

        imgrid[-1].set_yscale('log')
        #imgrid[-1].set_xscale('log')
        #imgrid[-1].yaxis.set_major_formatter(formatter)
       
        imgrid[-1].set_ylim(np.min(power[1:,:,:]),np.max(power[1:,:,:]))
        imgrid[-1].xaxis.set_major_formatter(lin_formatter)
        #imgrid[-1].axis('tight')
        #remove the dc component
        
        powerline, = imgrid[-1].plot((k.flatten())[1:],(power[0,:,:].flatten())[1:],marker='.',linestyle='None',markersize = 1)
        
        imgrid[-1].set_xlabel(r'$|k_{\perp} \rho_{ci}|$',fontsize=5)
        imgrid[-1].set_ylabel(r'$P_k$',fontsize=5,rotation='horizontal')
        
        #for img in imgrid:
        imgrid[-1].tick_params(which='both',axis='both', direction='in')
        

        fig.set_size_inches([5,3])
    

        # numicons = 2

        # for k in range(numicons):
        #     axicon = fig.add_axes([0.07+0.11*k,0.05,0.1,0.1])
        #     imarray.append(axicon.imshow(data_n[0,:,:],interpolation='nearest',alpha = .9))
        #     axicon.set_xticks([])
        #     axicon.set_yticks([])

        
        plt.tight_layout(pad=0.0, w_pad=0.1, h_pad=0.0)
        
        def update_img(n):
            
            tmp = data_n[n,:,:]
            imgrid[0].set_data(tmp)
            wire =data_c[n,:,:]
            #count = count+1;
           # cset = axhandle[0].contour(data_c[n,:,:],levels,colors='k',alpha=.7)
            
            print 'n: ', n
      
            try:
                #print 'collections: ',len(cset.collections)
                try:
                    ani_frame.cset
                except:
                    print 'csetnew not here'

                for coll in ani_frame.cset.collections:
                    try:
                        #print len(cset.collections)
                        #coll.set_linestyle('solid')
                        #axhandle[0].cset.collections.remove(coll)
                        axhandle[0].collections.remove(coll)
                    except:
                        print 'not in this collection'
  
            except:
                print 'no overcontour'
 
         
            try:
                ani_frame.cset = axhandle[0].contour(wire,levels,colors='k',alpha=.7,linewidths=.5)  
               # print len(csetnew.collections)
            except:
                print 'cant generate new contour set'

            #print t.shape,amp.shape
            ampdot.set_data(t[n],amp[n])

            powerline.set_data(k.flatten()[1:],power[n,:,:].flatten()[1:])
            #imgrid[2].axis('tight')
            #imgrid[2].plot(k.flatten(),power[n,:,:].flatten(),marker='.',linestyle='None',markersize = 1)
            #imgrid[2].set_ylim(np.max(np.min(power[:,:,:]),np.max(power[:,:,:])))
            #imgrid[2].set_ylim(
        
        ani = animation.FuncAnimation(fig,update_img,nt-1,interval=30)
        writer = animation.writers['ffmpeg'](fps=fps)

        ani.save(moviename+'.mp4',writer=writer,dpi=dpi)
        return ani

    ani_frame()


def savemovie(data,data2=None,dx=1,dy=1,xO=0,yO=0,
              moviename='output.avi',norm=False,
              overcontour=True,aspect='auto',meta=None,mxg=2,
              cache='/tmp/',hd=False,nlevels = 9,removeZero=True,
              t_array=None,outline=True,bk=None,fps=10.0):
    
    size = data.shape
    ndims = len(size)
    print 'Saving pictures -  this make take a while'
    print 'plot device: ', plt.get_backend()
    fig = plt.figure()
    


    if meta != None:
        r= meta['Rxy']['v'][:,5]
        DZ = meta['dz']
        #DZ = 1
            


    #matplotlib.use('Agg')
    
    files = []
    if ndims == 2: 
        
        #fig = plt.figure()
        scale = norm
        nt,nx = data.shape
        #ax = fig.add_subplot(111)
        #line, = 
        #ax.plot(data[0,:])
        #if scale:
            # Get data range
            #ax.set_ylim([np.min(data), np.max(data)])
          # while True:

        x = xO + dx*np.arange(nx)   
        for i in np.arange(nt):
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(x,data[i,:])
            
            print i
            #line.set_ydata(data[i,:])
            if not scale:
                ax.set_ylim([np.min(data[:]), np.max(data[:])])
                #fig.canvas.draw()
            filename = cache+str('%03d' % i) + '1D.png'
            textstr = r'$\T_ci$'+ '$=%.2f$'%(i)
            #props = dict(boxstyle='square', facecolor='white', alpha=0.3)
            # textbox = ax.text(xO, yO, textstr, 
            #                   transform=ax.transAxes, fontsize=10,
            #                   verticalalignment='top', bbox=props)
            print filename
            res = 100
            if hd:
                res = 130
            plt.savefig(filename, dpi=100)
            plt.close(fig)
            files.append(filename)
                
    
    elif ndims == 3: #typical nt x (nx or ny) X nz

        nt,nx,nz = data.shape
        
        if norm: 
            # amp = abs(data).max(1).max(1)
            # fourDamp = np.repeat(amp,nx*ny)
            # fourDamp = fourDamp.reshape(nt,nx,ny)
            # data_n = data/fourDamp
            data_n = normalize(data)
        else:
            data_n = data

        if data2 != None:
            data_c = data2
            if norm:
                data_c = normalize(data_c)
            
        else:
            data_c = data_n
            
        
        cmap = None
        #m = plt.imshow(data_n[0,:,:], interpolation='bilinear', cmap=cmap, animated=True,aspect=aspect)
        if meta != None:
            dzeta = (2*DZ*np.pi)/(nz-1)
            x = np.outer(r,np.cos(dzeta*np.arange(0,nz)))
            y = np.outer(r,np.sin(dzeta*np.arange(0,nz)))
            mxg = meta['MXG']['v']
            x = x[mxg:-mxg,:]
            y = y[mxg:-mxg,:]
            data_n = data_n[:,mxg:-mxg,:]
            if len(data_c.shape)==2:
                data_c = data_c[mxg:-mxg,:]
            else:
                data_c = data_c[:,mxg:-mxg,:]
        else:
            x = xO + dx*np.arange(nx)
            y = yO + dy*np.arange(nz)
            data_n = np.transpose(data_n,[0,2,1])
            
            if len(data_c.shape)==2:
                data_c = np.transpose(data_c)
            else:
                data_c = np.transpose(data_c,[0,2,1])
           
            print x.shape,y.shape,data_n.shape
        
        os.system("rm "+cache+"*png")
        #m = plt.contourf(x,y,data_n[0,:,:],30,cmap=cmap)
        # if overcontour:
        #c = plt.contour(x,y,data_c[0,:,:],8,colors='k')
        
        #construct a decent colormap that work from slide to slie

        #colormap = colors.Colormap()
        for i in np.arange(size[0]):
            fig = plt.figure()
            print i
            #m.set_data(data_n[i,:,:])
            ax = fig.add_subplot(111)
            #ax.annotate(str('%03d' % i),(xO +dx,yO+dy),fontsize = 20)
            level_fill =  np.linspace(np.min(data_n[i,:,:]), 
                                     np.max(data_n[i,:,:]),256)
            
            #norml = colors.BoundaryNorm(lev, 256)
            
            m = plt.contourf(x,y,data_n[i,:,:],levels = level_fill,cmap=plt.cm.winter)

            if outline:
                if bk == None:
                    bk = np.min(data[i,:,:])
                plt.contour(x,y,data_n[i,:,:],1,linewidths=1,
                            colors='r',alpha=1,
                            levels=[np.max(data_n[i])/10.0])
            
            #c = plt.contour(data[i,:,:],8,colors='k')
            #c.set_data(data[i,:,:])
            if overcontour:
               
                try:
                    for coll in c.collections:
                        try:
                            plt.gca().collections.remove(coll)
                        except:
                            print 'not in this collection'
                except:
                    print 'i = 0'

                if len(data_c.shape)==2:
                    wire = data_c
                else:
                    wire = data_c[i,:,:]
                levels = np.linspace(np.min(wire), 
                                     np.max(wire),nlevels)
                print np.where(np.min(np.abs(levels)) < np.abs(levels))
                if removeZero:
                    levels = levels[np.where(np.min(np.abs(levels)) < np.abs(levels))]
                try:
                    c = plt.contour(x,y,wire,levels,colors='k',alpha=.7)
                except:
                    print 'no contour for you'
                #ax.annotate(str('%03d' % i),(xO +dx,yO+dy),fontsize = 20)
           
                
            

            #fig.canvas.draw()         
            filename = cache+str('%03d' % i) + '.png'
            #textstr = r'$\T_ci$'+ '$=%.2f$'%(np.float(i))
            # textstr ='hello'
            # props = dict(boxstyle='square', facecolor='white')
            # textbox = ax.text(xO, yO, textstr, 
            #                   transform=ax.transAxes, fontsize=50,
            #                   verticalalignment='top', bbox=props)

            if t_array is not None:
                try:
                    ax.annotate(str('%03d' % t_array[i]),(xO +dx,yO+dy),fontsize = 20)

                except:
                    ax.annotate(str('%03d' % i),(xO +dx,yO+dy),fontsize = 20)
                                
            plt.savefig(filename, dpi=200)
            plt.close(fig)
            files.append(filename)
            #plt.clf()
        #plt.show()
    else:
      print "Sorry can't handle this number of dimensions"  
    
    print 'Making movie animation.mpg - this make take a while'
    command = ('mencoder',
               'mf://'+cache+'*.png',
               '-mf',
               'type=png:w=800:h=600:fps='+str(fps),
               '-ovc',
               'lavc',
               '-lavcopts',
               'vcodec=mpeg4',
               '-oac',
               'copy',
               '-o',
               moviename)
    
    subprocess.check_call(command)
    
    print files
    #cleanup = ('rm',files)
    os.system("rm "+cache+"*png")
    #matplotlib.use('pdf')
    #return 0

def test():
    x = np.arange(0, 2*np.pi, 0.01)
    t = np.arange(0, 2*np.pi, 0.1)
    nt = len(t)
    nx = len(x)

    # Animated line plots
    data = np.zeros([nt,nx])
    for i in np.arange(nt):
        data[i,:] = np.sin(x+i/10.0) * np.sin(10*x-i/5.0)
    
    showdata(data, loop=True)

    # Animated 2D plot
    y = x
    ny = len(y)

    data2d = np.zeros([nt,nx,ny])

    for i in np.arange(ny):
        data2d[:,:,i] = data * np.sin(y[i])

    showdata(data2d, loop=True)


def normalize(data):
    nt,nx,ny = data.shape
    amp = abs(data).max(1).max(1)
    fourDamp = np.repeat(amp,nx*ny)
    fourDamp = fourDamp.reshape(nt,nx,ny)
    data_n = data/fourDamp
    
    return data_n
