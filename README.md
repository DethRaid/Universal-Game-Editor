# Universal Game Editor
Originally named Universal Model Converter, is a tool used to convert and/or edit game content of any game supported by it's scripts.

*While it's name states you can edit game content, currently the API has not made it that far into development, please be patient as it is planned.*

UGE's API is built over a portable Anaconda interpreter under Python 3.4.3 for the purpose of supporting computers still running Windows XP.
(there's nothing py36 can do that can't be done in Py34)

The API is designed to preserve, validate, and optimize game data while providing many options to keep that data compatible with other formatting techniques.

TIE API itself can't really do anything except hold game data, it's support and functionality comes from what it can be extened with:

- **Scripts**
  This is where the basic functionality of UGE's API takes place, scripts are designed specifically for file I/O operation, including files which aren't actually read or written from/to the disk.
  The API provides a frontend accessible via inter-operable functions or class instances.
  The functions are designed to be easy enough for beginners to use, but verbose enough to integrate well with the OOP style professionals prefer.
- **Libraries**
  These offer a higher level of functionality and are granted moderated access to the API-backend.
  Libraries are designed for sharing common functionality between scripts and offer an advanced level of data control, allowing you to customize the data given to the backend.
  Note that any forwarded featurability for scripts must be registered with the API-frontend before use.
- **Plugins**
  These offer layers of functionality over UGE's API when ran as a program, Plugins have many ways of extending functionality over the API and can even extend upon other plugins.
  Note that Plugins operate on the data in the API, they do not extend the API itself.
- **Mods** *(not available yet)*
  These offer extendability over all of the above, Mods (Modifications) are mainly for experimental or unimplemented code and are merely an external hacky method of unofficial API/Plugin modifications.
  Note that the safety of mods may vary and may even (though not likely) break the API.


The API is also designed for use as a command-line utility and can be imported in applications like Blender and other Python 34+ applications.


<u>**Features**</u>:

**Plugins**
UGE comes with a few plugins out of the box that turn it into an actual application:

- VIEWER: A fast modern OpenGL+OpenCL+GLFW viewer with basic control (see docs for details).
- GUI: Extends the viewer with an intuitive full-featured UI.
- WIDGETS: Provides an interface for scripts to use widgets.
  (uses Tk with a popup unless explicitely disabled if the GUI is not detected)
- SIDE: A rework of the original Script IDE side-application integrated directly for editing scripts/libs.
  (uses Tk in a new window if the viewer and GUI are not detected)
- UPDATE: *(not available yet)* database integrations for tracking and collaborating on scripts/libs.
  (an account is required to upload and collaborate on your script)

Note that you can install and configure from multiple plugins of the same types if the stock plugins don't hold to your liking, and you can configure which plugins can be disabled.

**Scripts/Libs**
There are some special features on scripts and libs for developers.
scripts and libs are automatically reloaded on import/export when their code is updated, even if previously broken on startup.
This allows developers to work on or fix their scripts without having to restart UGE.
To add, exceptions in scripts cannot crash UGE, and are reported when hit, the script is simply discarded.

**Data Import/Export**
Since the file extension itself is unreliable, UGE can optionally use polling on an untrusted import to test a file by it's data, by which you can customize how the polling can be performed.
UGE also tries it's best to finish import and export processes, so any exceptions hit may only result in a broken import or export with only most of the data in tact.


<u>**Installation**</u>:

If you're using UGE as a typical program, there is no installation, everything was designed to be as portable as possible, so you could run it off a flash drive on a school or library computer.
(all dependancies are frozen for compatibility and included with UGE)

Otherwize, copy the UGE/ directory (the folder containing this readme) into where it's supposed to go.
for example `C:\Python34\Lib\site-packages\UGE\`.


<u>**Usage**</u>:

UGE is designed to be intuitively easy to use and follow, especially when using plugins.
Please refer to the plugin documentation for typical program usage information.

As a command-line application, please refer to the `[--help|-h] (page/command)` option for info on the many various commands and how to use them.

As an extension for another program, import the API `from UGE import API` and refer to the output of `API.help(Object=None)` for usage info.

**Important** do NOT import from API `from UGE.API import *` as you will break the API import structure and experience issues with global namespace leakage, and may even overwrite various internals.
(everything is contained in it's own secure bubble and should be kept that way)
