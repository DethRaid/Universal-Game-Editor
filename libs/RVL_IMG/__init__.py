# -*- coding: utf-8 -*-

def _t44(img,w,h,tile,x,y):
    tx,ty = 0,0
    for c in tile:
        if (y+ty)<h and (x+tx) < w: img[((y+ty)*w)+x+tx]=c
        if tx<3: tx+=1
        else: tx=0; ty+=1

def _t84(img,w,h,tile,x,y):
    tx,ty = 0,0
    for c in tile:
        if (y+ty)<h and (x+tx) < w: img[((y+ty)*w)+x+tx]=c
        if tx<7: tx+=1
        else: tx=0; ty+=1

def _t88(img,w,h,tile,x,y):
    tx,ty = 0,0
    for c in tile:
        if (y+ty)<h and (x+tx) < w: img[((y+ty)*w)+x+tx]=c
        if tx<7: tx+=1
        else: tx=0; ty+=1

def _c_t44(d):
    d1,d2,di = d

    p = [[0,0,0,255],[0,0,0,255],[0,0,0,255],[0,0,0,255]]

    p[0][0] = int(((d1>>11)&31)*(255./31))
    p[0][1] = int(((d1>>5)&63)*(255./63))
    p[0][2] = int((d1&31)*(255./31))

    p[1][0] = int(((d2>>11)&31)*(255./31))
    p[1][1] = int(((d2>>5)&63)*(255./63))
    p[1][2] = int((d2&31)*(255./31))

    if d1>d2:
        p[2][0] = ((p[0][0]*2) + p[1][0]) / 3
        p[2][1] = ((p[0][1]*2) + p[1][1]) / 3
        p[2][2] = ((p[0][2]*2) + p[1][2]) / 3
    
        p[3][0] = (p[0][0] + (p[1][0]*2)) / 3
        p[3][1] = (p[0][1] + (p[1][1]*2)) / 3
        p[3][2] = (p[0][2] + (p[1][2]*2)) / 3

    else:
        p[2][0] = (p[0][0] + p[1][0])/2; p[2][1] = (p[0][1] + p[1][1])/2; p[2][2] = (p[0][2] + p[1][2])/2
    
        p[3][3] = 0

    return [p[(di>>30)&3],p[(di>>28)&3],p[(di>>26)&3],p[(di>>24)&3],
            p[(di>>22)&3],p[(di>>20)&3],p[(di>>18)&3],p[(di>>16)&3],
            p[(di>>14)&3],p[(di>>12)&3],p[(di>>10)&3],p[(di>>8)&3],
            p[(di>>6)&3] ,p[(di>>4)&3] ,p[(di>>2)&3] ,p[(di>>0)&3]]

#_c_d = [bu16,bu16,bu32]
_c_d = struct( 8,
    d1=bu16,
    d2=bu16,
    di=bu32
)

# TODO: need a registration wrapper (@register()) for these to work as expected.
# (we want only these functions to be registered in the selected script-namespaces with no cross-interference)
#@register( UGE_MODEL_SCRIPT, UGE_IMAGE_SCRIPT, UGE_PALETTE_SCRIPT )
def readpal(Count,Format):
    pal = []
    
    switch(Format)
    if   case(0): # IA8
        #print "_IA8"
        pal = array([bu8,bu8],count=Count)(label='IA8 palette')
    elif case(1): # RGB565
        #print "_RGB565"
        pal = [[
            int(((d>>11)&31)*(255.0/31)),
            int(((d>>5)&63)*(255.0/63)),
            int((d&31)*(255.0/31)), 255] for d in array(bu16,count=Count)(label='RGB565 palette') ]
    elif case(2): # RGB5A3
        #print "_RGB5A3"
        pal = [[
            int(((d>>10)&31)*(255.0/31)),
            int(((d>>5)&31)*(255.0/31)),
            int((d&31)*(255.0/31)),255 ] if d>>15 else [
            int(((d>>0)&15)*(255.0/15)),
            int(((d>>4)&15)*(255.0/15)),
            int(((d>>8)&15)*(255.0/15)),
            int(((d>>12)&7)*(255.0/7))] for d in array(bu16,count=Count)(label='RGB5A3 palette') ]
    
    return pal #+[[0, 0, 0, 0]]*(16384 - Count)

