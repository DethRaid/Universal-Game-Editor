
ugeScriptType(UGE_MODEL_SCRIPT)
ugeScriptFormats({
    'Wavefront':['obj','mod']
    })


def XImportModelUI(): #still in development
    CheckBox('Calculate Normals')
    Text('included UV channels:')
    File('UV1')
    File('UV2')
    File('UV3')
    File('UV4')
    File('UV5')
    File('UV6')
    File('UV7')

def XugeImportModel(T,C):
    Verts,Normals,UVs,Object = [],[],[],'Default_Object'
    lines = string('\n')([])
    for line in lines: #collect mesh data first
        line=line.split(' ')
        if line[0]=='v': Verts+=[[float(line[1]),float(line[2])]+([float(line[3])] if len(line)==4 else [])]
        if line[0]=='vn': Normals+=[[float(line[1]),float(line[2])]+([float(line[3])] if len(line)==4 else [])]
        if line[0]=='vt': UVs+=[[float(line[1])]+([float(line[2])] if len(line)==3 else [])]
    for line in lines: #then build (safer)
        line=line.split(' ')
        if line[0]=='o': Object=str(line[-1])
        if line[0]=='f':
            ugeSetObject(Object)

            #I really need a function to do this.
            LP,CP = None,UGE_TRIANGLES #Last/Current Primitive
            if   len(line)==2: CP = UGE_POINTS
            elif len(line)==3: CP = UGE_LINES
            elif len(line)==4: CP = UGE_TRIANGLES
            elif len(line)==5: CP = UGE_QUADS
            elif len(line)>=6: CP = UGE_POLYGON
            if LP!=CP: ugeSetPrimitive(CP)
            LP=CP #update the last primitive to check with the next
            
            for FP in line[1:]:
                FP=FP.split('/') #[v] or [v,u,n]
                if FP!=['\r']:
                    #I'll never understand why this happens 0.o (with any Q3D OBJ export)
                    #['###','###','###']
                    #['\r'] <- at every face end
                    #then we also get an indexing error (not sure if every OBJ does this)
                    '''
                    SetFacepoint(Verts[int(FP[0])-1],
                        (Normals[int(FP[2])-1] if len(FP)==3 else ''),
                        (UVs[int(FP[1])-1] if len(FP)==3 and FP[1]!='' else ''))
                    '''
                    ugeSetFacepoint()

                    ugeSetVert(Verts[int(FP[0])-1])
                    if len(FP)==3:
                        ugeSetNormal(Normals[int(FP[2])-1])
                        if FP[1]!='':
                            try: ugeSetUV(UVs[int(FP[1])-1])
                            except: pass
                

