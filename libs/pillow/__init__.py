# -*- coding: utf8 -*-
import sys
from . import pkg_resources
sys.modules['pkg_resources']=pkg_resources

from API import ugeLoadExtension
ugeLoadExtension('Pillow-2.6.1-py2.7-win32.egg')

import PIL

from PIL import Image
from PIL import *
