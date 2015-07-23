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
Ambient sounds player inspired by Noizio, A Soft Murmur, etc...
"""

import argparse
from gi.repository import Gtk


from .ui import StatusIcon
from .sounds import Sound, Preset

def main():
    """
    Start the interface
    """

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Ambient sound player inspired by Noizio, A ' +
                                                 'Soft Murmur, etc...')

    parser.add_argument('--muted', action='store_true', help='start AmbientSounds muted')
    parser.add_argument('--preset', action='store', help='load the preset named PRESET')

    args = parser.parse_args()

    # Load the sounds and the presets
    Sound.load(args.muted)
    Preset.load(args.preset)

    # Display the status icon
    StatusIcon()

    Gtk.main()

if __name__ == "__main__":
    main()
