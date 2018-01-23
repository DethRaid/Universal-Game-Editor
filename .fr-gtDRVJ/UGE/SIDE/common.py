# -*- coding: utf-8 -*-
from __future__ import print_function

# noinspection PyUnresolvedReferences
import sys, os, traceback, time, thread, re
from sys import modules
# noinspection PyUnresolvedReferences
from array import array
#from SIDE.analysis import Interpreter # will use later for type-name matching (too slow atm)
# noinspection PyUnresolvedReferences
from ast import AST,PyCF_ONLY_AST

common = modules[__name__]
node_scopes = [[]] # [-1] is the current scope, anything lower is the current's parents
immediate_children = [[]]


try: range=xrange
except NameError: pass

sys.path.append(__file__.split('common')[0]+'Qt')

modules['/SIDE_debug/'] = False

class node:
    #__slots__ = [] # Tcll - if I could enable this, it would probably speed things up... (read-only attributes error)
    def __init__(this):
        this.dt = None
        this.assignment = ''
        this.label = ''
        this.parents = []
        this.children = 0
        this.expanded = None # True: expanded; False: collapsed; None: not expandable
        this.line = None
        
        this.notend = True
    
    __call__ = lambda this: (this.dt,this.assignment,this.label,this.parents,this.children,this.expanded,this.line)

def tracer(func):
    def wrapper( *args, **kwargs ):
        frame = sys._getframe(1)
        try: code, lasti, ln = frame.f_code, frame.f_lasti, frame.f_lineno
        finally: del frame

        datatype = args[0]
        name = fname = func.__name__
        if (name=='__init__' or name=='__call__') and hasattr(datatype,'__name__'): name = datatype.__name__ # UGE data type
        
        is_datatype = hasattr(datatype,'__dereferenced__')
        
        recursive = False
        if is_datatype: # pre
            Node = node()
            node_scopes[-1].append(Node)
            immediate_children[-1].append(Node)
            recursive = fname=='__init__' or name=='switch'
            if recursive: node_scopes.append([]); immediate_children.append([])
        
        try: called = func( *args,**kwargs ) # call the function to update the object's defaults
        except: traceback.print_exception(*sys.exc_info())#; return None
        
        #print(fname, name, recursive)
        
        if is_datatype: # post
            Node.line = ln # TODO: make sure we're not in an external resource before setting the line number.
            if recursive:
                called = datatype
                
                immediate = immediate_children.pop(-1)
                immediate[-1].notend = False
                
                children = node_scopes.pop(-1)
                node_scopes[-1].extend(children)
                Node.children = num_children = len(children)
                Node.expanded = True
                
                if 'struct' in name:
                    _names = [_N for _N,_T in zip(func.__globals__['keywords'],func.__globals__['datatypes']) if _T]
                    for _n,_v in zip(immediate[num_children-len(_names):],_names): _n.assignment = _v
                    
                if 'array' in name:
                    _stopped = func.__globals__['stop']!=None
                    _chL = num_children-_stopped
                    for _i,_n in enumerate(immediate[_chL-len(datatype.__value__):_chL]): _n.assignment = '[%i]'%_i
                    if _stopped: immediate[-1].assignment = '[-]'
            
            Node.parents = [_scope[-1] for _scope in node_scopes]
            if 'label' in kwargs: lb = kwargs['label']; Node.label = lb.items()[0][0] if lb.__class__==dict else lb.__str__()

            assignments = [] #Interpreter().run(code, lasti=lasti, current_line=True) # too slow atm
            Node.assignment = ', '.join(assignments) if assignments else ''
            
            Node.dt = called
            
        return None if fname=='__init__' else called
    return wrapper

sys.modules['/UGE_GLOBAL_WRAPPER/'] = tracer

from API import scripts, loadLibraries

CONST = scripts.CONST
FORMAT = scripts.FORMAT
FILE = scripts.FILE

from API.utilities import hashcolor
def text2color(name): c= QtGui.QColor(hashcolor(name)); c.setAlpha(64); return c

# noinspection PyUnresolvedReferences
from PyQt4 import QtCore, QtGui, QtOpenGL
# noinspection PyUnresolvedReferences
from PyQt4.Qt import Qt

global dSelClr; dSelClr = QtGui.QColor(255, 255, 0, 128)

# DEPRECATED: use the registration interface
global ugeTypes; ugeTypes = {}
global ugeFuncs; ugeFuncs = {}
global ugeConst; ugeConst = {v:c for v,c in scripts.CONST.__dict__.items() if v.startswith('UGE') and v!='UGE_CONSTANT'} # using c for categorization

#shared colors
global ugeFuncsClr; ugeFuncsClr = QtGui.QColor(128, 32, 255, 255)
global ugeBFuncsClr; ugeBFuncsClr = QtGui.QColor(0, 96, 160, 255)
global ugeConstClr; ugeConstClr = QtGui.QColor(128, 128, 0, 255)

class MEM(list): # dummy placeholder for data viewers
    size = 0
