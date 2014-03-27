import subprocess,sys,os
from scipy.io.idl import readsav
from scipy.io import netcdf
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from frame import Frame

# from reportlab.pdfgen import canvas
# from reportlab.lib.enums import TA_JUSTIFY
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch

import matplotlib.pyplot as plt
def magic(numList):
        s = ''.join(map(str, numList))
        return int(s)



def get_fig_rec(key,fig_dict,fig_list):
    #print 'in get fig and rec',type(fig_list), type(fig_dict)
    print(fig_dict.keys())
    print(key)
    if  (key) in fig_dict:
        
        fig,rec = fig_dict[key]
    else:
        rec = magic([2,2,(len(fig_dict) % 4)+1])
        print(rec)
        print(len(fig_dict)%4 == 0)
        if (len(fig_dict))%4 == 0: #need new page if True
            fig =plt.figure()
            fig_list.append(fig)
            fig_list = list(set(fig_list))
        else:
            fig = fig_list[-1]
            
        fig_dict[key] = (fig,rec)
        print(len(fig_list))
    return fig,rec
    

# a VERY simple grid visulization routine 
     
def examine_nc(gridname_nc,pp,fig_dict,fig_list):
    f = netcdf.netcdf_file(gridname_nc, 'r')
    

    rosetta  = dict(zip([x.lower() for x in f.variables.keys()],f.variables.keys()))

    dx = f.variables[rosetta['dx']].data
    dy = f.variables[rosetta['dy']].data
    
    print np.cumsum(np.mean(dx,axis=1))
    
   
    scalar_dump = open(gridname_nc+'_basic_info.txt','w')
    # sys.exit()
    scalar_dump.write('grid : '+gridname_nc+'\n') # python will
    for key_l in rosetta:
        key = rosetta[key_l]
    
        if (() == f.variables[key].shape):
            scalar_dump.write(str(key_l)+' : '+str(f.variables[key].data)+'\n') # python will 
            
        else:
            
            #print(np.mean(f.variables[key].data))
            ndim = (len(f.variables[key].dimensions))
            if ndim == 1:
                y = f.variables[key].data
            if ndim == 2:
                y = np.mean(f.variables[key].data,axis=1)

            scalar_dump.write(str(key_l)+' : '+str(np.mean(y))+'\n') # python will 

            frm = Frame(y,meta={'stationary':True,'title':key})
            frm.x = np.cumsum(np.mean(dx,axis=1))
           
            fig,rec = get_fig_rec(key_l,fig_dict,fig_list)
            frm.render(fig,rec)
            frm.ax.ticklabel_format(axis='x', style='sci', scilimits=(-1,1))
            frm.ax.ticklabel_format(axis='y', style='sci', scilimits=(-1,1))
            # yy = frm.ax.get_xticks()
            # print('tick truncation')
            # print(xx)           
            # # sys.exit()
            # ll = ['%.1f' % a for a in xx]
            # print(ll)
            # frm.ax.set_xticks(ll)
    
    
    scalar_dump.close()
    f.close()
    
    subprocess.call('enscript -f Courier12  -t basic -p '+gridname_nc+'_basic_info.ps '+gridname_nc+'_basic_info.txt',shell = True)
    subprocess.call('ps2pdf '+gridname_nc+'_basic_info.ps '+gridname_nc+'_basic_info.pdf',shell = True)
    
 
def examine_nclist(gridlist_nc):
    pp = PdfPages('grids.pdf')
    fig_dict = {}
    fig_list = []
    for grid in gridlist_nc:
        examine_nc(grid,pp,fig_dict,fig_list)
        
        print(fig_dict.keys())

    for elem in fig_list:
        elem.savefig(pp,format='pdf')

    pp.close()



