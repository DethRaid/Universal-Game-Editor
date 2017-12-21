# This is a map of the OOP method of sending and retrieving data to and from the API.
# this method was requested by many people who for some reason couldn't seem to understand the simplicity kick of the functional method.
# that said, there are a few more interesting tweaks you can do with this method that you actually can't precisely do in the other.

# NOTE: all UGEObject subclasses support these attributes:
# - Name
# - Index (required if Name is disabled)
# NOTE: all Heirarchical subclasses support these attributes:
# - Parent
# - Child
# - Next
# - Prev
# everything is optional and each may be disabled depending on the settings for the subclass (eg: Facepoint)

# NOTE: on a hierarchy of collections, Index reflects the root collection:
# Ref1 = Root.Objects['Name']
# Ref2 = Scene.Objects['Name']
# Ref1.Index is reflected from Root.Objects
# use Scene.Objects.Index('Name') to add and retrieve the local index.

# --- Data Creation ---
World = CurrentRoot.Worlds[Name]
Scene = World.Scenes[Name]
Object = Scene.Objects[Name]
    Object.Viewport = 0
    Object.Location = (X,Y,Z)
    Object.Rotation = (X,Y,Z(,W))
    Object.Scale    = (X,Y,Z)
Material = Object.Materials[Name] # ignored with rig objects
    Material.Ambient    = (R,G,B,A)
    Material.Diffuse    = (R,G,B,A)
    Material.Specular   = (R,G,B,A)
    Material.Emissive   = (R,G,B,A)
    Material.Glossiness = 25.0 # Shininess
Texture = Material.Textures[Name] # WIP
    #Texture.Params[index] = ??
Image = Texture.Images[Name]
    Image.Width         = 128
    Image.Height        = 128
    Image.Pixels[index] = (I/R(,A/G(,B(,A)))) or "path/imagefile"
    Image.Colors[index] = (I/R(,A/G(,B(,A)))) or "path/palettefile"

# Extended attributes:

# rig objects
Bone = Object.Bones[Name] # if any
    Bone.Viewport = 0
    Bone.Location = (X,Y,Z)
    Bone.Rotation = (X,Y,Z(,W))
    Bone.Scale    = (X,Y,Z)

# mesh objects
# NOTE: you can also set the full array instead of just an index
Vertice   = Object.Vertices[   index ] = (X(,Y(,Z(,W)))) # same for the rest
Normal    = Object.Normals[    index ]
BiNormal  = Object.BiNormals[  index ]
Tangent   = Object.Tangents[   index ]
Color     = Object.Colors[     channel, index ] # typically 2 channels
UV        = Object.UVs[        channel, index ] # typically 32 channels
Weight    = Object.Weights[    index ]
Primitive = Object.Primitives[ channel, index ] # unlimited channels supporting names, works as multimple meshes

Facepoint = Primitive.Facepoints[index]

    Facepoint.VerticeIndex           = index
    Facepoint.NormalIndex            = index
    Facepoint.BiNormalIndex          = index
    Facepoint.TangentIndex           = index
    Facepoint.ColorIndices[channel]  = index
    Facepoint.UVIndices[channel]     = index
    Facepoint.WeightIndices[Bone]    = index
    Facepoint.MaterialIndices[index] = index

    Facepoint.Vertice                = (X,Y,Z(,W))
    Facepoint.Normal                 = (I,J,K(,H))
    Facepoint.BiNormal               = (I,J,K(,H))
    Facepoint.Tangent                = (I,J,K(,H))
    Facepoint.Colors[channel]        = (I/R(,A/G(,B(,A))))
    Facepoint.UVs[channel]           = (S,T(,R(,Q)))
    Facepoint.Weights[Bone].Value    = 1.0
    Facepoint.Materials[index]       = Material

# NOTE: all collections support the read-only `.current` attribute, but only some are linked with respective read-only globals:
# - CurrentRoot (this is the base of everything)
# - CurrentWorld
# - CurrentScene
# - CurrentObject
# - CurrentBone
# - CurrentPrimitive
# - CurrentFacepoint
# - CurrentMaterial
# - CurrentTexture
# - CurrentImage

# --- Data Retrieval ---
for World in CurrentRoot.Worlds:
    for Scene in World.Scenes:
        for Object in Scene.Objects:
            Object.SubName
            Object.Viewport
            Object.Location
            Object.Rotation
            Object.Scale
            
            for Material in Object.Materials:
                Material.Ambient
                Material.Diffuse
                Material.Specular
                Material.Emissive
                Material.Glossiness
                
                for Texture in Material.Textures:
                    
                    for Image in Texture.Images:
                        Image.Width
                        Image.Height
                        Palette = Image.Colors
                        for Pixel in Image.Pixels:
                            if Palette: Pixel = Palette[Pixel.X]
            
            # Extended attributes:
            
            # rig
            for Bone in Object.Bones:
                Bone.Viewport
                Bone.Location
                Bone.Rotation
                Bone.Scale
            
            # mesh
            for Vertice in Object.Vertices:
            for Normal in Object.Normals:
            for BiNormal in Object.BiNormals:
            for Tangent in Object.Tangents:
            for channel,Colors in Object.Colors:
                for Color in Colors:
            for channel,UVs in Object.UVs:
                for UV in UVs:
            
            for Weight in Object.Weights:
            
            for mesh, Primitives in Object.Primitives:
                for Primitive in Primitives:
                    for Facepoint in Primitive.Facepoints:
                        Facepoint.VerticeIndex
                        Facepoint.NormalIndex
                        Facepoint.BiNormalIndex
                        Facepoint.TangentIndex
                        for channel, index in Facepoint.ColorIndices
                        for channel, index in Facepoint.UVIndices
                        for Bone, index in Facepoint.WeightIndices
                        for index, Mindex in Facepoint.MaterialIndices
                        
                        # NOTE: all items have the Index attribute which should be the same as the raw attributes above:
                        Facepoint.Vertice
                        Facepoint.Normal
                        Facepoint.BiNormal
                        Facepoint.Tangent
                        for channel, Color in Facepoint.Colors:
                        for channel, UV in Facepoint.UVs:
                        for Bone, Weight in Facepoint.Weights:
                        for index, Material in Facepoint.Materials:

# Global collections: (whatever is created above is created in these)
for Scene in CurrentRoot.Scenes:       # all Scenes
for Object in CurrentRoot.Objects:     # all Objects
for Material in CurrentRoot.Materials: # all Materials
for Texture in CurrentRoot.Textures:   # all Textures
for Image in CurrentRoot.Images:       # all Images
                    
# NOTE: if indices are missing, they will be supplied during iteration.
# eg:
# Object.Vertices[0]
# Object.Vertices[5]
# print( Object.Vertices ) # >>> collection( vector: [<vector X: 0.0,  Y: 0.0,  Z: 0.0 >, <vector X: 0.0,  Y: 0.0,  Z: 0.0 >] )
# 
# >>> for idx,Vertice in enumerate(Object.Vertices): print( '%i:'%idx, Vertice )
# 0: <vector X: 0.0,  Y: 0.0,  Z: 0.0 >
# 1: <vector X: 0.0,  Y: 0.0,  Z: 0.0 >
# 2: <vector X: 0.0,  Y: 0.0,  Z: 0.0 >
# 3: <vector X: 0.0,  Y: 0.0,  Z: 0.0 >
# 4: <vector X: 0.0,  Y: 0.0,  Z: 0.0 >
# 5: <vector X: 0.0,  Y: 0.0,  Z: 0.0 >
