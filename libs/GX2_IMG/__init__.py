
def readimg(fmt,offset=None): #TODO: more options for mips and channels
    if offset is not None: jump(offset)
    
    switch(fmt)
    
    #GX2_SURFACE_FORMAT_INVALID                  
    if case(0x00000000):
        pass
    # color write (100%)): texture read (100%)
    
    #GX2_SURFACE_FORMAT_TC_R8_UNORM               
    if case(0x00000001):
        pass
    # color write (50%)): texture read (100%)
    
    #GX2_SURFACE_FORMAT_TC_R8_UINT                
    if case(0x00000101):
        pass
    # color write (100%)): texture read (100%)
    
    #GX2_SURFACE_FORMAT_TC_R8_SNORM               
    if case(0x00000201):
        pass
    # color write (50%)): texture read (100%)
    
    #GX2_SURFACE_FORMAT_TC_R8_SINT                
    if case(0x00000301):
        pass
    # texture read (100%)
    
    #GX2_SURFACE_FORMAT_T_R4_G4_UNORM             
    if case(0x00000002):
        pass
    # color write (50%)): texture read (100%)
    
    #GX2_SURFACE_FORMAT_TCD_R16_UNORM             
    if case(0x00000005):
        pass
    # color write (50%)): texture read (100%)
    
    #GX2_SURFACE_FORMAT_TC_R16_UINT               
    if case(0x00000105):
        pass
    # color write (50%)): texture read (100%)
    
    #GX2_SURFACE_FORMAT_TC_R16_SNORM              
    if case(0x00000205):
        pass
    # color write (50%)): texture read (100%)
    
    #GX2_SURFACE_FORMAT_TC_R16_SINT               
    if case(0x00000305):
        pass
    # color write (100%)): texture read (100%)
    
    #GX2_SURFACE_FORMAT_TC_R16_FLOAT              
    if case(0x00000806):
        pass
    # color write (100%)): texture read (100%)
    
    #GX2_SURFACE_FORMAT_TC_R8_G8_UNORM            
    if case(0x00000007):
        pass
    # color write (50%)): texture read (100%)
    
    #GX2_SURFACE_FORMAT_TC_R8_G8_UINT             
    if case(0x00000107):
        pass
    # color write (100%)): texture read (100%)
    
    #GX2_SURFACE_FORMAT_TC_R8_G8_SNORM            
    if case(0x00000207):
        pass
    # color write (50%)): texture read (100%)
    
    #GX2_SURFACE_FORMAT_TC_R8_G8_SINT             
    if case(0x00000307):
        pass
    # color write (100%)): texture read (100%)
    
    #GX2_SURFACE_FORMAT_TCS_R5_G6_B5_UNORM        
    if case(0x00000008):
        pass
    # color write (100%)): texture read (100%)
    
    #GX2_SURFACE_FORMAT_TC_R5_G5_B5_A1_UNORM      
    if case(0x0000000a):
        pass
    # color write (100%)): texture read (100%)
    
    #GX2_SURFACE_FORMAT_TC_R4_G4_B4_A4_UNORM      
    if case(0x0000000b):
        pass
    # color write (100%)): texture read (100%)
    
    #GX2_SURFACE_FORMAT_TC_A1_B5_G5_R5_UNORM      
    if case(0x0000000c):
        pass #< flipped
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TC_R32_UINT               
    if case(0x0000010d):
        pass
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TC_R32_SINT               
    if case(0x0000030d):
        pass
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TCD_R32_FLOAT             
    if case(0x0000080e):
        pass
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TC_R16_G16_UNORM          
    if case(0x0000000f):
        pass
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TC_R16_G16_UINT           
    if case(0x0000010f):
        pass
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TC_R16_G16_SNORM          
    if case(0x0000020f):
        pass
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TC_R16_G16_SINT           
    if case(0x0000030f):
        pass
    # color write (100%)
    
    #GX2_SURFACE_FORMAT_TC_R16_G16_FLOAT          
    if case(0x00000810):
        pass
    
    #GX2_SURFACE_FORMAT_D_D24_S8_UNORM            
    if case(0x00000011):
        pass #< see Note 1
    
    #GX2_SURFACE_FORMAT_T_X24_G8_UINT             
    if case(0x00000111):
        pass #< see Note 1
    
    #GX2_SURFACE_FORMAT_D_D24_S8_FLOAT            
    if case(0x00000811):
        pass
    # color write (100%)
    
    #GX2_SURFACE_FORMAT_TC_R11_G11_B10_FLOAT      
    if case(0x00000816):
        pass
    # color write (100%)
    
    #GX2_SURFACE_FORMAT_TCS_R10_G10_B10_A2_UNORM  
    if case(0x00000019):
        pass
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TC_R10_G10_B10_A2_UINT    
    if case(0x00000119):
        pass
    # color write (100%)
    
    #GX2_SURFACE_FORMAT_T_R10_G10_B10_A2_SNORM    
    if case(0x00000219):
        pass #< A2 part is UNORM
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TC_R10_G10_B10_A2_SINT    
    if case(0x00000319):
        pass
    # color write (100%)
    
    #GX2_SURFACE_FORMAT_TCS_R8_G8_B8_A8_UNORM     
    if case(0x0000001a):
        pass
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TC_R8_G8_B8_A8_UINT       
    if case(0x0000011a):
        pass
    # color write (100%)
    
    #GX2_SURFACE_FORMAT_TC_R8_G8_B8_A8_SNORM      
    if case(0x0000021a):
        pass
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TC_R8_G8_B8_A8_SINT       
    if case(0x0000031a):
        pass
    # color write (100%)
    
    #GX2_SURFACE_FORMAT_TCS_R8_G8_B8_A8_SRGB      
    if case(0x0000041a):
        pass
    # color write (100%)
    
    #GX2_SURFACE_FORMAT_TCS_A2_B10_G10_R10_UNORM  
    if case(0x0000001b):
        pass #< flipped
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TC_A2_B10_G10_R10_UINT    
    if case(0x0000011b):
        pass #< flipped
    
    #GX2_SURFACE_FORMAT_D_D32_FLOAT_S8_UINT_X24   
    if case(0x0000081c):
        pass
    
    #GX2_SURFACE_FORMAT_T_X32_G8_UINT_X24         
    if case(0x0000011c):
        pass #< see Note 2
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TC_R32_G32_UINT           
    if case(0x0000011d):
        pass
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TC_R32_G32_SINT           
    if case(0x0000031d):
        pass
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TC_R32_G32_FLOAT          
    if case(0x0000081e):
        pass
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TC_R16_G16_B16_A16_UNORM  
    if case(0x0000001f):
        pass
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TC_R16_G16_B16_A16_UINT   
    if case(0x0000011f):
        pass
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TC_R16_G16_B16_A16_SNORM  
    if case(0x0000021f):
        pass
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TC_R16_G16_B16_A16_SINT   
    if case(0x0000031f):
        pass
    # color write (50%)
    
    #GX2_SURFACE_FORMAT_TC_R16_G16_B16_A16_FLOAT  
    if case(0x00000820):
        pass
    # color write (25%)
    
    #GX2_SURFACE_FORMAT_TC_R32_G32_B32_A32_UINT   
    if case(0x00000122):
        pass
    # color write (25%)
    
    #GX2_SURFACE_FORMAT_TC_R32_G32_B32_A32_SINT   
    if case(0x00000322):
        pass
    # color write (25%)
    
    #GX2_SURFACE_FORMAT_TC_R32_G32_B32_A32_FLOAT  
    if case(0x00000823):
        pass
    # texture read (100%)
    
    #GX2_SURFACE_FORMAT_T_BC1_UNORM               
    if case(0x00000031):
        pass
    # texture read (100%)
    
    #GX2_SURFACE_FORMAT_T_BC1_SRGB                
    if case(0x00000431):
        pass
    # texture read (100%)
    
    #GX2_SURFACE_FORMAT_T_BC2_UNORM               
    if case(0x00000032):
        pass
    # texture read (100%)
    
    #GX2_SURFACE_FORMAT_T_BC2_SRGB                
    if case(0x00000432):
        pass
    # texture read (100%)
    
    #GX2_SURFACE_FORMAT_T_BC3_UNORM               
    if case(0x00000033):
        pass
    # texture read (100%)
    
    #GX2_SURFACE_FORMAT_T_BC3_SRGB                
    if case(0x00000433):
        pass
    # texture read (100%)
    
    #GX2_SURFACE_FORMAT_T_BC4_UNORM               
    if case(0x00000034):
        pass
    # texture read (100%)
    
    #GX2_SURFACE_FORMAT_T_BC4_SNORM               
    if case(0x00000234):
        pass
    # texture read (100%)
    
    #GX2_SURFACE_FORMAT_T_BC5_UNORM               
    if case(0x00000035):
        pass
    # texture read (100%)
    
    #GX2_SURFACE_FORMAT_T_BC5_SNORM               
    if case(0x00000235):
        pass
    # texture read (100%)
    
    #GX2_SURFACE_FORMAT_T_NV12_UNORM              
    if case(0x00000081):
        pass #< see Note 3
    
    #GX2_SURFACE_FORMAT_LAST                      
    if case(0x0000083f):
        pass