def ugeExportModel(FType,Cmd):
    global vcnt,ncnt,ucnt
    vcnt,ncnt,ucnt=1,1,1 #index starts at 1

    def OBJ_Facepoint(FPID):
        global vcnt,ncnt,ucnt; v,vn,vt = ugeGetVertIndex(FPID),ugeGetNormalIndex(FPID),ugeGetUVIndex(FPID)
        return str(v+vcnt)+('/'+str(vt+ucnt)+('/'+str(vn+ncnt) if vn!=None else '') if vt!=None else ('//'+str(vn+ncnt) if vn!=None else ''))

    """
    mtlname = ugeGetFileName() # name of current file
    ugeExportFile("%s.mtl"%mtlname)
    string('\n')('# MTL created with UMC3.0')
    while ugeMaterialsExist(True):
        string('\n')('newmtl %s'%ugeGetMaterialName())

        AR,AG,AB,AA = ugeGetMaterialAmbient()
        DR,DG,DB,DA = ugeGetMaterialDiffuse()
        SR,SG,SB,SA = ugeGetMaterialSpecular()

        string('\n')('Ka %s %s %s'%(str(AR),str(AG),str(AB)))
        string('\n')('Kd %s %s %s'%(str(DR),str(DG),str(DB)))
        string('\n')('Ks %s %s %s'%(str(SR),str(SG),str(SB)))

        string('\n')('d 1.0')

        '''
        illum:
        0 - Color on and Ambient off
        1 - Color on and Ambient on
        2 - Highlight on
        3 - Reflection on and Ray trace on
        4 - Transparency: Glass on, Reflection: Ray trace on
        5 - Reflection: Fresnel on and Ray trace on
        6 - Transparency: Refraction on, Reflection: Fresnel off and Ray trace on
        7 - Transparency: Refraction on, Reflection: Fresnel on and Ray trace on
        8 - Reflection on and Ray trace off
        9 - Transparency: Glass on, Reflection: Ray trace off
        10 - Casts shadows onto invisible surfaces
        '''

        string('\n')('illum 2\n')
        string('\n')('\n')

        # map_Kd lenna.tga
     
    ugeSwitchFile() # last active
    """

    string('\n')('# OBJ created with UMC3.0')
    #string('\n')('mtllib %s\n'%mtlname)

    for SID in ugeGetScenes():
        for OID in ugeGetObjects(SID):
            if ugeMeshObject(OID):
                string('\n')('o %s'%ugeGetObjectName())

                for Vert in ugeGetVertArr(): string('\n')('v '+str(Vert[0])+' '+str(Vert[1])+(' '+str(Vert[2]) if len(Vert)==3 else ' 0.0'))
                string('\n')('')
                for Normal in ugeGetNormalArr(): string('\n')('vn '+str(Normal[0])+' '+str(Normal[1])+(' '+str(Normal[2]) if len(Normal)==3 else ' 0.0'))
                string('\n')('')
                for UV in ugeGetUVArr(None,0): string('\n')('vt '+str(UV[0])+' '+(str(UV[1]) if len(UV)==2 else ' 0.0'))
                string('\n')('')
                """
                if ugeMaterialsExist(): # only use the first material (OBJ doesn't support otherwize)
                    string('\n')('usemtl %s'%ugeGetMaterialName())
                """
                for PID in ugeGetPrimitives():
                    switch( ugeGetPrimType(PID) )
                    Facepoints = ugeGetFacePoints()
                    FPLen = len(Facepoints)

                    i=0
                    if case(UGE_POINTS):
                        while i<FPLen:
                            FP0=OBJ_Facepoint(Facepoints[i])
                            string('\n')('f '+FP0); i+=1
                    if case(UGE_LINES):
                        while i<FPLen-1:
                            FP0,FP1=OBJ_Facepoint(Facepoints[i]),OBJ_Facepoint(Facepoints[i+1])
                            string('\n')('f '+FP0+' '+FP1); i+=2
                    if case(UGE_LINESTRIP):
                        while i<FPLen-1:
                            FP0,FP1=OBJ_Facepoint(Facepoints[i]),OBJ_Facepoint(Facepoints[i+1])
                            string('\n')('f '+FP0+' '+FP1 if FP0!=FP1 else ''); i+=1
                    if case(UGE_LINELOOP):
                        while i<FPLen-1:
                            FP0,FP1=OBJ_Facepoint(Facepoints[i]),OBJ_Facepoint(Facepoints[i+1])
                            string('\n')('f '+FP0+' '+FP1 if FP0!=FP1 else ''); i+=1
                    if case(UGE_TRIANGLES):
                        while i<FPLen-2:
                            FP0,FP1,FP2=OBJ_Facepoint(Facepoints[i]),OBJ_Facepoint(Facepoints[i+1]),OBJ_Facepoint(Facepoints[i+2])
                            string('\n')('f '+FP2+' '+FP1+' '+FP0); i+=3
                    if case(UGE_TRIANGLESTRIP):
                        while i<FPLen-2:
                            FP0,FP1,FP2=OBJ_Facepoint(Facepoints[i]),OBJ_Facepoint(Facepoints[i+1]),OBJ_Facepoint(Facepoints[i+2])
                            string('\n')('f '+(FP0 if(i%2)else FP2)+' '+FP1+' '+(FP2 if(i%2)else FP0) if (FP0!=FP1!=FP2!=FP0) else ''); i+=1
                    if case(UGE_TRIANGLEFAN):
                        while i<FPLen-2:
                            FP0,FP1,FP2=OBJ_Facepoint(Facepoints[0]),OBJ_Facepoint(Facepoints[i+1]),OBJ_Facepoint(Facepoints[i+2])
                            string('\n')('f '+(FP0 if(i%2)else FP2)+' '+FP1+' '+(FP2 if(i%2)else FP0) if (FP0!=FP1!=FP2!=FP0) else ''); i+=1
                    if case(UGE_QUADS):
                        while i<FPLen-3:
                            FP0,FP1,FP2,FP3=OBJ_Facepoint(Facepoints[i]),OBJ_Facepoint(Facepoints[i+1]),OBJ_Facepoint(Facepoints[i+2]),OBJ_Facepoint(Facepoints[i+3])
                            string('\n')('f '+FP0+' '+FP1+' '+FP2+' '+FP3); i+=4
                    if case(UGE_QUADSTRIP):
                        while i<FPLen-3:
                            FP0,FP1,FP2,FP3=OBJ_Facepoint(Facepoints[i]),OBJ_Facepoint(Facepoints[i+1]),OBJ_Facepoint(Facepoints[i+2]),OBJ_Facepoint(Facepoints[i+3])
                            string('\n')('f '+FP0+' '+FP1+' '+FP2+' '+FP3 if (FP0!=FP1!=FP2!=FP3!=FP0!=FP2!=FP1!=FP3) else ''); i+=2
                    if case(UGE_POLYGON):
                        pass #TODO... (not widely used)

                string('\n')('')
                vcnt+=len(ugeGetVertArr(OID))
                ncnt+=len(ugeGetNormalArr(OID))
                ucnt+=len(ugeGetUVArr(OID,0))
