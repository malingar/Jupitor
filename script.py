#%pylab
import ser
import luckyshot
import scipy.ndimage
import scipy.misc
import MCUtils as mc
import pywt
from skimage import transform as tf

# shot at 6.6fps
filenames = {'Wesley':
        {'path':'../../../Lucky/Wesley Uranus Storm Data New/20141002/',
         'files':['20141002_131357_R650.ser','20141002_144929_R650.ser',
                  '20141002_133006_R650.ser','20141002_151119_R650.ser',
                  '20141002_134850_R650.ser','20141002_152709_R650.ser',
                  '20141002_141500_R650.ser','20141002_154854_R650.ser',
                  '20141002_143310_R650.ser','20141002_160535_R650.ser']},
        'Delcroix':
        {'path':('../../../Lucky/Delcroix Uranus Storm Data/'
                                    'uranus_20141003-04_ir685_PicDuMidi/'),
         'files':['ir685_1/2014-10-03-2242_5-MD-IR685-8.ser',
                  'ir685_1/2014-10-03-2250_5-MD-IR685-9.ser',
                  'ir685_1/2014-10-03-2258_5-MD-IR685-10.ser',
                  'ir685_1/2014-10-03-2306_5-MD-IR685-11.ser',
                  'ir685_1/2014-10-03-2314_6-MD-IR685-12.ser',
                  'ir685_1/2014-10-03-2322_6-MD-IR685-13.ser',
                  'ir685_2/2014-10-03-2336_5-MD-IR685-15.ser',
                  'ir685_2/2014-10-03-2344_5-MD-IR685-16.ser',
                  'ir685_2/2014-10-03-2352_5-MD-IR685-17.ser',
                  'ir685_2/2014-10-04-0000_5-MD-IR685-18.ser',
                  'ir685_2/2014-10-04-0008_6-MD-IR685-19.ser',
                  'ir685_2/2014-10-04-0016_6-MD-IR685-20.ser',
                  'ir685_2/2014-10-04-0024_6-MD-IR685-21.ser',
                  'ir685_2/2014-10-04-0040_7-MD-IR685-23.ser',
                  'ir685_2/2014-10-04-0048_7-MD-IR685-24.ser',
                  'ir685_2/2014-10-04-0056_7-MD-IR685-25.ser',
                  'ir685_2/2014-10-04-0104_7-MD-IR685-26.ser',
                  'ir685_2/2014-10-04-0112_8-MD-IR685-27.ser',
                  'ir685_2/2014-10-04-0120_8-MD-IR685-28.ser',
                  'ir685_3/2014-10-04-0144_2-MD-IR685-30.ser',
                  'ir685_3/2014-10-04-0203_4-MD-IR685-32.ser',
                  'ir685_3/2014-10-04-0221_2-MD-IR685-34.ser',
                  'ir685_3/2014-10-04-0243_4-MD-IR685-36.ser']}}
DelcroixDarks = ['ir685_1/2014-10-03-2331_8-MD-DARK-3.ser',
                 'ir685_2/2014-10-04-0129_8-MD-DARK-4.ser']


# Wesley Data
img = {}
stepsz = 1000. # frames
for i,fn in enumerate(filenames['Wesley']['files']):
    f = filenames['Wesley']['path']+fn
    print ('Reading{f}').format(f=f)
    header = ser.readheader(f)
    cnt = header['FrameCount']
    img[i] = {}
    bounds = np.append(np.arange(0,cnt,stepsz),cnt)
    for j,end in enumerate(bounds[1:]):
        print ('Coadding image {j} of {b}.').format(
                                            j=j+1,b=int(np.ceil(cnt/stepsz)))
        img[i][j]=luckyshot.shift_and_add(f,
                                ix=range(int(bounds[j]),int(end-1)),verbose=2)
    fig = plt.figure(figsize=(16,12))
    for i in img[0].keys():
        plt.subplot(3,3,i,xticks=[],yticks=[])
        plt.imshow(img[0][i][240-25:240+25,320-25:320+25],cmap=cm.gray)

# Delcroix Data
for i,fn in enumerate(filenames['Delcroix']['files']):
    f = filenames['Delcroix']['path']+fn
    print (f)

###

data = {}
scale = 10.0
for i,fn in enumerate(filenames['Wesley']['files'][0:1]):
    data[i] = np.zeros([50*scale,50*scale])
    f = filenames['Wesley']['path']+fn
    print ('Reading {i}, {f}').format(i=i,f=f)
    header = ser.readheader(f,verbose=False)
    for j in range(header['FrameCount']-1)[0:1]:
        img = ser.readframe(f,j,verbose=False)
        w,h = luckyshot.find_cob(img)
        #mc.print_inline('{w},{h}'.format(w=w,h=h))
        # Do this first crop to manage the size of the rescaled image
        crop = img[np.round(h)-25:np.round(h)+25,
                   np.round(w)-25:np.round(w)+25]
        zoomed = tf.rescale(crop,scale)
        w,h = luckyshot.find_cob(zoomed)
        tform = tf.SimilarityTransform(translation=(w-250,h-250))
        shift = tf.warp(zoomed,tform)
        print (luckyshot.find_cob(shift))
        data[i] += shift

# Grab just one reference frame
realimg = ser.readframe('../../../Lucky/Wesley Uranus Storm Data New/20141002/20141002_131357_R650.ser',100)
w,h = luckyshot.find_cob(realimg)
ref = realimg[np.round(h)-25:np.round(h)+25,np.round(w)-25:np.round(w)+25]
plt.figure()
plt.imshow(ref)

# Generate a fake distribution for a planet
# (x-x_0)**2 + (y-y_0)**2 == a**2
# Uranus =~ 4" diameter
def disk(x,y,a):
    return np.sqrt(a**2 - (x**2 + y**2))/a if (x**2 + y**2) < a**2 else 0.

def noisy(x,y,a,ratio=0.001):
    return np.random.uniform(0,1) if np.random.uniform(0,1)<0.1 else disk(x,y,a)

def normal_smear(x,psf):
    return [i+np.random.normal(scale=psf) for i in x]

def bulk_shift(xs,psf,shift):
    shift = np.random.normal(scale=psf)
    return np.array(xs)+shift,shift

diameter = 4. # arcseconds
pixsz=0.16 # arcseconds / pixel
dims=ref.shape
xr,yr=[-pixsz*dims[0]/2.,pixsz*dims[0]/2.],[-pixsz*dims[1]/2.,pixsz*dims[1]/2.]

samples = np.round(ref.sum())
img=np.zeros(dims)
psf = 2 # sigma in arcseconds
noise = 0.25 #percentage
xshift,yshift=0.,0.
for n in np.arange(0,samples,10e5):
    mc.print_inline('{n} of {s}'.format(n=n,s=samples))
    x = np.random.uniform(xr[0],xr[1],10e5)
    y = np.random.uniform(yr[0],yr[1],10e5)
    # Does this have the same effect as adding Gaussian blur?
    x,xshift=bulk_shift(normal_smear(x,psf),psf,xshift)
    y,yshift=bulk_shift(normal_smear(y,psf),psf,yshift)
    I = [noisy(a[0],a[1],diameter/2.,ratio=noise) for a in zip(x,y)]
    out,_,_=np.histogram2d(x,y,bins=dims,range=[xr,yr],weights=I)
    img+=out

plt.figure()
plt.imshow(img)
