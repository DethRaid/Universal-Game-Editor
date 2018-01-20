# -*- coding: utf8 -*-
from __future__ import print_function

ugeScriptType(UGE_MODEL_SCRIPT)
ugeScriptFormats({'Hal Labs HSD Archive': ['dat']}) # Tcll see this string: 'HSD_ArchiveParse: byte-order mismatch! Please check data format %x %x'
ugeScriptLibs(['RVL_IMG'])

# written by Tcll5850
# credit to Revel8n for deciphering some of the format for SSBM (most of the basics for models and some other stuff),
#    and for helping me (Tcll) to understand the display list formats and triangle encodings (initial credit to Milun for the base-format)
# credit to Milun and InternetExplorer for SSBM stage research and info.
# credit to Lars for the recommendation for WCTV support
# credit to Zankyou for figuring out the visibility bone flags on meshes
# Tcll - I'm forgetting someone here who helped on skype with various things.

# TODO:
# - order bones via matanim sections
# - define roots with data-structs or augments rather than functions (seamless integration)

# to look into:
# - materials/textures:  HSD_TExpGetType(root) == HSD_TE_TEV

# Notes:
# - strings are pretty much useless in this format, any strings found are likely for identifiers (not names)

# noinspection PyUnusedLocal,PyGlobalUndefined
def ugeImportModel(T,C):
    # augments: (custom data types or handlers)
    NULL = lambda v=None,label='',*args,**kwargs: '' # TODO: return None
    # ^ due to older display-list work, vectors accept an empty string as null data, while accepting None as direct data
    def ptr(value=None,label='',*args,**kwargs):
        pointer_value = bu32(value,label=' -- %s Offset'%label)
        pointer_value.__color__ = 0x00FF00
        return pointer_value+32
    
    #downscale = lambda v: v*.1
    
    # future definitions
    vec3, quat = struct(12,X=bf32,Y=bf32,Z=bf32), struct(16,X=bf32,Y=bf32,Z=bf32,W=bf32); vec4=quat # future: vec3=vec(3); quat=vec4=vec(4) # will be included as named.
    vec3.__color__ = 0xC0C0FF
    matrix34 = array(array(bf32,count=4),count=3) # future: matrix34 = matrix(3,4) # will be included as it's own data type.
    
    # Tcll - this really needs an update >_<
    # pathfinder interface:
    globals()['structs'] = {
    #   struct_name: [ expected_size, struct_function (for root structs) or _pass, {
    #       pointer_addr: sub-struct_name,
    #       ...
    #   }, isArray=False ],
    #   ...
    }
    class structPointers(object ):
        """registers structure definitions for the pathfinder
        
        arguments:
        - size (int): the size of the struct in bytes (-1 for undefined)
        - pointers (dict): location of pointer-value : expected struct name
        - isarray (bool): notifies the pathfinder to multiply `size` to match the overflow before testing for false padding
        - root (bool): marks this struct as a root struct
        
        usage:
        
        @structPointers( 8, { 0:'_pass', ... } )
        def struct2( offset ): ...
        
        @structPointers( 32, { 0:'root_struct1', 4:'struct2', ... }, root=True )
        def root_struct1( offset ): ...
        """
        # NOTE: see structs below for more examples.
        def __init__( this, size, pointers={}, isArray=False, root=False ):
            this.size=size; this.pointers = pointers; this.isarray = isArray; this.root = root
        def __call__( this, struct_function ):
            globals()['structs'][struct_function.__name__] = [ this.size, struct_function if this.root else _pass , this.pointers, this.isarray ]
            return struct_function

    # noinspection PyUnusedLocal
    @structPointers( -1, root=True ) # root because this defines _pass for non-root
    def _pass(offset): pass
    
    # NOTE: if you have an alignment issue with a pathfinder struct, it can be pretty difficult to find, so be careful.
    
    ################################################################################################
    ## Super Smash Bros. Melee players and trophies
    ################################################################################################
    
    # these global statements are needed, or else NameError (Python2 is not very good at namespaces/scopes)
    global BoneIDs; BoneIDs={}
    global BoneNames; BoneNames={}
    global materials; materials=[]
    global UV_Scales; UV_Scales={}
    global UV_Offsets; UV_Offsets={}
    global rigName; rigName='joint_obj'
    
    global _GAME; _GAME=None
    
    def MTX44(): return [[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]

    '''this will change'''
    str_off='%08X'.__mod__ #returns a hex-string of a given int offset '00000000'
    
    #-----------------------------------------------------------------------------------------------
    
    # noinspection PyUnusedLocal
    def color(A,offset): return [255,255,255,255] #yet to be seen (returning white)
    # noinspection PyUnusedLocal
    def _RGB565(v=None,label='',*args,**kw): D,r = bu16(),1./31; return [((D>>11)&31)*r,((D>>5)&63)*(1./63),(D&31)*r]
    _RGB8 = struct( 3, R=bu8, G=bu8, B=bu8 )
    _RGBX8s = struct( 4, R=bu8, G=bu8, B=bu8, A=bu8 )
    _RGBX8 = lambda v=None,label='',*args,**kw: _RGBX8s()[:3]
    _RGBA4s = struct( 2, RG=bu8, BA=bu8 )
    # noinspection PyUnusedLocal
    def  _RGBA4(v=None,label='',*args,**kw): RG,BA = _RGBA4s(); r = 1./15; return [(RG>>4)*r,(RG&15)*r,(BA>>4)*r,(BA&15)*r]
    # noinspection PyUnusedLocal
    def  _RGBA6(v=None,label='',*args,**kw): D,r = bu24(),1./63; return [(D>>18)*r,((D>>12)&63)*r,((D>>6)&63)*r,(D&63)*r]
    _RGBA8 = struct( 4, R=bu8, G=bu8, B=bu8, A=bu8 )
    DClrFmts=[ _RGB565, _RGB8, _RGBX8, _RGBA4, _RGBA6, _RGBA8 ].__getitem__ # direct color formats
    
    DataType = [bu8,bs8,bu16,bs16,bf32].__getitem__
    
    cmpCntVert = [2,3].__getitem__
    cmpCntNorm = [3,9].__getitem__
    cmpCntColor = [3,4].__getitem__
    cmpCntUV = [1,2].__getitem__
    
    globals()['first_step'] = True
    class pseudofloat(object):
        def __init__(this,exp): this.exp = exp
        __call__ = lambda this,v: v/(2.**this.exp)
        '''
        def __call__(this,v):
            pw = 2.**this.exp
            res = v/pw
            if globals()['first_step']:
                print('11 == %s'%this.exp.__value__)
                print('2.**11 == 2048.0 == %s'%pw)
                print('192/2048.0 == 0.09375 == %s'%res)
                globals()['first_step'] = False
                
            return res
        '''
    # WARNING: NOT NOOB FRIENDLY! (this returns a data struct representing the vector data)
    def DT( _attr ):
        if _attr==None: return None
        CPi, CPt, Cc, Dt, Exp, unk, SF, data = _attr
        if CPt == 0: return None # null
        
        switch(CPi)
        components = 3 # default
        if case(9): components = cmpCntVert(Cc)
        if case(10,25): components = cmpCntNorm(Cc)
        if case(11,12): components = cmpCntColor(Cc)
        if case(13,14,15,16,17,18,19,20): components = cmpCntUV(Cc)
        
        # here's some switch/case abuse ;)
        if CPt == 1: # direct data
            if case(0,1,2,3,4,5,6,7,8): return bu8 # influence/texture matrices (always direct)
            if case(11,12): # direct colors
                #alpha = attr.Cc
                return DClrFmts(SF)
        
        # assume indexed
        if case(9,10,13,14,15,16,17,18,19,20): # TODO: colors
            I = bu8 if CPt == 2 else bu16
            vec = array( DataType(Dt), count=components,
                # yes this is a mild performance hit, but there's no efficient way to prevent confusion
                # (the problem is _attr being set to the last CP-attribute for all fp_struct attributes)
                offset=lambda v=None, label='', *args, **kw: data+(I( label=' -- %s Index'%label )*SF), # determine the offset from the index
                map=pseudofloat(Exp) if Dt < 4 else None ) # parse our mantissas if needed
            vec.__color__ = 0xA0A0FF
            return vec
    
    _AttrLabels = {' -- Attributes':{' -- Attribute': [' -- CP_index',' -- CP_Type',' -- CmpCount',' -- Data_Type',' -- Exponent',' -- Unknown',' -- Stride/Format','Data']}}
    
    Attr = struct( 24, CPi=bu32, CPt=bu32, Cc=bu32, Dt=bu32, Exp=bu8, unk=bu8, SF=bu16, data=ptr); Attr.__color__ = 0xFFFF40
    AttrArr = array( Attr, [255,None,None,None,None,None,None,None], offset=ptr ); AttrArr.__color__ = 0xFFFF80
    WeightArr = array( struct( 8, bn=ptr, W=bf32 ), [32,0], map=lambda ws: ['bn%08X'%ws.bn,ws.W] ); WeightArr.__color__ = 0xA0A0FF
    InfluenceArr = array( ptr, stop=32, map=lambda p: WeightArr(offset=p) ); InfluenceArr.__color__ = 0xC0C0FF
    
    def InfluencePtrValidation(v=None, label='', *args, **kw):
        pointer_value = ptr()
        return InfluenceArr(offset=pointer_value,label=label) if pointer_value>32 else []
        
    Mesh = struct( 24, Str=ptr, Nx=ptr, attrs=AttrArr, flags=bu16, DL_size=bu16, DL_data=ptr, weights=InfluencePtrValidation ); Mesh.__color__ = 0xC0C0FF
    
    # TODO: move this:
    WCTVMesh = struct( Str=ptr, Nx=ptr, flags=bu16, DL_size=bu16, DL_data=ptr, attrs=AttrArr )
    
    def fp_map(fp=None, XF_Influence_array=[], OX=0,OY=0, SX=1,SY=1 ):
        ugeSetFacepoint()
        if fp.infl!=None: map( ugeSetWeight, *zip(*XF_Influence_array[fp.infl/3]) )
        if fp.txmtx0: pass
        if fp.txmtx1: pass
        if fp.txmtx2: pass
        if fp.txmtx3: pass
        if fp.txmtx4: pass
        if fp.txmtx5: pass
        if fp.txmtx6: pass
        if fp.txmtx7: pass
        if fp.vert: ugeSetUTVert(fp.vert)
        if fp.norm: ugeSetUTNormal(fp.norm)
        if fp.col0: ugeSetColor(fp.col0, channel=0) #color0
        if fp.col1: ugeSetColor(fp.col1, channel=1) #color1
        # TODO: these transformations should be applied internally: (will be done when texture matrices are supported)
        if fp.uv0: ugeSetUV([ (fp.uv0[0]*SX)+OX, (fp.uv0[1]*SY)+OY ], channel=0) #UV0
        if fp.uv1: ugeSetUV([ (fp.uv1[0]*SX)+OX, (fp.uv1[1]*SY)+OY ], channel=1) #UV1
        if fp.uv2: ugeSetUV([ (fp.uv2[0]*SX)+OX, (fp.uv2[1]*SY)+OY ], channel=2) #UV2
        if fp.uv3: ugeSetUV([ (fp.uv3[0]*SX)+OX, (fp.uv3[1]*SY)+OY ], channel=3) #UV3
        if fp.uv4: ugeSetUV([ (fp.uv4[0]*SX)+OX, (fp.uv4[1]*SY)+OY ], channel=4) #UV4
        if fp.uv5: ugeSetUV([ (fp.uv5[0]*SX)+OX, (fp.uv5[1]*SY)+OY ], channel=5) #UV5
        if fp.uv6: ugeSetUV([ (fp.uv6[0]*SX)+OX, (fp.uv6[1]*SY)+OY ], channel=6) #UV6
        if fp.uv7: ugeSetUV([ (fp.uv7[0]*SX)+OX, (fp.uv7[1]*SY)+OY ], channel=7) #UV7
        if fp.vmtxarr: print('vert matrix array found, please report!')
        if fp.nmtxarr: print('normal matrix array found, please report!')
        if fp.txmtxarr: print('UV matrix array found, please report!')
        if fp.lmtxarr: print('light matrix array found, please report!')
        #if fp.nbt!=None: ugeSetUTNormal(None if fp.nbt=='' else vector(1,_attr[25],fp.nbt)) #NBT (NX,NY,NZ, BX,BY,BZ, TX,TY,TZ)
        '''NBT:
        0x000003C07C: read 0x00000019 as 25 CP_index
        0x000003C080: read 0x00000003 as 3  CP_Type
        0x000003C084: read 0x00000001 as 1  CompCnt: NBT
        0x000003C088: read 0x00000004 as 4  Data_Type
        0x000003C08C: read 0x00 as 0        Exponent
        0x000003C08D: read 0x00 as 0        unk
        0x000003C08E: read 0x0024 as 36     stride
        0x000003C090: read 0x00007200 as 29184  offset
        '''
        return fp # not that the array cares about the mapped value, but still
    
    _FPLabels = (' -- XF_Influence_index, -- TexMtx0, -- TexMtx1, -- TexMtx2, -- TexMtx3, -- TexMtx4, -- TexMtx5, -- TexMtx6, -- TexMtx7'
           ', -- Vert Index/value, -- Normal Index/value, -- Color0 Index/value, -- Color1 Index/value'
           ', -- UV0 Index/value, -- UV1 Index/value, -- UV2 Index/value, -- UV3 Index/value, -- UV4 Index/value, -- UV5 Index/value, -- UV6 Index/value, -- UV7 Index/value'
           ', -- vert matrix array, -- normal matrix array, -- texture matrix array, -- light matrix array, -- NBT Index/value').split(',')
    _CP_enum = {
        '78': ( UGE_POLYGON,         'Polygon' ), # possible support based on pattern (hasn't actually been seen)
        '80': ( UGE_QUADS,           'Quads' ),
        '88': ( UGE_QUADSTRIP,       'QuadStrip' ), # possible support based on pattern (hasn't actually been seen)
        '90': ( UGE_TRIANGLES,       'Triangles' ),
        '98': ( UGE_TRIANGLESTRIP,   'TriangleStrip' ),
        'A0': ( UGE_TRIANGLEFAN,     'TriangleFan' ),
        'A8': ( UGE_LINES,           'Lines' ),
        'B0': ( UGE_LINESTRIP,       'LineStrip' ),
        'B8': ( UGE_POINTS,          'Points' ) }
    def prim_map(command,_attr=None):
        _Type,_LB = _CP_enum[command]
        ugeSetPrimitive(_Type)
        
        # build the facepoint struct using the attributes: (uge structs support None for disabled fields)
        fp_struct = struct(
            infl    = DT(_attr[0] ),
            txmtx0  = DT(_attr[1] ),
            txmtx1  = DT(_attr[2] ),
            txmtx2  = DT(_attr[3] ),
            txmtx3  = DT(_attr[4] ),
            txmtx4  = DT(_attr[5] ),
            txmtx5  = DT(_attr[6] ),
            txmtx6  = DT(_attr[7] ),
            txmtx7  = DT(_attr[8] ),
            vert    = DT(_attr[9] ),
            norm    = DT(_attr[10]),
            col0    = DT(_attr[11]),
            col1    = DT(_attr[12]),
            uv0     = DT(_attr[13]),
            uv1     = DT(_attr[14]),
            uv2     = DT(_attr[15]),
            uv3     = DT(_attr[16]),
            uv4     = DT(_attr[17]),
            uv5     = DT(_attr[18]),
            uv6     = DT(_attr[19]),
            uv7     = DT(_attr[20]),
            vmtxarr = DT(_attr[21]),
            nmtxarr = DT(_attr[22]),
            txmtxarr= DT(_attr[23]),
            lmtxarr = DT(_attr[24]),
            nbt     = DT(_attr[25]),
        ); fp_struct.__color__ = 0xA0A0A0
        
        fp_array = array( fp_struct, count=bu16, map=fp_map ); fp_array.__color__ = 0xFF80FF
        return fp_array(label={' -- FacePoints in %s'%_LB:{' -- FacePoint':_FPLabels}})
    
    @structPointers( 24, {
        0:'_pass',
        4:'_mesh',
        8:'_pass', # (facepoint attributes)
        16:'_pass', # (display-list data)
        20:'_pass' }) # (weights)
    def _mesh(Mesh_Offset,Material_Offset,rig,vBone):
        global BoneIDs
        name='me%08X'%Mesh_Offset
        # Tcll - I need to look into this code more:
        # pobj_type(pobj) == POBJ_SHAPEANIM && pobj->u.shape_set
        
        #if _GAME=='WCTV': # TODO: remove from here
        #    me = WCTVMesh( offset=offset, label={' -- Mesh':['String','Next Mesh',' -- Unknown Flags',' -- Display List size','Display List',_AttrLabels]} )
        #else:
        me = Mesh( offset=Mesh_Offset, label={' -- Mesh':['String','Next Mesh', _AttrLabels,' -- Unknown Flags',' -- Display List size','Display List', {' -- XF Influence Array':''}]})
        
        ugeSetMesh( name )
        _material( Material_Offset, False) # define our material (if needed)
        SX, SY = UV_Scales[Material_Offset] if Material_Offset in UV_Scales else (1, 1)
        OX, OY = UV_Offsets[Material_Offset] if Material_Offset in UV_Offsets else (0, 0)
        fp_map.func_defaults = ( None, me.weights, OX,OY, SX,SY ) # quicker and safer than globals
        
        if me.flags&255 == 0x89: print('visibility flags found for object: %s'%name)
        # ^ this will soon fix those meshes which are still at the center, transforming via the visibility bone.
        
        _attr = { CP_ID:None for CP_ID in range(26) }
        for attr in me.attrs: _attr[attr.CPi] = attr
        prim_map.func_defaults = ( None, _attr )
        primitive_array = array( bh8, stop='00', offset=me.DL_data, map=prim_map ); primitive_array.__color__ = 0xFFA8FF
        primitive_array(label={' -- Primitives':' -- Primitive Type'})
        
        _material(Material_Offset) # apply the material to the current mesh
        if me.Nx>32: _mesh( me.Nx, Material_Offset, rig, vBone)

    #-----------------------------------------------------------------------------------------------
    
    Palette = struct( 16, data=ptr, Fmt=bu32, unk1=bu32, Cnt=bu16, unk2=bu16 ); Palette.__color__ = 0x40FFA0
    @structPointers( 16, {0: '_pass' } ) # (palette data)
    def _palette(Palette_Offset):
        pl = Palette( offset=Palette_Offset, label={' -- Palette Header':['Data',' -- Format',' -- Unknown',' -- Color Count',' -- Unknown']})
        
        # hack (fixes index errors by reading the max amount)
        '''
        switch(imgFormat)
        if case(8): clrCount = 16
        if case(9): clrCount = 256
        if case(10): clrCount = 16384 #NOTE: slightly possible EOF error
        '''
        jump(pl.data, label=' -- Color Data')
        ugeSetImagePalette( readpal(pl.Cnt,pl.Fmt) )

    imageData={}
    Image = struct( 24, data=ptr, W=bu16, H=bu16, Fmt=bu32 ); Image.__color__ = 0x48FF48
    @structPointers( 24, {0: '_pass' } ) # (image data)
    def _image(Image_Offset):
        im = Image( offset=Image_Offset, label={' -- Image Header':['Data',' -- Width',' -- Height',' -- Format']})
        dataOffset = im.data
        jump(dataOffset, label=' -- Pixel Data')
        ugeSetImage('im%08X'%dataOffset)
        if dataOffset not in imageData: imageData[dataOffset] = readimg(im.W,im.H,im.Fmt) # prevent memory overload
        ugeSetImageWidth(im.W); ugeSetImageHeight(im.H)
        ugeSetImageData( imageData[dataOffset] )
        
    Texture = struct( 92,
        Str=ptr, Nx=ptr, unk1=bu32, flags=bu32, unk2=bu32, unk3=bu32, unk4=bu32, unk5=bf32,
        X=bf32, Y=bf32, A=bf32, x=bf32, y=bf32, wrapS=bu32, wrapT=bu32, scaleX=bu8, scaleY=bu8,
        unk6=bu16, unk7=bu32, unk8=bf32, unk9=bu32, img=ptr, pal=ptr, unk10=bu32, unk11=ptr )
    Texture.__color__ = 0xFFF040
    @structPointers( 92, {
        0:'_pass', # string
        4:'_texture',
        76:'_image',
        80:'_palette',
        88:'_pass' })
    def _texture(Texture_Offset,Material_Offset):
        name='tx%08X'%Texture_Offset
        tx = Texture( offset=Texture_Offset, label={' -- Texture':[
            'String','Next Texture',' -- Unknown',' -- Layer Flags',' -- Unknown',' -- Unknown',' -- Unknown',' -- Unknown',
            ' -- (?) TexClamp Max X',' -- (?) TexClamp Max Y',' -- (?) TexClamp Angle',' -- (?) TexClamp Min X',' -- (?) TexClamp Min Y',
            ' -- Wrap S',' -- Wrap T',' -- Scale X',' -- Scale Y',' -- Unknown',' -- Unknown',' -- Unknown',' -- Unknown',
            'Image','Palette',' -- Unknown','Unknown'] } )
        
        global UV_Offsets; UV_Offsets[Material_Offset] = [0,0]
        TextureParams = [UGE_TEX_REPEAT, UGE_TEX_REPEAT]
        if tx.wrapS == 0: TextureParams[0] = UGE_TEX_CLAMP_EDGE
        if tx.wrapS == 2: TextureParams[0] = UGE_TEX_MIRRORED_REPEAT
        if tx.wrapT == 0: TextureParams[1] = UGE_TEX_CLAMP_EDGE
        if tx.wrapT == 2: TextureParams[1] = UGE_TEX_MIRRORED_REPEAT; UV_Offsets[Material_Offset][1] = -1
        
        #TODO: apply texture settings
        ugeSetTexture(name)
        ugeSetTexParam( UGE_TEX_2D, UGE_TEX_WRAP_S, TextureParams[0] )
        ugeSetTexParam( UGE_TEX_2D, UGE_TEX_WRAP_T, TextureParams[1] )
        
        global UV_Scales; UV_Scales[Material_Offset] = [tx.scaleX,tx.scaleY]
        
        if tx.img>32: _image(tx.img)
        if tx.pal>32: _palette(tx.pal)
        if tx.Nx>32: _texture(tx.Nx,Material_Offset)

    RGBA8 = struct(4,R=bu8,G=bu8,B=bu8,A=bu8); RGBA8.__color__ = 0xE0E0E0
    Colors = struct( 20, D=RGBA8, A=RGBA8, S=RGBA8, trans=bf32, Sh=bf32 ); Colors.__color__ = 0xFFA860
    def colors(offset):
        cl = Colors( offset=offset, label={' -- Material-Colors':[' -- Diffuse',' -- Ambient',' -- Specular',' -- (?) Transparency',' -- Shininess']})
        ugeSetMatAmbient(cl.A)
        ugeSetMatDiffuse(cl.D)
        ugeSetMatSpecular(cl.S)
        ugeSetMatShine(cl.Sh)

    # noinspection PyUnusedLocal
    @structPointers( 32, {0: '_pass' } ) # (data)
    def _unknown1(offset): pass
    
    Material = struct( 24, Str=ptr, Fl=bu32, Tex=ptr, Clr=ptr, unk1=bu32, unk2=ptr ); Material.__color__ = 0xFFA080
    @structPointers( 24, {
        0:'_pass', # string
        8:'_texture',
        12:'_pass', # (A,D,S color data)
        20:'_pass', }) # unknown (not documented) (detected by path finder in KAR)
    def _material(Material_Offset,_apply=True):
        name='ma%08X'%Material_Offset
        if Material_Offset not in materials:
            ugeSetMaterial(name, False) # define only
            ma = Material( offset=Material_Offset, label={' -- Material':['String',' -- Blending Flags','Texture','Material-Colors',' -- Unknown','Unknown (KAR)']})
            
            # render mode flags: (referenced from SSBM: boot.dol - Data5)
            # RENDER_SPECULAR
            
            if ma.Tex>32: _texture(ma.Tex,Material_Offset)
            if ma.Clr>32: colors(ma.Clr) # colors are already defaulted
            materials.append(Material_Offset)
        else: ugeSetMaterial(name,_apply)
    
    Object = struct( 16, Str=ptr, Nx=ptr, Mat=ptr, Msh=ptr ); Object.__color__ = 0xC0C0C0
    @structPointers( 16, {
        0:'_pass', # string
        4:'_object',
        8:'_material',
        12:'_mesh' })
    def _object(Object_Offset, rig, vBone):
        name = 'ob%08X'%Object_Offset
        ob = Object( offset=Object_Offset, label={' -- Object':['String','Next Object','Material','Mesh']})
        if ob.Nx>32: _object(ob.Nx, rig, vBone)
        if ob.Mat>32: _material(ob.Mat,False) # define first, apply below
        if ob.Msh>32:
            ugeSetObject( name )
            ugeSetObjectParent( rig )
            _mesh(ob.Msh,ob.Mat, rig, vBone)
    
    Bone = struct( 64, Str=ptr, Fl=bu32, Ch=ptr, Nx=ptr, Obj=ptr, Rot=vec3, Sca=vec3, Loc=vec3, inv=ptr, unk=bu32 ); Bone.__color__ = 0xF8D060
    @structPointers( 64, {
        0:'_pass', # string
        8:'_bone',
        12:'_bone',
        16:'_object',
        56:'_pass' # (IB matrix)
    }, root=True)
    def _bone(Bone_Offset, parent=None, prev=None, rig ='joint_obj'):
        global BoneIDs,BoneNames
        BoneNames[Bone_Offset] = name ='bn%08X'%Bone_Offset
        bn = Bone( offset=Bone_Offset, label={' -- Bone': ['String',' -- Unknown Flags','Child Bone','Next Bone','Object',
            ' -- Rotation',' -- Scale',' -- Location','Inverse-Bind Matrix',' -- Unknown'] } )
        
        # flag names: (referenced from SSBM: boot.dol - Data5)
        # JOBJ_USE_QUATERNION   = ?? # (jobj->flags & JOBJ_USE_QUATERNION)
        # JOBJ_INSTANCE         = ?? # !(jobj->flags & JOBJ_INSTANCE)
        
        ugeSetObject(rig) # make sure we're using our Rig object (or create it if not available)
        BoneIDs[Bone_Offset] = BID = ugeSetBone(name) # BoneIDs for matanim structs
        ugeSetBoneParent(parent)#; ugeSetBonePrev(prev)
        ugeSetBoneLoc(bn.Loc); ugeSetBoneRot(bn.Rot); ugeSetBoneSca(bn.Sca)
        
        # World Inverse-Bind (only important for fast rendering, not needed here as it's calculated from the LRS above)
        #ibm = list(matrix34(offset=bn.inv,label=' -- Inverse-Bind Matrix'))+[[0.,0.,0.,1.]] if bn.inv>32 else pibm # or use parent matrix
        if bn.Ch>32: _bone(bn.Ch,BID,None, rig=rig)
        if bn.Nx>32: _bone(bn.Nx,parent,BID, rig=rig)
        if bn.Obj>32: _object(bn.Obj, rig=rig, vBone=Bone_Offset)
    
    ################################################################################################
    ## Super Smash Bros. Melee stages
    ################################################################################################
        
    @structPointers( 156, {
            0:'_bone',
            4:'_pass', # MapQuinList
            8:'_pass', # MatAnimAList
            12:'_pass', # MapHeadFList
            16:'_pass', # _MapHeadC
            24:'_pass', # MapPlitBl
            28:'_pass', # MapHeadD
            40:'_pass' }) # AllorNot?? (bone)
    def _MapHeadB(offset):
        jump(offset, label=' -- MapHeadB Struct') # Tcll - is this a weight-link rather than an actual bone?? (like Pl files)
        
        ptr0 = bu32(label=' -- bone Pointer')+32
        ptr1 = bu32(label=' -- Unknown Pointer')+32
        ptr2 = bu32(label=' -- Unknown Pointer')+32
        ptr3 = bu32(label=' -- Unknown Pointer')+32
        ptr4 = bu32(label=' -- Unknown Pointer')+32
        unk0 = bu32(label=' -- Unknown')
        ptr5 = bu32(label=' -- Unknown Pointer')+32
        ptr6 = bu32(label=' -- Unknown Pointer')+32
        unk1 = bu32(label=' -- Unknown')
        unk2 = bu32(label=' -- Unknown')
        ptr7 = bu32(label=' -- Unknown Pointer')+32
        unk3 = bu32(label=' -- Unknown')
        unk4 = bu32(label=' -- Unknown')

        name = str_off(offset)
        if ptr0>32: _bone(ptr0,rig='jobj_MHB.%s'%name)
    
    @structPointers( 12, {
            0:'_bone',
            4:'_pass' }, # array([bu16,bu16])() Halves
            True)
    def _MapHeadJD(offset):
        jump(offset, label=' -- BoneDef Struct')
        
        Bone = bu32(    label=' -- Bone Pointer')+32
        Halves = bu32(  label=' -- Unknown Pointer')+32
        Halvesn = bu32( label=' -- Unknown')

        name = str_off(offset)
        if Bone>32: _bone(Bone,rig='jobj_MHJD.%s'%name)

    # Tcll - OMG!!! my program is out-classing hackers, including myself! =D
    # now all that's left to do is make it self-aware. ^_^
    @structPointers( 48, {
        0:'_MapHeadJD',
        8:'_pass', # _MapHeadB
        16:'_pass', # unknown (not documented) (detected by path finder)
        24:'_pass', # _MapHeadE
        32:'_pass', # unknown (not documented) (detected by path finder)
        40:'_pass', # unknown (not documented) (detected by path finder)
    }, root=True)
    def _MapHead(offset):
        jump(offset, label=' -- MapHead Struct')
        
        JDFA = bu32(    label=' -- MapHeadJD Array Pointer')+32
        JDFn = bu32(    label=' -- Unknown')
        MHBA = bu32(    label=' -- MapHeadB Array Pointer')+32
        MHBn = bu32(    label=' -- Unknown')
        unk1 = bu32(    label=' -- Unknown Array Pointer') # pointer detected by path finder
        unk2 = bu32(    label=' -- Unknown')
        MHE = bu32(     label=' -- MapHeadE Array Pointer')+32
        MHEn = bu32(    label=' -- Unknown')
        unk3 = bu32(    label=' -- Unknown Array Pointer') # pointer detected by path finder
        unk4 = bu32(    label=' -- Unknown')
        unk5 = bu32(    label=' -- Unknown Array Pointer') # pointer detected by path finder
        unk6 = bu32(    label=' -- Unknown')

        #TODO: (1 or 2) (both seem to use the same bones, which would create 2 rig objects of the same bones)
        # 1: ignore JDFA and create rig objects with MHBA (similar to matAnim)
        # 2: create a global rig object with JDFA and link the bones through MHBA
        if JDFA>32:
            for i in range(JDFn): _MapHeadJD(JDFA+(12*i))
            '''
            for i,(bone_ptr,ptr1,unk0) in enumerate( array([bu32,bu32,bu32],count=(None if JDFn==0 else JDFn))(offset=JDFA) ):
                if bone_ptr>0: _bone(bone_ptr+32,'MH_jobj_%i'%i)
            '''
        # ^ not sure if I should get rid of this and do this through MHBA
    
    ################################################################################################
    ## Super Smash Bros. Melee other (stuff that isn't currently supported in UMC/UGE)
    ################################################################################################
        
    @structPointers( 12, {
        0:'_matAnim',
        4:'_matAnim',
        8:'_pass' # matAnimB
    }, root=True)
    def _matAnim(offset): pass
        
    ################################################################################################
    ## Kirby Air-Ride stars and some maps
    ################################################################################################
    
    KAR2 = struct( 44, bn=ptr, unk1=bu32, unk2=bf32, unk3=bu32, a0=ptr, a1=ptr, a2=ptr, a3=ptr, a4=ptr, a5=ptr, bn2=ptr ); KAR2.__color__ = 0x8080FF
    @structPointers( 44, {
        0:'_bone',
        16:'_pass', #'unk7'],
        20:'_pass', #'unk7'],
        24:'_pass', #'unk7'],
        28:'_pass', #'unk7'],
        32:'_pass', #'unk7'],
        36:'_pass', #'unk7'],
        40:'_bone'
    }, root=True)
    def _KARStruct2(offset):
        k2 = KAR2( offset=offset, label={ ' -- KAR Struct 2': ['Bone',' -- Unknown',' -- Unknown',' -- Unknown','Attribute','Attribute','Attribute','Attribute','Attribute','Attribute','Bone'] } )
        
        name = str_off(offset)
        if k2.bn>32: _bone(k2.bn,rig='KAR_jobj.%s'%name)
        if k2.bn2>32: _bone(k2.bn2,rig='KAR_jobj2.%s'%name)
        
    KAR1 = struct( 44, Str=ptr, kar2=ptr, unk1=ptr, mtx=ptr, kar3=ptr, unk2=ptr, kar7=ptr ); KAR1.__color__ = 0xFF8080
    @structPointers( 44, {
        0:'_pass',
        4:'_KARStruct2',
        8:'_pass', #'unk4'],
        12:'_pass', # (matrix)
        16:'_pass', #'unk5'],
        20:'_pass',
        24:'_pass' #'unk6']
    }, root=True)
    def _KARStruct1(offset):
        k1 = KAR1( offset=offset, label={ ' -- KAR Struct 1': ['Unknown','Struct 2','Unknown','Matrix','Struct 5','Unknown','Struct 7'] } )
        if k1.kar2>32: _KARStruct2(k1.kar2)
        
    @structPointers( 20, {
        0:'_bone',
        16:'_pass' })
    def _unknown2(offset):
        jump(offset, label=' -- _Unknown2 Struct')
        
        bone_ptr = bu32(    label=' -- bone Pointer')+32
        unk0 = bu32(    label=' -- Unknown')
        unk1 = bu32(    label=' -- Unknown')
        unk2 = bu32(    label=' -- Unknown')
        ptr2 = bu32(    label=' -- Unknown Pointer')+32
        
        name = str_off(offset)
        if bone_ptr>32: _bone(bone_ptr, rig='unk_jobj.%s'%name)
    
    @structPointers( 16, {
        0:'_unknown2',
        4:'_pass',
        12:'_pass' }, root=True)
    def _unknown(offset):
        jump(offset, label=' -- _Unknown Struct')
        
        ptr0 = bu32(    label=' -- bone Pointer')+32
        ptr1 = bu32(    label=' -- Unknown Pointer')+32
        unk0 = bu32(    label=' -- Unknown')
        ptr2 = bu32(    label=' -- Unknown Pointer')+32
        
        if ptr0>32: _unknown2(ptr0)
        
    ################################################################################################
    ## Wii Channel TV
    ################################################################################################

    def _wctv_palette(offset,imageNames):
        jump(offset,      label=' -- sub-Pallet Struct')
        
        palData = bu32(   label=' -- Pallet Data Offset')+32
        palFormat = bu32( label=' -- Format')
        image_ID = bu32(  label=' -- Unknown')
        clrCount = bu16(  label=' -- Color Count')
        pal_unk2 = bu16(  label=' -- Unknown')
        
        jump(palData, label=' -- Pallet Data')
        pal = readpal(clrCount,palFormat)
        
        ugeSetImage(imageNames[image_ID])
        ugeSetImagePalette(pal)

    #@structpointers( 24, [0,'_pass'] )
    def _wctv_image(offset, palette_offset, texture_offset):
        jump(offset, label=' -- Image Struct')
        
        imgData = bu32( label=' -- Pixel Data Offset')+32
        imgWidth = bu16(label=' -- Width')
        imgHeight= bu16(label=' -- Height')
        imgFormat=bu8(  label=' -- Format')
        wctv_unk0=bu8(  label=' -- Unknown') # channel??
        wctv_unk1=bu8(  label=' -- Unknown')
        wctv_unk2=bu8(  label=' -- Unknown')
        
        jump(imgData, label=' -- Pixel Data')
        name = 'img'+str_off(imgData)
        ugeSetImage(name)
        ugeSetImageWidth(imgWidth)
        ugeSetImageHeight(imgHeight)
        ugeSetImageData( readimg(imgWidth,imgHeight,imgFormat) )
        
        if palette_offset>32: _palette(palette_offset)
        return name

    def _wctv_Texture(offset,material): # texture structures offset from texture array
        jump(offset, label=' -- sub-Texture Struct')
        
        name='tex'+str_off(offset)
        
        Image = bu32(       label=' -- Image Offset')+32
        wctv_tx_unk0 = bu32(label=' -- Unknown Offset')+32
        
        wctv_tx_unk1 = bu8( label=' -- Unknown')
        
        WrapS = bu8(        label=' -- Wrap S')
        WrapT = bu8(        label=' -- Wrap T')

        ScaleX = bu8(       label=' -- Scale X')
        ScaleY = bu8(       label=' -- Scale Y')
        
        wctv_tx_unk2 = bu8( label=' -- Unknown')
        wctv_tx_unk3 = bu8( label=' -- Unknown')
        wctv_tx_unk4 = bu8( label=' -- Unknown')
        
        wctv_tx_unk5 = bu32(label=' -- Unknown')
        wctv_tx_unk6 = bu32(label=' -- Unknown')
        wctv_tx_unk7 = bu32(label=' -- Unknown')

        global UV_Offsets; UV_Offsets[material] = [0,0]
        global UV_Scales; UV_Scales[material] = [1,1]
        
        TextureParams = [UGE_TEX_REPEAT, UGE_TEX_REPEAT]
        if WrapS == 0: TextureParams[0] = UGE_TEX_CLAMP_EDGE
        if WrapS == 2: TextureParams[0] = UGE_TEX_MIRRORED_REPEAT
        if WrapT == 0: TextureParams[1] = UGE_TEX_CLAMP_EDGE
        if WrapT == 2: TextureParams[1] = UGE_TEX_MIRRORED_REPEAT; UV_Offsets[material][1] = -1
        
        #TODO: apply texture settings
        ugeSetTexture(name)#, TextureParams)
        ugeSetTexParam( UGE_TEX_2D, UGE_TEX_WRAP_S, TextureParams[0] )
        ugeSetTexParam( UGE_TEX_2D, UGE_TEX_WRAP_T, TextureParams[1] )
        
        if Image>32: return _wctv_image(Image, 0, offset)
            
    @structPointers( 56, {
        0:'_pass',
        8:'_pass',
        12:'_pass',
        16:'_pass',
        20:'_pass',
        24:'_pass',
        28:'_pass',
        44:'_pass',
        48:'_pass' })
    def _wctv_material(offset,_apply=True):
        name='mat'+str_off(offset)
        if offset not in materials:
            jump(offset, label=' -- Material Struct')
            ugeSetMaterial(name, False)
                
            _String = bu32(     label=' -- string Offset')+32 # this is not a name, but some sort of identifier, probably for a function.
            wctv_ma_flags= bu32(label=' -- Unknown Flags')
            Texture = bu32(     label=' -- Texture Offset')+32 # currently 0
            Colors = bu32(      label=' -- Material Colors Offset')+32
            Textures = bu32(    label=' -- Texture Array Offset')+32
            wctv_ma_unk3 = bu32(label=' -- Unknown Offset') # BP-TEV array?? (pseudo-shaders)
            Palettes = bu32(    label=' -- Pallet Array Offset')+32
            wctv_ma_unk5 = bu32(label=' -- Unknown Offset')+32 # BP-XF matrix register array??
            wctv_ma_unk6 = bu32(label=' -- Unknown')
            wctv_ma_unk7 = bu32(label=' -- Unknown')
            wctv_ma_unk8 = bu32(label=' -- Unknown')
            wctv_ma_unk9 = bu32(label=' -- Unknown Offset')+32 # texture matrix array??
            wctv_ma_unk10= bu32(label=' -- Unknown Offset')+32 # SD_ColExpRawDesc array??
            wctv_ma_unk11= bu32(label=' -- Unknown')
            wctv_ma_unk12= bu32(label=' -- Unknown')
            
            if Textures>32:
                images = [ _wctv_Texture(texture+32,offset) for texture in array(bu32,)(offset=Textures) ]
                if Palettes>32: [ _wctv_palette(palette+32,images) for palette in array(bu32,)(offset=Palettes) ]
            materials.append(offset)
        else: ugeSetMaterial(name,_apply)
    
    @structPointers( 64, {
        0:'_pass',
        4:'_wctv_object',
        12:'_wctv_material',
        16:'_mesh' })
    def _wctv_object(offset):
        jump(offset, label=' -- Object Struct')
        
        _String = bu32(     label=' -- string Offset')+32 # this is not a name, but some sort of identifier, probably for a function.
        Next = bu32(        label=' -- Next Object Struct Offset')+32
        wctv_ob_unk = bu32( label=' -- Unknown') # normally 0x00000004
        Material = bu32(    label=' -- Material Struct Offset')+32
        Mesh = bu32(        label=' -- Mesh Struct Offset')+32
        
        if Next>32: _wctv_object(Next)
        if Material>32: _wctv_material(Material,False)
        if Mesh>32: _mesh(Mesh,Material) # TODO: objects supporting multiple meshes
    
    @structPointers( 64, {
        0:'_pass',
        8:'_wctv_bone',
        12:'_wctv_bone',
        16:'_wctv_object',
        56:'_pass' }) # (IB marix)
    def _wctv_bone(offset, parent=None, prev=None, pibm=MTX44(), rig = 'joint_obj'):
        jump(offset, label=' -- Bone Struct')
        name = 'bn'+str_off(offset)
        
        _String = bu32( label=' -- string Offset')+32 # this is not a name, but some sort of identifier, probably for a function.
        Flags = bu32(   label=' -- Unknown Bone Flags')
        Child = bu32(   label=' -- Child Bone Struct Offset')+32
        Next = bu32(    label=' -- Next Bone Struct Offset')+32
        Object = bu32(  label=' -- Object Struct Offset')+32
        
        # make sure we're using our Rig object (or create it if not available)
        ugeSetObject(rig) ##
        BID = ugeSetBone(name) ##
        
        ugeSetBoneParent(parent) ##
        ugeSetBonePrev(prev) ##
        
        Rotation = array(bf32,count=3)()
        Scale    = array(bf32,count=3)()
        Location = array(bf32,count=3)()
        ugeSetBoneLoc(Location) ##
        ugeSetBoneRot(Rotation) ##
        ugeSetBoneSca(Scale) ##
        
        inv_off = bu32( label=' -- Inverse-Bind Matrix Offset')+32
        bn_unk2 = bu32( label=' -- Unknown')
        if inv_off>32: # World Inverse-Bind
            ibm = array(array(bf32,count=4),count=3)(offset=inv_off)+[[0.,0.,0.,1.]]
        else: ibm=pibm  # use parent matrix
        
        global BoneIDs; BoneIDs[offset] = BID # for matanim structs
        global BoneNames; BoneNames[offset] = name
        
        if Child>32: _wctv_bone(Child,BID,None,ibm, rig=rig)
        if Next>32: _wctv_bone(Next,parent,BID,pibm, rig=rig)
        if Object>32: _wctv_object(Object)
    
    @structPointers( 8, {
        0:'_wctv_bone',
        4:'_pass' })
    def _wctv_unk2(offset):
        jump(offset, label=' -- WCTV_Unknown2 Struct')
        
        bone_ptr = bu32()+32
        unk3_ptr = bu32()+32
        
        if bone_ptr>32: _wctv_bone(bone_ptr,rig='WCTV_joint_obj')
    
    @structPointers( -1, {0: '_wctv_unk2' } )
    def _wctv_unk1(offset): pass # just a placeholder

    #-----------------------------------------------------------------------------------------------
    '''
    @structpointers( 24, {
        0:'_pass',
        8:'_wctv_unk1' }, root=True)
    def _wctv_unk0(offset):
        global _GAME; _GAME='WCTV'
        jump(offset, label=' -- WCTV_Unknown0 Struct')

        string_offset = bu32()+32
        flags = bu32()
        for unk2_offset in array(bu32)(offset=bu32()+32): _wctv_unk2(unk2_offset+32)
    '''
    ################################################################################################
    ## main header:
    ################################################################################################
    block_size = bu32(  label=' -- DataBlock Size')
    pointer_tbl = bu32( label=' -- Pointer Table Offset')+32
    pointer_cnt = bu32( label=' -- Pointer Count')
    root_cnt = bu32(    label=' -- Root Structure Count')
    ref_cnt = bu32(     label=' -- Reference Structure Count')
    tmp1 = bu32(        label=' -- Unknown') #001B?
    unk1 = bu32(        label=' -- Pad?')
    unk2 = bu32(        label=' -- Pad?')
    
    ################################################################################################
    ## path finder: ( designed by Tcll )
    ################################################################################################
    
    # Tcll - What does this do?
    # Well to put it into perspective (if it looks like a duck and quacks like a duck, then it must be a duck),
    # all we're given is a list of pointer addresses (relocations), and a root pointer. (aside from a useless string address)
    # We don't know what this mysterious root pointer points to, so we have to guess,
    # but first we need to collect some information to give us an accurate guess...
    # So we resolve the pointer addresses into a list of struct addresses (or pointers to structs),
    # and add any root pointers to that list. (saving the pointer addresses for testing if an expected pointer exists)
    # Now we can make a good guess as to the size of our root struct, as well as the sizes of it's children.
    
    # For some added information, what we've done with the decorator-class above (structPointers),
    # is build a collection of pre-defined structs with their sizes, (relative) pointer locations, and associate functions.
    
    # Now what we do with our given and expected information is put them together to determine our result.
    # First we start with the root size and gather structures matching or less than the given size.
    # Once we have a struct, if the size is smaller than the given size, we test that the extended data is pad-bytes (0s).
    # If valid, we now test that the expected pointer locations are valid (also searching for invalid pointers).
    # ^(this is why we saved our pointer addresses mentioned above)
    # Finally, if those are valid, we test that the structs at those pointers are valid,
    # following the same recursive routine until we hit a 'pass'.
    # (which marks either data, something unknown, or a struct with an undetermined size)
    
    # NOTE: ignorant tests with struct sizes of -1 are in place for unknown data and 'pass'.
    
    # NOTE: testing arrays of structures is done by modulo-ing (%) the given struct size by the associated expected size,
    # and using the remainder to test for pad-bytes. (yes modulo is the remainder of divide (/))
    # If that's valid, test the first structure of the array.
    
    # If all tests are positive, we can call our associated root-struct function.
    
    # NOTE: (is it really a duck?) just because all tests are positive doesn't mean we have a valid structure-path.
    # Note that the testing done is only based on what's known, so certain things can easily look like,
    # and be mistaken for other things without enough collected information (like the current matanim struct for example).
    # Unfortunately there's not much of a discrete way to validate the data in structs without doing something overly complex,
    # meaning testing would take hours due to the verbosity of the testing depth.
    # So it's left up to an exception to catch the invalid data and attempt to try another root struct.
    # This can be a double-edged sword though as the path may be correct,
    # while the invalid data is just something left to be figured out, causing the pathfinder to choke.
    # (at this point, any invalid data added to UGE's backend is not removed, the data is simply dealt with until finished)
    
    relocation_array = array(bu32,count=pointer_cnt); relocation_array.__color__ = 0x40FF40
    relocations = relocation_array(offset=pointer_tbl,label={' -- relocations':' -- pointer-address'})
    pointers = {pointer_tbl} # using a set to efficiently remove duplicate entries
    for addr in relocations:
        jump(addr+32)
        p = bu32( label=' -- Pointer' ); p.__color__ = 0xBBFFBB
        pointers.add(p+32)
    for i in range(root_cnt):
        jump(pointer_tbl+(pointer_cnt*4)+(i*8))
        p = bu32( label=' -- Root Pointer' ); p.__color__ = 0xFFDDBB
        pointers.add(p+32)
        
    def test_path(struct_name, given_size, struct_offset):
        """walker to validate the path recursively"""
        expected_size, func, ptrs, isArray = structs[struct_name]
        if expected_size == -1: return True # allow ignorance
        if given_size != expected_size:
            if given_size > expected_size:
                padSize = given_size%expected_size if isArray else given_size-expected_size
                if sum(array(bu8,count=padSize,offset=struct_offset+(given_size-padSize))( label=' -- pad-byte validity')):
                    print('      invalid path: given size %i > expected size %i for struct %s'%(given_size,expected_size,struct_name)); return False
            # this error shouldn't occur, but just in case, it's better to catch it anyway...
            else: print('      invalid path: given size %i < expected size %i for struct %s'%(given_size,expected_size,struct_name)); return False
        
        pid = 0
        jump(struct_offset, label=' -- validating struct %s'%struct_name)
        for i in range(expected_size): # !important: test each byte of the structure
            if i in ptrs:
                name = ptrs[i]
                pointer=struct_offset+i
                jump(pointer)
                location = bu32(label=' -- pointer %i of struct %s'%(pid,struct_name))+32
                pid += 1
                if pointer-32 not in relocations:
                    if location==32: continue # 0-pointer
                    else: print('      invalid path: 0-pointer expected, but found data at location %i for struct %s.'%(i,struct_name)); return False
                if location in pointers: size = min([address for address in pointers if address>location])-location
                else: print("      invalid path: couldn't determine size of sub-struct %s at location %i for struct %s."%(name,i,struct_name)); return False
                if not test_path(name, size, location): return False
            elif (struct_offset+i)-32 in relocations: print('      invalid path: pointer found in expected data-space at location %i for struct %s.'%(i,struct_name)); return False
        
        return True
    
    # TODO: test 2nd-priority root structures of non-fixed size, such as raw image data.
    # TODO: struct priority (2 structs have the same size, which do we use first?)
    # TODO: gather all root structs, and determine the order from what's given. (matanim should be parsed before joint, but yet is supplied afterwards.)
    # wisdom from Tcll: you can't trust anything for what it is in this format.
    for i in range(root_cnt):
        jump(pointer_tbl+(pointer_cnt*4)+(i*8), label=' -- Root Structs') # get to the root node
        
        root_offset = bu32(label=' -- Data Offset')+32
        string_offset = bu32(label=' -- string Offset') # could be a dictionary key: { str(key): value }
        root_size = min([address for address in pointers if address>root_offset])-root_offset # a root pointer should never be the last pointer.
        # ^ note: this is the given size, which could be larger than the expected size.

        # resolve the given root size into a dictionary of possible root structures (by size)
        roots = {root_size:[]} # { 48; ['root5', ... ], 44: ['root8', ... ] } (valid sizes determined from if sum(padding)==0)
        # ^ initial root size included to prevent pad-scanning issues.
        for structname, (structsize, structfunc, structptrs, isArray) in structs.items():
            if structfunc!=_pass: # root structures always have their own function
                if 0<structsize<=root_size:
                    for _structsize in roots:
                        if structsize==_structsize: roots[structsize].append(structname)
                    else:
                        jump(root_offset+structsize, label=' -- validating root struct oversize')
                        pad_bytes = array(bu8, count=root_size-structsize)( label=' -- initial pad-byte validity' )
                        if sum(pad_bytes)==0: roots[structsize] = [structname]
        found = False
        rl = len(roots)
        print('\nfound %i possible size categor%s for root %i of size %i:'%(rl, 'y' if rl == 1 else 'ies', i, root_size))
        for _size, root_names in roots.items():
            rs = len(root_names)
            if root_names:
                print('  scanning %i possible root struct%s of size %i.'%(rs, '' if rs == 1 else 's', _size))
                for ni,root_name in enumerate(root_names,1):
                    print('    %i: %s'%(ni, root_name))
                    if test_path(root_name, _size, root_offset):
                        print('      found a valid path, attempting to parse...')
                        # noinspection PyBroadException
                        try: structs[root_name][1](root_offset); print('      parsing succeeded'); found=True; break
                        except:
                            import sys,traceback # TODO: remove
                            print('      parsing failed, reason:\n'); traceback.print_exception( *sys.exc_info() ); print()
                if found: break
                else: print('    could not find a valid path.')
        if not found: print("could not find anything out of what's currently known.")
        
        # Tcll - possible test: if index has something to do with selection

1+None