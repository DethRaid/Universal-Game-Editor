#!/usr/bin/env python
# -*-coding: utf8-*-
"""essais de désassemblage de code"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from collections import deque, namedtuple
import dis
import sys

from dis import (findlabels, findlinestarts)

__version__ = '0.2.0'

record = namedtuple("record",
         "line lasti label index op opname oparg has value")

def record_disassemble(co, lasti=-1, current_line=False):
    """Disassemble a code object."""
    code = co.co_code
    labels = findlabels(code)
    L = list(findlinestarts(co))
    linestarts = dict(L)
    if current_line:
        if lasti < 0:
            raise ValueError("Bytecode index expected (lasti).")
        M = [p for p in L if p[0] <= lasti]
        i = M[-1][0]
        n = L[len(M)][0] if len(M) < len(L) else len(code)
    else:
        n = len(code)
        i = 0
    extended_arg = 0
    free = None
    while i < n:
        args = []
        app = args.append
        c = code[i]
        op = ord(c)
        if i in linestarts:
            app(linestarts[i])
        else:
            app(None)

        if i == lasti: app(True)
        else: app(False)
        if i in labels: app(True)
        else: app(False)
        app(i)
        app(op)
        app(dis.opname[op])
        i = i+1
        if op >= dis.HAVE_ARGUMENT:
            oparg = ord(code[i]) + ord(code[i+1])*256 + extended_arg
            extended_arg = 0
            i = i+2
            if op == dis.EXTENDED_ARG:
                extended_arg = oparg*65536L
            app(oparg)
            if op in dis.hasconst:
                app('const')
                app(co.co_consts[oparg])
            elif op in dis.hasname:
                app('name')
                app(co.co_names[oparg])
            elif op in dis.hasjrel:
                app('jrel')
                app(i + oparg)
            elif op in dis.haslocal:
                app('local')
                app(co.co_varnames[oparg])
            elif op in dis.hascompare:
                app('compare')
                app(cmp_op[oparg])
            elif op in dis.hasfree:
                app('free')
                if free is None:
                    free = co.co_cellvars + co.co_freevars
                app(free[oparg])
            else:
                args.extend((None, None))
        else:
            args.extend((None, None, None))
        yield record(*args)

class VarnamesError(Exception): pass

def dissect_calling_line(level=0):
    f = sys._getframe(2+level)
    try:
        code, lasti, ln = f.f_code, f.f_lasti, f.f_lineno
    finally:
        del f
    return code, list(record_disassemble(code, lasti=lasti, current_line=True))

# Étape suivante: simuler le comportement d'un interprète

actiondict = {}

def action(*opnames):
    def decorator(func):
        for name in opnames:
            actiondict[name] = func
        return func
    return decorator

item0 = object()
item1 = object()
item2 = object()
TOS = -1
TOS1 = -2
TOS2 = -3
TOS3 = -4

class InvalidVarnamesExpression(Exception): pass

# nice pointer on opcodes: http://unpyc.sourceforge.net/Opcodes.html

class Interpreter(object):
    def __init__(self):
        self.stack = []
        self.names = None
        
    def critical(self, *index):
        return any(self.stack[i] in (item1, item2) for i in index)
    
    def push(self, *values):
        self.stack.extend(values)
    
    def pop(self, n=1):
        assert n >= 1
        t = tuple(self.stack[-n:])
        del self.stack[-n:]
        return t
    
    def run(self, code, records):
        self.code = code
        self.names = []
        del self.stack[:]
        self.to_find = 1
        try:
            for rec in records:
                getattr(self, rec.opname)(rec)
            return tuple(self.names)
        except StopIteration:
            return tuple(self.names)
        finally:
            del self.stack[:]
            self.names = None

    @action('STOP_CODE','NOP','PRINT_EXPR','PRINT_NEWLINE',
            'DELETE_NAME', 'DELETE_GLOBAL', 'SETUP_LOOP',
            'SETUP_EXCEPT', 'SETUP_FINALLY', 'DELETE_FAST',
            'SET_LINENO', 'HAVE_ARGUMENT')
    def do_nothing(self, rec):
        pass
    
    @action('POP_TOP')
    def pop_top(self, rec):
        if self.critical(TOS):
            raise InvalidVarnamesExpression
        self.pop(1)
    
    @action('ROT_TWO')
    def rot2(self, rec):
        a, b = self.pop(2)
        self.push(b, a)
    
    @action('ROT_THREE')
    def rot3(self, rec):
        a, b, c = self.pop(3)
        self.push(c, a, b)
        
    @action('ROT_FOUR')
    def rot4(self, rec):
        a, b, c, d = self.pop(4)
        self.push(d, a, b, c)
    
    @action('DUP_TOP')
    def dup_top(self, rec):
        if self.critical(TOS):
            raise InvalidVarnamesExpression
        self.push(self.stack[TOS])
    
    @action('BREAK_LOOP', 'CONTINUE_LOOP', 'JUMP_FORWARD',
            'LIST_APPEND', 'RETURN_VALUE', 'YIELD_VALUE',
            'IMPORT_STAR', 'EXEC_STMT', 'POP_BLOCK',
            'END_FINALLY', 'WITH_CLEANUP', 'POP_JUMP_IF_TRUE',
            'POP_JUMP_IF_FALSE',
            'JUMP_IF_TRUE_OR_POP', 'JUMP_IF_FALSE_OR_POP',
            'JUMP_ABSOLUTE', 'FOR_ITER', 'RAISE_VARARGS',
            'EXTENDED_ARG')
    def error(self, rec):
        raise InvalidVarnamesExpression

    @action('LOAD_CONST', 'LOAD_NAME', 'LOAD_LOCALS', 'BUILD_MAP',
            'LOAD_GLOBAL', 'LOAD_FAST', 'LOAD_CLOSURE',
            'LOAD_DEREF',)
    def push0(self, rec):
        self.push(item0)
    
    @action('SETUP_WITH')
    def push03(self, rec):
        self.push(item0, item0, item0)
    
    @action('UNARY_POSITIVE', 'UNARY_NEGATIVE', 'UNARY_NOT',
            'UNARY_CONVERT', 'UNARY_INVERT', 'GET_ITER',
            'SLICE+0',
            'LOAD_ATTR', 'IMPORT_FROM')
    def pop1push0(self, rec):
        if self.critical(TOS):
            raise InvalidVarnamesExpression
        self.pop(1)
        self.push(item0)

    @action('BINARY_POWER','BINARY_MULTIPLY','BINARY_DIVIDE',
            'BINARY_FLOOR_DIVIDE','BINARY_TRUE_DIVIDE','BINARY_MODULO',
            'BINARY_ADD','BINARY_SUBTRACT','BINARY_SUBSCR',
            'BINARY_LSHIFT','BINARY_RSHIFT','BINARY_AND',
            'BINARY_XOR','BINARY_OR','INPLACE_POWER',
            'INPLACE_MULTIPLY','INPLACE_DIVIDE','INPLACE_FLOOR_DIVIDE',
            'INPLACE_TRUE_DIVIDE','INPLACE_MODULO','INPLACE_ADD',
            'INPLACE_SUBTRACT','INPLACE_LSHIFT','INPLACE_RSHIFT',
            'INPLACE_AND','INPLACE_XOR','INPLACE_OR',
            'SLICE+1','SLICE+2', 'COMPARE_OP', 'IMPORT_NAME',
            )
    def pop2push0(self, rec):
        if self.critical(TOS, TOS1):
            raise InvalidVarnamesExpression
        self.pop(2)
        self.push(item0)    
    
    @action('SLICE+3', 'BUILD_CLASS')
    def pop3push0(self, rec):
        if self.critical(TOS, TOS1, TOS2):
            raise InvalidVarnamesExpression
        self.pop(3)
        self.push(item0)
    
    @action('STORE_SLICE+0', 'STORE_MAP')
    def pop2spec1(self, rec):
        if self.critical(TOS):
            raise InvalidVarnamesExpression
        elif self.critical(TOS1):
            raise VarnamesError("can't assign to slice or subscript")
        self.pop(2)
        
    @action('STORE_SLICE+1', 'STORE_SLICE+2', 'STORE_SUBSCR')
    def pop3spec2(self, rec):
        if self.critical(TOS, TOS1):
            raise InvalidVarnamesExpression
        elif self.critical(TOS2):
            raise VarnamesError("can't assign to slice or subscript")
        self.pop(3)
        
    @action('STORE_SLICE+3',)
    def pop4spec3(self, rec):
        if self.critical(TOS, TOS1, TOS2):
            raise InvalidVarnamesExpression
        elif self.critical(TOS3):
            raise VarnamesError("can't assign to slice")
        self.pop(4)
    
    @action('DELETE_SLICE+0', 'PRINT_ITEM', 'PRINT_NEWLINE_TO', 'DELETE_ATTR')
    def pop1(self, rec):
        if self.critical(TOS):
            raise InvalidVarnamesExpression
        self.pop(1)
    
    @action('DELETE_SLICE+1','DELETE_SLICE+2', 'DELETE_SUBSCR',
            'PRINT_ITEM_TO',)
    def pop2(self, rec):
        if self.critical(TOS, TOS1):
            raise InvalidVarnamesExpression
        self.pop(2)

    @action('DELETE_SLICE+3')
    def pop3(self, rec):
        if self.critical(TOS, TOS1, TOS2):
            raise InvalidVarnamesExpression
        self.pop(3)
        
    @action('MAKE_FUNCTION')
    def popmany1(self, rec):
        n = 1 + rec.value
        if self.critical(*range(-n,0)):
            raise InvalidVarnamesExpression
        self.pop(n)
        self.push(item0)
        
    @action('MAKE_CLOSURE')
    def popmany2(self, rec):
        n = 2 + rec.value
        if self.critical(*range(-n,0)):
            raise InvalidVarnamesExpression
        self.pop(n)
        self.push(item0)
    
    @action('CALL_FUNCTION')
    def call(self, rec):
        k, a = divmod(rec.oparg, 256)
        n = 2 * k + a + 1
        if self.critical(*range(-n, 0)):
            raise InvalidVarnamesExpression
        self.pop(n)
        self.push(item1 if rec.lasti else item0)

    @action('CALL_FUNCTION_VAR', 'CALL_FUNCTION_KW')
    def call(self, rec):
        k, a = divmod(rec.oparg, 256)
        n = 2 * k + a + 1 + 1
        if self.critical(*range(-n, 0)):
            raise InvalidVarnamesExpression
        self.pop(n)
        self.push(item1 if rec.lasti else item0)

    @action('CALL_FUNCTION_VAR_KW')
    def call(self, rec):
        k, a = divmod(rec.oparg, 256)
        n = 2 * k + a + 1 + 2
        if self.critical(*range(-n, 0)):
            raise InvalidVarnamesExpression
        self.pop(n)
        self.push(item1 if rec.lasti else item0)
   
    @action('BUILD_TUPLE', 'BUILD_LIST')
    def uple(self, rec):
        t = self.pop(rec.oparg)
        self.push(t)
        
    @action('BUILD_SLICE')
    def build_slice(self, rec):
        n = rec.oparg
        assert n in (2, 3)
        if self.critical(*range(-n, 0)):
            raise InvalidVarnamesExpression
        self.pop(n)
        self.push(item0)

    
    @action('STORE_NAME', 'STORE_GLOBAL')
    def store_name(self, rec):
        if self.critical(TOS):
            self.names.append(rec.value)
            self.to_find -= 1
            if self.to_find <= 0:
                raise StopIteration
        self.pop(1)
        
    @action('STORE_ATTR')
    def store_attr(self, rec):
        if self.critical(TOS):
            raise InvalidVarnamesExpression
        if self.critical(TOS1):
            self.names.append(self.code.co_names[rec.value])
            self.to_find -= 1
            if self.to_find <= 0:
                raise StopIteration
        self.pop(2)
        
    @action('STORE_FAST')
    def store_fast(self, rec):
        if self.critical(TOS1):
            self.names.append(self.code.co_varnames[rec.value])
            self.to_find -= 1
            if self.to_find <= 0:
                raise StopIteration
        self.pop(1)



    @action('UNPACK_SEQUENCE')
    def unpack(self, rec):
        if self.critical(TOS):
            x = self.pop()[0]
            if x is item1:
                t = (item2 for i in range(rec.oparg))
                self.to_find = rec.oparg
            else:
                raise InvalidVarnamesExpression
        else:
            x = self.pop()[0]
            t = tuple(x)[::-1]
            if len(t) != rec.oparg:
                # print(x, t, rec)
                raise ValueError(("Expected", rec.oparg, "values to unpack, got", len(t)))
        self.push(*t)
        
    @action('DUP_TOPX')
    def dup_topx(self, rec):
        count = rec.oparg
        assert 1 <= count <= 5
        t = tuple(range(-count, 0))
        if self.critical(*t):
            raise InvalidVarnamesExpression
        self.push(*self.stack[-count:])

for k, v in actiondict.items():
    setattr(Interpreter, k, v)

def varnames(verbose=False):
    code, L = dissect_calling_line(1)
    if verbose:
        for rec in L:
            print(rec)
    I = Interpreter()
    names = I.run(code, L)
    return names

if __name__ == '__main__':

    EXP = []
    def check(value):
        assert value == next(EXP[-1])

    from contextlib import contextmanager
    
    @contextmanager
    def expected(*values):
        EXP.append(iter(values))
        try:
            yield
        finally:
            del EXP[-1]

    EXPECTED = None

    def f():
        t = varnames(verbose=True)
        print(t)
        check(t)
        if len(t) == 1:
            return t[0]
        else:
            return t
    
    with expected(('t1',)):
        t1 = f()
    with expected(('x', 'y', 'z')):
        x,y,z = f()
    with expected(('t2',), ('t3',), ('t4',), ('t4',),):
        t2,v = f(), 1
        v, t3 = 1, f()
        v,v2,t4 = 1,2,f()
        v,v2,v3,t4 = 1,2,3,f()
    with expected(('t5',), ('t6',), ('t7',),):
        v,v2,v3,v4,t5 = 1,2,3,4,f()
        v,v2,v3,v4,v5,t6 = 1,2,3,4,5,f()
        v,v2,v3,v4,v5,v6,v7,v8,t7 = 1,2,3,4,5,6,7,8,f()
    with expected(('x', 'y', 'z'), ('x', 'y', 'z'), ('x', 'y', 'z'),):
        v,(x,y,z) = 1,f()
        v,v2,(x,y,z) = 1,2,f()
        v,v2,v3,(x,y,z) = 1,2,3,f()
    with expected(('t8',), ('x', 'y', 'z')):
        v,v2,t8,v3,v4 = 1,2,f(),3,4
        v,v2,(x,y,z),v3,v4 = 1,2,f(),3,4
        
    class A(object):
        def __init__(self, n, name='foo'):
            pass
    
    u = 1
    L = [i for i in range(5)]
    with expected(('x', 'y'), ('x', 'y'), ('x', 'z'), ('x', 'z'), ('b',)):
        a, b, (x, y), c = A(3, 'hello'), str(3 ** (5 +2)/1.41), f(), 21 ** 2
        a.eggs, (x, y), b, c = dir(), f(),str(3 ** (5 +u)/1.41),  21 ** (u+1)
        a.eggs,  b, c, (x, z) = dir(), str(3 ** (5 +u)/1.41),  21 ** (u+1), f()
        a.eggs,  b, c, (x, z)= dir(), L[1:5:2],  21 ** (u+1), f()
        c, b = 1, f()
        
