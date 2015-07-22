#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright (c) 2014-2015 Muges
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Module defining the constants used in AmbientSounds
"""

import os, sys

# Version of AmbientSounds
VERSION = "0.1.0"

# Directory containing the main.py script (or the current directory)
try:
    APP_DIR = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
except AttributeError:
    APP_DIR = os.getcwd()

# Directories where the sounds are searched
SOUNDS_DIRS = [os.path.expanduser("~/.config/ambientsounds/sounds"),
               "/usr/share/ambientsounds/sounds",
               os.path.join(APP_DIR, "sounds")]

# Directory containing the presets
PRESETS_DIR = os.path.expanduser("~/.config/ambientsounds/presets")

# Directory containing the icons
ICON_PATH = os.path.join(APP_DIR, "icons")
