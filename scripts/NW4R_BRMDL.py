# -*- coding: utf-8 -*-
ugeScriptType(UGE_MODEL_SCRIPT)
ugeScriptFormats({'Havok':['mdl0']})

''' UGE model import/export script written by Tcll5850 '''

def ugeImportModel(FT,Cmd):
    # NOTE: far from complete and still very buggy
    # NOTE: complex structural automation used (for debugging) with lacking backend support

    # Tcll - making up for lacking automation support:
    
    class index(object):
        __slots__ = [ 'List', 'Type', '__dereferenced__' ]
        def __init__(this, List, Type): this.List,this.Type = List,Type; __dereferenced__=True
        def __call__(this,Value=None,label='',*args,**kwargs):
            if Value is None: return this.List[this.Type()]
    
    # NOTE: this deprecates the `relation` arguments in string and array.
    class relate(object):
        __slots__ = [ 'offset','relation' ]
        def __init__(this,offset,relation=0): this.offset,this.relation = offset,relation
        def __call__(this,value=None,label='',*args,**kwargs):
            offset, relation = this.offset,this.relation
            if callable(offset): offset=offset()
            if callable(relation): relation=relation()
            return offset+relation
        
    class store(object):
        __slots__ = [ 'Struct','Value', '__dereferenced__' ]
        def __init__(this,Struct): this.Struct = Struct; __dereferenced__=True
        def __call__(this,value=None,label='',*args,**kwargs): this.Value = this.Struct(value,label=label); return this.Value
        retrieve = lambda this,value=None,label='',*args,**kwargs: this.Value
            
    class ResourceMapper(object):
        def __init__(this): this.map = lambda v: v
        __call__ = lambda this,v: this.map(v)
    ResourceMap = ResourceMapper()
        
    # data structs:
    sto32 = store(bu32)
    rel32 = relate(bu32,0)
    str8 = string(bu8,offset=relate(rel32,-1))
    vec3 = struct(12,X=bf32,Y=bf32,Z=bf32)
    vec4 = struct(16,X=bf32,Y=bf32,Z=bf32,W=bf32)
    matrix34 = array(vec4,count=3)
    bounds2 = struct(x=bf32,y=bf32,X=bf32,Y=bf32)
    bounds3 = struct(x=bf32,y=bf32,z=bf32,X=bf32,Y=bf32,Z=bf32)
    
    ResourceNode = struct(16, ID=bu16, Pad=bu16, Prev=bu16, Next=bu16, String=bu32, Data=bu32 )
    ResourceNodes = array(ResourceNode,count=lambda: bu32()+1, map=ResourceMap)
    ResourceGroup = struct( size = bu32, Nodes = ResourceNodes )
    
    #global header:
    magic = string(4)(label=' -- MDL0_Magic')
    DataLen = bu32(   label=' -- Data_Length')
    version = bu32(   label=' -- Version')
    brres_rel = bs32( label=' -- Brres_Relation')

    ResourceGroups = struct(
        Definitions= bu32 if version>7 else None,
        Bones      = bu32 if version>7 else None,
        Vertices   = bu32 if version>7 else None,
        Normals    = bu32 if version>7 else None,
        Colors     = bu32 if version>7 else None,
        UVs        = bu32 if version>7 else None,
        FurVectors = bu32 if version>9 else None,
        FurLayers  = bu32 if version>9 else None,
        Materials  = bu32 if version>7 else None,
        TEVs       = bu32 if version>7 else None,
        Objects    = bu32 if version>7 else None,
        Textures   = bu32 if version>7 else None,
        Palettes   = bu32 if version>7 else None,
        Unk3       = bu32 if version>10 else None )(
        labels = {' -- Resource Groups':['','','','','','','','','',' -- Pseudo-Shaders','','','','']}
    )
    
    #local header:
    header = struct(
        Name =          str8,
        header_len =    bu32,
        MDL0_offset =   bs32,
        unk1 =          bu32,
        unk2 =          bu32,
        num_verticies = bu32,
        num_faces =     bu32,
        unk3 =          bu32,
        Def_Count =     bu32,
        unk_flags =     bu32,
        unk5 =          bu16,
        Data_Offset =   bu16,
        boundbox = bounds3 )()

    _Links = array( bu32, count=bu32 )(label=' -- Definition Links')
    
    global _Bones
    _Definitions={'NodeTree':[],'NodeMix':{},'DrawOpa':{},'DrawXlu':{} }
    _Bones=[]
    _Vertices={}
    _Normals={}
    _Colors={}
    _UVs={}
    _materials={} #{OID:Mat_Name}
    _textures=[]
    
    if ResourceGroups.Unk3:
        label('''\n\nThis MDL0 uses an unknown resource.
              please contact Tcll at tcll5850@gmail.com and be sure to
              send me the MDL0 so I may add support for this data.\n'''.lstrip())
    
    # Tcll - I know these blocks are complex...
    # once I can improve automation support, I can work on simplifying the complexity here into something understandable.
    # not to mention, Python's magic support only goes so far before things get silly...
    
    if ResourceGroups.Definitions:
        Def_BoneMap = struct(4, BoneID=bu16, ParentID=bu16 )
        WeightStruct = struct(6, BoneID=index( _Links, bu16 ), weight=bf32 )
        WeightArr = array( WeightStruct, count=bu8 )
        Def_Influence = struct( Link=bu16, Weights=WeightArr )
        Def_MatMap = struct(7, MatID=bu16, ObjectID=bu16, BoneID=bu16, ZPriority=bu8)
        Def_SInfluence = struct(4, Link=bu16, BoneID=bu16 )
        def DMap(Type):
            global name; switch(Type)
            if case(2): _Definitions[name].append( Def_BoneMap() )
            if case(3): I = Def_Influence(); _Definitions[name][I.Link] = I.Weights
            if case(4): M = Def_MatMap(); _Definitions[name][M.ObjectID] = M.MatID
            if case(5): I = Def_SInfluence(); _Definitions[name][I.Link] = [[I.BoneID,1.0]]
        DArray = array(bu8,stop=1,map=DMap)
        def DefMap(RN):
            if RN.ID == 0xFFFF: return
            DMap.__globals__['name'] = name = str8(offset=ResourceGroups.Definitions+RN.String-1)
            DArray(offset=ResourceGroups.Definitions+RN.Data, label=' -- %s'%name)
        ResourceMap.map = DefMap; rel32.relation = ResourceGroups.Definitions; ResourceGroup(offset=rel32.relation,label=' -- Definitions')
        
    if ResourceGroups.Bones:
        ugeSetObject(header.Name+'_Rig') # create the rig object and link the bones to it
        Bone = struct( -1, size=bu32, MDL0_header=bs32, name=str8, ID=bu32, Link=bu32, flags=bu32, skip=bu64,
            Sca=vec3, Rot=vec3, Loc=vec3, Bounds=bounds3, parent=bs32, child=bs32, next=bs32, prev=bs32, part2=bs32,
            WBind=matrix34, IBind=matrix34 )
        BO2D = {}
        def BoneMap(RN):
            if RN.ID == 0xFFFF: return
            global _Bones; BO = rel32.relation = ResourceGroups.Bones+RN.Data
            bn = Bone(offset=BO, label=' -- %s'%str8(offset=ResourceGroups.Bones+RN.String-1))
            # noinspection PyUnusedLocal
            _UNUSED, _F15, _F14, _F13, _F12, _F11, _F10, _HasGeometry, _F8, _F7, _HasChildren, _F5, _F4, _FixedScale, \
            _FixedRotation, _FixedTranslation, _NoTransform = field( ['16',1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], bn.flags )
            BO2D[BO] = [ ugeSetBone(bn.name), BO+bn.parent, BO+bn.prev, bn.WBind+[[0,0,0,1]], bn.IBind+[[0,0,0,1]] ]
            _Bones+=[bn.name]
        ResourceMap.map = BoneMap; rel32.relation = ResourceGroups.Bones; ResourceGroup(offset=rel32.relation,label=' -- Bones')
    
        for BO,(I, Pa, Pr, WB, IB) in BO2D.items():
            ugeSetBone(I)
            if Pa!=BO: ugeSetBoneParent(BO2D[Pa][0])
            if Pr!=BO: ugeSetBonePrev(BO2D[Pr][0])
            # calculate and decompose a local bind matrix (can't rely on the supplied LRS)
            L,R,S = ugeMtxDecompose( ugeMtxMultiply( BO2D[Pa][4], WB ) if Pa!=None else WB )
            ugeSetBoneLoc(L); ugeSetBoneRot(R); ugeSetBoneSca(S)

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
    DTCEnum= [ _RGB565, _RGB8, _RGBX8, _RGBA4, _RGBA6, _RGBA8 ]
    DTEnum = [bu8,bs8,bu16,bs16,bf32]
    def VectorArray(hdr,ArrayDict,colors=False,dimBase=2):
        if colors: vector = DTCEnum[hdr.CmpType]
        else: DT = DTEnum[hdr.CmpType]; dim = dimBase+hdr.CmpCnt;\
            vector = struct( hdr.stride, X = DT, Y = DT if dim>1 else None, Z = DT if dim>2 else None )
        ArrayDict[hdr.ID] = array( vector,count=hdr.count, offset=rel32.relation+hdr.data,
            map= None if colors else ((2.**hdr.exp).__rdiv__ if hdr.CmpType<4 else None) )(label=' -- Vectors')
    
    VectorHeader = struct( -1, size = bu32, MDL0_header = bs32, data = bu32,
        name = str8, ID = bu32, CmpCnt = bu32, CmpType = bu32, exp = bu8, stride = bu8, count = bu16 )
    _VHLabels = [' -- Data Size',' -- MDL0-Header Offset',' -- Data Offset',' -- Array Name',' -- Array ID',
        ' -- GX Component Count',' -- GX Component Type',' -- Exponent',' -- Array Stride',' -- Vector Count']
    
    # IDK why Havok devs lost a few brain cells here...
    ColorVectorHeader = struct( -1, size = bu32, MDL0_header = bs32, data = bu32,
        name = str8, ID = bu32, CmpCnt = bu32, CmpType = bu32, stride = bu8, scale = bu8, count = bu16 )
    _CVHLabels = [' -- Data Size',' -- MDL0-Header Offset',' -- Data Offset',' -- Array Name',' -- Array ID',
        ' -- GX Component Count',' -- GX Component Type',' -- Array Stride',' -- Scale',' -- Vector Count']
    
    if ResourceGroups.Vertices:
        def VertMap(RN):
            if RN.ID == 0xFFFF: return
            rel32.relation = ResourceGroups.Vertices+RN.Data; VectorArray( VectorHeader( offset=rel32.relation,
                label={ ' -- %s' % str8( offset=ResourceGroups.Vertices + RN.String - 1 ): _VHLabels } ), _Vertices )
        ResourceMap.map = VertMap; rel32.relation = ResourceGroups.Vertices; ResourceGroup(offset=rel32.relation,label=' -- Vertices')
    if ResourceGroups.Normals:
        def NormalMap(RN):
            if RN.ID == 0xFFFF: return
            rel32.relation = ResourceGroups.Normals+RN.Data; VectorArray( VectorHeader(offset=rel32.relation,
                label={' -- %s'%str8(offset=ResourceGroups.Normals+RN.String-1):_VHLabels}), _Normals, dimBase=3 )
        ResourceMap.map = NormalMap; rel32.relation = ResourceGroups.Normals; ResourceGroup(offset=rel32.relation,label=' -- Normals')
    if ResourceGroups.UVs:
        def UVMap(RN):
            if RN.ID == 0xFFFF: return
            rel32.relation = ResourceGroups.UVs+RN.Data; VectorArray( VectorHeader(offset=rel32.relation,
                label={' -- %s'%str8(offset=ResourceGroups.UVs+RN.String-1):_VHLabels}), _UVs, dimBase=1 )
        ResourceMap.map = UVMap; rel32.relation = ResourceGroups.UVs; ResourceGroup(offset=rel32.relation,label=' -- UVs')
    if ResourceGroups.Colors:
        def ColorMap(RN):
            if RN.ID == 0xFFFF: return
            rel32.relation = ResourceGroups.Colors+RN.Data; VectorArray( ColorVectorHeader(offset=rel32.relation,
                label={' -- %s'%str8(offset=ResourceGroups.Colors+RN.String-1):_CVHLabels}), _Colors, colors=True )
        ResourceMap.map = ColorMap; rel32.relation = ResourceGroups.Colors; ResourceGroup(offset=rel32.relation,label=' -- Colors')
    
    if ResourceGroups.Materials:
        Texture = struct( name=string(bu8,offset=relate(relate(ugeGetFileOffset,bu32),-1)), # Tcll - teh haxing (basic functions should work in the official version)
            padding = bu32, unk1 = bu32, unk2 = bu32, index1 = bu32, index2 = bu32,
            WrapS = bu32, WrapT = bu32, Min_Filter = bu32, Mag_Filter = bu32,
            LOD_Bias = bf32, Max_Antisotropy = bu32, Clamp_Bias = bu8, Interpolation = bu8, unk3 = bu16 )
        def TexMap(tx):
            Texture_Name = tx.name; ugeSetTexture(Texture_Name)
            if Texture_Name not in _textures: ugeSetImage(Texture_Name); ugeSetImageData(Texture_Name); _textures.append(Texture_Name)
            return tx
        TexArr = array( Texture, count=sto32.retrieve, offset=rel32, map=TexMap )
        Material = struct(-1, size = bu32, MDL0_header = bs32, name = str8, ID = bu32, XLU = bu32,
            TexGens = bu8, Light_Channels = bu8, Active_Stages = bu8, Indirect_Textures = bu8, Cull_Mode = bu32,
            Alpha_Testing = bu8, Light_Set = bu8, Fog_Set = bu8, unk = bu8, unk2 = bu32, unk3 = bu32, TEV_Offset = bu32,
            Texture_Layer_Count = sto32, Texture_Layers = TexArr, P2 = bu32, Settings = bu32, P3 = bu32 )
        def MatMap(RN):
            if RN.ID == 0xFFFF: return
            rel32.relation = ResourceGroups.Materials+RN.Data
            ma = Material(offset=rel32.relation, label=' -- %s'%str8(offset=ResourceGroups.Materials+RN.String-1))
            ugeSetMaterial(ma.name,False); _materials[ma.ID] = ma.name
        ResourceMap.map = MatMap; rel32.relation = ResourceGroups.Materials; ResourceGroup(offset=rel32.relation,label=' -- Materials')
        '''
        for RN in RList(Materials):
            string_relation_hack.offset = relation_hack.offset = Materials+RN.Data; string_relation_hack.offset-=1 # important
            ma = Material()
            
            jump(Materials+D,label=' -- Material')
            
            Block_Size=bu32(        label=' -- Data_Size')
            MDL0_header=bs32(       label=' -- MDL0_Header_Offset')
            Material_Name=str8(offset=Materials+D+bu32(label=' -- String_Offset')-1)
            ID=bu32(                label=' -- Material_ID')
            
            XLU=bu32(               label=' -- is_XLU')
            
            TexGens = bu8(          label=' -- TexGens')
            Light_Channels = bu8(   label=' -- Light_Channels')
            AStages = bu8(          label=' -- Activ_TEV_Stages')
            Indirect_Textures = bu8(label=' -- Indirect_Textures')
            
            Cull=bu32(              label=' -- Cull_Mode')
            
            Alpha_Testing = bu8(    label=' -- Alpha_Testing')
            Light_Set = bu8(        label=' -- Light_Set')
            Fog_Set = bu8(          label=' -- Fog_Set')
            M_unk2 = bu8(           label=' -- Unknown')
            
            M_unk3 = bu32(          label=' -- Unknown')
            M_unk4 = bu32(          label=' -- Unknown')
            
            TEV=bu32(               label=' -- TEV_Offset')
            texture_count=bu32(     label=' -- Texture_Layer_Count')
            Layers=bu32(            label=' -- Texture_Layers_Offset')
            P2=bu32(                label=' -- Part_2_Offset')
            Setup=bu32(             label=' -- Material_Settings_Offset')
            P3=bu32(                label=' -- Part_3_Offset')
            
            ugeSetMaterial(Material_Name)
            _materials[ID] = Material_Name
            #try:
            #    OID = _Definitions['DrawXlu' if XLU else 'DrawOpa'][ID]
            #    _materials[OID] = Material_Name
            #except: pass #not all materials are used
            
            L = Materials+D+Layers
            jump(L,label=' -- Texture Layers')
            
            for i in range(texture_count):
                Texture_Name=str8(offset=L+(52*i)+bu32(label=' -- String_Offset')-1)
                padding = bu32(         label=' -- pad')
                unk1 = bu32(            label=' -- Unknown')
                unk2 = bu32(            label=' -- Unknown')
                id1 = bu32(             label=' -- index1')
                id2 = bu32(             label=' -- index2')
                UWrap_Mode = bu32(      label=' -- UWrap_Mode')
                VWrap_Mode = bu32(      label=' -- VWrap_Mode')
                Min_Filter = bu32(      label=' -- Min_Filter')
                Mag_Filter = bu32(      label=' -- Mag_Filter')
                LOD_Bias = bf32(        label=' -- LOD_Bias')
                Max_Antisotropy = bu32( label=' -- Max_Antisotropy')
                Clamp_Bias = bu8(       label=' -- Clamp_Bias')
                Interpolation = bu8(    label=' -- Interpolation')
                unk3 = bu16(            label=' -- Unknown')
                
                ugeSetTexture(Texture_Name)
                if Texture_Name not in _textures:
                    ugeSetImage(Texture_Name)
                    ugeSetImageData(Texture_Name)
                    _textures+=[Texture_Name]
        '''
    def CPT(T): #face-point index/value formats
        if T == 0: return '' #null
        if T == 1: return None #direct data (handled by code)
        if T == 2: return bu8() #8bit index
        if T == 3: return bu16() #16bit index
    
    if ResourceGroups.Objects:
        XF_VtxMtxCache=[[0, 0.0]]*16
        #XF_NrmMtxCache=[[0, 0.0]]*16
        
        XFLength = store(bu16)
        XF_Register = struct( Length=XFLength, Command=bu16, Structures=array(bu32, count=relate(XFLength.retrieve,1)), padding=bu8 ) # Tcll - more abuse :P
        CP_Register = struct(5, Command=bh8, Value=bu32)
        def RegMap(command):
            switch(command)
            if case('08'): Reg = CP_Register()
            if case('10'): Reg = XF_Register()
            return Reg
        
        global FacePoint
        AttrSize = store(bu32)
        Registers = array( bh8, stop='00', map=RegMap )
        def getAttributes(value=None,label='',*args,**kwargs):
            global FacePoint
            Attributes=struct( AttrSize.retrieve(), relate(rel32,24), padding=bu(10), Registers=Registers)
            Attrs = Attributes()
            
            CP_Types = [0]*26
            for Reg in Attrs.Registers:
                switch(Reg.__class__)
                if case(CP_Register):
                    switch(Reg.Command)
                    if case('50'): CP_Types[:13] = data = field( [1,1,1,1,1,1,1,1,1,3,3,3,3], Reg.Value )
                    if case('60'): CP_Types[13:] = data = field( [3,3,3,3,3,3,3,3,3,3,3,3,3], Reg.Value )
                if case(XF_Register): pass

            CPT1 = [None,bu8].__getitem__
            CPT3 = [None,None,bu8,bu16].__getitem__
            FacePoint = struct(
                infl    = CPT1(CP_Types[0]),
                txmtx0  = CPT1(CP_Types[1]),
                txmtx1  = CPT1(CP_Types[2]),
                txmtx2  = CPT1(CP_Types[3]),
                txmtx3  = CPT1(CP_Types[4]),
                txmtx4  = CPT1(CP_Types[5]),
                txmtx5  = CPT1(CP_Types[6]),
                txmtx6  = CPT1(CP_Types[7]),
                txmtx7  = CPT1(CP_Types[8]),
                vert    = CPT3(CP_Types[9]),
                norm    = CPT3(CP_Types[10]),
                col0    = CPT3(CP_Types[11]),
                col1    = CPT3(CP_Types[12]),
                uv0     = CPT3(CP_Types[13]),
                uv1     = CPT3(CP_Types[14]),
                uv2     = CPT3(CP_Types[15]),
                uv3     = CPT3(CP_Types[16]),
                uv4     = CPT3(CP_Types[17]),
                uv5     = CPT3(CP_Types[18]),
                uv6     = CPT3(CP_Types[19]),
                uv7     = CPT3(CP_Types[20]),
                vmtxarr = CPT3(CP_Types[21]),
                nmtxarr = CPT3(CP_Types[22]),
                txmtxarr= CPT3(CP_Types[23]),
                lmtxarr = CPT3(CP_Types[24]),
                nbt     = CPT3(CP_Types[25]),
            ); FacePoint.__color__ = 0xA0A0A0
            return Attrs
        '''
        
                if   case('20'): #vert matrix
                    label(' -- Primitive Type ( XF_Vert_Matrix )')
                    link_index = bu16(); Adr,Len = field( ['12','4'], bu16() ) # <-- Tcll: thanks BJ :)
                    # XF_VtxMtxCache[ Adr/12 ] = [ [BoneID, Weight], ... ] (use the BoneID to get the bone's name when setting weights)
                    ##XF_VtxMtxCache[ Adr/12 ] = _Definitions['NodeMix'][ link_index ] if link_index in _Definitions['NodeMix'] else [ [ _Links[ link_index ], 1.0 ] ]
                    _Link = _Links[ Defs[ link_index ] ]
                    XF_VtxMtxCache[ Adr/12 ] = _Definitions['NodeMix'][ Defs[ link_index ] ] if _Link==0xFFFFFFFF else [ [ _Link, 1.0 ] ]
                    
                    #Pachirisu(v11).mdl0
                    #0x0000003A42: read 0x20 as '20' -- Primitive Type ( XF_Vert_Matrix )
                    #0x0000003A43: read 0x0002 as 2
                    #0x0000003A45: read 0xB024 as 45092
                    #KeyError: 2
                    # tcll - ^ fixed with best guess and testing: _Links[ 2 ]
                    # this is likely not right, but it works.
                    # I did ask BlackJax96 multiple times for help on this, but never got anywhere on this particular issue...
                    # (BJ helped me fix the link_index above as I was reading the data backwards, but the KeyError was ignored)
                
                elif case('28'): #normal matrix (3x3)
                    label(' -- Primitive Type ( XF_Normal_Matrix )')
                    bu32(label=" -- TODO")
                    #Adr,Len,Val = field( ['12','4','16'], bu32() )
                    ##XF_NrmMtxCache[XFAddr/12]=_Definitions['NodeMix'][Link] #[ [BoneID, Weight], [] ]
                    #if( ( readNum( f, 2, 2, true ) - 0xb000 ) / 0x0c > 7 )
                
                elif case('30'): #UV matrix
                    label(' -- Primitive Type ( XF_UV_Matrix )')
                    bu32(label=" -- TODO")
                    #Adr,Len,Val = field( ['12','4','16'], bu32() )
                elif case('38'): #light matrix
                    label(' -- Primitive Type ( XF_Light_Matrix )')
                    bu32(label=" -- TODO")
                    #Adr,Len,Val = field( ['12','4','16'], bu32() )
        '''
        globals()['USED'] = False
        def PrimMap(command):
            switch(command)
            if case('20'):
                link_index = bu16(); Adr,Len = field( ['12','4'], bu16() ) # <-- Tcll: thanks BJ :)
                #_Link = _Links[ Defs[ link_index ] ]
                #XF_VtxMtxCache[ Adr/12 ] = _Definitions['NodeMix'][ Defs[ link_index ] ] if _Link==0xFFFFFFFF else [ [ _Link, 1.0 ] ]
                
                #Pachirisu(v11).mdl0
                #0x0000003A42: read 0x20 as '20' -- Primitive Type ( XF_Vert_Matrix )
                #0x0000003A43: read 0x0002 as 2
                #0x0000003A45: read 0xB024 as 45092
                #KeyError: 2
                # tcll - ^ fixed with best guess and testing: _Links[ 2 ]
                # this is likely not right, but it works.
                # I did ask BlackJax96 multiple times for help on this, but never got anywhere on this particular issue...
                # (BJ helped me fix the link_index above as I was reading the data backwards, but the KeyError was ignored)
                return
            if case('28'): bu32(label=" -- TODO"); return
            if case('30'): bu32(label=" -- TODO"); return
            if case('38'): bu32(label=" -- TODO"); return
            FacePoints = array(FacePoint, count=bu16)
            FacePoints()
            #bu16(label = ' -- count')
            #if not globals()['USED']: FacePoint(); globals()['USED'] = True
        
        Primitives = array( bh8, stop='00', offset=relate(rel32,36), map=PrimMap )
        Def_Arr = array(bu16,offset=rel32,count=bu32)
        Object=struct( size=bu32, MDL0_header=bs32, Link=bu32, CPL=bu32, CPH=bu32, INVTXSPEC=bu32,
            Attr_size=AttrSize, Attr_flags=bu32, Attributes=getAttributes, Buffer_Size=bu32, Data_Size=bu32,
            Primitives=Primitives, Elem_Flags=bu32, unk=bu32, name=str8, ID=bu32, vert_count=bu32, face_count=bu32,
            vert_input=bu16, normal_input=bu16, color_inputs=array(bu16,count=2), UV_inputs=array(bu16,count=8),
            fur_vectors_input=bu16 if version>9 else None, fur_layers_input=bu16 if version>9 else None, Def_Table=Def_Arr )

        def ObjMap(RN):
            if RN.ID == 0xFFFF: return
            rel32.relation = ResourceGroups.Objects+RN.Data
            obName = str8(offset=ResourceGroups.Objects+RN.String-1) # not the best method, but whatever...
            
            ugeSetObject(obName)
            if _Definitions['NodeTree']: ugeSetObjectParent(header.Name+'_Rig')
            
            ob = Object(offset=rel32.relation, label=' -- %s'%obName)
            
            try:
                try: MID = _Definitions['DrawXlu'][ob.ID]
                except: MID = _Definitions['DrawOpa'][ob.ID]
                ugeSetMaterial(_materials[MID])
            except: pass # object has no material
            
        ResourceMap.map = ObjMap; rel32.relation = ResourceGroups.Objects; ResourceGroup(offset=rel32.relation,label=' -- Objects')
        """
        for _I,_pad,_P,_N,S,D in RList(Objects):
            jump(Objects+D,label=' -- Object')
            
            Block_Size=bu32(    label=' -- Data_Size')
            MDL0_header=bs32(   label=' -- MDL0_Header_Offset')
            Link=bu32(          label=' -- Link_ID/Def_Table')
            if Link == 0xFFFFFFFF: Link=-1
            
            CPL=field( [1,1,1,1,1,1,1,1,1,3,3,3,3],bu32(label=' -- CP_Lo')
            )+field( [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3],bu32(label=' -- CP_Hi')) #TODO: use attribute definitions
            
            INVTXSPEC=bu32(     label=' -- XF_Specs')
            Attribute_size=bu32(    label=' -- Attribute_Size')
            
            Attribute_flags=bu32(   label=' -- Attribute_Flags') #0x00000080 or 0x000000A0
            #^I honestly don't think these have anything to do with the arrributes
            
            Attributes_offset=bu32( label=' -- Attributes_Offset')+34+Objects+D
            Buffer_Size=bu32(   label=' -- Data_Buffer_Size')
            Data_Size=bu32(     label=' -- Data_Size')
            Primitives_Offset=bu32(label=' -- Data_Offset')+36+Objects+D
            Elm_Flags=bu32(     label=' -- Element_Flags') # unused here (determines what's enabled)(CPL does this automatically) :P
            unk3=bu32(          label=' -- Unknown') #usually 0
            Object_Name=str8(offset=Objects+D+bu32(label=' -- String_Offset')-1)
            ID=bu32(            label=' -- Object_ID')
            num_verts=bu32(     label=' -- Vert_Count')
            num_faces=bu32(     label=' -- Face_Count')
            
            label('\n -- Vert_Input:');         vert_input=bu16()
            label('\n -- Normal_Input:');       normal_input=bu16()
            label('\n -- Color_Inputs:');       color_inputs=array(bu16,count=2)
            label('\n -- UV_Inputs:');          UV_inputs=array(bu16,count=8)
            if version>9:
                label('\n -- Fur_Vectors_Input:');  fur_vectors_input=bu16()
                label('\n -- Fur_Layers_Input:');   fur_layers_input=bu16()
            
            Def_Tbl=bu32(       label=' -- Definition_Table_Offset')+Objects+D
            if Link==-1: # TODO: use def table
                jump(Def_Tbl,   label=' -- Definition_Table')
                Defs=array(bu16,count=bu32(label=' -- Definition_Count'))()
            
            # TODO: really need to use the attribute structures, the CP and XF data above is really only for show
            # (the attribute structures define the same exact data and more, such as the UV attribute groups which give texture matrix binding information (I think))
            #jump(Attributes_offset) # when I can fully understand this :/
            
            # precalculation uses less iteration steps per facepoint (increases read perfomance)
            attributes = [(CPI,CPV) for CPI,CPV in enumerate(CPL) if CPV]
            
            ugeSetObject(Object_Name)
            ugeSetObjectParent(MDL0_Name+'_Rig' if bool(len(_Definitions['NodeTree'])) else None)
            
            jump(Primitives_Offset,label=' -- Primitives:')
            while True:
                switch(bh8()) #primitive ID
                t=None
                
                # XF vert/normal matrix data: 0x0002 B 024
                if   case('00'): break
                if   case('20'): #vert matrix
                    label(' -- Primitive Type ( XF_Vert_Matrix )')
                    link_index = bu16(); Adr,Len = field( ['12','4'], bu16() ) # <-- Tcll: thanks BJ :)
                    # XF_VtxMtxCache[ Adr/12 ] = [ [BoneID, Weight], ... ] (use the BoneID to get the bone's name when setting weights)
                    ##XF_VtxMtxCache[ Adr/12 ] = _Definitions['NodeMix'][ link_index ] if link_index in _Definitions['NodeMix'] else [ [ _Links[ link_index ], 1.0 ] ]
                    _Link = _Links[ Defs[ link_index ] ]
                    XF_VtxMtxCache[ Adr/12 ] = _Definitions['NodeMix'][ Defs[ link_index ] ] if _Link==0xFFFFFFFF else [ [ _Link, 1.0 ] ]
                    
                    #Pachirisu(v11).mdl0
                    #0x0000003A42: read 0x20 as '20' -- Primitive Type ( XF_Vert_Matrix )
                    #0x0000003A43: read 0x0002 as 2
                    #0x0000003A45: read 0xB024 as 45092
                    #KeyError: 2
                    # tcll - ^ fixed with best guess and testing: _Links[ 2 ]
                    # this is likely not right, but it works.
                    # I did ask BlackJax96 multiple times for help on this, but never got anywhere on this particular issue...
                    # (BJ helped me fix the link_index above as I was reading the data backwards, but the KeyError was ignored)
                
                elif case('28'): #normal matrix (3x3)
                    label(' -- Primitive Type ( XF_Normal_Matrix )')
                    bu32(label=" -- TODO")
                    #Adr,Len,Val = field( ['12','4','16'], bu32() )
                    ##XF_NrmMtxCache[XFAddr/12]=_Definitions['NodeMix'][Link] #[ [BoneID, Weight], [] ]
                    #if( ( readNum( f, 2, 2, true ) - 0xb000 ) / 0x0c > 7 )
                
                elif case('30'): #UV matrix
                    label(' -- Primitive Type ( XF_UV_Matrix )')
                    bu32(label=" -- TODO")
                    #Adr,Len,Val = field( ['12','4','16'], bu32() )
                elif case('38'): #light matrix
                    label(' -- Primitive Type ( XF_Light_Matrix )')
                    bu32(label=" -- TODO")
                    #Adr,Len,Val = field( ['12','4','16'], bu32() )
                
                elif case('78'): t,n = UGE_POLYGON,      'Polygon' #possible support based on pattern (hasn't actually been seen)
                elif case('80'): t,n = UGE_QUADS,        'Quads'
                elif case('88'): t,n = UGE_QUADSTRIP,    'QuadStrip' #possible support based on pattern (hasn't actually been seen)
                elif case('90'): t,n = UGE_TRIANGLES,    'Triangles'
                elif case('98'): t,n = UGE_TRIANGLESTRIP,'TriangleStrip'
                elif case('A0'): t,n = UGE_TRIANGLEFAN,  'TriangleFan'
                elif case('A8'): t,n = UGE_LINES,        'Lines'
                elif case('B0'): t,n = UGE_LINESTRIP,    'LineStrip'
                elif case('B8'): t,n = UGE_POINTS,       'Points'
                
                if t: # not a matrix
                    label(' -- Primitive Type ( '+n+' )')
                    ugeSetPrimitive(t)
                    
                    for v in range(bu16(label=' -- Facepoint_Count')):
                        ugeSetFacepoint()
                        
                        weights = [] if Link==-1 else [[_Links[Link], 1.0 ]]
                        
                        for CPI,CPV in attributes:
                            D=CPT(CPV)
                            
                            #not sure if anything other than matrix indecies can be direct data
                            #(there doesn't seem to be a defined relation to specific formatting values for direct data) >_>
                            # ^ it looks like verts and other vectors will always be indexed
                            switch(CPI)
                            if   case( 0): #vert/nor_mtx
                                if CPV==1: weights = XF_VtxMtxCache[bu8(label=' -- Vert/Normal_Mtx value')/3]
                            elif case( 1): #uv[0]_mtx (unknown processing)
                                if CPV==1: bu8(label=' -- UV[0]_Mtx value')/3
                            elif case( 2): #uv[1]_mtx
                                if CPV==1: bu8(label=' -- UV[1]_Mtx value')/3
                            elif case( 3): #uv[2]_mtx
                                if CPV==1: bu8(label=' -- UV[2]_Mtx value')/3
                            elif case( 4): #uv[3]_mtx
                                if CPV==1: bu8(label=' -- UV[3]_Mtx value')/3
                            elif case( 5): #uv[4]_mtx
                                if CPV==1: bu8(label=' -- UV[4]_Mtx value')/3
                            elif case( 6): #uv[5]_mtx
                                if CPV==1: bu8(label=' -- UV[5]_Mtx value')/3
                            elif case( 7): #uv[6]_mtx
                                if CPV==1: bu8(label=' -- UV[6]_Mtx value')/3
                            elif case( 8): #uv[7]_mtx
                                if CPV==1: bu8(label=' -- UV[7]_Mtx value')/3
                            
                            #I'm aware of 'dmt', 'CT', and 'ev' not being defined for direct data: ( where do I define them?? )
                            #I've only coded the basis for direct data support just in case it can be made avaliable.
                            elif case( 9): #vert
                                if CPV==1: ugeSetUTVert(Vector(1, dmt, CT, ev)[0]); label(' -- Vert value')
                                elif CPV>1: label(' -- Vert Index'); ugeSetVert(_Vertices[vert_input][D], flag = UGE_UNTRANSFORMED)
                            
                            elif case(10): #normal
                                if CPV==1: ugeSetUTNormal(Vector(1, dmt, CT, ev)[0]); label(' -- Normal value')
                                elif CPV>1: label(' -- Normal Index'); ugeSetNormal(_Normals[normal_input][D], flag = UGE_UNTRANSFORMED)
                            
                            elif case(11): #color[0]
                                if CPV==1: ugeSetColor(color(1,CT)[0], channel=0); label(' -- Color[0] value')
                                elif CPV>1: label(' -- Color[0] Index'); ugeSetColor(_Colors[color_inputs[0]][D], channel=0)
                            elif case(12): #color[1]
                                if CPV==1: ugeSetColor(color(1,CT)[0], channel=1); label(' -- Color[1] value')
                                elif CPV>1: label(' -- Color[1] Index'); ugeSetColor(_Colors[color_inputs[1]][D], channel=1)
                            
                            elif case(13): #uv[0]
                                if CPV==1: ugeSetUV( Vector(1, dmt, CT, ev)[0], channel=0); label(' -- UV[0] value')
                                elif CPV>1: label(' -- UV[0] Index');   ugeSetUV(_UVs[UV_inputs[0]][D], channel=0)
                                ''' I'm lazy:
                            elif case(14): #uv[1]
                                if CPV==1: U[1]=('' if I=='' else Vector(1, dmt, CT, ev)[0]); label(' -- UV[1] value')
                                elif CPV>1: label(' -- UV[1] Index');   U[1]=_UVs[UV_inputs[1]][D]
                            elif case(15): #uv[2]
                                if CPV==1: U[2]=('' if I=='' else Vector(1, dmt, CT, ev)[0]); label(' -- UV[2] value')
                                elif CPV>1: label(' -- UV[2] Index');   U[2]=_UVs[UV_inputs[2]][D]
                            elif case(16): #uv[3]
                                if CPV==1: U[3]=('' if I=='' else Vector(1, dmt, CT, ev)[0]); label(' -- UV[3] value')
                                elif CPV>1: label(' -- UV[3] Index');   U[3]=_UVs[UV_inputs[3]][D]
                            elif case(17): #uv[4]
                                if CPV==1: U[4]=('' if I=='' else Vector(1, dmt, CT, ev)[0]); label(' -- UV[4] value')
                                elif CPV>1: label(' -- UV[4] Index');   U[4]=_UVs[UV_inputs[4]][D]
                            elif case(18): #uv[5]
                                if CPV==1: U[5]=('' if I=='' else Vector(1, dmt, CT, ev)[0]); label(' -- UV[5] value')
                                elif CPV>1: label(' -- UV[5] Index');   U[5]=_UVs[UV_inputs[5]][D]
                            elif case(19): #uv[6]
                                if CPV==1: U[6]=('' if I=='' else Vector(1, dmt, CT, ev)[0]); label(' -- UV[6] value')
                                elif CPV>1: label(' -- UV[6] Index');   U[6]=_UVs[UV_inputs[6]][D]
                            elif case(20): #uv[7]
                                if CPV==1: U[7]=('' if I=='' else Vector(1, dmt, CT, ev)[0]); label(' -- UV[7] value')
                                elif CPV>1: label(' -- UV[7] Index');   U[7]=_UVs[UV_inputs[7]][D]
                                '''
                            
                            elif case(21): pass #vert_mtx_arr
                            elif case(22): pass #normal_mtx_arr
                            elif case(23): pass #uv_mtx_arr
                            elif case(24): pass #light_mtx_array
                            elif case(25): pass #NBT (NX,NY,NZ, BX,BY,BZ, TX,TY,TZ)
                            #elif case(255):pass #CP_NULL
                            
                            #debugging:
                            #if D!='': label(' - '+str(pos)+' > '+str(Buffer_Size)+' ?')
                            
                        for BID,W in weights: ugeSetWeight( _Bones[BID], W )
                        
            try:
                try: MID = _Definitions['DrawXlu'][ID]
                except: MID = _Definitions['DrawOpa'][ID]
                ugeSetMaterial(_materials[MID])
            except: pass # object has no material
        """

