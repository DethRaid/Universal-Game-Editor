from __future__ import print_function

ugeScriptType(UGE_MODEL_SCRIPT)
ugeScriptFormats({'Sm4sh WiiU':['nud']})

# script written by Tcll(5850) aka DarkPikachu
# credit to Random Talking Bush for deciphering the nud, vbn, and nut formats

def ugeImportModel(FT,UIC):
    switch(FT)
    if case('nud'):
        m = ugeGetFileName()

        ##########################################################################################
        ugeImportFile('model.vbn') #m+'.vbn')

        ugeSetObject('VBN')
        
        big = string(4)()=='VBN ' # 'VBN ' if big else ' NBV'
        skip(4)
        BoneCount = u32(big=big)
        skip(16)
        
        BoneName_array = []

        for x in range(BoneCount):
            BoneName = string()(0x44).split(chr(0))[0] #"%03i-%s"%(x,string()) # read until 0x00
            BoneName_array.append( BoneName )
            ugeSetBone(BoneName)
            BoneParent = s16(big=big)
            if BoneParent>-1: ugeSetBoneParent(BoneName_array[BoneParent])
            skip(0x06)

        for x in range(BoneCount):
            ugeSetBone(x)
            ugeSetBoneLoc(f32(['','',''],big=big))
            ugeSetBoneRot(f32(['','',''],big=big))
            ugeSetBoneSca(f32(['','',''],big=big))

        ##########################################################################################
        ugeImportFile('model.nut') #m+'.vbn')

        magic = string(4)() #'NTWU'

        version = bu16()
        fileCount = bu16()
        skip(8)

        for i in range(fileCount):
            blockSize = bu32()
            unk = bu32() # nomally 0
            dataSize = bu32()
            HeaderSize = bu16()
            unk2 = bu16()
            MIPFlag = bu16()
            dataFormat = bu16()

            if magic == 'NTWU':
                width = bu16()
                height = bu16()

            if magic == 'NTP3':
                width = u16()
                height = u16()

            MipMaps = bu32()
            unk3 = bu32()
            dataOffset = bu32()+16
            OFFSET2 = bu32()+16
            OFFSET3 = bu32()+16
            unk4 = bu32()

            if HeaderSize >= 0x60:
                Size = bu32()
                unk5 = bu16()
                unk6 = bu16()
                unk7 = bu32()
                unk8 = bu32()

            if HeaderSize >= 0x70:
                unk9 = bu32()
                unk10 = bu32()
                unk11 = bu32()
                unk12 = bu32()

            if HeaderSize >= 0x80:
                unk13 = bu32()
                unk14 = bu32()
                unk15 = bu32()
                unk16 = bu32()

            if HeaderSize >= 0x90:
                unk17 = bu32()
                unk18 = bu32()
                unk19 = bu32()
                unk20 = bu32()

            eXt = string(4)()
            unk0x20 = bu32()
            unk0x10 = bu32()
            unk21 = bu32()
            GIDX = string(4)()
            unk0x10_2 = bu32()
            unk22 = bu16()
            fileID = bu16()
            unk23 = bu32()

        ##########################################################################################
        ugeSwitchFile(m+'.nud')

        big = True
        
        NDP3 = string(4)()
        filesize = bu32()
        unknown1 = bu16()
        ObjectCount = bu16()
        unknown2 = bu16()
        somethingsets = bu16()
        FacepointBlock = bu32() + 0x30
        FacepointBlockSize = bu32()
        P1VectorBlockSize = bu32()
        P2VectorBlockSize = bu32()

        MeshGroupBlock = (ObjectCount+1) * 0x30
        P1VectorBlock = FacepointBlock + FacepointBlockSize
        P2VectorBlock = P1VectorBlock + P1VectorBlockSize
        StringTable = P2VectorBlock + P2VectorBlockSize
        
        thisfloat1 = bf32()
        thisfloat2 = bf32()
        thisfloat3 = bf32()
        thisfloat4 = bf32()

        MaxMeshCount = 0
        for CurrentObject in range( ObjectCount ):
            jump((CurrentObject+1)*0x30, label=' -- Object')

            floata = bf32()
            floatb = bf32()
            floatc = bf32()
            floatd = bf32()
            floate = bf32()
            floatf = bf32()
            floatg = bf32()
            floath = bf32()

            ObjectName = string()( offset= StringTable+bu32() )
            identifiera = bu32()
            SingleBind = bs16()
            MeshCount = bu16()
            positionb = bu32()

            for CurrentMesh in range(MaxMeshCount, MaxMeshCount+MeshCount): #p

                MeshName = ObjectName
                if CurrentMesh-MaxMeshCount>0: MeshName += ' (%i)'%(CurrentMesh-MaxMeshCount)

                print('Processing Mesh: %s'%MeshName)

                ugeSetObject(MeshName) #TODO: add multi-mesh support to objects (move this up 1 level)
                ugeSetObjectParent('VBN')

                jump( MeshGroupBlock+(CurrentMesh*0x30), label=' -- Mesh Data' )

                FacepointData = FacepointBlock + bu32()
                P1VectorData = P1VectorBlock + bu32()
                P2VectorData = P2VectorBlock + bu32()
                VectorCount = bu16()
                VectorAttributes = bu8()
                UVAttributes = bu8()
                TextureLayer1Properties = bu32()
                TextureLayer2Properties = bu32()
                TextureLayer3Properties = bu32()
                TextureLayer4Properties = bu32()
                FacepointCount = bu16()
                FacepointAttributes = bu8()
                PolyFlag = bu8()
                
                skip( 0x0C )

                #Face_array = []
                Vert_array = []
                Normal_array = []
                Color_Array = []
                UV_array = []
                UV2_array = []
                UV3_array = []
                UV4_array = []
                # up to UV8??
                Weight_array = []

                jump( P1VectorData, label=' -- Vector Data' ) #seek_set
                for v in range(VectorCount):

                    ###
                    if not (VectorAttributes>>4)&4:
                        vx, vy, vz = f32(['','',''],big=big)
                        Vert_array.append([vx, vy, vz])
                    
                        if VectorAttributes==0x00:
                            floatyval = f32(big=big)
                        elif VectorAttributes==0x06:
                            nx, ny, nz, nq = f16(['','','',''],big=big)
                            Normal_array.append([nx, ny, nz])
                        elif VectorAttributes==0x07:
                            nx, ny, nz, nq,\
                            bx, by, bz, bq,\
                            tx, ty, tz, tq = f16(['']*12,big=big)
                            Normal_array.append([nx, ny, nz])
                        elif VectorAttributes==0x08:
                            nx, ny, nz,\
                            bx, by, bz,\
                            tx, ty, tz = f16(['']*9,big=big)
                            Normal_array.append([nx, ny, nz])
                        
                        b = SingleBind if SingleBind>-1 else 0
                        Weight_array.append( [[BoneName_array[b], 1.0]] )
                    ###
                        
                    colorr, colorg, colorb, colora = [0,0,0,255] # black preferred over white
                    if UVAttributes in (0x12,0x22,0x32,0x42):
                        colorr, colorg, colorb, colora = u8(['','','','']) # don't need big=big
                        colorr *= 2
                        colorg *= 2
                        colorb *= 2
                        colora /= 127.
                        if colorr >= 254: colorr = 255
                        if colorg >= 254: colorg = 255
                        if colorb >= 254: colorb = 255
                        if colora >= 254: colora = 255
                    Color_Array.append([colorr,colorg,colorb,colora])

                    tu = f16(big=big) * 2
                    tv = ((f16(big=big) * 2) * -1) + 1
                    UV_array.append([tu, tv])
                    
                    if UVAttributes >= 0x22:
                        tu2 = f16(big=big) * 2
                        tv2 = ((f16(big=big) * 2) * -1) + 1
                        UV2_array.append([tu2, tv2])
                        
                    if UVAttributes >= 0x32:
                        tu3 = f16() * 2
                        tv3 = ((f16() * 2) * -1) + 1
                        UV3_array.append([tu3, tv3])
                        
                    if UVAttributes >= 0x42:
                        tu4 = f16() * 2
                        tv4 = ((f16() * 2) * -1) + 1
                        UV4_array.append([tu4, tv4])
                        
                ###
                if (VectorAttributes>>4)&4:
                    jump( P2VectorData, label=' -- Vector Data Part 2' )
                    for v in range(VectorCount):
                        vx, vy, vz = f32(['','',''],big=big)
                        Vert_array.append([vx, vy, vz])
                    
                        if VectorAttributes==0x40:
                            floatyval = f32(big=big)
                        elif VectorAttributes==0x46:
                            nx, ny, nz, nq = f16(['','','',''],big=big)
                            Normal_array.append([nx, ny, nz])
                        elif VectorAttributes==0x47:
                            nx, ny, nz, nq,\
                            bx, by, bz, bq,\
                            tx, ty, tz, tq = f16(['']*12,big=big)
                            Normal_array.append([nx, ny, nz])
                        elif VectorAttributes==0x48:
                            nx, ny, nz,\
                            bx, by, bz,\
                            tx, ty, tz = f16(['']*9,big=big)
                            Normal_array.append([nx, ny, nz])
                        
                        Weight_array.append( zip(
                            [BoneName_array[b] for b in u8(['','','',''])],
                            [w/255. for w in u8(['','','',''])] ) )
                ###

                # data is actually PT! o.o
                ugeSetVertArr(Vert_array)
                if Normal_array: ugeSetNormalArr(Normal_array)
                if Color_Array: ugeSetColorArr(Color_Array)
                if UV_array: ugeSetUVArr(UV_array,0)
                if UV2_array: ugeSetUVArr(UV2_array,1)
                if UV3_array: ugeSetUVArr(UV3_array,2)
                if UV4_array: ugeSetUVArr(UV4_array,3)

                jump( FacepointData, label=' -- Facepoint Data' )
                switch( FacepointAttributes )

                if case( 0x00 ): # Tri-Strips??
                    # not sure what to do here
                    print("You've found a model using the missing format")
                    '''
                    FaceCount = FacepointCount
                    FaceStart = ugeGetFileOffset()
                    VerStart = (FaceCount * 2) + FaceStart

                    StartDirection = 1
                    f1 = u16(big=big) + 1
                    f2 = u16(big=big) + 1  
                    FaceDirection = StartDirection
                    while ugeGetFileOffset() != VerStart:
                        f3 = u16(big=big)
                        if f3==0xFFFF:
                            f1 = u16(big=big) + 1
                            f2 = u16(big=big) + 1
                            FaceDirection = StartDirection 
                        else:
                            f3 += 1
                            FaceDirection *= -1
                            if (f1!=f2)and(f2!=f3)and(f3!=f1): Face_array.append( [f3,f2,f1] if FaceDirection > 0 else [f2,f3,f1] )
                            f1 = f2
                            f2 = f3
                    '''
                if case( 0x40 ):
                    ugeSetPrimitive(UGE_TRIANGLES)
                    for f in range(FacepointCount): #TODO: bring down 1 level (if possible)
                        i = u16(big=big)
                        ugeSetFacepoint()

                        ugeSetVertIndex(i)
                        if Normal_array: ugeSetNormalIndex(i)
                        if Color_Array: ugeSetColorIndex(i)
                        if UV_array: ugeSetUVIndex(i,0)
                        if UV2_array: ugeSetUVIndex(i,1)
                        if UV3_array: ugeSetUVIndex(i,2)
                        if UV4_array: ugeSetUVIndex(i,3)

                        for BN,WV in Weight_array[i]:
                            if WV>0: ugeSetWeight( BN, WV )

            MaxMeshCount += MeshCount
            
            # what exactly does this do??
            '''
            if BoneArray.count > 0 do(
                skinMod = skin ()
                addModifier msh skinMod
                for i = 1 to BoneCount do    (
                    maxbone = getnodebyname BoneArray[i].name
                    if i != BoneCount then
                        skinOps.addBone skinMod maxbone 0
                    else
                        skinOps.addBone skinMod maxbone 1
               
                )

                modPanel.setCurrentObject skinMod

                for i = 1 to Weight_array.count do (
                    w = Weight_array[i]
                    bi = #() --bone index array
                    wv = #() --weight value array
               
                    for j = 1 to w.boneids.count do
                    (
                        boneid = w.boneids[j]
                        weight = w.weights[j]
                        append bi boneid
                        append wv weight
                    )   
               
                    skinOps.ReplaceVertexWeights skinMod i bi wv

                )

            )
            '''
