# -*- coding: utf-8 -*-
"""
 *  Copyright (C) 2010-2018 Tcll5850
 *
 *  This Program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2, or (at your option)
 *  any later version.
 *
 *  This Program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with GNU Make; see the file COPYING.  If not, write to
 *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
 *  http://www.gnu.org/copyleft/gpl.html
"""
# float.h rehash (since python only provides DBL_EPSILON from sys.float_info.epsilon)
from ctypes import c_float
FLT_EPSILON = 1.
while c_float(1.+FLT_EPSILON*.5).value!=1.: FLT_EPSILON = c_float(FLT_EPSILON*.5).value
del c_float

# constants from blender-mathutils: (possibly more performative than the math module)
M_PI       = 3.14159265358979323846  # pi
M_PI_2     = 1.57079632679489661923  # pi/2
M_PI_4     = 0.78539816339744830962  # pi/4
M_SQRT2    = 1.41421356237309504880  # sqrt(2)
M_SQRT1_2  = 0.70710678118654752440  # 1/sqrt(2)
M_SQRT3    = 1.73205080756887729352  # sqrt(3)
M_SQRT1_3  = 0.57735026918962576450  # 1/sqrt(3)
M_1_PI     = 0.318309886183790671538 # 1/pi
M_E        = 2.7182818284590452354   # e
M_LOG2E    = 1.4426950408889634074   # log_2 e
M_LOG10E   = 0.43429448190325182765  # log_10 e
M_LN2      = 0.69314718055994530942  # log_e 2
M_LN10     = 2.30258509299404568402  # log_e 10

class   Root(object): __slots__ = []
class Object(object): __slots__ = []

# IMPORTANT - all imports should be done here, sub-module references should use `from . import ______`
# NOTE: the load order should not be changed, it works from the branches to the root for solidity
from ..OBJECT import *
from .uge_vector import UGEVector, VectorProp
from .uge_image import *
from .uge_texture import *
from .uge_shader import *
from .uge_material import *
from .uge_rig import *
from .uge_mesh import *
from .uge_object import *
from .uge_scene import *
from .uge_world import *
from .uge_root import *

# noinspection PyStatementEffect
Roots['UGE_Default_Root']

