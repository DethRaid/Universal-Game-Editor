# -*- coding: utf-8 -*-

from . import CONST, FILE, FORMAT, scripts, modules
from .utilities import timer

# Tcll - this area (including related sub-modules) needs the most work:

# noinspection PyBroadException
def _ImportModel( filepath, script ): # TODO: general import function (script will contain the type-NS among other info with the module)
    
    #front = modules[ 'API.frontend' ]
    #FILE = modules[ 'API.backend.FILE' ]
    #FORMAT = modules[ 'API.backend.FORMAT' ]

    scripts.reload()  # check for valid changes to the scripts
    if filepath == '': return
    else:
        # master = FILE._master; FILE._master = '' # reset the master file for exports and sub-files
        try:  # can we get our hands on the file, and does the script work?
            FILE.ugeImportFile( filepath )  # set the file data
            #FORMAT._Reset( )  # reset the data for importing
            print("Converting from import format...")
            time = timer( )
            # _LOG('-- importing %s --\n'%filepath.split('/')[-1])

            # modules['/struct()_datatypes/'].clear()
            modules[ '/struct()_keywords/' ], modules[ '/struct()_names/' ] = { }, { }  # new temporary spaces
            structkeywords, structnames = modules[ '/UGE_ScriptStructKWN/' ][ script.__name__ ]
            modules[ '/struct()_keywords/' ].update( dict( structkeywords.items( ) ) )
            modules[ '/struct()_names/' ].update( dict( structnames.items( ) ) )

            # Tcll - credit to Gribouillis for this block:
            # ---
            NS = dict( CONST.UGE_MODEL_SCRIPT.NS.items( ) );
            NS[ '__builtins__' ] = modules[ '__builtin__' ]  # clone and set
            if script.__name__ in modules[ '/UGE_ScriptLibs/' ]:  # apply libs
                for libName, regDict in modules[ '/UGE_ScriptLibs/' ][ script.__name__ ].items( ):
                    # NS.update( dict( regDict.items() ) )
                    NS.update( dict( regDict.__dict__.items( ) ) )

                    libstructkeywords, libstructnames = modules[ '/UGE_LibStructKWN/' ][ libName ]
                    modules[ '/struct()_keywords/' ].update( dict( libstructkeywords.items( ) ) )
                    modules[ '/struct()_names/' ].update( dict( libstructnames.items( ) ) )
                    # Tcll - ^ not this though, this was me. :P

            function( script.ugeImportModel.__code__, NS )( filepath.split( '.' )[ -1 ].lower( ),
                None )  # clone and call
            # ---

            time.checkpoint( )

            #FORMAT._Verify( )
            #FORMAT._Transform( )
            #FORMAT._Finalize( )
            # l=open('session.ses','w'); l.write(str([1.1,FORMAT.Libs])); l.close() # export verified UGE session data

            FILE._ClearFiles( )  # clear the file data to be used for writing
            # input('break me!')

        except:
            #FORMAT._Recall( )
            # FILE._master = master
            # print "Error! Check 'session-info.log' for more details.\n"
            import sys, traceback
            print()
            traceback.print_exception( *sys.exc_info( ) )
            print()

        # COMMON._ImgScripts = {} #reset
        modules[ '/struct()_keywords/' ] = { }

        # modules['data.LOGGING'].WRITE_LOG(0) #write log
        scripts.clean() # remove pyc files

# noinspection PyBroadException
def _ExportModel( filepath, script ):

    # Tcll - would be nice if I could do this once w/o infecting the outer namespace we're running in
    # that also means w/o references to API.frontend.FILE and the like.
    #front = modules[ 'API.frontend' ]
    #FILE = modules[ 'API.backend.FILE' ]
    #FORMAT = modules[ 'API.backend.FORMAT' ]

    scripts.reload()  # check for valid changes to the scripts
    if filepath == '': return
    else:
        FILE._ClearFiles( )  # clear the file data again... just in case
        try:
            FILE.ugeExportFile( filepath )  # add the file to the data space
            #FORMAT._Reset( False );
            FORMAT.ActiveScene = None
            print('converting to export format...')

            # modules['/struct()_datatypes/'].clear()
            modules[ '/struct()_keywords/' ], modules[ '/struct()_names/' ] = { }, { }  # new temporary spaces
            structkeywords, structnames = modules[ '/UGE_ScriptStructKWN/' ][ script.__name__ ]
            modules[ '/struct()_keywords/' ].update( dict( structkeywords.items( ) ) )
            modules[ '/struct()_names/' ].update( dict( structnames.items( ) ) )

            # Tcll - credit to Gribouillis for this block:
            # ---
            NS = dict( CONST.UGE_MODEL_SCRIPT.NS.items( ) )
            NS[ '__builtins__' ] = modules[ '__builtin__' ]  # clone and set
            if script.__name__ in modules[ '/UGE_ScriptLibs/' ]:  # apply libs
                for libName, regDict in modules[ '/UGE_ScriptLibs/' ][ script.__name__ ].items( ):
                    # NS.update( dict( regDict.items() ) )
                    NS.update( dict( regDict.__dict__.items( ) ) )

                    libstructkeywords, libstructnames = modules[ '/UGE_LibStructKWN/' ][ libName ]
                    modules[ '/struct()_keywords/' ].update( dict( libstructkeywords.items( ) ) )
                    modules[ '/struct()_names/' ].update( dict( libstructnames.items( ) ) )
                    # Tcll - ^ not this though, this was me. :P

            function( script.ugeExportModel.__code__, NS )( filepath.split( '.' )[ -1 ].lower( ),
                { } )  # clone and call
            # ---

            FILE._WriteFiles( )
            print("Done!")

        except:
            # print "Error! Check 'session-info.log' for more details.\n"
            import sys, traceback
            print();
            traceback.print_exception( *sys.exc_info( ) );
            print()

        # __WLOG(0) #write log
        scripts.clean() # remove pyc files