def XugeExportModel(FT,UIC): # WIP (not functional yet)
    # exporting will be supported once materials are fully supported in UGE
    # NOTE: UMC is UGE

    #to build resource groups:
    #    1: sort names alphabetically
    #    2: insert empty string
    #    3: add names to the table

    #group names by length
    #compair names in binary tree fashon
    #chars are in R>L order, bits in L>R

    def CompareBits(b1, b2=0):
            i=8
            while i>0:
                i-=1
                if (b1 & 1<<(i-1)) != (b2 & 1<<(i-1)): return i-1 #(not sure)
            return 0

    #def GenerateID(name="") #Generate the MDL0 Group ID
    #    return -1 if name=="" else ((len(name) - 1) << 3) | CompareBits(ord(name[len(name)-1]))

    _name, _id, _index, _left, _right = "",0,0,[],[]

    def IsRight(Cname):
        global _name, _id
        return False if len(_name) != len(Cname) else ((ord(Cname[(_id >> 3)]) >> (_id & 7)) & 1) != 0

    def GenerateId(Cname, Cid, Cindex, Cleft, Cright):
        global _name, _id, _left, _right

        for i in range(len(_name)):

            if (_name[i] != Cname[i]):
                _id = (i << 3) | CompareBits(ord(_name[i]), ord(Cname[i]))

                if IsRight(comparison): _left,_right = this,comparison
                else: _left,_right = comparison,this

                return _id

        return 0