"""
Tcll - a note on the policy of functions supplied to scripts:

All functions should have multiple (at least 3) ways of doing the same action,
for example, accessing the attributes of a UGEObject:

simple access:
ugeFunction( None ) # current
ugeFunction( 'Name' )
ugeFunction( UGEObject/Proxy )

extended access:
ugeFunction( None or False ) # global
ugeFunction( True ) # local ( `Roots.current.World.current.Scenes.current.Objects` vs `Roots.current.Objects` for example )

the collection() class helps with most of the access as you can index an object via it's name, instance, or even it's proxy,
so all you really have to do is reference the object in the collection, if it's name doesn't exist, it will be created.
(the instance index is better for comparison than for data-referencing)

one thing to note though is a function should NOT return a direct instance to a UGEObject, but rather it's proxy
this is very important for future compatibility and for keeping the frontend in order.
and also from a noob's perspective, as object orientation is not the easiest thing to understand
(after all, the frontend is designed mainly for noobs)

also, if an unsupported argument has been passed,
unless the action would be detrimental to the backend, a function should NOT raise an exception.
the idea is to complete the operation at all costs and assume the best action if needed.

NOTE: breaking the formatting backend is not an easy thing to do.
data verification after importing is designed to resolve most harmful disruptions, making the data safe to use.
that aside, this new interface offers in-place verification, or small incompatibility checks within the base-classes.
(this means less function-sided verification code since most of the verification is already done for you)

"""
'''
modules['/Roots_backup/'] = None
def _Reset():
    modules['/Roots_backup/'] = [Roots.objects[:],Roots.current,Roots.NextID]
    
    objects = Roots.objects
    pop = objects.pop
    while objects: pop()
    Roots.current = Roots['UGE_Default_Root']
    
def _Finalize():
    print('Finalizing...')
    modules['/Roots_backup/'] = None
    
def _Recall():
    if not modules['/Roots_backup/']: return # nothing to recall
    
    objects = Roots.objects
    pop = objects.pop
    while objects: pop()
    Roots.current = None
    
    Roots,current = modules['/Roots_backup/']
    objects.extend(objects)
    Roots.current = current
    
    _Finalize()
'''
########################################################################################################################
# DEPRECATED: everything below here is to be removed (everything should be done real-time in the sub-modules)
########################################################################################################################
'''
# DEPRECATED: matrices are considered to be inefficient
def _Transform(): # TODO: this functionality should be integrated into the base-classes
    ZeroMtx = matrix( [ [ 0.0 ] * 4 ] * 4 )
    print('Transforming data...')
    for CurrentObject in Roots._current.Objects.objects: # Tcll - really need to fix this issue
        ObjectData = CurrentObject.Data
        if ObjectData == '_mesh':
            Parent = CurrentObject.Parent
            while Parent: # search for the parent rig
                if Parent.Data=='_rig': break
                Parent = Parent.Parent
            # DEPRECATED: favor goes to vector (UT) or vector.local (PT)
            Verts = ObjectData.Verts;       UTVerts = ObjectData.UTVerts
            Normals = ObjectData.Normals;   UTNormals = ObjectData.UTNormals
            Weights = ObjectData.Weights
            if Parent!=None: # make sure we have bones to transform with
                Bones = Parent.Data.Bones.objects
                for CurrentMesh in ObjectData.Meshes.objects: # need these for the transformation pairs
                    for CurrentPrimitive in CurrentMesh.Primitives.objects:
                        for CurrentFacePoint in CurrentPrimitive.FacePoints.objects:
                            VertID = CurrentFacePoint.VertID; NormalID = CurrentFacePoint.NormalID
                            Vert = Verts[VertID]; UTVert = UTVerts[VertID]
                            WeightIDs = CurrentFacePoint.WeightIDs; Count = len(WeightIDs)
                            Influence = matrix([[0.]*4]*4)
                            for BoneID,WeightID in WeightIDs: # build influence matrix
                                CurrentBone = Bones[BoneID]
                                Influence += (-CurrentBone.Inverse*CurrentBone.Inverse if Count>1 else -CurrentBone.Inverse)*Weights[WeightID]
                                # Tcll - ^ I still don't understand why -inverse*inverse works instead of bind*inverse
                            if Influence!=ZeroMtx:
                                if Vert==None and UTVert==None:
                                    Verts[VertID] = vector([0.,0.,0.,1.])
                                    UTVerts[VertID] = vector([0.,0.,0.,1.])
                                    if NormalID!=None:
                                        Normals[NormalID] = vector([0.,0.,0.,1.])
                                        UTNormals[NormalID] = vector([0.,0.,0.,1.])
                                        
                                elif Vert==None: # transform
                                    # noinspection PyUnusedLocal
                                    (m00,m01,m02,m03),(m10,m11,m12,m13),(m20,m21,m22,m23),(m30,m31,m32,m33) = Influence
                                    VX,VY,VZ = UTVert[:3]
                                    Verts[VertID] = vector( (m00*VX)+(m01*VY)+(m02*VZ)+m03 ,
                                                            (m10*VX)+(m11*VY)+(m12*VZ)+m13 ,
                                                            (m20*VX)+(m21*VY)+(m22*VZ)+m23 )
                                    if NormalID!=None:
                                        NX,NY,NZ = UTNormals[NormalID][:3]
                                        Normals[NormalID] = vector( (m00*NX)+(m01*NY)+(m02 * NZ) ,
                                                                    (m10*NX)+(m11*NY)+(m12 * NZ) ,
                                                                    (m20*NX)+(m21*NY)+(m22 * NZ) ) # rotation only
                                        
                                elif UTVert==None: # un-transform
                                    Influence*=-1 # invert the values of the influence
                                    # noinspection PyUnusedLocal
                                    (m00,m01,m02,m03),(m10,m11,m12,m13),(m20,m21,m22,m23),(m30,m31,m32,m33) = Influence
                                    VX,VY,VZ = Vert[:3]
                                    UTVerts[VertID] = vector( (m00*VX)+(m01*VY)+(m02*VZ)+m03 ,
                                                              (m10*VX)+(m11*VY)+(m12*VZ)+m13 ,
                                                              (m20*VX)+(m21*VY)+(m22*VZ)+m23 )
                                    if NormalID!=None:
                                        NX,NY,NZ = Normals[NormalID][:3]
                                        UTNormals[NormalID] = vector( (m00*NX)+(m01*NY)+(m02 * NZ) ,
                                                                      (m10*NX)+(m11*NY)+(m12 * NZ) ,
                                                                      (m20*NX)+(m21*NY)+(m22 * NZ) ) # rotation only
            
            # fix any stragglers (make sure there are NO Nones)
            VertID = 0
            for Vert,UTVert in zip(Verts,UTVerts):
                if Vert==None and UTVert==None:
                    Verts[VertID] = vector([0.,0.,0.,1.])
                    UTVerts[VertID] = vector([0.,0.,0.,1.])
                if Vert==None: Verts[VertID] = vector(list(UTVerts[VertID]))
                elif UTVert==None: UTVerts[VertID] = vector(list(Verts[VertID]))
                VertID += 1
                
            NormalID = 0
            for Normal,UTNormal in zip(Normals,UTNormals):
                if Normal==None and UTNormal==None:
                    Normals[NormalID] = vector([0.,0.,0.,1.])
                    UTNormals[NormalID] = vector([0.,0.,0.,1.])
                if Normal==None: Normals[NormalID] = vector(*UTNormals[NormalID])
                elif UTNormal==None: UTNormals[NormalID] = vector(*Normals[NormalID])
                NormalID += 1
'''
"""
# noinspection PyUnresolvedReferences
def _VerifyBoneTree( bone, Parent ): # TODO: this functionality should be integrated into the base-classes
    #m = _compose(bone.Location,bone.Rotation,bone.Scale)
    trans = matrix()
    trans.compose(bone.Location,bone.Rotation,bone.Scale)
    
    #print(bone.Name(),'old:',bone.Rotation)
    
    wmtx = Parent
    Relation = bone.Relation # relation specs: Bind: parent; Inverse: -world
    if Relation==CONST.UGE_PARENT:          wmtx = Parent*trans;   bone.Bind, bone.Inverse = trans, -wmtx
    #if Relation==CONST.UGE_OBJECT: (Blender's armature-objects)
    if Relation==CONST.UGE_WORLD:           wmtx = trans;          bone.Bind, bone.Inverse = trans*-Parent, -trans
    if Relation==CONST.UGE_INVERSE_PARENT:  wmtx = -trans*Parent;  bone.Bind, bone.Inverse = -trans, trans*-Parent
    #if Relation==CONST.UGE_INVERSE_OBJECT:
    if Relation==CONST.UGE_INVERSE_WORLD:   wmtx = -trans;         bone.Bind, bone.Inverse = -(Parent*trans), trans
    
    # update LRS to local Euler coords
    bone.Location, bone.Rotation, bone.Scale = bone.Bind.decompose( quat=False ) 
    
    #print(bone.Name(),'new:',bone.Rotation)
    
    if bone.Child: _VerifyBoneTree(bone.Child,wmtx )
    if bone.Next: _VerifyBoneTree(bone.Next,wmtx )
    
def _Verify(): # TODO: this functionality should be integrated into the base-classes
    # Check Relations and fill in the blanks:
    print("Verifying data...")
    
    #TODO: check materials, textures, and images
    
    Objects = Roots.current.Objects
    for CurrentObject in Objects.objects:
        if CurrentObject==None: continue # TODO: remove, this shouldn't be happening >.>
        ObjectData = CurrentObject.Data
        
        Parent = CurrentObject.Parent
        Parents = []
        while Parent: # make sure parents don't infinite-loop over each other
            if Parent.Parent in Parents: Parent.Parent = None
            else: Parents.append(Parent) # Tcll - not worried too much about performance here
            Parent = Parent.Parent
        
        if ObjectData=='_rig': # most of the old verification should now be done before-hand
            Bones = ObjectData.Bones
            for CurrentBone in Bones.objects: # fix relation IDs
                
                if CurrentBone.Parent:
                    Parent = CurrentBone.Parent
                    CurrentBone.Parent = Bones[Parent]
                    Parents = []
                    while Parent: # make sure parents don't infinite-loop over each other
                        if Parent.Parent in Parents: Parent.Parent = None
                        else: Parents.append(Parent) # Tcll - not worried too much about performance here
                        Parent = Parent.Parent
                    del Parents
                    
                if CurrentBone.Child:
                    Child = CurrentBone.Child
                    CurrentBone.Child = Bones[CurrentBone.Child]
                    Children = []
                    while Child: # make sure children don't infinite-loop over each other
                        if Child.Child in Children: Child.Child = None
                        else: Children.append(Child) # Tcll - not worried too much about performance here
                        Child = Child.Child
                    del Children
                    
                if CurrentBone.Prev:
                    Prev = CurrentBone.Prev
                    CurrentBone.Prev = Bones[CurrentBone.Prev]
                    PrevBones = []
                    while Prev: # make sure prev-bones don't infinite-loop over each other
                        if Prev.Prev in PrevBones: Prev.Prev = None
                        else: PrevBones.append(Prev) # Tcll - not worried too much about performance here
                        Prev = Prev.Prev
                    del PrevBones
                        
                if CurrentBone.Next:
                    Next = CurrentBone.Next
                    CurrentBone.Next = Bones[CurrentBone.Next]
                    NextBones = []
                    while Next: # make sure next-bones don't infinite-loop over each other
                        if Next.Next in NextBones: Next.Next = None
                        else: NextBones.append(Next) # Tcll - not worried too much about performance here
                        Next = Next.Next
                    del NextBones
                
            for CurrentBone in Bones.objects:
                if not CurrentBone.Parent: _VerifyBoneTree( CurrentBone, matrix() )
        
        #if ObjectData=='_mesh':
    '''
    for OID,(ObjectName, VP, OLRS, (SDType,SDName,SDD1,SDD2), POID) in enumerate(FORMAT.Libs[3]):

        if SDType=='_Mesh':
            invalid = []
            for MID,MatID in enumerate(SDD1):
                try: mat = FORMAT.Libs[4][MatID] # IndexError here if invalid refernce
                except IndexError: invalid.append(MID)
            for MID in list(reversed(invalid)): FORMAT.Libs[3][OID][3][2].pop(MID)
                        
            Verts, NBTs, Colors, UVs, Weights, Primitives = SDD2
            
            #TODO: validate and fill empty vectors
            
            empty = []
            for PID, Prim in enumerate(Primitives):
                if len(Prim[1])==0: empty.append(PID) # empty primitive
                else: pass #TODO: validate vector IDs
                
            for EPID in list(reversed(empty)): FORMAT.Libs[3][OID][3][3][5].pop(EPID) # remove empty primitives
    '''
"""
########################################################################################################################
# UGE-matrix manipulation functions
########################################################################################################################
# NOTE: just because matrices are no longer used in the API doesn't mean scripts and libs don't need support.

