from __future__ import print_function

ugeScriptType(UGE_MODEL_SCRIPT)
ugeScriptFormats({'Blender ~2.49':['blend','blend1','blend2']}) # targeted format, not fixed

# designed by Tcll5850 following these sources: (old URLs may not be valid, contact me for saved sources)
# - Hypered - Blender's native file format - http://hy.io/blender/ (need the page name)
# - The mystery of the blend - http://www.atmind.nl/blender/mystery_ot_blend.html
# - Blender 2.49b

def ugeImportModel(T,C):
    target = 249 #don't change this
    #I'm still looking into the 26x format
    
    #global header:
    magic = string(7)(label=' -- magic') # BLENDER
    
    ptr = (u32 if string(1)(label=' -- pointer size')=='_' else u64) # '_':32bit, '-':64bit
    big = string(1)(        label=' -- endian')=='V'  # 'v':little, 'V':big
    version = int(string(3)(label=' -- version'))
    
    if version>target:
        print("your file version is too high ("+str(version)+")")
        print("this plugin supports up to version {0}".format(str(target)))
        
    else:
        str32 = string(4)
        
        while True: 
            #header:
            code = str32(label=' -- Code' )
            sz   = u32(  label=' -- size', big=big )
            M_A  = ptr(  label=' -- Old Memory Address', big=big )
            SDNA = u32(  label=' -- SDNA Index', big=big )
            cnt  = u32(  label=' -- Structure Count', big=big )
            
            switch(code)
            if case('ENDB'): break
            elif case('DNA1'):
                identifier = str32() #'SDNA'
                
                NameIdentifier = str32() #'NAME'
                NCount = u32( label=' -- Name_Count', big=big )
                Names  = array( string(), count=NCount )()
                
                Typeidentifier = str32() #'TYPE'
                TCount = u32( label=' -- Type_Count', big=big )
                Types  = array( string(), count=TCount )()

                Lengthidentifier = str32() #'TLEN'
                Lengths = array( u16, count=TCount )( big=big )

                Structidentifier = str32(); sz-=4 #'STRC'
                SCount  = u32( label=' -- Struct_Count', big=big )
                Structs = array( u16, count=SCount )( big=big )

                FCount = u16( label=' -- Field_Count', big=big )
                Fields = array( u16, count=FCount )( big=big )
                
            else:
                skip(sz)

def XugeExportModel(T,C): #later
    pass
