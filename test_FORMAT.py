# this is what should be done when used in 3rd-party software
import API
API.UGE_GLOBAL_WRAPPER = lambda f: f
API.init(1) # do not load plugins or mods (future support: 2 will load API-specific mods)
CONST = API.CONST

# just to make things more like the frontend (done automatically in API.IO, but that's for scripts)
UGE_TRIANGLES = CONST.UGE_TRIANGLES
UGE_UNTRANSFORMED = CONST.UGE_UNTRANSFORMED

# NOTE: this is where the frontend begins in the scripts:

Root = CurrentRoot

World = Root.Worlds.current
Scene = World.Scenes.current
Objects = Scene.Objects

rigObject = Objects['Rig']
Bones = rigObject.Bones
Bone = Bones['NewBone']

meshObject = Objects['Mesh']
meshObject.Parent = rigObject

Vertices = meshObject.Vertices
Normals = meshObject.Normals
Colors = meshObject.Colors
UVs = meshObject.UVs

Primitives = meshObject.Primitives
Primitive = Primitives.new(UGE_TRIANGLES)

Facepoints = Primitive.Facepoints
Facepoint = Facepoints.new()

Facepoint.Vertice = {'ZXYW':(1.,0.,0.,1.), 'flag':UGE_UNTRANSFORMED}
Vertice = Facepoint.Vertice

Facepoint.Normal = {'X':1., 'Y':1., 'Z':1., 'flag':UGE_UNTRANSFORMED}
Normal = Facepoint.Normal

Facepoint.Colors = ( (1.,0.,0.,1.), (0.,0.,1.,1.) ) # NOTE: RGBA not supported, yet
(CI0, C0), (CI1, C1) = Facepoint.Colors

Facepoint.UVs = ( (1.,0.,0.,1.), (0.,0.,1.,1.) ) # NOTE: RGBA not supported, yet
UV0 = Facepoint.UVs[0]
UV7 = Facepoint.UVs[7]

# breakpoint for debugging
if True: pass
