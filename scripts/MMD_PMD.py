from __future__ import print_function

ugeScriptType(UGE_MODEL_SCRIPT)
ugeScriptFormats({
    'Miku Miku Dance':['pmd'],
    })
ugeScriptType(UGE_ANIMATION_SCRIPT)
ugeScriptFormats({
    'Miku Miku Dance':['vmd'],
    })

# built by Tcll5850, with credit to Roo525's inspiration.
# direct reimplementation from pymeshio.pmd with my own terms
def ugeImportModel(T,C):
    def EOF(): return ugeGetFileOffset()>=ugeGetFileSize()
    
    # hacks: ( expect additional security on these in the future )
    cp93220 = lambda big=False,label='': string(code='cp932')(20,label=label); cp93220._size_ = 20
    cp93250 = lambda big=False,label='': string(code='cp932')(50,label=label); cp93250._size_ = 50
    cp932100 = lambda big=False,label='': string(code='cp932')(100,label=label); cp932100._size_ = 100
    # future: automation_object = automate( callable, *args, **kwargs )
    sys.modules['/stack/'] = []
    def Set(t):
        def local1(big=False,label=''): sys.modules['/stack/'].append(t(label=label)); return sys.modules['/stack/'][-1]
        local1._size_=t._size_; return local1
    def Get(): return lambda:sys.modules['/stack/'][-1]
    # future: push( callable ); value = pop(); ( not useable outside of struct or array definitions )
    
    signature = string(3)(label=' -- Signature') #'Pmd'
    if signature=='Pmd': # is the file valid? continue if so
        version = f32(label=' -- Version')
        name = string(code='cp932')(20,label=' -- model name')
        comment = string(code='cp932')(256,label=' -- comment')
        
        facepoints = array( [ f32,f32,f32, f32,f32,f32, f32,f32, u16,u16, u8,u8 ], count=u32 )( label=' -- facepoints',
            labels=[ ' -- X', ' -- Y', ' -- Z', ' -- I', ' -- J', ' -- K', ' -- S', ' -- T',
                ' -- bone 1 index', ' -- bone 2 index', ' -- weight ( 0-100 )', ' -- edge flag'] )
        triangles = array( u16, count=u32 )( label=' -- triangles' )
        
        materials = array( [ f32,f32,f32, f32, f32, f32,f32,f32, f32,f32,f32, s8, u8, u32, cp93220 ], count=u32 )( label=' -- materials',
            labels=[' -- Diffuse R', ' -- Diffuse G', ' -- Diffuse B', ' -- Alpha', ' -- Specular Factor',
                ' -- Specular R', ' -- Specular G', ' -- Specular B', ' -- Ambient R', ' -- Ambient G', ' -- Ambient B',
                ' -- toon index', ' -- edge flag', ' -- vertex?? count', ' -- image file'] )
        
        bones = array( [ cp93220, u16,u16, u8, u16, f32,f32,f32 ], count=u16 )( label=' -- bones',
            labels=[' -- bone name', ' -- parent index', ' -- tail index', ' -- type', ' -- IK index', ' -- L X', ' -- L Y', ' -- L Z'] )
        IK_List = array( [u16,u16,Set(u8),u16,f32, array(u16,count=Get()) ],count=u16 )( label=' -- IK List',
            labels=[' -- index',' -- target',' -- length',' -- iterations',' -- weight',' -- children'] )
        
        morphs = array( [cp93220,Set(u32),u8, array([ u32, f32,f32,f32 ],count=Get()) ],count=u16 )( label=' -- morphs', # shape animations??
            labels=[' -- morph name', ' -- index count', ' -- type', ' -- data [ index, X,Y,Z ]'] )
        morph_indices = array( u16, count=u8 )( label=' -- morph indices')
        
        bone_groups = array( cp93250, count=u8 )( label=' -- bone group names')
        bone_display_list = array( [ u16, u8 ], count=u32 )( label=' -- bone display list', labels=[' -- bone index', ' -- group index'] )
        
        english_name, english_comment, english_bone_names, english_morph_names, english_bone_group_names = '','',[],[],[]
        if not EOF(): # extension 1 ( english names )
            if u8(label=' -- has english names')==1:
                emnCnt = len(morphs)-sum(m[0]=='base' for m in morphs)
                english_name =  string(code='cp932')(20,label=' -- english model name')
                english_comment = string(code='cp932')(256,label=' -- english comment')
                english_bone_names = array( cp93220,count=len(bones) )( label=' -- english bone names' )
                english_morph_names = array( cp93220,count=emnCnt )( label=' -- english morph names' )
                english_bone_group_names = array( cp93250,count=len(bone_groups) )( label=' -- english bone names' )
        toon_textures = [] if EOF() else array( cp932100,count=10 )( label=' -- toon textures' ) # extension 2 ( toon textures )
        rigidbodies, joints = [],[]
        if not EOF(): # extension 3 ( rigidbodies and joints )
            rigidbodies = array( [ cp93220, s16,s8,u16,u8, f32,f32,f32, f32,f32,f32, f32,f32,f32, f32,f32,f32,f32,f32, u8 ], count=u32 )( label=' -- rigidbodies',
                labels=[' -- rigidbody name',' -- bone index', ' -- collision group', ' -- no collision group', ' -- shape type',
                    ' -- S X', ' -- S Y', ' -- S Z', ' -- L X', ' -- L Y', ' -- L Z', ' -- R X', ' -- R Y', ' -- R Z',
                    ' -- mass', ' -- linear damping', ' -- angular damping', ' -- restitution', ' -- friction', ' -- mode'] )
            joints = array( [ cp93220, u32,u32, f32,f32,f32, f32,f32,f32, f32,f32,f32, f32,f32,f32, f32,f32,f32, f32,f32,f32, f32,f32,f32, f32,f32,f32 ], count=u32 )( label=' -- joints',
                labels=[' -- joint name',' -- rigidbody index a', ' -- rigidbody index b', ' -- L X', ' -- L Y', ' -- L Z', ' -- R X', ' -- R Y', ' -- R Z',
                    ' -- T min X',' -- T min Y',' -- T min Z',' -- T max X',' -- T max Y',' -- T max Z',' -- R min X',' -- R min Y',' -- R min Z',' -- R max X',' -- R max Y',' -- R max Z',
                    ' -- spring constant L X', ' -- spring constant L Y', ' -- spring constant L Z', ' -- spring constant R X', ' -- spring constant R Y', ' -- spring constant R Z'] )
        
    else: print('Invalid PMD file')

