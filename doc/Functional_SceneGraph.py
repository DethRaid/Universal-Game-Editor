# This is a map of the functional method of sending and retrieving data to and from the API.
# this method was designed for newcommers to 3D programming as they likely don't understand the concept of Object Orientation.
# this method simply wraps the functionality found in the OOP method.

# --- Data Creation ---
World = ugeSetWorld( Name )
Scene = ugeSetScene( Name )

Object = ugeSetObject( Name )
ugeSetObjectSubName(  Name        ) # defaults to Object.Name
ugeSetObjectParent(   Name        )
ugeSetObjectViewport( 0           )
ugeSetObjectLoc(      (X,Y,Z)     )
ugeSetObjectRot(      (X,Y,Z(,W)) )
ugeSetObjectSca(      (X,Y,Z)     )

Material = ugeSetMaterial( Name, assign = True ) # assign defaults to True, which assigns the material to the Object
ugeSetMaterialAmbient(    (R,G,B,A) )
ugeSetMaterialDiffuse(    (R,G,B,A) )
ugeSetMaterialSpecular(   (R,G,B,A) )
ugeSetMaterialEmissive(   (R,G,B,A) )
ugeSetMaterialGlossiness( 25.0 )

Texture = ugeSetTexture( Name ) # WIP

Image = ugeSetImage( Name )
ugeSetImageWidth(  128 )
ugeSetImageHeight( 128 )
ugeSetImagePixels( [(I/R(,A/G(,B(,A)))), ... ] or "path/imagefile" )
ugeSetImageColors( [(I/R(,A/G(,B(,A)))), ... ] or "path/palettefile" )

# Extended attributes:

# rig objects
Bone = ugeSetBone( Name )
ugeSetBoneViewport( 0           )
ugeSetBoneLoc(      (X,Y,Z)     )
ugeSetBoneRot(      (X,Y,Z(,W)) )
ugeSetBoneSca(      (X,Y,Z)     )

# mesh objects
ugeSetVertices(  [(X(,Y(,Z(,W)))), ... ], flag = UGE_PRETRANSFORMED ) # flag specifies (defaults to) if the vectors come pre-transformed (in T-pose)
ugeSetNormals(   [(I,J,K(,H)), ... ],     flag = UGE_PRETRANSFORMED )
ugeSetBiNormals( [(I,J,K(,H)), ... ],     flag = UGE_PRETRANSFORMED )
ugeSetTangents(  [(I,J,K(,H)), ... ],     flag = UGE_PRETRANSFORMED )
ugeSetColors(    [(I/R(,A/G(,B(,A)))), ... ], channel = 0 )
ugeSetUVs(       [(S,T(,R(,Q))), ... ],       channel = 0 )
ugeSetWeights(   [ 1.0, ... ] )

Primitive = ugeSetPrimitive( UGE_PRIMITIVE_TYPE or Primitive or index, mesh = None ) # mesh will use Object.SubName if None

Facepoint = ugeSetFacepoint( None or Facepoint or index ) # None creates a new Facepoint

ugeSetFpVerticeIndex(  index )
ugeSetFpNormalIndex(   index )
ugeSetFpBiNormalIndex( index )
ugeSetFpTangentIndex(  index )
ugeSetFpColorIndex(    index, channel = 0 )
ugeSetFpUVIndex(       index, channel = 0 )
# these are reversed because both arguments are required
ugeSetFpWeightIndex(   Bone,  index )
ugeSetFpMaterialIndex( index, index ) # refers to ugeSetMaterialIndex( Facepoint.Materials[index], Object.Materials[index] )

ugeSetFpVertice(  (X(,Y(,Z(,W)))), flag = UGE_PRETRANSFORMED )
ugeSetFpNormal(   (I,J,K(,H)),     flag = UGE_PRETRANSFORMED )
ugeSetFpBiNormal( (I,J,K(,H)),     flag = UGE_PRETRANSFORMED )
ugeSetFpTangent(  (I,J,K(,H)),     flag = UGE_PRETRANSFORMED )
ugeSetFpColor(    (I/R(,A/G(,B(,A)))), channel = 0 )
ugeSetFpUV(       (S,T(,R(,Q))),       channel = 0 )
# these are reversed because both arguments are required
ugeSetFpWeight(   Bone,  1.0 )
ugeSetFpMaterial( index, Material )

