# -*- coding: utf-8 -*-
'''
This module provides an interface to treat C-API extensions like python treats basic python extensions.
'''
# credit to minamina for a working portable MinGW compiler

import os, subprocess

# g++ -pipe YourFiles1.cpp YourFile2.cpp -o/dev/stdout -Wall | ./x0