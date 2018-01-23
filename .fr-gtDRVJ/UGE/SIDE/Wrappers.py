# -*- coding: utf-8 -*-

from SIDE.common import *

from SIDE.Selectors import Types, Functions, Constants
from SIDE.CodeEditor import Editor

from SIDE.TreeViewer import TreeView
from SIDE.HexViewer import HexView
from SIDE.TextViewer import TextView

modules['/SIDE_viewers/'] = None

# holds the tree, file data, and gl viewers

# noinspection PyUnresolvedReferences
class viewWrapper(QtGui.QSplitter): # 1 instance per imported file ( per script )
    def __init__(this, parent,FID):
        QtGui.QSplitter.__init__(this, parent)
        this.setOrientation(QtCore.Qt.Horizontal)
        this.setHandleWidth(3)
        
        this.FID = FID
        this.current_node = None
        #this.GoData = []
        '''
        # Go Button:
        GoButton = QtGui.QPushButton("Go ->\n(F5)")
        GoButton.setMinimumWidth(35)
        GoButton.setMaximumWidth(35)
        #GoButton.setMaximumHeight(25)
        #GoButton.AddAction(self.Go)
        QtCore.QObject.connect(GoButton, QtCore.SIGNAL("clicked()"), this.Go )
        '''
        #data tree viewer
        this.treeView = TreeView(this)
        this.treeView.onselect = this.selected
        this.treeView.ondeselect = this.deselected
        #this.treeView.setColumnCount(2)
        #this.treeView.setHeaderLabels(['Function Call','Return Value'])
        
        viewSplit = QtGui.QSplitter()
        viewSplit.setOrientation(QtCore.Qt.Vertical)

        this.dataView = QtGui.QTabWidget()
        this.dataView.setMovable(False) #Not ready yet...
        this.dataView.setTabShape(this.dataView.Triangular)
        this.dataView.setTabPosition(this.dataView.South)
        this.hexView = HexView(this)
        this.dataView.addTab(this.hexView,'Hex')
        this.textView = TextView(this)
        this.dataView.addTab(this.textView,'Text')
        #textView.setLineWrapMode(textView.NoWrap)

        this.glView = QtGui.QTabWidget()
        this.glView.setTabShape(this.glView.Triangular)
        this.glView.addTab(QtOpenGL.QGLWidget(),'Model')

        viewSplit.addWidget(this.dataView)
        viewSplit.addWidget(this.glView)
        
        #this.addWidget(GoButton)
        this.addWidget(this.treeView)
        this.addWidget(viewSplit)

        this.editor = None

    def deselected(this):
        this.hexView.selections = []
        this.editor.dselections = []

    def selected(this):
        n = this.treeView.rows[ this.treeView.selections[0] ]
        offset = n.dt.__addr__
        size = n.dt.__size__
        this.hexView.selections = [[offset,offset+size-1]]
        this.hexView.scrollTo(offset/this.hexView.row_width)
        if n.line != None:
            this.editor.dselections = [n.line]
            this.editor.action_scrollTo(n.line)
            
    def Go(this): # run the import and export functions in the script
        
        FILE._current = FILE._file[this.FID ]
        FILE._current.offset = 0
        this.hexView.data.offset = 0
        this.hexView.data_highlights = map( lambda v: [], this.hexView.data )
        
        common.node_scopes = [[]]
        common.immediate_children = [[]]
        this.treeView.rows = common.node_scopes[0]
        #this.current_node = this.treeView.root = node() # current_node to be updated
        
        ScriptFile = bytes(this.editor.file.split('/')[-1]).__str__() # WARNING: python3 does this differently
        bad = scripts.reload(ScriptFile)
        
        # TODO: use more than just the model scope.
        if not bad: CONST.UGE_MODEL_SCRIPT.Import(ScriptFile[:-3])
        
        this.hexView.repaint()
        this.treeView.updateScrollbars()
        this.treeView.repaint()


# holds the code editor and wrapper for the file data viewers

# noinspection PyUnresolvedReferences
class mainWrapper(QtGui.QSplitter):
    def __init__(this, parent):
        QtGui.QSplitter.__init__(this, parent)
        
        this.setOrientation(QtCore.Qt.Horizontal)
        this.setHandleWidth(3)

        this.openFiles = {} # { 'filename': tabIndex }

        #TODO: list namespace selections:
        this.selectors = QtGui.QTabWidget()
        this.selectors.setMinimumWidth(200)
        this.selectors.setMaximumWidth(200)
        
        this.selectors.addTab(Types(this),'Types')
        this.selectors.addTab(Functions(this),'Functions')
        this.selectors.addTab(Constants(this),'Constants')
        
        this.editor = Editor(this)
        
        this.viewers = QtGui.QTabWidget()
        this.viewers.setTabsClosable(True)
        QtCore.QObject.connect( this.viewers, QtCore.SIGNAL("currentChanged(int)"), this.tabChange )
        QtCore.QObject.connect( this.viewers, QtCore.SIGNAL("tabCloseRequested(int)"), this.tabClose )
        this.viewers.hide()

        # TODO: move to SIDE.py for global configs
        # Script Editor Font
        fnt = QtGui.QFont()
        fnt.setFamily('Courier New')
        fnt.setPointSize(9)
        fnt.setFixedPitch(True)
        
        this.editor.setFont(fnt) #TODO: (this.window.editorFont)

        this.addWidget(this.selectors)
        this.addWidget(this.editor)
        this.addWidget(this.viewers)

    def tabClose(this,tabIndex):
        viewers = this.viewers.widget(tabIndex)
        this.viewers.removeTab(tabIndex)
        for f,i in this.openFiles.items():
            if i==tabIndex: this.openFiles.pop(f)
            if i>tabIndex: this.openFiles[f]-=1
        FILE.ugeRemoveFile(viewers.FID ) # NOTE: file index is still maintained
        viewers.hexView.data = None
        viewers.textView.data = None
        viewers.hexView = None
        viewers.textView = None
        viewers.treeView = None
        del viewers

        if len(this.openFiles)==0: this.viewers.hide()
        
    def tabChange(this,tabIndex):
        viewers = this.viewers.widget(tabIndex)
        if viewers!=None: FILE.ugeSetMasterFile(viewers.FID )
        
    def openTestFile(this):
        path = QtGui.QFileDialog.getOpenFileName(this, "Open File", '', "All files (*.*)")
        testFileName = path.split('/')[-1]
        
        if path!='':
            if this.viewers.isHidden: this.viewers.show()
                
            if testFileName not in this.openFiles:
                viewers = viewWrapper(this, None)
                viewers.editor = this.editor
                FILE.ugeSetMasterFile( '' )
                viewers.FID = FILE.ugeImportFile(str(path ) )
                this.openFiles[testFileName] = this.viewers.addTab( viewers, testFileName )
                viewers.hexView.setData( FILE._current )
                viewers.textView.setData( FILE._current )
                viewers.treeView.offlen = len(hex(len( FILE._current ) ) ) - 2
                #viewers = None # release viewWrapper instance (this.viewers has it now)
            this.viewers.setCurrentIndex(this.openFiles[testFileName])
            
            window = modules['/SIDE_window/']
            window.runAct.setEnabled(True)
            window.runAct2.setEnabled(True)

    def go(this): this.viewers.currentWidget().Go()