# --- Data Retrieval ---
for World in ugeGetWorlds():
    ugeGetWorldName(World)
    
    for Scene in ugeGetScenes(World):
        ugeGetSceneName(Scene)
        
        for Object in ugeGetObjects(Scene):
            ugeGetObjectName(Object)
            ugeGetObjectSubName(Object)
            ugeGetObjectParent(Object)
            ugeGetObjectViewport(Object)
            ugeGetObjectLoc(Object)
            ugeGetObjectRot(Object)
            ugeGetObjectSca(Object)
            
            for Material in ugeGetMaterials(Object):
                ugeGetMaterialName(Material)
                ugeGetMaterialAmbient(Material)
                ugeGetMaterialDiffuse(Material)
                ugeGetMaterialSpecular(Material)
                ugeGetMaterialEmissive(Material)
                ugeGetMaterialGlossiness(Material)
                
                for Texture in ugeGetTextures(Material):
                    ugeGetTextureName(Texture)
                    
                    for Image in ugeGetImages(Texture):
                        ugeGetImageName(Image)
                        ugeGetImageWidth(Image)
                        ugeGetImageHeight(Image)
                        Palette = ugeGetImageColors(Image)
                        for Pixel in ugeGetImagePixels(Image):
                            if Palette: Pixel = Palette[Pixel[0]]
            
            # Extended attributes:
            
            # rig
            for Bone in ugeGetBones(Object):
                ugeGetBoneName(Bone)
                ugeGetBoneParent(Bone)
                ugeGetBoneViewport(Bone)
                ugeGetBoneLoc(Bone)
                ugeGetBoneRot(Bone)
                ugeGetBoneSca(Bone)
            
            # mesh
            for Vertice in ugeGetVertices(Object,   flag = UGE_PRETRANSFORMED ):
            for Normal in ugeGetNormals(Object,     flag = UGE_PRETRANSFORMED ):
            for BiNormal in ugeGetBiNormals(Object, flag = UGE_PRETRANSFORMED ):
            for Tangent in ugeGetTangents(Object,   flag = UGE_PRETRANSFORMED ):
            for channel,Colors in ugeGetColors(Object):
                for Color in Colors:
            for channel,UVs in ugeGetUVs(Object):
                for UV in UVs:
            
            for Weight in ugeGetWeights(Object):
            
            for mesh, Primitives in ugeGetPrimitives(Object):
                for Primitive in Primitives:
                    for Facepoint in ugeGetFacepoints(Primitive):
                        ugeGetFpVerticeIndex(  Facepoint )
                        ugeGetFpNormalIndex(   Facepoint )
                        ugeGetFpBiNormalIndex( Facepoint )
                        ugeGetFpTangentIndex(  Facepoint )
                        for channel, index in ugeGetFpColorIndices(   Facepoint ):
                        for channel, index in ugeGetFpUVIndices(      Facepoint ):
                        for Bone, index in ugeGetFpWeightIndices(     Facepoint ):
                        for index, Mindex in ugeGetFpMaterialIndices( Facepoint ):
                        
                        ugeGetFpVertice(   Facepoint, flag = UGE_PRETRANSFORMED )
                        ugeGetFpNormal(    Facepoint, flag = UGE_PRETRANSFORMED )
                        ugeGetFpBiNormal(  Facepoint, flag = UGE_PRETRANSFORMED )
                        ugeGetFpTangent(   Facepoint, flag = UGE_PRETRANSFORMED )
                        for channel, Color in ugeGetFpColors(     Facepoint ):
                        for channel, UV in ugeGetFpUVs(           Facepoint ):
                        for Bone, Weight in ugeGetFpWeights(      Facepoint ):
                        for index, Material in ugeGetFpMaterials( Facepoint ):

# Global collections: (whatever is created above is created in these)
for Scene in ugeGetScenes(CurrentRoot):       # all Scenes
for Object in ugeGetObjects(CurrentRoot):     # all Objects
for Material in ugeGetMaterials(CurrentRoot): # all Materials
for Texture in ugeGetTextures(CurrentRoot):   # all Textures
for Image in ugeGetImages(CurrentRoot):       # all Images
