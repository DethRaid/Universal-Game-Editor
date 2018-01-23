#!/usr/bin/env python

# Tcll - broke python3 support and slightly improved performance and usability for python2:
# - changed record to it's own class and re-implemented record_disassemble() directly into Interpreter.run() (keeping debugging verbosity)
# - removed varnames() and dissect_calling_line() for a direct interface in tracer() (similar to my interface in SIDE.common)
# - replaced f() with a C() class instance and wrapped the call with tracer() similar to my interface
# - removed varname-specific errors (execution no longer stopps as we want to return what we find, if anything)

# Tcll - in my experiences, I've learned not to rely on poor-quality 3rd-party modules to get the job done.
# the only exceptions here would be py3 support and high-performance modules (not numpy, I've gotten more performance out of list objects than numpy arrays)

"""french comment removed (VS2010 destroys this file)"""
import sys, dis

__version__ = '0.2.0'

# french comment removed (VS2010 destroys this file)

actiondict = {}

def action(*opnames):
    def decorator(func):
        for name in opnames: actiondict[name] = func
        return func
    return decorator

item0 = object()
item1 = object()
item2 = object()
TOS = -1
TOS1 = -2
TOS2 = -3
TOS3 = -4

# nice pointer on opcodes: http://unpyc.sourceforge.net/Opcodes.html

