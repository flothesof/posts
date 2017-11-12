import numpy as np
from matplotlib.colors import hsv_to_rgb
import matplotlib.pyplot as plt

def compute_hue(z):
    "Computes the hue corresponding to the complex number z."
    H = np.angle(z) / (2*np.pi) + 1
    return np.mod(H, 1)
    
def eval_func_on_grid(f, re, im,  N): 
    """Evaluates the complex function at the nodes of the grid defined by re, im and N.
    re and im are  tuples: re=(a,b) and im=(c,d) defining the rectangular region
    N is the number of nodes per unit interval."""
    l = re[1] - re[0]
    h = im[1] - im[0]
    resL = N*l #horizontal resolution
    resH = N*h #vertical resolution
    x = np.linspace(re[0], re[1],resL)
    y = np.linspace(im[0], im[1], resH)
    x, y = np.meshgrid(x,y)
    z = x + 1j*y
    w = f(z)
    return w
    
def classical_domaincol(w, s):
    """Implements classical domain coloring on w, complex array of values of f(z)
    and with the constant saturation s."""
    
    indi = np.where(np.isinf(w))#detects the values w=a+ib, with a or b or both =infinity
    indn = np.where(np.isnan(w))#detects nans
  
    H = compute_hue(w)
    S = s*np.ones_like(H)
    modul = np.absolute(w)
    V= (1.0-1.0/(1+modul**2))**0.2
    # the points mapped to infinity are colored with white; hsv_to_rgb(0,0,1)=(1,1,1)=white
    H[indi]=0.0 
    S[indi]=0.0  
    V[indi]=1.0
    #hsv_to_rgb(0,0,0.5)=(0.5,0.5, 0.5)=gray  
    H[indn]=0
    S[indn]=0
    V[indn]=0.5
    HSV = np.dstack((H,S,V))
    RGB = hsv_to_rgb(HSV)
    return RGB      
    
    
def plot_domain(color_func, f,   re=[-1,1], im= [-1,1], Title='',
                s=0.9, N=200, daxis=None, ax=None):
    w = eval_func_on_grid(f, re, im, N)
    domc = color_func(w, s)
    if ax is None:
        ax = plt.gca()
    ax.set_xlabel("$\Re(z)$")
    ax.set_ylabel("$\Im(z)$")
    ax.set_title(Title)
    if(daxis):
         ax.imshow(domc, origin="lower", extent=[re[0], re[1], im[0], im[1]])
       
    else:
        ax.imshow(domc, origin="lower")
        ax.axis('off')
        
def modulus_domaincol(w, s): 
    """Domain coloring with modulus track.
    w the array of values
    s is the constant Saturation"""
   
    H = compute_hue(w)
    modulus = np.absolute(w)
    c= np.log(2)
    Logm=np.log(modulus)/c#log base 2
    Logm=np.nan_to_num(Logm)

    V=Logm-np.floor(Logm)
    S = s*np.ones_like(H, float)

    HSV = np.dstack((H,S,V**0.2))# V**0.2>V for V in[0,1];this choice  avoids too dark colors
    RGB=hsv_to_rgb(HSV) 
    return RGB
    
    
def perfract(x, t, m, M):
    "Periodized version of x related to some scale t."
    x=x/t
    return m+(M-m)*(x-np.floor(x))
    
def contour_domaincol(w,s):
    H=compute_hue(w) 
    m=0.7 # brightness is restricted to [0.7,1]; interval suggested by E Wegert
    M=1
    n=15 # n=number of isochromatic lines per cycle 
    isol=perfract(H, 1.0/n, m, M) # isochromatic lines
    modul=np.absolute(w)
    Logm=np.log(modul)
    Logm=np.nan_to_num(Logm) 
    modc=perfract(Logm, 2*np.pi/n, m, M)# lines of constant log-modulus
   
    V=modc*isol 
    S = 0.9*np.ones_like(H, float) 
    HSV = np.dstack((H,S,V))
    RGB = hsv_to_rgb(HSV)
   
    return RGB
    