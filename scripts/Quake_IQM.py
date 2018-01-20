# -*- coding: utf-8 -*-

ugeScriptType(UGE_MODEL_SCRIPT); ugeScriptFormats({ 'InterQuake Model format': ['iqm'] })
# built by Tcll5850.

def ugePollModel(): return string()() == 'INTERQUAKEMODEL'

def ugeImportModel( FileType, UI ):    
    header = struct(magic=string(),version=u32,filesize=u32,flags=u32)(label=' -- header')                                   
    
    strcnt, strtbl = u32(label=' -- string count'), u32(label=' -- string table offset')
    meshes = array( struct(name=string(offset=u32,relation=strtbl),image_name=string(offset=u32,relation=strtbl),initial_vec=u32,vec_count=u32,initial_tri=u32,tri_count=u32),
        count=u32(label=' -- mesh count') )( offset=u32(label=' -- mesh array offset'), label={' -- meshes ':' -- mesh'})     
    _attributes, _vector_count = array( struct(Type=u32,flags=u32,Format=u32,stride=u32,offset=u32), count=u32(label=' -- attributes array count') ), u32(label=' -- vector count')
    attrs = _attributes( offset=u32(label=' -- attributes offset'), label={' -- attributes ':' -- attr'} )                        
    _formats = [s8,u8,s16,u16,s32,u32,f16,f32,f64]; _labels = [' -- verts',' -- UVs',' -- normals',' -- tangents',' -- blend indices',' -- blend weights',' -- colors']
    vectors = { a.Type: array( array(_formats[a.Format],count=a.stride), count=_vector_count )( offset=a.offset, label='' if a.Type>len(_labels)-1 else _labels[a.Type] ) for a in attrs }    
    _idx3_array = array( struct(i1=u32,i2=u32,i3=u32), count=u32(label=' -- count') )
    triangles = _idx3_array( offset=u32(label=' -- triangles array offset'), label={' -- triangles':' -- triangle'} )
    adj_tris = _idx3_array( offset=u32(label=' -- adjacent triangles array offset'), label={' -- adjacent triangles':' -- triangles'} )                    
    vec3, quat = struct(X=f32,Y=f32,Z=f32), struct(X=f32,Y=f32,Z=f32,W=f32) # future: vec3=vec(3); quat=vec(4) # will be included as named: vec3, vec4, and quat
    bones = array( struct(name=string(offset=u32,relation=strtbl),parent=s32,loc=vec3,rot=quat,sca=vec3), 
        count=u32(label=' -- bone count') )( offset=u32(label=' -- bone array offset') , label={' -- bones ':' -- bone'} )
    # TODO: no backend animation support yet.
    num_poses, ofs_poses = u32(label=' -- num_poses'),u32(label=' -- ofs_poses')
    num_anims, ofs_anims = u32(label=' -- num_anims'),u32(label=' -- ofs_anims')
    num_frames, num_framechannels, ofs_frames, ofs_bounds = u32(label=' -- num_frames'),u32(label=' -- num_framechannels'),u32(label=' -- ofs_frames'),u32(label=' -- ofs_bounds')
    num_comment, ofs_comment = u32(label=' -- num_comment'),u32(label=' -- ofs_comment')
    num_extensions, ofs_extensions = u32(label=' -- num_extensions'),u32(label=' -- ofs_extensions')
    
    rig = ugeSetObject('Rig') # static rig object
    for name,parent,L,R,S in bones:
        ugeSetBone( name ); ugeSetBoneParent( parent if parent>=0 else None )
        #L,R,S = ugeMtxDecompose( ugeMtxCompose(L,R,S), quat=False )
        # TODO: ^ remove this line (for some unknown reason, matrix composition during verification yields different results with quaternions)
        ugeSetBoneLoc(L); ugeSetBoneRot(R); ugeSetBoneSca(S)
    types = [ugeSetVertArr,ugeSetUVArr,ugeSetNormalArr,lambda T:None,lambda bI:None,lambda bW:None,ugeSetColorArr] # future (replace lambda T): ugeSetTangentArr
    indices = [ugeSetVertIndex,ugeSetUVIndex,ugeSetNormalIndex,lambda T:None,lambda bI:None,lambda bW:None,ugeSetColorIndex] # future (replace lambda T): ugeSetTangentIndex
    weights = [zip(i,w) for i,w in zip(vectors[4],vectors[5])] if 4 in vectors else [] # [ ( (i,w), (i,w), (i,w), (i,w) ), ... ]
    for mesh in meshes:
        ugeSetObject( mesh.name ); ugeSetObjectParent( rig )
        for attr in attrs: types[attr.Type](vectors[attr.Type]) # ( V,U,N,T,bI,W,C, ... reserved ..., custom ... )[attr.Type]
        ugeSetPrimitive(UGE_TRIANGLES)
        for tri in triangles[mesh.initial_tri:][:mesh.tri_count]:
            [(ugeSetFacepoint(), [indices[attr.Type](i) for attr in attrs], [ ugeSetWeight( I,W/255.0 ) for I,W in weights[i] if (I+W)>0 ]) for i in tri]
        img=mesh.image_name; ugeSetMaterial(img); ugeSetTexture(img); ugeSetImage(img); ugeSetImageData(img)
    
def XugeExportModel( FileType, UICommands ): pass 