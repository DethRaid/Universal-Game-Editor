# -*- coding: utf-8 -*-
"""
Python's extended builtin types made available as direct builtins in python's own flavor.
"""

# Use of these types is meant for direct construction for injection by the API or mods,
# and for comparison in the frontend if ever needed.

import sys
class _c: __slots__=['a']; _m=lambda a:None
member_descriptor = _c.a.__class__
# noinspection PyProtectedMember
function = _c._m.__class__
# noinspection PyProtectedMember
method = _c()._m.__class__
builtin_function_or_method = len.__class__
mappingproxy = type.__dict__.__class__
generator = (i for i in []).__class__
code = compile('','','exec').__class__
module = sys.__class__
#namespace = sys.implementation.__class__
try: raise TypeError
except TypeError:
    tb = sys.exc_info()[2]
    traceback = type(tb)
    frame = type(tb.tb_frame)
    tb = None
del _c, tb

numtype = {int,float}.__contains__

def iterable(o: object) -> bool:
    """Return whether the object is iterable (i.e., some kind of array or collection).
    
    Note that instances of classes with a\n__iter__() method are iterable."""
    return '__iter__' in o.__dict__ or hasattr(o,'__iter__')

__builtins__.update(sys.modules[__name__].__dict__)