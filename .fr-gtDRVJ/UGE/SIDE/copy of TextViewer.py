
from SIDE.common import *
#from API.backend import FILE

class TextView(QtGui.QAbstractScrollArea):
    '''
    A custom Hex Editor class usng QPainter
    optimized to work with UMC (read only) file data.
    '''

    # for the non-UMC developer,
    # this class can be customized (through extensive work)
    # to fit your API as a QHexEdit widget.

    _printable = range(32,0x7F)
    _ansi = range(0x82, 0x8D)+range(0x91, 0x9D)+range(0x9F, 256)
    _control = [9,10,0x0D]

    # colors
    addressColor        = QtGui.QColor(  0,   0, 128, 255)
    textColor           = QtGui.QColor(  0,   0,   0, 255)
    
    non_printable_text  = QtGui.QColor(255,   0,   0, 255)
    ansi_text           = QtGui.QColor(  0,   0, 128, 255)
    control_text        = QtGui.QColor(  0, 128,   0, 255)

    selectionColor      = QtGui.QColor(  0,   0,   0,  63)
    rowColor            = QtGui.QColor(  0,   0,   0,  19)
    colColor            = QtGui.QColor(  0,   0,   0,  11)
    # makes gray rows stand out more:
    addressColor        = QtGui.QColor(  0,   0,   0,  15)


    def __init__(this, parent = None):
        QtGui.QAbstractScrollArea.__init__(this, parent)
        
        this.highlighting = False

        this.lines = 0

        this.selection_start = -1
        this.selection_end = -1

        this.data = MEM()

        # quick QString display list for drawing ASCII text
        this._Q_char_table = { c: QtCore.QString(chr(c)) for c in range(256)}
        
        # default to a simple monospace font
        this.setFont(QtGui.QFont("Courier New", 7))

        this._painter = QtGui.QPainter()

        #this.repaint = this.viewport().repaint
        return

    def repaint(this): this.viewport().repaint(); return

    def setFont(this, f):
        # recalculate all of our metrics/offsets
        fm = QtGui.QFontMetrics(f)
        this.font_width  = fm.width('X')
        this.font_height = fm.height()
        this.updateScrollbar()
        # TODO: assert that we are using a fixed font & find out if we care?
        QtGui.QAbstractScrollArea.setFont(this,f)
        return
    
    def updateScrollbar(this):
        this.verticalScrollBar().setMaximum( this.lines )
        return

    '''
    on to the events:
    '''

    # most of this is still ported from my works on the original QHexEdit widget.
    def paintEvent(this, event) :
 
        painter = this._painter
        painter.begin(this.viewport())

        startPos = this.verticalScrollBar().value()
        widget_height = this.height() # in pixels

        painter.translate( # set scroll
            -this.horizontalScrollBar().value() * this.font_width,
            -startPos * this.font_height
        )

        endPos = startPos+1+(widget_height/this.font_height) # improve speed by only drawing what's shown
        if endPos>this.lines: endPos=this.lines # make sure the widget height doesn't cause an index error


        _data = this.data.data
        _pos = 0
        offset = 0
        while _pos<startPos: so = _data.index(10); offset+=so; _data = _data[so+1:]; _pos+=1

        #draw primary address:
        ll = len(_pos.__str__())
        painter.drawText(0, _pos*this.font_height, 8*this.font_width, this.font_height, Qt.AlignTop,
                    QtCore.QString( '%s%s'%( ''.join([' ']*(8-ll)), _pos.__str__() ) ))

        xpos = 9
        for ci in _data:

            painter.drawText(
                xpos*this.font_width, _pos*this.font_height, this.font_width, this.font_height, Qt.AlignTop, this._Q_char_table[ci])

            if ci==10:
                _pos+=1
                xpos=9

                if _pos==endPos: break
                #draw next address:
                ll = len(_pos.__str__())
                painter.drawText(0, _pos*this.font_height, 8*this.font_width, this.font_height, Qt.AlignTop,
                    QtCore.QString( '%s%s'%( ''.join([' ']*(8-ll)), _pos.__str__() ) ))

            else: xpos+=1

        #draw the address line
        painter.setPen(QtGui.QPen(this.palette().shadow().color()))
        painter.fillRect(0, 0, int(8.5*this.font_width), (startPos*this.font_height)+widget_height, this.selectionColor)

        painter.end()
 
        return

    #input events:

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
                #self.highlighting = True

                #self.selection_start = self.pixelToByte(x, y)
                self.selection_end = self.selection_start

                self.repaint()

        return
 
 
    def mousePressEvent(self, event) :
        if(event.button() == Qt.LeftButton) :
            x = event.x() + self.horizontalScrollBar().value() * self.font_width
            y = event.y()
 
            #self.highlighting = True
            
            #offset = self.pixelToByte(x, y)
            #self.selection_start, self.selection_end = (offset,offset) if offset < self.data.size else (-1,-1)
            
            self.repaint()

        return
        
    def mouseMoveEvent(self, event) :
        if self.highlighting :
            x = event.x() + self.horizontalScrollBar().value() * self.font_width
            y = event.y()

            """
            offset = self.pixelToByte(x, y)
 
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
        if(event.button() == Qt.LeftButton): self.highlighting = False
        return
 
    def scrollTo( self, offset) :
        self.updateScrollbars()
        self.verticalScrollBar().setValue(offset)
        self.repaint()
        return

    def selectAll(self) :
        self.selection_start = 0
        self.selection_end   = self.data.size
        return

    def deselect(self) :
        self.selection_start = -1
        self.selection_end   = -1
        return

    def keyPressEvent(self, event) :
        if (event.modifiers() & Qt.ControlModifier) :
            key = event.key()
            
            if key == Qt.Key_A: self.selectAll(); self.repaint()
            
            elif key == Qt.Key_Home: self.scrollTo(0)
            elif key == Qt.Key_End: self.scrollTo(self.lines)
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
        QtGui.QAbstractScrollArea.keyPressEvent(self,event)
        return

    def setData(this, data) :
        this.data = data
            
        #set defaults
        this.lines = this.data.data.count(0x0A)
        
        this.deselect()
        this.updateScrollbar()
        
        #this.repaint()
        return
        
