
from SIDE.common import *

class HexView(QtGui.QAbstractScrollArea):
    '''
    A custom Hex Editor class usng QPainter
    optimized to work with UMC (read only) file data.
    '''

    # for the non-UMC developer,
    # this class can be customized (through extensive work)
    # to fit your API as a QHexEdit widget.

    # Pre-Definitions:

    highlightingNone=0
    highlightingHex=1
    highlightingText=2

    # quick QString display list for drawing ASCII text
    _printable = range(32,0x7F)
    _ansi = list(range(0x82, 0x8D))+list(range(0x91, 0x9D))+list(range(0x9F, 256))
    _control = [9,10,0x0D]

    def __init__(this, parent = None):
        QtGui.QAbstractScrollArea.__init__(this, parent)
        
        # colors
        this.headerColor        = QtGui.QColor(0xE0,0xE0,0xE0, 255)
        this.addressColor       = QtGui.QColor(  0,   0,   0, 255)
        this.textColor          = QtGui.QColor(  0,   0,   0, 255)
        
        this.non_printable_text = QtGui.QColor(255,   0,   0, 255)
        this.ansi_text          = QtGui.QColor(  0,   0, 128, 255)
        this.control_text       = QtGui.QColor(  0, 128,   0, 255)

        selectionColor          = QtGui.QColor(  0,   0,   0,  63)
        this.rowColor           = QtGui.QColor(  0,   0,   0,  19)
        this.colColor           = QtGui.QColor(  0,   0,   0,  11)
        # makes gray rows stand out more:
        this.colColorDark       = QtGui.QColor(  0,   0,   0,  15)
        
        this.highlighting = 0

        this.group_width = 1
        this.row_width = 16

        this.unprintable_char = QtCore.QString('.')

        this.show_Rows = False

        this.selection_start = -1
        this.selection_end = -1

        this.selections = []

        this.hexAddrLen = 0
        this.intAddrLen = 0
        this.hexPos = 0
        this.textPos = 0

        this.data = MEM()


        this._Q_char_table = { c: QtCore.QString(chr(c)) for c in range(256)}
        #this.data_highlights = []
        
        # default to a simple monospace font
        this.setFont(QtGui.QFont("Courier New", 8))

        this._painter = QtGui.QPainter()

        #this.repaint = this.viewport().repaint
        return

    def repaint(this): this.viewport().repaint(); return

    def setFont(this, f):
        # recalculate all of our metrics/offsets
        fm = QtGui.QFontMetrics(f)
        this.font_width  = fm.width('X')
        this.font_height = fm.height()
        #this.updateScrollbar()
        # TODO: assert that we are using a fixed font & find out if we care?
        QtGui.QAbstractScrollArea.setFont(this,f)
        return
    
    def updateScrollbar(this):
        this.verticalScrollBar().setMaximum( len(this.data)/this.row_width+bool(len(this.data)%this.row_width) )
        return

    '''
    on to the events:
    '''

    # most of this is still ported from my works on the original QHexEdit widget.
    def paintEvent(this, event) :
        painter = this._painter
        painter.begin(this.viewport())

        #grayRow = False

        W = this.font_width # rectangle width
        H = this.font_height # rectangle height
 
        startLine = this.verticalScrollBar().value()
        widget_height = this.height() # in pixels
        widget_width = this.width() # in pixels

        sly = startLine*H
        
        painter.translate(0, -sly) # set scroll position

        endLine = startLine+1+(widget_height/H) # improve speed by only drawing what's shown
        if endLine*this.row_width>len(this.data): endLine = len(this.data)/this.row_width+bool(len(this.data)%this.row_width)
        # ^ make sure the widget height doesn't cause an index error
            
        pxHexPos = this.hexPos*W
        #draw the address line
        painter.fillRect(0, sly, widget_width, H, this.headerColor )
        painter.fillRect(0, (startLine+1)*H, pxHexPos-(W+(W/2)), (startLine*H)+widget_height, this.headerColor)

        for line in range(startLine,endLine):
            Y = (line+1)*H

            indexstart = line*this.row_width
            indexend = len(this.data)-indexstart
            if indexend>this.row_width: indexend = indexstart+this.row_width 
            row_data = this.data[ indexstart:indexend ]
            
            # address
            addr = line*16
            painter.setPen(this.addressColor)
            painter.drawText(0, Y, pxHexPos, H, Qt.AlignTop, (('  %s0%ii:%s0%ix'%('%',this.intAddrLen,'%',this.hexAddrLen))%(addr,addr)).upper() )
            
            # Row highlight
            #if grayRow: painter.fillRect( pxHexPos, Y, (this.font_width*((this.row_width*3)-1)), H, this.rowColor )
            
            for lineIndex,c in enumerate(row_data):
                o = (line*this.row_width)+lineIndex
                
                # change FG color here (after first byte)
                if c in this._printable: painter.setPen(this.textColor)
                elif c in this._ansi:    painter.setPen(this.ansi_text)
                elif c in this._control: painter.setPen(this.control_text)
                else:                    painter.setPen(this.non_printable_text)
                
                # position
                hX = (this.hexPos + (lineIndex * 3))
                if lineIndex > 3: hX+=1
                if lineIndex > 7: hX+=2
                if lineIndex > 11: hX+=1
                hX*=W
                tX = (this.textPos + lineIndex) * W

                # highlight coords
                p,s = (W, 3) if lineIndex else (0, 2)
                if lineIndex==4 or lineIndex==12: p+=W; s+=1
                if lineIndex==8: p+=W+W; s+=2
                
                # Data-Type highlights
                for dt in this.data._types[o]:
                    split = o==dt.__addr__; color=QtGui.QColor(dt.__color__); color.setAlpha(64)
                    painter.fillRect( hX-(0 if split else p), Y, W*(2 if split else s), H, color )
                    painter.fillRect( tX, Y, W, H, color )

                # Dynamic Selection highlight
                for dss,dse in this.selections:
                    if dss<=o<=dse:
                        sp,ss = (p,s) if dss<=(o-1)<=dse else (0,2)
                        painter.fillRect( hX-sp, Y, W*ss, H, dSelClr )
                        painter.fillRect( tX, Y, W, H, dSelClr )

                # Selection highlight
                if this.selection_start>=0:
                    if this.selection_start<=o<=this.selection_end:
                        sp,ss = (p,s) if this.selection_start<=(o-1)<=this.selection_end else (0,2)
                        painter.fillRect( hX-sp, Y, W*ss, H, this.selectionColor )
                        painter.fillRect( tX, Y, W, H, this.selectionColor )
                '''
                # Column highlight
                if lineIndex in range(4,8)+range(12,16):
                    painter.fillRect( 
                        hX-(0 if lineIndex in (4,12) else W), Y, 
                        W*(2 if lineIndex in (4,12) else 3), H, 
                        this.colColorDark if grayRow  else this.colColor )
                '''
                #Draw Byte
                painter.drawText( hX, Y, W*2, H, Qt.AlignTop, ("%02x"%c).upper() )
                painter.drawText( tX, Y, W, H, Qt.AlignTop, this._Q_char_table[c] )
                if line == startLine:
                    painter.setPen(this.addressColor)
                    painter.drawText( hX, sly, W*2, H, Qt.AlignTop, ("%02x"%lineIndex).upper() )
                    painter.drawText( tX, sly, W, H, Qt.AlignTop, ("%01x"%lineIndex).upper() )
         
            if this.show_Rows: grayRow = not grayRow
            else: grayRow = False

        painter.end()
 
        return

    def toggleRows(this): this.show_Rows = not this.show_Rows; this.repaint()

    #input events:
       
    def pixelToByte(self, x, y) : 
        word = -1
        if self.highlighting == self.highlightingHex:
            x = max(self.hexPos, min(x, self.textPos))-self.hexPos
    
            # scale x/y down to character from pixels
            if (x % self.font_width >= self.font_width / 2 ):
                x = x / self.font_width+1
            else:
                x = x / self.font_width

            y /= self.font_height
            x /= ((self.group_width * 2) + 1) # make x relative to rendering mode of the bytes

        elif self.highlighting == self.highlightingText:
            x = max(self.textPos, min(x, self.textPos + (self.row_width*self.font_width)))-self.textPos

            # scale x/y down to character from pixels
            x /= self.font_width
            y /= self.font_height
            
            x /= self.group_width # make x relative to rendering mode of the bytes

        else:
            #Q_ASSERT(0)
            pass
    
        #// starting offset in bytes
        start_offset = self.verticalScrollBar().value()*(self.row_width*self.group_width)

        #// convert byte offset to word offset, rounding up
        #start_offset /= self.group_width

        word = ((y * self.row_width) + x) + start_offset
    
        return word
 
    def isInViewableArea(self, index): 
        '''
        returns true if the word at the given index is in the viewable area
        '''
        firstViewableWord = self.verticalScrollBar().value() * self.row_width
        viewableLines     = self.viewport().height() / self.font_height
        viewableWords     = viewableLines * self.row_width
        lastViewableWord  = firstViewableWord + viewableWords
        return index >= firstViewableWord and index < lastViewableWord
        
    def mouseDoubleClickEvent(self, event) :
        if(event.button() == Qt.LeftButton) :
            x = event.x(); y = event.y()

            if (x >= self.hexPos and x < self.textPos):
                self.highlighting = self.highlightingHex

                #self.selection_start = self.pixelToByte(x, y)
                #self.selection_end = self.selection_start

                self.repaint()

        return
 
 
    def mousePressEvent(self, event) :
        if(event.button() == Qt.LeftButton) :
            x = event.x(); y = event.y()
 
            self.highlighting = self.highlightingHex if x < self.textPos else self.highlightingText
            
            #offset = self.pixelToByte(x, y)
            #self.selection_start, self.selection_end = (offset,offset) if offset < self.data.size else (-1,-1)
            
            self.repaint()

        return
        
    def mouseMoveEvent(self, event) :
        if(self.highlighting != self.highlightingNone) :
            x = event.x(); y = event.y()
 
            #offset = self.pixelToByte(x, y)

            """
            if(self.selection_start != -1) :
                self.selection_end = (self.row_width-self.selection_start)+self.selection_start if offset == -1 else offset
                if(self.selection_end < 0): self.selection_end = 0
                '''
                if(not self.isInViewableArea(self.selection_end)) :
                    #TODO: scroll to an appropriate location
                    pass
                '''
            """
            self.repaint()

        return
 
    def mouseReleaseEvent(self, event) :
        if(event.button() == Qt.LeftButton): self.highlighting = self.highlightingNone
        return
 
    def scrollTo( this, line):
        mod = line-int((this.height()/this.font_height)*.5)
        this.verticalScrollBar().setValue(mod if mod>0 else 0)
        this.repaint()

    def selectAll(self):
        self.selection_start = 0
        self.selection_end   = self.data.__len__()
        self.deselect() # ^later
        return

    def deselect(self):
        self.selection_start = -1
        self.selection_end   = -1
        return

    def keyPressEvent(self, event) :
        if (event.modifiers() & Qt.ControlModifier) :
            key = event.key()
            
            if key == Qt.Key_A: self.selectAll(); self.repaint()
            
            elif key == Qt.Key_Home: self.scrollTo(0)
            elif key == Qt.Key_End: self.scrollTo(self.data.__len__() - (self.row_width * self.group_width))
            
            elif key == Qt.Key_Down:
                while True:
                    offset = self.verticalScrollBar().value() * (self.row_width * self.group_width)
                    if(offset + 1 < self.data.__len__()) :
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
        QtGui.QAbstractScrollArea.keyPressEvent(self,event)
        return

    def setData(this, data) :
        this.data = data
        this.data_highlights = [list() for i in xrange(len(data))]
            
        #set defaults
        this.hexAddrLen = len(hex(len(this.data)))-2
        this.intAddrLen = len('%i'%(len(this.data)))
        this.hexPos = this.intAddrLen+this.hexAddrLen+5
        this.textPos = this.hexPos+(this.row_width*3)+6
        
        this.deselect()
        this.updateScrollbar()
        
        #this.repaint()
        return
        