# noinspection PyUnresolvedReferences
#import numpy, scipy # TODO: remove (numpy sucks at performance)
#from .. import UGE_GLOBAL_WRAPPER, register

#@UGE_GLOBAL_WRAPPER
#@register([CONST.UGE_MODEL_SCRIPT,CONST.UGE_ANIMATION_SCRIPT],True)
#def ugeMtxTranspose(Mtx) -> vector: """Transposes (flips) a matrix."""; return Mtx.transpose()

#def _det(m) -> list: return numpy.linalg.det(m) # TODO: need to support more than just 4x4 matrices to remove numpy

'''
    (n00,n01,n02,n03),(n10,n11,n12,n13),(n20,n21,n22,n23),(n30,n31,n32,n33) = m
    return (n00 * (n11 * (n22 * n33 - n23 * n32) + n12 * (n23 * n31 - n21 * n33) + n13 * (n21 * n32 - n22 * n31)) +
            n01 * (n10 * (n23 * n32 - n22 * n33) + n12 * (n20 * n33 - n23 * n30) + n13 * (n22 * n30 - n20 * n32)) +
            n02 * (n10 * (n21 * n33 - n23 * n31) + n11 * (n23 * n30 - n20 * n33) + n13 * (n20 * n31 - n21 * n30)) +
            n03 * (n10 * (n22 * n31 - n21 * n32) + n11 * (n20 * n32 - n22 * n30) + n12 * (n21 * n30 - n20 * n31)));
'''

