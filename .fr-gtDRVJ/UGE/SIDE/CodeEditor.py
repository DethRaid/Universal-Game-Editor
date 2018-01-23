# -*- coding: utf-8 -*-

from SIDE.common import *
#import ast

class Editor(QtGui.QAbstractScrollArea):
    """
    A custom Code Editor class using QPainter
    optimized to work with UMC Scripts.
    """
    
    def __init__(this, parent = None):
        QtGui.QAbstractScrollArea.__init__(this, parent)

        # colors
        this.headerColor        = QtGui.QColor(0xE0,0xE0,0xE0, 255)
        this.addressColor       = QtGui.QColor(  0,   0,   0, 255)
        this.textColor          = QtGui.QColor(  0,   0,   0, 255)
        this.cursorColor        = QtGui.QColor(  0,   0,   0, 255)
        this.selectionColor     = QtGui.QColor( 64,  64,  64,  64)
        this.indentColor        = QtGui.QColor(192, 192, 192, 128)
        this.eLineColor         = QtGui.QColor(255,   0,   0, 255)

        this.added_functions = []
        this.added_types = {}
        for t,v in ugeTypes.items(): this.added_types[t] = text2color(v)

        # --- syntax colors --- :
        # basics
        this.kwClr = QtGui.QColor(255, 128,   0, 255) # keywords
        this.FCClr = QtGui.QColor(  0,   0, 255, 255) # functions/classes
        this.biClr = QtGui.QColor(0xA0,   0, 0xA0, 255) # built-ins
        this.ugeReqClr = QtGui.QColor(128,   0,   0, 255) # required functions
        this.ugeRClr = QtGui.QColor(  0, 128, 128, 255) # registration functions
        this.ugeFClr = ugeFuncsClr # builtin functions
        this.ugeBFClr = ugeBFuncsClr # backend functions
        this.ugeCClr = ugeConstClr # backend constants
        this.strClr = QtGui.QColor(  0, 0xA0,   0, 255)
        this.numClr = QtGui.QColor(32, 32, 192, 255)
        # comments
        this.ccmClr = QtGui.QColor(160, 160, 160, 255) # code comment
        this.cmClr = QtGui.QColor(255,   0,   0, 255) # single-line comment
        # operators
        this.opClr = QtGui.QColor(128, 128, 128, 255)
        this.semiClr = QtGui.QColor(96, 96, 96, 160)
        this.dotClr = QtGui.QColor(64, 64, 128, 255)
        this.closingClr = QtGui.QColor(32, 32, 128, 255)
        

        this.keywords = "import|as|from|global|del|if|elif|else|and|or|not|pass|assert|while|for|in|continue|break|try|except|finally|raise|with|class|def|return|yield|exec|lambda|print".split('|')
        this.builtins = __builtins__.keys()
        this.befuncs = ugeFuncs.keys()
        this.beconsts = ugeConst.keys()
        this.rfuncs = sum(['ugeImport{0} ugeExport{0}'.format(scope[4:-7].capitalize()).split() for scope in scripts.scopes],[])
        this.required = "ugeScriptType|ugeScriptFormats|ugeScriptLibs".split('|')
        '''
        this.words = { c: [
            [ w for w in keywords if w.startswith(c) ],
            [ w for w in builtins if w.startswith(c) ],
            [ w for w in befuncs if w.startswith(c) ],
            [ w for w in beconsts if w.startswith(c) ]
            ] for c in '_ABCDEFGHIJKLMNOPQRSTUVWXZabcdefghijklmnopqrstuvwxyz' }
        '''
        this.highlighting = False

        this.numLines = 0
        this.addrlen = 0
        this.textWidth = 0
        this.indents = [0]

        this.cursorPos = 0
        this.drawcursor = True
        this.activeColumn = 0

        this.initcurpos = -1
        this.selections = [[0,0]]
        this.dselections = []

        this.code = ''
        this.lines = []
        this.fgcolors = []
        this.bgcolors = []
        this.errors = []
        
        this.file = ''
        this.unsaved = False

        """
        #intellisense:
        def _dummy_type(Type, this=this):
            this.moddict.update(Type.NS)
        def _dummy_fmts(Formats): pass
        def _dummy_libs(Libs): pass
        this.basemoddict = {
            'sys': sys,
            'ugeScriptType':    _dummy_type,
            'ugeScriptFormats': _dummy_fmts,
            'ugeScriptLibs':    _dummy_libs,
            'UGE_MODEL_SCRIPT':     backend.UGE_MODEL_SCRIPT,
            'UGE_ANIMATION_SCRIPT': backend.UGE_ANIMATION_SCRIPT,
            'UGE_IMAGE_SCRIPT':     backend.UGE_IMAGE_SCRIPT,
            'UGE_PALETTE_SCRIPT':   backend.UGE_PALETTE_SCRIPT,
            'UGE_PALLET_SCRIPT':    backend.UGE_PALLET_SCRIPT,
            'UGE_COMPRESSION_SCRIPT': backend.UGE_COMPRESSION_SCRIPT,
            'UGE_ARCHIVE_SCRIPT':   backend.UGE_ARCHIVE_SCRIPT
        }
        this.basemoddict.update(__builtins__) # not really needed
        this.moddict = {}
        """
        this.codebase = {}
        #this.compiled = None

        # quick QString access for drawing ASCII text
        this._Q_char_table = { chr(c): QtCore.QString(chr(c)) for c in range(256)}
        
        # default to a simple monospace font
        this.setFont(QtGui.QFont("Courier New", 8))

        this._painter = QtGui.QPainter()
        this._painting = False

        # noinspection PyUnusedLocal
        def cursorBlink(CE):
            while True:
                if not sys.modules['/SIDE_window/']: break
                CE.drawcursor = not CE.drawcursor
                CE.repaint()
                time.sleep(.5)
        #thread.start_new_thread( cursorBlink, (this,) )

    def repaint(this):
        if not this._painting: this.viewport().repaint()

    # noinspection PyAttributeOutsideInit
    def setFont(this, f):
        # recalculate all of our metrics/offsets
        fm = QtGui.QFontMetrics(f)
        this.font_width  = fm.width('X')
        this.font_height = fm.height()
        this.updateScrollbars()
        # TODO: assert that we are using a fixed font & find out if we care?
        QtGui.QAbstractScrollArea.setFont(this,f)
        return
    
    def updateScrollbars(this):
        max_rows = (this.height()/this.font_height)
        max_cols = (this.width()/this.font_width)-6
        this.verticalScrollBar().setMaximum( this.numLines-max_rows if this.numLines>max_rows else 0 )
        this.horizontalScrollBar().setMaximum( this.textWidth-max_cols if this.textWidth>max_cols else 0 )
        return

    '''
    on to the events:
    '''
    #input events:
 
    def pixelToOffset(this, x,y):
        """returns the exact character offset: this.code[offset]"""
        mouseX = (this.horizontalScrollBar().value()+(x/this.font_width))-(this.addrlen+3)
        mouseY = this.verticalScrollBar().value()+(y/this.font_height)
        if mouseY<len(this.lines): 
            maxX = len(this.lines[mouseY])-1
            return len(''.join(this.lines[:mouseY]))+( maxX if mouseX>maxX else mouseX if mouseX>0 else 0 )
        else: return len(this.code)-1

    def event(this, event):
        if event.type() == QtCore.QEvent.ToolTip:
            offset = this.pixelToOffset(event.x(),event.y())
            if offset in this.codebase: QtGui.QToolTip.showText( event.globalPos(), this.codebase[offset] )
            else: QtGui.QToolTip.hideText(); event.ignore()

            return True
        return super(Editor, this).event(event)

        
    def mouseMoveEvent(this, event) :
        x,y = event.x(),event.y()

        if x>(this.addrlen+3)*this.font_width:
            this.cursor().setShape(Qt.IBeamCursor)
        else:
            this.cursor().setShape(Qt.ArrowCursor)

        if this.highlighting:
            offset = this.pixelToOffset(x+(this.font_width/2), y)
            this.drawcursor = True

            this.cursorPos=offset
            this.selections[0] = [this.initcurpos,offset-1] if this.initcurpos<offset else [offset,this.initcurpos]
            
            # scroll
            mouseY = y/this.font_height
            maxY = this.height()/this.font_height
            vsb = this.verticalScrollBar(); vsbval = vsb.value()
            if mouseY>maxY: vsb.setValue(min(vsbval+(mouseY-maxY), vsb.maximum))
            elif mouseY<0: vsb.setValue(max(vsbval+mouseY,0))

            this.repaint()

    def mousePressEvent(this, event):
        if event.button() == Qt.LeftButton:
            x,y = event.x(),event.y()
            offset = this.pixelToOffset(x, y)
            
            this.cursorPos,this.initcurpos=offset,offset
            this.activeColumn = len(this.code[:offset].splitlines(True)[-1])
            this.highlighting = True
            this.selections[0] = [offset,offset]
            
            this.repaint()
 
    def mouseReleaseEvent(this, event) :
        if event.button() == Qt.LeftButton: this.highlighting = False

    # noinspection PyUnusedLocal
    def mouseDoubleClickEvent(this, event) :
        if event.button() == Qt.LeftButton:
            x,y = event.x(),event.y()
            '''
            if (x >= self.hexPos and x < self.textPos):
                #self.highlighting = True

                #self.selection_start = self.pixelToOffset(x, y)
                self.selection_end = self.selection_start
            '''
            this.repaint()
    
 
    def action_scrollTo( this, line) :
        mod = line-int((this.height()/this.font_height)*.5)
        this.verticalScrollBar().setValue(mod if mod>0 else 0)
        this.repaint()
        return

    def action_deselect(this) : this.selections = [[-1,-1]]; return
    def action_selectAll(this):
        area = [[0,len(this.code)]]
        if this.selections == area: this.deselect()
        else: this.selections = area
        return

    def action_cut(this):
        this.action_copy()
        S,E = this.selections[0]
        if S<E: this.code = this.code[:S]+this.code[E+1:]
        this.selections[0][1] = S; this.cursorPos = S
        this.update()
        this.repaint()
        
    def action_copy(this):
        S,E = this.selections[0]
        if S<E: sys.modules['/SIDE_clipboard/'].setText(this.code[S:E+1])
        
    def action_paste(this):
        S,E = this.selections[0]
        text = sys.modules['/SIDE_clipboard/'].text().__str__()
        this.code = this.code[:S]+text+this.code[E+1:] if S<E else this.code[:this.cursorPos]+text+this.code[this.cursorPos:]
        this.cursorPos+=len(text)
        this.update()
        this.repaint()

    def keyPressEvent(this, event) :
        key = event.key()
        mod = event.modifiers()

        #XPos = this.horizontalScrollBar().value()
        #YPos = this.verticalScrollBar().value()

        if mod & Qt.ControlModifier:
            
            if key == Qt.Key_A: this.action_selectAll(); this.repaint()
            
            elif key == Qt.Key_Home: this.action_scrollTo(0)
            elif key == Qt.Key_End: this.action_scrollTo(this.numLines)
            '''
            elif key == Qt.Key_Down:
                while True:
                    offset = self.verticalScrollBar().value() * (self.row_width * self.group_width)
                    if(offset + 1 < self.data.size) :
                        self.scrollTo(offset + 1)
                    #return so we don't pass on the key event
                    return
                
            elif key == Qt.Key_Up:
                while True:
                    offset = self.verticalScrollBar().value() * (self.row_width * self.group_width)
                    if(offset > 0) :
                        self.scrollTo(offset - 1)
                    #return so we don't pass on the key event
                    return
            '''
        else:
            #print key
            this.drawcursor = True

            R,C = len(this.code[:this.cursorPos].splitlines(True)),this.activeColumn #convert offset to row/column

            S,E = this.selections[0]
            if 31<key<128: # normal key press
                if S<E:
                    this.code = this.code[:S]+ str(event.text()) +this.code[E+1:]
                    this.selections[0][1] = S; this.cursorPos=S+1
                else:
                    this.code = this.code[:this.cursorPos]+ str(event.text()) +this.code[this.cursorPos:]
                    this.cursorPos+=1
                this.unsaved = True

            if key==16777220: # \n
                if S<E:
                    this.code = this.code[:S]+ '\n' +this.code[E+1:]
                    this.selections[0][1] = S; this.cursorPos=S+1
                else:
                    this.code = this.code[:this.cursorPos]+ '\n' +this.code[this.cursorPos:]
                    this.cursorPos+=1
                this.unsaved = True

            if key==16777219: # backspace
                if this.cursorPos > 0:
                    if S<E:
                        this.code = this.code[:S]+this.code[E+1:]
                        this.selections[0][1] = S; this.cursorPos=S
                    else:
                        this.code = this.code[:this.cursorPos-1]+this.code[this.cursorPos:]
                        this.cursorPos-=1
                    this.unsaved = True

            if key==16777223: # delete
                if this.cursorPos < len(this.code):
                    if S<E:
                        this.code = this.code[:S]+this.code[E+1:]
                        this.selections[0][1] = S; this.cursorPos=S
                    else:
                        this.code = this.code[:this.cursorPos]+this.code[this.cursorPos+1:]
                    this.unsaved = True

            #BUG: blank lines cause (c) to be 0, meaning the cursor goes above the line
            if key==16777235: # U
                this.cursorPos = len(''.join(this.lines[:R-2])) # position at start of line
                c = len(this.lines[R-2])-1
                this.cursorPos += C if c>C else c

            if key==16777237: # D
                last = this.cursorPos
                this.cursorPos = len(''.join(this.lines[:R])) # position at start of line
                c = len(this.lines[R])-1
                this.cursorPos += C if c>C else c
                if this.cursorPos==last: this.cursorPos += 1

            if key==16777234: this.cursorPos-=1 # L

            if key==16777236: this.cursorPos+=1 # R

            #NS = backend
            #'''
            '''
            try: exec "TempFile('blank')"+this.code in NS # process any new code
            except:
                import traceback
                type, val, tb = sys.exc_info()#;tb = traceback.extract_tb(i[2])[0]
                print
                traceback.print_exception(
	                type, val, tb#,
	                #limit = 2
	                #file = sys.stdout
	                )
                print
            #'''
            
            if this.unsaved:
                window = sys.modules['/SIDE_window/']
                window.saveAct.setEnabled(True)
                window.saveAct2.setEnabled(True)
                i = window.documents.currentIndex()
                window.documents.setTabText(i,this.file.split('/')[-1]+' *')
            #this.compiled = compile(this.code, '<string>', 'exec')
            this.update()

            this.action_deselect()


            #this.collect()
            #this.parse()
            this.repaint()


        #QtGui.QAbstractScrollArea.keyPressEvent(this,event)
        return

    def colorbg(this,word,start,end):
        if word not in this.added_types: this.added_types[word] = text2color(word)
        clr = this.added_types[word]
        while start<end: this.bgcolors[start].append(clr); start+=1

    def parse(this,data):
        """ does all in 1 run:
        - syntax highlighting
        - error checking
        #- indentation marking
        #- intellisense collection
        """
        
        # I got tired of sys, inspect, tokenize, re, regex, ast... they all can't do.
        # so I'm building a parser that CAN do:
        # - data offsets (rather than line/column)
        # - indentation level
        # - coding errors
        # - accurate intellisense

        # ast can't track if/elif/else and string-types (and possibly other objects) properly, and isn't friendly with exceptions
        # tokenize can't track indentation properly and again doesn't like exceptions (it's also harder to use and many times slower than ast)
        # sys and inspect are really the same, but the frames aren't exactly accurate when it comes to line numbers, and don't provide columns for some reason, and again, exceptions
        # re and regex are just too much of a headache to learn to use, though these can work perfectly with incomplete code

        # to add, this is the fastest thing I've used yet
        
        offset = 0
        size = len(this.code)
        
        numbers = '0123456789'
        binary = '01'
        octal = '01234567'
        hexidecimal = 'abcdef'; hexidecimal = numbers + hexidecimal + hexidecimal.upper()
        floating = '.'+numbers+'eEjJ'

        numrange = {'x':hexidecimal,'b':binary,'o':octal}
        
        alphabet = 'abcdefghijklmnopqrstuvwxyz'; alphabet = '_' + alphabet.upper() + alphabet
        wordrange = numbers + alphabet
        
        whitespace = ' \t\n'
        newline = '\\'
        whiteline = whitespace+newline

        operators = '<>,^*/%+-~&|!='
        linesep = ';'
        indent = ':'
        
        dot = '.'

        openings = '([{'
        closings = '}])'

        definitionbreaks = whiteline+openings+indent+linesep
        breaks = definitionbreaks+closings+operators+dot
        
        lc = '\n'

        ugeExtTypes = ['struct','array']
        ugeRawTypes = ['string']+ugeExtTypes+list('usfh')+['b%s'%t for t in 'usfh']
        
        #wordstart = None
        mod = 0
        
        while True: # using a while so skipping sections will be easier, and because they're much faster than for loops
            c = data[offset]
            #print offset, c, c == '#'
            
            if c == '#': # comment
                color = this.ccmClr if data[offset+1]=='#' else this.cmClr
                Len = data[offset:].find('\n')
                this.fgcolors[offset:offset+Len] = [ color ]*Len
                offset+=Len; lc = data[offset-1]; continue

            if c in 'rRuU':
                if data[offset+1:] in '"\'': this.fgcolors[offset] = this.strClr; offset+=1; lc = c; continue
            if c == "'": # sq or stq string
                ending = "'''" if data[offset:offset+3]=="'''" else "'"; endlen = len(ending)
                Len = data[offset+endlen:].find(ending)+(endlen*2)
                this.fgcolors[offset:offset+Len] = [ this.strClr ]*Len
                offset+=Len; lc = c; continue
            if c == '"': # dq or dtq string
                ending = '"""' if data[offset:offset+3]=='"""' else '"'; endlen = len(ending)
                Len = data[offset+endlen:].find(ending)+(endlen*2)
                this.fgcolors[offset:offset+Len] = [ this.strClr ]*Len
                offset+=Len; lc = c; continue
            
            if c in alphabet:
                if lc in breaks: # start of word
                    #keywords,builtins,befuncs,beconsts = this.words[c]
                    
                    wordstart = offset
                    while data[offset] in wordrange and offset<size: offset+=1 # find end of word

                    word = data[wordstart:offset]
                    wlen = len(word)

                    lc = word[-1]
                    
                    if word in ugeRawTypes:
                        wordend = offset

                        syntaxerror = False
                        while offset<size: # start of call "bu  ("
                            ch = data[offset]
                            if ch == '(': break
                            if ch not in whiteline: syntaxerror = True # validate whitespace ( including \ )
                            offset+=1 
                        
                        if syntaxerror: this.errors[wordend:offset] = ['Syntax Error']*(offset-wordend)
                        else:
                            offset+=1 # after '('
                            argstart = offset
                            while data[offset] in whiteline and offset<size: offset+=1
                            argtextstart = offset
                            
                            number = True
                            
                            syntaxerror = False
                            level = 0
                            while True: # find true end of arguments
                                ch = data[offset]
                                if ch == '(': level+=1
                                if ch == ')':
                                    if level==0: break
                                    else: level-=1
                                if ch not in whiteline and ch not in numbers: number = False
                                if offset == size: syntaxerror = True; break
                                offset += 1
                            argend = offset

                            # we need to backtrack to find the end of the text ( assuming 1 argument knowing there may be multiple )
                            offset-=1 # before ')'
                            while data[offset] in whiteline and offset<size: offset-=1
                            argtextend = offset

                            offset = argend+1
                            if syntaxerror: this.errors[argstart:offset] = ['Syntax Error']*(offset-argstart)
                            else:
                                arg = data[ argtextstart : argtextend ] # stripped of whitespace
                                arglen = len(arg)
                                
                                if word=='string': this.colorbg(word,wordstart,offset)
                                elif word in ugeExtTypes:
                                    pname = (wordstart+mod).__str__(); plen = len(pname)+1
                                    name='%s%s'%(word,pname)
                                    this.colorbg(name,wordstart,wordend)
                                    
                                    offset = argstart
                                    while data[offset] in whiteline and offset<size: offset+=1
                                    structstart = offset
                                    syntaxerror = False
                                    
                                    iss = word=='struct'
                                    ech = ')' if iss else ','
                                    level = int(iss)
                                    while True: # find true end of first argument
                                        ch = data[offset]
                                        if ch in openings: level+=1
                                        if ch in closings:
                                            if level==0: syntaxerror = True; break
                                            else: level-=1
                                        if ch == ech:
                                            if level==0: break
                                        if offset == size: syntaxerror = True; break
                                        offset += 1
                                    if syntaxerror: this.errors[structstart-iss:offset+iss] = ['Syntax Error']*((offset-structstart)+(iss*2))
                                    else:
                                        this.colorbg(name,structstart-iss,offset+iss) # full struct
                                    mod+=plen
                                    
                                elif arglen and number:
                                    offset+=1 # ')'
                                    this.colorbg('%s(%s)'%(word,arg),wordstart,offset) # full call
                                    
                                elif arglen>2:
                                    if arg[0] == '0':
                                        p = arg[1]
                                        if p in numrange:
                                            rng = numrange[p]

                                            advnum = True
                                            offset = argtextstart+2
                                            while offset<argtextend:
                                                # noinspection PyUnboundLocalVariable
                                                if ch not in rng: advnum = False; break
                                                offset += 1
                                                
                                            if advnum:
                                                offset+=1 # ')'
                                                this.colorbg('%s(%s)'%(word,eval(arg)),wordstart,offset) # full call
                                    
                                else: pass # undeterminable
                                
                            offset = wordend # parse everything in between
                        
                        continue

                    if word in this.added_types:
                        this.colorbg(word,wordstart,offset) # full call
                        continue
                    
                    if word in this.required: this.fgcolors[wordstart:offset] = [ this.ugeReqClr ]*wlen; continue
                    if word in this.beconsts: this.fgcolors[wordstart:offset] = [ this.ugeCClr ]*wlen; continue
                    if word in this.befuncs: this.fgcolors[wordstart:offset] = [ this.ugeBFClr if word.startswith('uge') else this.ugeFClr ]*wlen; continue
                    if word in this.builtins: this.fgcolors[wordstart:offset] = [ this.biClr ]*wlen; continue
                            
                    if word in this.keywords:
                        this.fgcolors[wordstart:offset] = [ this.kwClr ]*wlen
                    
                        if word in ('def','class'):
                            while data[offset] in whiteline and offset<size: offset+=1
                            namestart = offset
                            while data[offset] in wordrange and offset<size: offset+=1
                            name = data[namestart:offset]
                            if name[0] in numbers or name in this.keywords: this.errors[namestart:offset] = ['Syntax Error']*(offset-namestart)
                            else: this.fgcolors[namestart:offset] = [ this.ugeRClr if name in this.rfuncs else this.FCClr ]*(offset-namestart)
                            
                            lc = data[offset-1]
                        continue
                    continue

            if c == ';': this.fgcolors[offset] = this.semiClr; offset+=1; lc = c; continue
            if c == '\\': this.fgcolors[offset] = this.semiClr; offset+=1; lc = c; continue
            if c in operators: this.fgcolors[offset] = this.opClr; offset+=1; lc = c; continue
            if c in openings+closings: this.fgcolors[offset] = this.closingClr; offset+=1; lc = c; continue
            
            # TODO: negative numbers (not conflicting with operators)
            if c in numbers:
                if c == '.' and data[offset+1] not in floating and data[offset-1] not in floating: this.fgcolors[offset] = this.dotClr; offset+=1; lc = c; continue
                p = data[offset+1]; numstart = offset; rng = numrange[p] if c == '0' and p in numrange else floating
                if p in numrange: offset+=2
                while data[offset] in rng and offset<size: offset+=1
                this.fgcolors[numstart:offset] = [ this.numClr ]*(offset-numstart); lc = data[offset-1]; continue
                
            
            offset+=1
            lc = c
                
            if offset >= size: break
            
        

    """
    def collect(this): #intellisense
        this.codebase = {}
        for toktype, toktext, (srow, scol), (erow, ecol), line in this.tokens:
            if toktype == tokenize.NAME:
                if toktext in this.keywords: continue
                '''
                if toktext in this.moddict:
                    print toktext, ':', this.moddict[toktext]
                else:
                    print toktext
                #'''
                offset = len(''.join(this.lines[:srow-1]))+scol
                for i in xrange(toktext.__len__()):
                    if toktext in this.moddict:
                        Type = this.moddict[toktext]
                        this.codebase[offset+i] = str(Type)
                        '''
                        if Type.__class__ in this.collect.__class__: Type = Type.__code__
                        if Type.__class__ in this.collect.__code__.__class__:
                        '''
                    else:
                        this.codebase[offset+i] = "No Data"
    """

    # Tcll - most of this is still ported from my works on the original QHexEdit widget.
    # noinspection PyUnusedLocal
    def paintEvent(this, event):
 
        painter = this._painter
        this._painting = True
        painter.begin(this.viewport())

        TextStartX = this.horizontalScrollBar().value() # in columns
        TextStartY = this.verticalScrollBar().value() # in lines
        widget_height = this.height() # in pixels
        widget_width = this.width() # in pixels

        painter.translate( -TextStartX * this.font_width, -TextStartY * this.font_height ) # set scroll

        TextEndX = TextStartX+(widget_width/this.font_width)
        if TextEndX>this.textWidth: TextEndX = this.textWidth

        TextEndY = TextStartY+1+(widget_height/this.font_height) # improve speed by only drawing what's shown
        if TextEndY>this.numLines: TextEndY=this.numLines # make sure the widget height doesn't cause an index error
        
        painter.fillRect(TextStartX*this.font_width, 0,
            int((this.addrlen+0.5)*this.font_width),
            (TextStartY*this.font_height)+widget_height,
            this.headerColor)

        
        xstart = this.addrlen+3+TextStartX
        xpos = xstart

        ln = TextStartY
        x2,y1,y2 = this.font_width, ln*this.font_height, this.font_height

        drawln = True
        allspace = True
        
        S,E = this.selections[0]
        
        for o in xrange( len(''.join(this.lines[:TextStartY])),
                len(this.code) if TextEndY>len(this.lines) else len(''.join(this.lines[:TextEndY])) ):
            c=this.code[o]
            x1 = xpos*this.font_width

            if drawln:
                dln = ln+1 # line number
                painter.setPen( this.addressColor )
                painter.drawText( TextStartX*x2, y1, 8*x2, y2, Qt.AlignTop,
                    '%s%s'%( ' '*(this.addrlen-len(dln.__str__())), dln.__str__()) )
                drawln = False
            
            # data-type bg color(s)
            bgcs = this.bgcolors[o]
            for bgci in xrange(len(bgcs)): painter.fillRect( x1,y1,x2,y2, bgcs[bgci] )
            if ln+1 in this.dselections: painter.fillRect( x1,y1,x2,y2, dSelClr )
            
            # simple indent guide (TODO: make advanced)
            if allspace and c!=' ': allspace=False
            if allspace and xpos>xstart and (xpos-xstart)%4==0:
                painter.setPen( this.indentColor ); painter.drawLine(x1,y1,x1,y1+y2)
                
            if this.errors[o]:
                painter.setPen( this.eLineColor )
                for es in xrange(x1,x1+x2): painter.drawPoint(es, y1+y2 + ((es&3)-(es&2))-(2*((es&3)==3)))

            if S<E and S<=o<=E: painter.fillRect( x1,y1,x2,y2, this.selectionColor)

            painter.setPen( this.fgcolors[o] )
            painter.drawText( x1,y1,x2,y2, Qt.AlignTop, c)
                
            if o==this.cursorPos and this.drawcursor:
                painter.setPen( this.cursorColor ); painter.drawLine(x1,y1,x1,y1+y2)

            xpos+=1
            if c=='\n': ln+=1; y1=ln*y2; drawln=True; xpos=xstart; allspace=True
            o+=1

        painter.end()
        this._painting = False
        this.updateScrollbars()
        '''
        time.sleep(0.5)
        this.drawcursor = not this.drawcursor
        this.repaint()
        '''
        return
    
    def update(this):
        this.lines = this.code.splitlines(True)
        this.numLines = len(this.lines) # set defaults
        this.addrlen = len(this.numLines.__str__())+3
        this.textWidth = max([len(l) for l in this.lines])
        this.indents = [0]*(this.numLines+1)
        this.fgcolors = [QtGui.QColor(0, 0, 0, 255)]*len(this.code)
        this.bgcolors = [ list() for i in this.code ]
        this.errors = [None]*len(this.code)
        this.parse(this.code)

    def setText(this, text=''):
        this.code = text
        this.update()
        this.action_deselect()
        this.updateScrollbars()
        this.unsaved = False
        return
        