#@register( UGE_MODEL_SCRIPT, UGE_IMAGE_SCRIPT )
def readimg(Width,Height,Format):
    ratio = (Width*Height)
    img = []

    switch(Format)
    if case(0): #I4 (8bit = 2 pixels)
        #print "I4 (8bit = 2 pixels)"
        img = [[0]]*ratio # [ [I], ... ] * (W*H)
        
        for c,row in enumerate( array( array( array(bu8,count=32), count=Width/8 ), count=Height/8 )(label={'RGB565 image':'RGB565 row'}) ):
            y = c*8
            for r,cell in enumerate(row):
                _t88(img,Width,Height,sum([[(d&240)|(d>>4),((d&15)<<4)|(d&15)] for d in cell ],[]),r*8,y)
        '''
        tile = [[0]]*64
        for y in range(0,Height,8):
            for x in range(0,Width,8):
                for i,d in enumerate( array(bu8,count=32)() ):
                    i*=2
                    tile[i][0] = (d&240)|(d>>4) #format 8bit (FF,EE,DD,CC,...)
                    tile[i+1][0] = ((d&15)<<4)|(d&15)

                _t88(img,Width,Height,tile,x,y)
        #img = [[p[0],p[0],p[0],255] for p in dst]
        '''
    if case(1): #I8
        #print "I8"
        img = [[0]]*ratio # [ [I], ... ] * (W*H)

        for c,row in enumerate( array( array( array(bu8,count=32), count=Width/8 ), count=Height/4 )(label={'I8 image':'I8 row'}) ):
            y = c*4
            for r,tile in enumerate(row): _t84(img,Width,Height,tile,r*8,y)
        '''
        for y in range(0,Height,4):
            for x in range(0,Width,8): _t84(img,Width,Height,array([bu8],count=32)(),x,y)
        #img = [[p[0],p[0],p[0],255] for p in dst]
        '''

    if case(2): #IA4
        #print "IA4"
        img = [[0,255]]*ratio # [ [I,A], ... ] * (W*H)
        #dst = [[0,255]]*ratio

        tile = [[0,255]]*32
        for y in range(0,Height,4):
            for x in range(0,Width,8):
                for i,d in enumerate(array(bu8,count=32)()):
                    tile[i][0] = (d&240)|(d>>4)
                    tile[i][1] = ((d&15)<<4)|(d&15)

                _t84(img,Width,Height,tile,x,y)
        #img = [[p[0],p[0],p[0],p[1]] for p in dst]

    if case(3): #IA8
        #print "IA8"
        img = [[0,255]]*ratio # [ [I,A], ... ] * (W*H)

        for c,row in enumerate( array( array( array([[bu8,bu8]
                ],count=16), count=Width/4 ), count=Height/4 )(label={'IA8 image':'IA8 row'}) ):
            y = c*4
            for r,tile in enumerate(row): _t44(img,Width,Height,array([[bu8,bu8]],count=16)(),r*4,y)
        '''
        for y in range(0,Height,4):
            for x in range(0,Width,4):
                _t44(img,Width,Height,array([[bu8,bu8]],count=16)(),x,y)
        #img = [[p[0],p[0],p[0],p[1]] for p in dst]
        '''

    if case(4): #RGB565
        #print "RGB565"
        img = [[0,0,0]]*ratio # [ [R,G,B], ... ] * (W*H)
        
        for c,row in enumerate( array( array( array(bu16,count=16), count=Width/4 ), count=Height/4 )(label={'RGB565 image':'RGB565 row'}) ):
            y = c*4
            for r,cell in enumerate(row):
                _t44(img,Width,Height,[[
                    int(((d>>11)&31)*(255.0/31)),
                    int(((d>>5)&63)*(255.0/63)),
                    int((d&31)*(255.0/31)), 255] for d in cell ],r*4,y)
        '''
        for y in range(0,Height,4):
            for x in range(0,Width,4):
                _t44(img,Width,Height,[[
                    int(((d>>11)&31)*(255.0/31)),
                    int(((d>>5)&63)*(255.0/63)),
                    int((d&31)*(255.0/31)), 255] for d in array(bu16,count=16)() ],x,y)
        ''
        tile = [[0,0,0]]*16
        i,x,y = 0,0,0
        for d in bu16(['']*ratio):
            tile[i][0] = int(((d>>11)&31)*(255.0/31))
            tile[i][1] = int(((d>>5)&63)*(255.0/63))
            tile[i][2] = int((d&31)*(255.0/31))

            i+=1
            if i==16:
                i=0
                _t44(img,Width,tile,x*4,y*4)
                x+=1
                if x==Width/8: x=0; y+=1
        #'''
                
    if case(5): #RGB5A3
        #print "RGB5A3"
        img = [[0,0,0,255]]*ratio # [ [R,G,B,A], ... ] * (W*H)
        
        for c,row in enumerate( array( array( array(bu16,count=16), count=Width/4 ), count=Height/4 )(label={'RGB5A3 image':'RGB5A3 row'}) ):
            y = c*4
            for r,cell in enumerate(row):
                _t44(img,Width,Height,[[
                    int(((d>>10)&31)*(255.0/31)),
                    int(((d>>5)&31)*(255.0/31)),
                    int((d&31)*(255.0/31)),255 ] if d>>15 else [
                    int(((d>>0)&15)*(255.0/15)),
                    int(((d>>4)&15)*(255.0/15)),
                    int(((d>>8)&15)*(255.0/15)),
                    int(((d>>12)&7)*(255.0/7))] for d in cell ],r*4,y)
        '''
        for y in range(0,Height,4):
            for x in range(0,Width,4):
                _t44(img,Width,Height,[[
                    int(((d>>10)&31)*(255.0/31)),
                    int(((d>>5)&31)*(255.0/31)),
                    int((d&31)*(255.0/31)),255 ] if d>>15 else [
                    int(((d>>0)&15)*(255.0/15)),
                    int(((d>>4)&15)*(255.0/15)),
                    int(((d>>8)&15)*(255.0/15)),
                    int(((d>>12)&7)*(255.0/7))] for d in array(bu16,count=16)() ],x,y)
        '''

    if case(6): #RGBA8
        #print "RGBA8"
        img = [[0,0,0,255]]*ratio # [ [R,G,B,A], ... ] * (W*H)
        
        for c,row in enumerate( array( array( [ array([bu8,bu8],count=16), array([bu8,bu8],count=16)
                ], count=Width/4 ), count=Height/4 )(label={'RGBA8 image':'RGBA8 row'}) ):
            y = c*4
            for r,(AR,GB) in enumerate(row): _t44(img,Width,Height,[[R,G,B,A] for (A,R),(G,B) in zip(AR,GB)],r*4,y)
            
    if case(8): #CI4
        #print "CI4"
        img = [0]*ratio
        
        #dst = [[0]]*ratio
        for y in range(0,Height,8):
            for x in range(0,Width,8):
                tile = [0]*64
                for i,d in enumerate(array(bu8,count=32)()):
                    i*=2
                    tile[i] = (d>>4) #format 8bit (FF,EE,DD,CC,...)
                    tile[i+1] = (d&15)

                _t88(img,Width,Height,tile,x,y)
        #img = [p[0] for p in dst] #[Palette[p[0]] for p in dst]

    if case(9): #CI8 (TODO)
        #print "CI8"
        img = [0]*ratio
        #dst = [[0]]*ratio
        for y in range(0,Height,4):
            for x in range(0,Width,8):
                _t84(img,Width,Height,array(bu8,count=32)(),x,y)
        #img = [p[0] for p in dst] #[Palette[p[0]] for p in dst]

    if case(10): #CI14 (TODO)
        #print "CI14"
        img = [0]*ratio
        #dst = [[0]]*ratio
        #'''
        for y in range(0,Height,4):
            for x in range(0,Width,4):
                _t44(img,Width,Height,array(bu16,count=16)(),x,y)
        #img = [p[0] for p in dst] #[Palette[p[0]] for p in dst]

    if case(14): #CMPR
        #print "CMPR"
        img = [[0,0,0,255]]*ratio

        for c,row in enumerate( array( array( array( _c_d, count=4 ), count=Width/8 ), count=Height/8 )(label={'CMPR image':'CMPR row'}) ):
            y = c*8
            for r,(c1,c2,c3,c4) in enumerate(row):
                t1,t2,t3,t4=_c_t44(c1),_c_t44(c2),_c_t44(c3),_c_t44(c4)
                x = r*8
                tile =  t1[0:4]+t2[0:4]+ t1[4:8]+t2[4:8]+\
                            t1[8:12]+t2[8:12]+ t1[12:16]+t2[12:16]+\
                        t3[0:4]+t4[0:4]+ t3[4:8]+t4[4:8]+\
                            t3[8:12]+t4[8:12]+ t3[12:16]+t4[12:16]
                _t88(img,Width,Height,tile,x,y)
                
    return img