#def _inv(m) -> list: return numpy.linalg.inv(numpy.array(m)).tolist() # TODO: need to support more than just 4x4 matrices to remove numpy

"""
    # faster code no longer indexes:
    (n00,n01,n02,n03),(n10,n11,n12,n13),(n20,n21,n22,n23),(n30,n31,n32,n33) = m
    '''
    det  =  Mtx[0][3]*Mtx[1][2]*Mtx[2][1]*Mtx[3][0] - Mtx[0][2]*Mtx[1][3]*Mtx[2][1]*Mtx[3][0] - \
            Mtx[0][3]*Mtx[1][1]*Mtx[2][2]*Mtx[3][0] + Mtx[0][1]*Mtx[1][3]*Mtx[2][2]*Mtx[3][0] + \
            Mtx[0][2]*Mtx[1][1]*Mtx[2][3]*Mtx[3][0] - Mtx[0][1]*Mtx[1][2]*Mtx[2][3]*Mtx[3][0] - \
            Mtx[0][3]*Mtx[1][2]*Mtx[2][0]*Mtx[3][1] + Mtx[0][2]*Mtx[1][3]*Mtx[2][0]*Mtx[3][1] + \
            Mtx[0][3]*Mtx[1][0]*Mtx[2][2]*Mtx[3][1] - Mtx[0][0]*Mtx[1][3]*Mtx[2][2]*Mtx[3][1] - \
            Mtx[0][2]*Mtx[1][0]*Mtx[2][3]*Mtx[3][1] + Mtx[0][0]*Mtx[1][2]*Mtx[2][3]*Mtx[3][1] + \
            Mtx[0][3]*Mtx[1][1]*Mtx[2][0]*Mtx[3][2] - Mtx[0][1]*Mtx[1][3]*Mtx[2][0]*Mtx[3][2] - \
            Mtx[0][3]*Mtx[1][0]*Mtx[2][1]*Mtx[3][2] + Mtx[0][0]*Mtx[1][3]*Mtx[2][1]*Mtx[3][2] + \
            Mtx[0][1]*Mtx[1][0]*Mtx[2][3]*Mtx[3][2] - Mtx[0][0]*Mtx[1][1]*Mtx[2][3]*Mtx[3][2] - \
            Mtx[0][2]*Mtx[1][1]*Mtx[2][0]*Mtx[3][3] + Mtx[0][1]*Mtx[1][2]*Mtx[2][0]*Mtx[3][3] + \
            Mtx[0][2]*Mtx[1][0]*Mtx[2][1]*Mtx[3][3] - Mtx[0][0]*Mtx[1][2]*Mtx[2][1]*Mtx[3][3] - \
            Mtx[0][1]*Mtx[1][0]*Mtx[2][2]*Mtx[3][3] + Mtx[0][0]*Mtx[1][1]*Mtx[2][2]*Mtx[3][3]
    '''
    det = ( n00 * (n11 * (n22 * n33 - n23 * n32) + n12 * (n23 * n31 - n21 * n33) + n13 * (n21 * n32 - n22 * n31)) +
            n01 * (n10 * (n23 * n32 - n22 * n33) + n12 * (n20 * n33 - n23 * n30) + n13 * (n22 * n30 - n20 * n32)) +
            n02 * (n10 * (n21 * n33 - n23 * n31) + n11 * (n23 * n30 - n20 * n33) + n13 * (n20 * n31 - n21 * n30)) +
            n03 * (n10 * (n22 * n31 - n21 * n32) + n11 * (n20 * n32 - n22 * n30) + n12 * (n21 * n30 - n20 * n31)) )
    '''
    return[[( Mtx[1][2]*Mtx[2][3]*Mtx[3][1] - Mtx[1][3]*Mtx[2][2]*Mtx[3][1] + Mtx[1][3]*Mtx[2][1]*Mtx[3][2] - Mtx[1][1]*Mtx[2][3]*Mtx[3][2] - Mtx[1][2]*Mtx[2][1]*Mtx[3][3] + Mtx[1][1]*Mtx[2][2]*Mtx[3][3]) /det,
            ( Mtx[0][3]*Mtx[2][2]*Mtx[3][1] - Mtx[0][2]*Mtx[2][3]*Mtx[3][1] - Mtx[0][3]*Mtx[2][1]*Mtx[3][2] + Mtx[0][1]*Mtx[2][3]*Mtx[3][2] + Mtx[0][2]*Mtx[2][1]*Mtx[3][3] - Mtx[0][1]*Mtx[2][2]*Mtx[3][3]) /det,
            ( Mtx[0][2]*Mtx[1][3]*Mtx[3][1] - Mtx[0][3]*Mtx[1][2]*Mtx[3][1] + Mtx[0][3]*Mtx[1][1]*Mtx[3][2] - Mtx[0][1]*Mtx[1][3]*Mtx[3][2] - Mtx[0][2]*Mtx[1][1]*Mtx[3][3] + Mtx[0][1]*Mtx[1][2]*Mtx[3][3]) /det,
            ( Mtx[0][3]*Mtx[1][2]*Mtx[2][1] - Mtx[0][2]*Mtx[1][3]*Mtx[2][1] - Mtx[0][3]*Mtx[1][1]*Mtx[2][2] + Mtx[0][1]*Mtx[1][3]*Mtx[2][2] + Mtx[0][2]*Mtx[1][1]*Mtx[2][3] - Mtx[0][1]*Mtx[1][2]*Mtx[2][3]) /det],
           [( Mtx[1][3]*Mtx[2][2]*Mtx[3][0] - Mtx[1][2]*Mtx[2][3]*Mtx[3][0] - Mtx[1][3]*Mtx[2][0]*Mtx[3][2] + Mtx[1][0]*Mtx[2][3]*Mtx[3][2] + Mtx[1][2]*Mtx[2][0]*Mtx[3][3] - Mtx[1][0]*Mtx[2][2]*Mtx[3][3]) /det,
            ( Mtx[0][2]*Mtx[2][3]*Mtx[3][0] - Mtx[0][3]*Mtx[2][2]*Mtx[3][0] + Mtx[0][3]*Mtx[2][0]*Mtx[3][2] - Mtx[0][0]*Mtx[2][3]*Mtx[3][2] - Mtx[0][2]*Mtx[2][0]*Mtx[3][3] + Mtx[0][0]*Mtx[2][2]*Mtx[3][3]) /det,
            ( Mtx[0][3]*Mtx[1][2]*Mtx[3][0] - Mtx[0][2]*Mtx[1][3]*Mtx[3][0] - Mtx[0][3]*Mtx[1][0]*Mtx[3][2] + Mtx[0][0]*Mtx[1][3]*Mtx[3][2] + Mtx[0][2]*Mtx[1][0]*Mtx[3][3] - Mtx[0][0]*Mtx[1][2]*Mtx[3][3]) /det,
            ( Mtx[0][2]*Mtx[1][3]*Mtx[2][0] - Mtx[0][3]*Mtx[1][2]*Mtx[2][0] + Mtx[0][3]*Mtx[1][0]*Mtx[2][2] - Mtx[0][0]*Mtx[1][3]*Mtx[2][2] - Mtx[0][2]*Mtx[1][0]*Mtx[2][3] + Mtx[0][0]*Mtx[1][2]*Mtx[2][3]) /det],
           [( Mtx[1][1]*Mtx[2][3]*Mtx[3][0] - Mtx[1][3]*Mtx[2][1]*Mtx[3][0] + Mtx[1][3]*Mtx[2][0]*Mtx[3][1] - Mtx[1][0]*Mtx[2][3]*Mtx[3][1] - Mtx[1][1]*Mtx[2][0]*Mtx[3][3] + Mtx[1][0]*Mtx[2][1]*Mtx[3][3]) /det,
            ( Mtx[0][3]*Mtx[2][1]*Mtx[3][0] - Mtx[0][1]*Mtx[2][3]*Mtx[3][0] - Mtx[0][3]*Mtx[2][0]*Mtx[3][1] + Mtx[0][0]*Mtx[2][3]*Mtx[3][1] + Mtx[0][1]*Mtx[2][0]*Mtx[3][3] - Mtx[0][0]*Mtx[2][1]*Mtx[3][3]) /det,
            ( Mtx[0][1]*Mtx[1][3]*Mtx[3][0] - Mtx[0][3]*Mtx[1][1]*Mtx[3][0] + Mtx[0][3]*Mtx[1][0]*Mtx[3][1] - Mtx[0][0]*Mtx[1][3]*Mtx[3][1] - Mtx[0][1]*Mtx[1][0]*Mtx[3][3] + Mtx[0][0]*Mtx[1][1]*Mtx[3][3]) /det,
            ( Mtx[0][3]*Mtx[1][1]*Mtx[2][0] - Mtx[0][1]*Mtx[1][3]*Mtx[2][0] - Mtx[0][3]*Mtx[1][0]*Mtx[2][1] + Mtx[0][0]*Mtx[1][3]*Mtx[2][1] + Mtx[0][1]*Mtx[1][0]*Mtx[2][3] - Mtx[0][0]*Mtx[1][1]*Mtx[2][3]) /det],
           [( Mtx[1][2]*Mtx[2][1]*Mtx[3][0] - Mtx[1][1]*Mtx[2][2]*Mtx[3][0] - Mtx[1][2]*Mtx[2][0]*Mtx[3][1] + Mtx[1][0]*Mtx[2][2]*Mtx[3][1] + Mtx[1][1]*Mtx[2][0]*Mtx[3][2] - Mtx[1][0]*Mtx[2][1]*Mtx[3][2]) /det,
            ( Mtx[0][1]*Mtx[2][2]*Mtx[3][0] - Mtx[0][2]*Mtx[2][1]*Mtx[3][0] + Mtx[0][2]*Mtx[2][0]*Mtx[3][1] - Mtx[0][0]*Mtx[2][2]*Mtx[3][1] - Mtx[0][1]*Mtx[2][0]*Mtx[3][2] + Mtx[0][0]*Mtx[2][1]*Mtx[3][2]) /det,
            ( Mtx[0][2]*Mtx[1][1]*Mtx[3][0] - Mtx[0][1]*Mtx[1][2]*Mtx[3][0] - Mtx[0][2]*Mtx[1][0]*Mtx[3][1] + Mtx[0][0]*Mtx[1][2]*Mtx[3][1] + Mtx[0][1]*Mtx[1][0]*Mtx[3][2] - Mtx[0][0]*Mtx[1][1]*Mtx[3][2]) /det,
            ( Mtx[0][1]*Mtx[1][2]*Mtx[2][0] - Mtx[0][2]*Mtx[1][1]*Mtx[2][0] + Mtx[0][2]*Mtx[1][0]*Mtx[2][1] - Mtx[0][0]*Mtx[1][2]*Mtx[2][1] - Mtx[0][1]*Mtx[1][0]*Mtx[2][2] + Mtx[0][0]*Mtx[1][1]*Mtx[2][2]) /det]]
    '''
    m[0][0] = ( n12*n23*n31 - n13*n22*n31 + n13*n21*n32 - n11*n23*n32 - n12*n21*n33 + n11*n22*n33) /det
    m[0][1] = ( n03*n22*n31 - n02*n23*n31 - n03*n21*n32 + n01*n23*n32 + n02*n21*n33 - n01*n22*n33) /det
    m[0][2] = ( n02*n13*n31 - n03*n12*n31 + n03*n11*n32 - n01*n13*n32 - n02*n11*n33 + n01*n12*n33) /det
    m[0][3] = ( n03*n12*n21 - n02*n13*n21 - n03*n11*n22 + n01*n13*n22 + n02*n11*n23 - n01*n12*n23) /det
    m[1][0] = ( n13*n22*n30 - n12*n23*n30 - n13*n20*n32 + n10*n23*n32 + n12*n20*n33 - n10*n22*n33) /det
    m[1][1] = ( n02*n23*n30 - n03*n22*n30 + n03*n20*n32 - n00*n23*n32 - n02*n20*n33 + n00*n22*n33) /det
    m[1][2] = ( n03*n12*n30 - n02*n13*n30 - n03*n10*n32 + n00*n13*n32 + n02*n10*n33 - n00*n12*n33) /det
    m[1][3] = ( n02*n13*n20 - n03*n12*n20 + n03*n10*n22 - n00*n13*n22 - n02*n10*n23 + n00*n12*n23) /det
    m[2][0] = ( n11*n23*n30 - n13*n21*n30 + n13*n20*n31 - n10*n23*n31 - n11*n20*n33 + n10*n21*n33) /det
    m[2][1] = ( n03*n21*n30 - n01*n23*n30 - n03*n20*n31 + n00*n23*n31 + n01*n20*n33 - n00*n21*n33) /det
    m[2][2] = ( n01*n13*n30 - n03*n11*n30 + n03*n10*n31 - n00*n13*n31 - n01*n10*n33 + n00*n11*n33) /det
    m[2][3] = ( n03*n11*n20 - n01*n13*n20 - n03*n10*n21 + n00*n13*n21 + n01*n10*n23 - n00*n11*n23) /det
    m[3][0] = ( n12*n21*n30 - n11*n22*n30 - n12*n20*n31 + n10*n22*n31 + n11*n20*n32 - n10*n21*n32) /det
    m[3][1] = ( n01*n22*n30 - n02*n21*n30 + n02*n20*n31 - n00*n22*n31 - n01*n20*n32 + n00*n21*n32) /det
    m[3][2] = ( n02*n11*n30 - n01*n12*n30 - n02*n10*n31 + n00*n12*n31 + n01*n10*n32 - n00*n11*n32) /det
    m[3][3] = ( n01*n12*n20 - n02*n11*n20 + n02*n10*n21 - n00*n12*n21 - n01*n10*n22 + n00*n11*n22) /det
    # something many people forget about is the power of immutability, which tuples can't do as they're read-only.
    # performance with lists isn't as bad as everyone makes it out to be. (though it's not good either)
    return m
    """

