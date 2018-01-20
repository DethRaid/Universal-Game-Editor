# -*- coding: utf-8 -*-

from __future__ import print_function

# noinspection PyUnresolvedReferences
from .scripts import DATA,FORMAT,FILE
# noinspection PyUnresolvedReferences
from . import CWD, scripts

try:
    # noinspection PyShadowingBuiltins
    input = raw_input
except NameError: pass

# noinspection PyUnresolvedReferences,PyBroadException
def terminal():
    globals()["execute"] = True
    globals()["quit"] = lambda: globals().__setitem__("execute",False)
    while execute: 
        try:
            src = input('>>> ')
            try:
                r = eval(src,globals())
                if r!=None: print(r)
            except SyntaxError: exec src in globals()
        except:
            import sys,traceback
            print(); traceback.print_exception( *sys.exc_info() ); print()
            continue
            
#FORMAT.Roots[0].Objects[0].Data.Bones[1].Bind.decompose()