class Interpreter(object):
    def __init__(self):
        self.stack = []
        self.names = None
        
    def critical(self, *index):
        l = len(self.stack)
        for i in index:
            if -l-1<i<l and self.stack[i] in (item1, item2): return True
    
    def push(self, *values):
        self.stack.extend(values)
    
    def pop(self, n=1):
        #assert n > 0
        if n<1: return
        t = self.stack[-n:]
        del self.stack[-n:]
        return t
    
    def run(self, code, lasti=-1, current_line=False, verbose=False):
        order = "line lasti label index op opname oparg has value".split()
        record = type('record',(object,),{k:None for k in order})
        records = []
        
        """Disassemble the code object."""
        co = code.co_code
        labels = dis.findlabels(co)
        L = list(dis.findlinestarts(code))
        linestarts = dict(L)
        if current_line:
            if lasti < 0:
                raise ValueError("Bytecode index expected (lasti).")
            M = [p for p in L if p[0]<=lasti]
            i,n = M[-1][0], ( L[len(M)][0] if len(M) < len(L) else len(co) )
        else: i,n = 0,len(co)
        
        free = None
        while i < n:
            rec = record()
            
            if i in linestarts: rec.line = linestarts[i]
            rec.lasti = i==lasti
            rec.label = i in labels
            rec.index = i
            rec.op = op = ord(co[i])
            rec.opname = dis.opname[op]
            i = i+1
            if op >= dis.HAVE_ARGUMENT:
                oparg = ord(co[i]) + ord(co[i+1])*256; i = i+2
                if op == dis.EXTENDED_ARG: extended_arg = oparg*65536L
                rec.oparg = oparg
                if op in dis.hasconst:      rec.has, rec.value = 'const',   code.co_consts[oparg]
                elif op in dis.hasname:     rec.has, rec.value = 'name',    code.co_names[oparg]
                elif op in dis.hasjrel:     rec.has, rec.value = 'jrel',    i+oparg
                elif op in dis.haslocal:    rec.has, rec.value = 'local',   code.co_varnames[oparg]
                elif op in dis.hascompare:  rec.has, rec.value = 'compare', dis.cmp_op[oparg]
                elif op in dis.hasfree:     rec.has, rec.value = 'free',    (code.co_cellvars + code.co_freevars)[oparg] if free is None else free[oparg]

            records.append(rec); rec = None
        
        
        if verbose:
            def strattr(d,k): item = getattr(d,k); return "'%s'"%item if item.__class__==str else item # adds '' for strings
            print '\n'.join('record(%s )'%','.join(' %s=%s'%(k,strattr(rec,k)) for k in order) for rec in records)
        
        
        self.code = code
        self.names = []
        del self.stack[:]
        self.to_find = 1
        try:
            for rec in records: getattr(self, rec.opname)(rec)
            return self.names
        except StopIteration:
            return self.names
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
        if self.critical(TOS): return
        #    raise InvalidExpression
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
        if self.critical(TOS): return
        #    raise InvalidExpression
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
        return #raise InvalidExpression

    @action('LOAD_CONST')
    def push0(self, rec):
        #if not self.critical(TOS): self.names.append(rec.value)
        self.push(item0)

    @action('LOAD_NAME', 'LOAD_LOCALS', 'BUILD_MAP',
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
        if self.critical(TOS): return
        #    raise InvalidExpression
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
        if self.critical(TOS, TOS1): return
        #    raise InvalidExpression
        self.pop(2)
        self.push(item0)    
    
    @action('SLICE+3', 'BUILD_CLASS')
    def pop3push0(self, rec):
        if self.critical(TOS, TOS1, TOS2): return
        #    raise InvalidExpression
        self.pop(3)
        self.push(item0)
    
    @action('STORE_SLICE+0', 'STORE_MAP')
    def pop2spec1(self, rec):
        if self.critical(TOS): return
        #    raise InvalidExpression
        elif self.critical(TOS1): return
        #    raise Error("can't assign to slice or subscript")
        self.pop(2)
        
    @action('STORE_SLICE+1', 'STORE_SLICE+2', 'STORE_SUBSCR')
    def pop3spec2(self, rec):
        if self.critical(TOS, TOS1): return
        #    raise InvalidExpression
        elif self.critical(TOS2): return
        #    raise Error("can't assign to slice or subscript")
        self.pop(3)
        
    @action('STORE_SLICE+3',)
    def pop4spec3(self, rec):
        if self.critical(TOS, TOS1, TOS2): return
        #    raise InvalidExpression
        elif self.critical(TOS3): return
        #    raise Error("can't assign to slice")
        self.pop(4)
    
    @action('DELETE_SLICE+0', 'PRINT_ITEM', 'PRINT_NEWLINE_TO', 'DELETE_ATTR')
    def pop1(self, rec):
        if self.critical(TOS): return
        #    raise InvalidExpression
        self.pop(1)
    
    @action('DELETE_SLICE+1','DELETE_SLICE+2', 'DELETE_SUBSCR',
            'PRINT_ITEM_TO',)
    def pop2(self, rec):
        if self.critical(TOS, TOS1): return
        #    raise InvalidExpression
        self.pop(2)

    @action('DELETE_SLICE+3')
    def pop3(self, rec):
        if self.critical(TOS, TOS1, TOS2): return
        #    raise InvalidExpression
        self.pop(3)
        
    @action('MAKE_FUNCTION')
    def popmany1(self, rec):
        n = 1 + rec.value if rec.value.__class__==int else 0
        if self.critical(*range(-n,0)): return
        #    raise InvalidExpression
        self.pop(n)
        self.push(item0)
        
    @action('MAKE_CLOSURE')
    def popmany2(self, rec):
        n = 2 + rec.value if rec.value.__class__==int else 0
        if self.critical(*range(-n,0)): return
        #    raise InvalidExpression
        self.pop(n)
        self.push(item0)
    
    @action('CALL_FUNCTION')
    def call(self, rec):
        k, a = divmod(rec.oparg, 256)
        n = 2 * k + a + 1
        if self.critical(*range(-n, 0)): return
        #    raise InvalidExpression
        self.pop(n)
        self.push(item1 if rec.lasti else item0)

    @action('CALL_FUNCTION_VAR', 'CALL_FUNCTION_KW')
    def call(self, rec):
        k, a = divmod(rec.oparg, 256)
        n = 2 * k + a + 1 + 1
        if self.critical(*range(-n, 0)): return
        #    raise InvalidExpression
        self.pop(n)
        self.push(item1 if rec.lasti else item0)

    @action('CALL_FUNCTION_VAR_KW')
    def call(self, rec):
        k, a = divmod(rec.oparg, 256)
        n = 2 * k + a + 1 + 2
        if self.critical(*range(-n, 0)): return
        #    raise InvalidExpression
        self.pop(n)
        self.push(item1 if rec.lasti else item0)
   
    @action('BUILD_TUPLE', 'BUILD_LIST')
    def uple(self, rec):
        if rec.oparg:
            t = self.pop(rec.oparg)
            self.push(t)
        
    @action('BUILD_SLICE')
    def build_slice(self, rec):
        n = rec.oparg
        assert n in (2, 3)
        if self.critical(*range(-n, 0)): return
        #    raise InvalidExpression
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
        if self.critical(TOS): return
        #    raise InvalidExpression
        if self.critical(TOS1):
            self.names.append(rec.value if rec.value.__class__==str else self.code.co_names[rec.value])
            self.to_find -= 1
            if self.to_find <= 0:
                raise StopIteration
        self.pop(2)
        
    @action('STORE_FAST')
    def store_fast(self, rec):
        if self.critical(TOS1):
            self.names.append(rec.value if rec.value.__class__==str else self.code.co_varnames[rec.value])
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
            else: return
            #    raise InvalidExpression
        else:
            x = self.pop()[0]
            if x.__class__() == list: t = x[::-1]
            else: return
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
            raise InvalidExpression
        self.push(*self.stack[-count:])

for k, v in actiondict.items():
    setattr(Interpreter, k, v)

if __name__ == '__main__':
    def tracer(func):
        def wrapper( *args, **kwargs ):
            
            frame = sys._getframe(1)
            try: code, lasti, ln = frame.f_code, frame.f_lasti, frame.f_lineno
            finally: del frame

            I = Interpreter()
            t = I.run( code, lasti=lasti, current_line=True, verbose=True )
            
            print(t)
            if len(t) == 1: return t[0]
            else: return t
            
        return wrapper
        
    class C(object):
        def __init__(this): pass
        @tracer
        def __call__(this,offset=0,label = ''): pass

    f = C()
    
    t1 = f(label=' -- test')
    
    x,y,z = f()
    '''
    t2,v = f(), 1
    v, t3 = 1, f()
    v,v2,t4 = 1,2,f()
    v,v2,v3,t4 = 1,2,3,f()

    v,v2,v3,v4,t5 = 1,2,3,4,f()
    v,v2,v3,v4,v5,t6 = 1,2,3,4,5,f()
    v,v2,v3,v4,v5,v6,v7,v8,t7 = 1,2,3,4,5,6,7,8,f()

    v,(x,y,z) = 1,f()
    v,v2,(x,y,z) = 1,2,f()
    v,v2,v3,(x,y,z) = 1,2,3,f()

    v,v2,t8,v3,v4 = 1,2,f(),3,4
    v,v2,(x,y,z),v3,v4 = 1,2,f(),3,4
        
    class A(object):
        def __init__(self, n, name='foo'):
            pass
    
    u = 1
    L = [i for i in range(5)]

    a, b, (x, y), c = A(3, 'hello'), str(3 ** (5 +2)/1.41), f(), 21 ** 2
    a.eggs, (x, y), b, c = dir(), f(),str(3 ** (5 +u)/1.41),  21 ** (u+1)
    a.eggs,  b, c, (x, z) = dir(), str(3 ** (5 +u)/1.41),  21 ** (u+1), f()
    a.eggs,  b, c, (x, z)= dir(), L[1:5:2],  21 ** (u+1), f()
    c, b = 1, f()
    
    # f() doesn't HAVE to have a var
    f()

    l = [f()]
    '''
    # this is rather a standard:
    result = C()( offset=f( label=' -- test' ) )
    result = C()( # offset not found
        offset=f( label=' -- test' ) )
    # should print:
    # ['offset']
    # ['result']
    
    # think of C as being any of these:
    
    # - struct(     R=bu8, G=bu8, B=bu8, A=bu8  )( offset=bu32() )
    # - array(      bf32, count=3               )( offset=bu32() )
    # - string(                                 )( offset=bu32() )
    # - bf(         4                           )( offset=bu32() )
    
    # where f is obviousely bu32()
