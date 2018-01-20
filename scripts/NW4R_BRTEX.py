
ugeScriptType(UGE_IMAGE_SCRIPT)
ugeScriptFormats({ 'NTDO_IMG': ['tex0'] })
ugeScriptLibs(['RVL_IMG'])#revolution'])

def ugeImportImage(FT,CMD):

    ##Begin header:
    magic = string()(4, label=' -- TEX0_Magic')
    str_tbl = bu32(     label=' -- String_Table_Offset')
    num_images = bu32(  label=' -- Face_Count')
    brres_hdr = bs32(   label=' -- Brres_Header')
    Data_Offset = bu32( label=' -- Data_Offset')
    
    name = string(bu8)(offset=bu32(label=' -- String_Offset'))
    unk3=bu32(          label=' -- Unknown') #usually 0

    Width=bu16(         label=' -- Width')
    Height=bu16(        label=' -- Height')
    Format=bu32(        label=' -- Format')
    Channels=bu32(      label=' -- Channels')

    jump(Data_Offset, label=' -- Image Data')

    img = readimg(Width,Height,Format)
    
    ugeSetImageWidth(Width)
    ugeSetImageHeight(Height)
    ugeSetImageData(img)
    
def XugeExportImage(FT,CMD):
    pass
