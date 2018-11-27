import ser
import numpy as np
import scipy.ndimage
import MCUtils as mc

def find_cob(img,verbose=1):
    """Returns the cob in [width,height] pixels. Makes assumptions."""
    # The smoothing here helpts tamp down detector noise
    blurred = scipy.ndimage.gaussian_filter(img,sigma=5)
    xhist_b = blurred.sum(axis=0)
    yhist_b = blurred.sum(axis=1)
    # Find a pixel near the peak
    xc = np.where(xhist_b==xhist_b.max())[0][0]
    yc = np.where(yhist_b==yhist_b.max())[0][0]
    # Pull out the region around there
    xhist_r = xhist_b[xc-10:xc+10]
    yhist_r = yhist_b[yc-10:yc+10]
    # Fit a second order polynomial
    xfit = np.polyfit(np.arange(xc-10,xc+10),xhist_r,2)
    yfit = np.polyfit(np.arange(yc-10,yc+10),yhist_r,2)
    # Find the root of the first derivative (i.e. the peak)
    w = np.poly1d(xfit).deriv().r[0]
    h = np.poly1d(yfit).deriv().r[0]
    if verbose>1:
        print ('CoB at [{w},{h}].').format(w=w,h=h)
    return w,h

def shift_and_add(filename,ix=None,verbose=1):
    """Performs a _shift and add_ style coadd on a sequence of images of a
    planet. Recenters the center of brightness to the center of the image.
    The file indicated by filename is assumed to be .ser format. The ix keyword
    takes a list of frame numbers to use.
    """
    if verbose>1:
        print ('Reading: {f}').format(f=filename)
    header = ser.readheader(filename)
    cnt = header['FrameCount']
    img = np.zeros([header['ImageHeight'],header['ImageWidth']])
    for i in (ix if ix else range(cnt-1)):
        frame = ser.readframe(filename,i,header=header)
        w,h=find_cob(frame)
        vec = [header['ImageHeight']/2.-h,header['ImageWidth']/2.-w]
        if verbose:
            mc.print_inline('Shift and adding {i} by {vec}'.format(i=i,vec=vec))
        img+=scipy.ndimage.interpolation.shift(frame,vec)/cnt
    return img
