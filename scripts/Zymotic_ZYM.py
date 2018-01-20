
ugeScriptType(UGE_MODEL_SCRIPT)
ugeScriptFormats({ 'Zymotic Model Format': ['zym'] })

# written by Tcll5850
# ported from sources:
# - Nexuiz/sources/darkplaces/model_zymotic.h (main resource)

def ugeImportModel( FileType, UICommands ): # Commands are supplied from the GUI

    jump(0) # temporary fix for SIDE re-run freeze

    lump = struct(8, start=bu32, length=bu32 )

    ID = string(12)(label=' -- id') # "ZYMOTICMODEL"
    Type = bu32(label=' -- type') # 0 (vertex morph) 1 (skeletal pose) or 2 (skeletal scripted)
    filesize = bu32(label=' -- filesize')
    # for clipping uses:
    Min,Max = bf32(['','',''],label=' -- min'),bf32(['','',''],label=' -- max')
    radius = bf32(label=' -- radius')

    numverts   = bu32(label=' -- numverts')
    numtris    = bu32(label=' -- numtris')
    numshaders = bu32(label=' -- numshaders')
    numbones   = bu32(label=' -- numbones') # this may be zero in the vertex morph format (undecided)
    numscenes  = bu32(label=' -- numscenes') # 0 in skeletal scripted models

    lump( label=' -- lump_scenes', prefix=' -- ' ) # prefix is for labeling using the struct's varnames
    lump( label=' -- lump_poses', prefix=' -- ' )
    lump( label=' -- lump_bones', prefix=' -- ' )
    lump( label=' -- lump_vertbonecounts', prefix=' -- ' )
    lump( label=' -- lump_texcoords', prefix=' -- ' )
    lump( label=' -- lump_render', prefix=' -- ' )
    lump( label=' -- lump_shaders', prefix=' -- ' )
    lump( label=' -- lump_trizone', prefix=' -- ' )

def XugeExportModel( FileType, UICommands): pass 