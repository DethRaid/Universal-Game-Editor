# -*- coding: utf-8 -*-
ugeScriptType(UGE_IMAGE_SCRIPT)
ugeScriptFormats({ 'PIL': [
'bmp','dib',
'eps',
'gif',
'im',
'jpg','jpeg','jpe','jfif',
'jp2','jpx',
'msp',
'pcx',
'png',
'ppm',
'spi',
'tif','tiff',
'webp',
'xbm',
'xv',
'cur',
'dcx',
'fli',
'flc',
'fpx',
'gbr',
'gd',
'ico',
'icns',
'imt',
'ipct','naa',
#MCIDAS
'mpo',
'pcd',
'psd',
'sgi',
'tga',
'wal',
'xpm',
'palm',
'pdf',
#PIXAR
'bufr',
'fits',
'grib',
'hdf5',
'mpeg',
'wmf',
# other seen formats not documented:
'pgm',
'pbm',
#'lut',
'j2k',
'bdf',
#'pil',
#'ggr',
'bw',
'ras',
'rgb',
'mpo',
#'doc'
] })
ugeScriptLibs(['pillow'])

def ugeImportImage(FT,CMD):
    im = Image.open(StringIO( string()(0).__value__ )) # these functions come from the pillow library
    Width,Height = im.size; img,plt = [],[]

    ugeSetImageWidth(Width)
    ugeSetImageHeight(Height)
    
    # TODO: support single-color transparency (UMC itself doesn't support this)
    switch(im.mode)
    if case('1'):ugeSetImageData([ [P] for P in im.getdata()])
    if case('L'):ugeSetImageData([ [P] for P in im.getdata()])
    if case('LA'):ugeSetImageData([ list(P) for P in im.getdata()])
    if case('RGB'):ugeSetImageData([ list(P) for P in im.getdata()])
    if case('RGBA'):ugeSetImageData([ list(P) for P in im.getdata()])
    if case('RGBX'):ugeSetImageData([ list(P[:3]) for P in im.getdata()])
    if case('CMYK'):
        ugeSetImageData(
            [ [255*(1-C)*(1-K), 255*(1-M)*(1-K), 255*(1-Y)*(1-K)] for C,M,Y,K in im.getdata()]
        )
    if case('YCbCr'):pass # not supported (need an algorithm)
    if case('LAB'): pass # not supported (need an algorithm)
    if case('HSV'):
        fl = 1.0/100
        def hsv_to_rgb(h, s, v):
            if s == 0.0: v*=255; return [v, v, v]
            i = int(h*6.) # XXX assume int() truncates!
            f = (h*6.)-i; p,q,t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))), int(255*(v*(1.-s*(1.-f)))); v*=255; i%=6
            if i == 0: return [v, t, p]
            if i == 1: return [q, v, p]
            if i == 2: return [p, v, t]
            if i == 3: return [p, q, v]
            if i == 4: return [t, p, v]
            if i == 5: return [v, p, q]
        ugeSetImageData([ hsv_to_rgb(h, s*fl, v*fl) for h, s, v in im.getdata()])
    if case('I'):   pass # not supported (not sure how this works)
    if case('F'):   pass # not supported (not sure how this works)
    if case('P'):
        ugeSetImageData([[P]for P in im.getdata()])
        m=len(im.palette.mode);p=im.getpalette()
        ugeSetImagePalette([p[o:o+m]for o in range(0,len(p),m)]) # not finished yet, but usable (data only)
    
def ugeExportImage(FT,CMD):
    from StringIO import StringIO
    
    '''
    def rgb_to_hsv(r, g, b):
        maxc = max(r, g, b)
        minc = min(r, g, b)
        v = maxc
        if minc == maxc:
            return 0.0, 0.0, v
        s = (maxc-minc) / maxc
        rc = (maxc-r) / (maxc-minc)
        gc = (maxc-g) / (maxc-minc)
        bc = (maxc-b) / (maxc-minc)
        if r == maxc:
            h = bc-gc
        elif g == maxc:
            h = 2.0+rc-bc
        else:
            h = 4.0+gc-rc
        h = (h/6.0) % 1.0
        return h, s, v
    '''
    name = ugeGetImageName()
    width = ugeGetImageWidth()
    height = ugeGetImageHeight()
    pixels = ugeGetImageData()
    palette = ugeGetImagePalette()

    mode = ['L','LA','RGB','RGBA'][len(pixels[0])-1]
    pmode= None
    if palette!=[] and mode=='L': mode='P'; pmode = ['L','LA','RGB','RGBA'][len(palette[0])-1]
    
    pilimg = PIL.Image.new( mode, (width,height))
    pilimg.putdata([tuple(p) for p in pixels])
    if mode=='P': pilimg.putpalette( palette, pmode )
    
    imgio = StringIO()
    pilimg.save(imgio, format=FT)
    imgio.seek(0)
    string()(imgio.read())

    