#@UGE_GLOBAL_WRAPPER
#@register([CONST.UGE_MODEL_SCRIPT,CONST.UGE_ANIMATION_SCRIPT],True)
#def ugeMtxInvert(Mtx) -> vector: """Inverts a supplied matrix."""; return Mtx.__neg__()

#def _dot(a,b) -> list: return numpy.dot(numpy.array(a), numpy.array(b)).tolist() # TODO: need to support more than just 4x4 matrices to remove numpy

#notes:
# _dot( 4, 3 ) == 4*3
# _dot( 4, [3,4,5] ) == [ 4*3, 4*4, 4*5 ]
# _dot( 4, [[0,1,2],[3,4,5]] ) == [ [ 4*0, 4*1, 4*2 ], [ 4*3, 4*4, 4*5 ] ]

# _dot( [3,4,5], 3 ) == [ 3*3, 4*3, 5*3 ]
# _dot( [3,4,5], [3,4,5] ) == (3*3)+(4*4)+(5*5)
# _dot( [3,4,5], [[0,1,2],[3,4,5]] ) == [ (3*0)+(4*3)+5, (3*1)+(4*4)+5, (3*2)+(4*5)+5 ] # where numpy fails: (ValueError: objects are not aligned)

# _dot( [[0,1,2],[3,4,5]], 3 ) == [ [ 0*3, 1*3, 2*3 ], [ 3*3, 4*3, 5*3 ] ]
# _dot( [[0,1,2],[3,4,5]], [3,4,5] ) == [ (0*3)+(1*4)+(2*5), (3*3)+(4*4)+(5*5) ]
'''
    #both pointer and return support
    dst[0][0] = a[0][0]*b[0][0] + a[0][1]*b[1][0] + a[0][2]*b[2][0] + a[0][3]*b[3][0]
    dst[0][1] = a[0][0]*b[0][1] + a[0][1]*b[1][1] + a[0][2]*b[2][1] + a[0][3]*b[3][1]
    dst[0][2] = a[0][0]*b[0][2] + a[0][1]*b[1][2] + a[0][2]*b[2][2] + a[0][3]*b[3][2]
    dst[0][3] = a[0][0]*b[0][3] + a[0][1]*b[1][3] + a[0][2]*b[2][3] + a[0][3]*b[3][3]
    dst[1][0] = a[1][0]*b[0][0] + a[1][1]*b[1][0] + a[1][2]*b[2][0] + a[1][3]*b[3][0]
    dst[1][1] = a[1][0]*b[0][1] + a[1][1]*b[1][1] + a[1][2]*b[2][1] + a[1][3]*b[3][1]
    dst[1][2] = a[1][0]*b[0][2] + a[1][1]*b[1][2] + a[1][2]*b[2][2] + a[1][3]*b[3][2]
    dst[1][3] = a[1][0]*b[0][3] + a[1][1]*b[1][3] + a[1][2]*b[2][3] + a[1][3]*b[3][3]
    dst[2][0] = a[2][0]*b[0][0] + a[2][1]*b[1][0] + a[2][2]*b[2][0] + a[2][3]*b[3][0]
    dst[2][1] = a[2][0]*b[0][1] + a[2][1]*b[1][1] + a[2][2]*b[2][1] + a[2][3]*b[3][1]
    dst[2][2] = a[2][0]*b[0][2] + a[2][1]*b[1][2] + a[2][2]*b[2][2] + a[2][3]*b[3][2]
    dst[2][3] = a[2][0]*b[0][3] + a[2][1]*b[1][3] + a[2][2]*b[2][3] + a[2][3]*b[3][3]
    dst[3][0] = a[3][0]*b[0][0] + a[3][1]*b[1][0] + a[3][2]*b[2][0] + a[3][3]*b[3][0]
    dst[3][1] = a[3][0]*b[0][1] + a[3][1]*b[1][1] + a[3][2]*b[2][1] + a[3][3]*b[3][1]
    dst[3][2] = a[3][0]*b[0][2] + a[3][1]*b[1][2] + a[3][2]*b[2][2] + a[3][3]*b[3][2]
    dst[3][3] = a[3][0]*b[0][3] + a[3][1]*b[1][3] + a[3][2]*b[2][3] + a[3][3]*b[3][3]
    return dst
    '''

