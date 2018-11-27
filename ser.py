# This is just a quick script for reading .ser movie files.
import numpy as np
import struct

def readheader(filename,verbose=1):
    header = {}
    with open(filename,'rb') as f:
        header['FileID'] = f.read(14) #str
        header['LuID'] = struct.unpack('<I',f.read(4))[0] #int32
        header['ColorID'] = struct.unpack('<I',f.read(4))[0] #int32
        header['LittleEndian'] = struct.unpack('<I',f.read(4))[0] #int32
        header['ImageWidth'] = struct.unpack('<I',f.read(4))[0] #int32
        header['ImageHeight'] = struct.unpack('<I',f.read(4))[0] #int32
        header['PixelDepth'] = struct.unpack('<I',f.read(4))[0] #int32
        header['BytePerPixel'] = 1 if header['PixelDepth']<=8 else 2
        header['FrameCount'] = struct.unpack('<I',f.read(4))[0] #int32
        header['Observer'] = struct.unpack('<40s',f.read(40))[0] #str
        header['Instrument'] = struct.unpack('<40s',f.read(40))[0] #str
        header['Telescope'] = struct.unpack('<40s',f.read(40))[0] #str
        header['DateTime'] = struct.unpack('<8s',f.read(8))[0] #"Date"
        header['DateTime_UTC'] = struct.unpack('<8s',f.read(8))[0] #"Date"
    if verbose:
        
        print ('{f} - {d}').format(f=filename,d=header['DateTime'])
        print ('    Dims: {h}x{w}').format(
                                w=header['ImageWidth'],h=header['ImageHeight'])
        print ('    Frames: {n}').format(n=header['FrameCount'])
    return header

def readtrailer(filename,verbose=1):
    header = readheader(filename,verbose=verbose)
    offset = (header['FrameCount'] * header['ImageWidth'] *
              header['ImageHeight'] * header['BytePerPixel'])
    trailer = []
    return trailer

def readframe(filename,frame,header=False,verbose=1):
    if not header:
        header = readheader(filename,verbose=verbose)
    if frame > header['FrameCount']-1:
        print ('ERROR: Frame #{frame} requested of {count} available.').format(
                                                frame=frame, count=FrameCount)
        return False
    HeaderBytes = 178
    ImagePixels = header['ImageWidth']*header['ImageHeight']
    ImageBytes = ImagePixels*header['BytePerPixel']
    with open(filename,'rb') as f:
        f.seek(HeaderBytes+ImageBytes*frame)
        f.read(ImageBytes)
        fmt = '{endian}{pixels}{fmt}'.format(
                            endian='>' if header['LittleEndian'] else '<',
                            pixels=ImagePixels,
                            fmt='H' if header['BytePerPixel']==2 else 'B')
        img = np.array(struct.unpack(fmt,f.read(ImageBytes))).reshape(
                                    header['ImageHeight'],header['ImageWidth'])

        return img
