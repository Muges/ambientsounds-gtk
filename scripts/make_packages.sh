#!/usr/bin/env bash

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

# Version of the package
version=`python2 -c "from ambientsoundsgtk.constants import VERSION;print VERSION"`

# Application directory
appdir=`pwd`

# Create temporary directory
tmpdir=`mktemp -d`
mkdir "$tmpdir/ambientsounds-gtk"

# Copy python files
cp -r "$appdir/ambientsoundsgtk" "$tmpdir/ambientsounds-gtk"
find "$tmpdir/ambientsounds-gtk/ambientsoundsgtk" -name "*.pyc" -delete

# Copy icons
cp -r "$appdir/icons" "$tmpdir/ambientsounds-gtk"
rm "$tmpdir/ambientsounds-gtk/icons/hicolor/16x16/apps/ambientsounds-gtk.xcf"

cp "$appdir/ambientsounds-gtk.desktop" "$tmpdir/ambientsounds-gtk"
cp "$appdir/ambientsounds-gtk" "$tmpdir/ambientsounds-gtk"
cp "$appdir/CHANGELOG.rst" "$tmpdir/ambientsounds-gtk"
cp "$appdir/COPYING" "$tmpdir/ambientsounds-gtk"
cp "$appdir/README.rst" "$tmpdir/ambientsounds-gtk"
cp "$appdir/screenshot.png" "$tmpdir/ambientsounds-gtk"

# Make package
cd "$tmpdir"
zip -q -FSr "$appdir/ambientsounds-gtk-$version.zip" "ambientsounds-gtk"

# Download sound files
wget "https://github.com/Muges/ambientsounds/archive/master.zip" -O "$tmpdir/master.zip"
unzip "$tmpdir/master.zip" -d "$tmpdir"

cp -r "$tmpdir/ambientsounds-master" "$tmpdir/ambientsounds-gtk/sounds"

# Make full package
cd "$tmpdir"
zip -q -FSr "$appdir/ambientsounds-gtk-full-$version.zip" "ambientsounds-gtk"

rm -r "$tmpdir"