#@UGE_GLOBAL_WRAPPER
#@register([CONST.UGE_MODEL_SCRIPT,CONST.UGE_ANIMATION_SCRIPT],True)
#def ugeMtxMultiply(a,b) -> vector: """Multiply a matrix by another matrix."""; return a*b

#def _cross(a,b) -> list: return numpy.cross(numpy.array(a),numpy.array(b)).tolist() # TODO: remove numpy

#@UGE_GLOBAL_WRAPPER
#@register([CONST.UGE_MODEL_SCRIPT,CONST.UGE_ANIMATION_SCRIPT],True)
#def ugeMtxDecompose(Mtx,quat=False,extended=False) -> list:
#    """Decompose a matrix44 into associated Euler Location, Rotation (optional quat), and Scale, with extended Shear and Perspective values.
#
#    usage:
#    L,R,S = ugeMtxDecompose( matrix44 )
#    L,Q,S = ugeMtxDecompose( matrix44, quat=True )
#    L,R,S,Sh,Ps = ugeMtxDecompose( matrix44, extended=True )
#    """
#    return vector(Mtx).decompose(quat)

#@UGE_GLOBAL_WRAPPER
#@register([CONST.UGE_MODEL_SCRIPT,CONST.UGE_ANIMATION_SCRIPT],True)
#def ugeMtxCompose(location=[0,0,0],rotation=[0,0,0],scale=[1,1,1],shear=[0,0,0],perspective=[0,0,0,1]) -> vector:
#    """Compse a matrix44 from the supplied Euler coords.
#
#    usage:
#    M = ugeMtxDecompose( Loc, Rot, Sca )
#    M = ugeMtxDecompose( Loc, Quat, Sca )
#    M = ugeMtxDecompose( Loc, Rot, Sca, Shear, Persp )
#    """
#    return vector.compose(vector(location),vector(rotation),vector(scale),vector(shear),vector(perspective))