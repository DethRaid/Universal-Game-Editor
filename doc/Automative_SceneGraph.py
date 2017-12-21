# this is a map of the fully automated layout that UGE's backend deals with pretty much directly
# Tcll - this method was designed personally by my own programming preferences, and is particularly for those few who like to see their work done for them.
# in comparison with the OOP method, it's pretty much similar except that object attributes aren't directly set by the user.

# automation is the representation of an object from a data structure to supply data by,
# and can be started from pretty much anywhere in either of the functional or OOP methods, and can be directed at particular areas where helpful.
# this map starts from the very base assuming complete, no-interference automation from anywhere.

# NOTE: all UGEObject subclasses (represented by a dict) support these attributes:
# - 'Name'
# - 'Index' (required if Name is disabled)
# NOTE: all Heirarchical subclasses (also represented by a dict) support these attributes:
# - 'Parent'
# - 'Child'
# - 'Next'
# - 'Prev'
# everything is optional and each may be disabled depending on the settings for the subclass (eg: Facepoint)

# --- Data Creation ---
CurrentRoot.Worlds = [ # unfortunately the functional method does not yet have a way to set all worlds through automation.
  { 'Name'  : WorldName,
    'Scenes': [
      { 'Name'   : SceneName,
        'Objects': [
          { 'Name'      : ObjectName,
            'SubName'   : DataName,
            'Parent'    : ObjectName,
            'Viewport'  : 0,
            'Location'  : {'ZYX':(Z,Y,X)},
            'Rotation'  : {'X':X, 'Y':Y, 'Z':Z(, 'W':W)},
            'Scale'     : (X,Y,Z),
            'Materials' : [
              { 'Name'      : MaterialName,
                'Ambient'   : (R,G,B,A),
                'Diffuse'   : (R,G,B,A),
                'Specular'  : (R,G,B,A),
                'Emissive'  : (R,G,B,A),
                'Glossiness': 25.0,
                'Textures'  : [
                  { 'Name'  : TextureName,
                    'Images': [
                      { 'Name'  : ImageName,
                        'Width' : 128,
                        'Height': 128,
                        'Pixels': [ (I/R(,A/G(,B(,A)))), ... ],
                        'Colors': [ (I/R(,A/G(,B(,A)))), ... ]
                      },
                      ...
                    ]
                  },
                  ...
                ],
                'Shaders'   : [] # WIP
              },
              ...
            ],

            # Extended attributes:

            # rig objects
            'Bones'     : [
              { 'Name'    : BoneName,
                'Parent'  : BoneName,
                'Viewport': 0,
                'Location': (X,Y,Z),
                'Rotation': (X,Y,Z(,W)),
                'Scale'   : (X,Y,Z),
              },
              ...
            ],

            # mesh objects
            'Vertices'  : [ {'X':X, 'Y':Y, 'Z':Z(, 'W':W)(, 'flag':UGE_UNTRANSFORMED)}, ... ],
            'Normals'   : [ (I,J,K(,H)), ... ],
            'BiNormals' : [ (I,J,K(,H)), ... ],
            'Tangents'  : [ (I,J,K(,H)), ... ],
            'Colors'    : { channel: [ (I/R(,A/G(,B(,A)))), ... ], ... },
            'UVs'       : { channel: [ (S,T(,R(,Q))), ... ], ... },
            'Weights'   : [ 1.0, ... ],
            'Primitives': {
              meshName: [
                { 'Type'      : UGE_PRIMITIVE_TYPE,
                  'Facepoints': [
                    { 'Vertice'        : (X(,Y(,Z(,W)))),
                      'Normal'         : (I,J,K(,H)),
                      'BiNormal'       : (I,J,K(,H)),
                      'Tangent'        : (I,J,K(,H)),
                      'Colors'         : { channel: (I/R(,A/G(,B(,A)))), ... },
                      'UVs'            : { channel: (S,T(,R(,Q))), ... },
                      'Weights'        : { Bone: 1.0, ... },
                      'Materials'      : [ Material ],
                      # or (don't use both as they overwrite each other)
                      'VerticeIndex'   : index,
                      'NormalIndex'    : index,
                      'BiNormalIndex'  : index,
                      'TangentIndex'   : index,
                      'ColorIndices'   : { channel: index, ... },
                      'UVIndices'      : { channel: index, ... },
                      'WeightIndices'  : { Bone: index, ... },
                      'MaterialIndices': [ index ]
                    },
                    ...
                  ]
                },
                ...
              ],
              ...
            }
          },
          ...
        ]
      },
      ...
    ]
  },
  ...
]

# --- Data Retrieval ---

# for automation to work with data retrieval, you need to define struct and array data types with names matching the UGEObject attributes,
# and feed the intended UGEObject to the automation structure.

# for example:

facepoint = struct(
    VerticeIndex = bu16,
    NormalIndex = bu16,
    UVIndices = array( bu16, count=1 ) # single UV support
    )

primitive = struct(
    Type = bu8,
    Facepoints = array( facepoint, count=bu16 )
    )

for Primitive in CurrentObject.Primitives: # not exactly true automation, but this is just an example.
    primitive( Primitive )
