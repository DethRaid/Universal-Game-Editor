
#ugeScriptName('MMD_PMX')
ugeScriptType(UGE_MODEL_SCRIPT)
ugeScriptFormats( {'MMD PMX': ['pmx']} )

def ugeImportModel( FT, UI ): # NOTE: little-endian byte-order
    vec4 = struct( X=f32, Y=f32, Z=f32, W=f32 )
    vec3 = struct( X=f32, Y=f32, Z=f32 )
    vec2 = struct( X=f32, Y=f32 )
    
    signature = string(4)()
    version = f32()
    flags = array(u8,count=u8)() # these can almost be called "attributes"
    # flags: [ encoding, extended_UV, ... ] index byte-sizes: [ ..., vert, tex, mat, bone, morph, rBody ]
    
    # define index structs (hacks done with script's namespace)
    NULL = lambda v,big=False,*a,**kw: None # Tcll - this augment seems to be used alot, so it may likely get built-in. :)
    _iNames = ['vertIdx', 'texIdx', 'matIdx', 'boneIdx', 'morphIdx', 'rBodyIdx']
    for _n in _iNames: globals()[_n] = NULL
    for _i,_s in enumerate(flags[2:]): globals()[_iNames[_i]] = u(_s)
    pmxstr = string(u32, code=[None,'UTF8'][flags[0]])
    
    BDef2 = struct( b1=boneIdx, b2=boneIdx, f0=f32 )
    BDef4 = struct( b1=boneIdx, b2=boneIdx, b3=boneIdx, b4=boneIdx,
                    f0=f32, f1=f32, f2=f32, f3=f32, )
    SDef = struct( b1=boneIdx, b2=boneIdx, f0=f32, v0=vec3, v1=vec3, v2=vec3 )
    facepoint = struct(
        vertex = vec3,
        normal = vec3,
        uv = vec2,
        deform = switch( u8, [ boneIdx, BDef2, BDef4, SDef ] ),
        edge = f32 )
    
    material = struct(
        name = pmxstr,
        english_name = pmxstr,
        diffuse = vec4, # Tcll - what, you've never heard of RGBA diffuse colors, or of colors being vectors?
        specular = vec4, # NOTE: W is the factor, not the alpha
        ambient = vec3,
        flag = u8,
        edge = vec4, # NOTE: W is edge size, not alpha
        texture_index = texIdx,
        sphere_tex_index = texIdx,
        sphere_mode = u8,
        toon_index = switch( u8, [ texIdx, u8 ] ),
        coment = pmxstr,
        facepoint_count = u32 ) # Tcll - heh, another format like the BGE backend 9_9
    
    header = struct(
        name = pmxstr,
        english_name = pmxstr,
        comment = pmxstr,
        english_comment = pmxstr,
        
        facepoints = array(facepoint,count=u32),
        indices = array(vertIdx,count=u32),
        textures = array(pmxstr,count=u32),
        materials = array(material,count=u32),
        bone_count = u32,
        morph_count = u32,
        display_count = u32,
        rBody_count = u32,
        joint_count = u32,
    ); header() # just so we get <struct 'header'> instead of <struct>

    

def ugeExportModel( FileType, UICommands):
    ##your code here
    return
        