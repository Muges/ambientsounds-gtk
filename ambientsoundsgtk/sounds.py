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
Module handling the playback of the ambient sounds, using pygame
"""

import pygame
pygame.mixer.init(frequency=48000)

import os, json
from mutagen.oggvorbis import OggVorbis

from constants import SOUNDS_DIRS, PRESETS_DIR

class SoundInfos(object):
    """
    Object containing the informations (author, license and url) about a sound
    """
    def __init__(self, filename):
        self.filename = filename

        basename = os.path.basename(filename)
        self.name = os.path.splitext(basename)[0]
        self.license = None
        self.author = None
        self.url = None

        self.read()

    def read(self):
        """
        Read the informations from the ogg vorbis tags
        """
        tags = OggVorbis(self.filename)

        try:
            self.name = tags["title"][0]
        except (KeyError, IndexError):
            pass

        try:
            self.license = tags["copyright"][0]
        except (KeyError, IndexError):
            pass

        try:
            self.author = tags["artist"][0]
        except (KeyError, IndexError):
            pass

        try:
            self.url = tags["contact"][0]
        except (KeyError, IndexError):
            pass

    def as_html(self):
        """
        Returns a html representation of the informations
        """
        return u" • <a href=\"{0.url}\">{0.name} by {0.author} ({0.license})</a>".format(self)

class Sound(object):
    """
    Sound object, the sound is extracted from an ogg file, and is
    played with pygame.
    """

    sounds = {}
    master_volume = 100
    muted = True

    def __init__(self, filename):
        """
        Create a volume object from an ogg file.
        """
        self.filename = filename
        self.volume = 0

        self.infos = SoundInfos(filename)
        Sound.sounds[self.infos.name] = self

        # The pygame.mixer.Sound object (only loaded when necessary)
        self.sound = None

        self.stopped = True

    def set_volume(self, volume=None):
        """
        Set the volume
        """
        if volume != None:
            self.volume = min(max(0, int(volume)), 100)

        if Sound.muted:
            volume = 0
        else:
            volume = Sound.master_volume*self.volume

        if volume == 0:
            if not self.stopped:
                # The volume is 0 and the sound is still playing : stop it
                self.stopped = True
                self.sound.fadeout(1000)
        else:
            if self.sound == None:
                # The volume isn't 0 and the sound isn't playing : start it
                self.sound = pygame.mixer.Sound(self.filename)

            self.sound.set_volume(volume/10000.)

            if self.stopped:
                self.stopped = False
                self.sound.play(-1, 0, 1000)

    @staticmethod
    def set_master_volume(volume):
        """
        Set the master volume
        """
        Sound.master_volume = min(max(0, int(volume)), 100)
        for sound in Sound.sounds.values():
            sound.set_volume()

    @staticmethod
    def set_muted(muted):
        """
        Mute or unmute without changing the volume value
        """
        if Sound.muted != muted:
            Sound.muted = muted
            for sound in Sound.sounds.values():
                sound.set_volume()

    @staticmethod
    def toggle_muted():
        """
        Mute or unmute without changing the volume value
        """
        Sound.set_muted(not Sound.muted)

    @staticmethod
    def load(muted=True):
        """
        Load the sounds from the sound directories
        """
        for sound_dir in SOUNDS_DIRS:
            if os.path.isdir(sound_dir):
                for filename in os.listdir(sound_dir):
                    if os.path.splitext(filename)[1] == ".ogg":
                        Sound(os.path.join(sound_dir, filename))

        pygame.mixer.set_num_channels(len(Sound.sounds))

        Sound.set_muted(muted)

    @staticmethod
    def sorted():
        """
        Return an iterator over the sounds sorted by names
        """
        for name in sorted(Sound.sounds):
            yield Sound.sounds[name]

class Preset(object):
    """
    Object storing volumes for each track
    """

    presets = {}
    current_preset = None

    def __init__(self, filename):
        """
        Initialize a preset that will be stored in the file `filename` (without reading or writing
        the file)
        """
        self.filename = filename
        self.name = os.path.splitext(os.path.basename(filename))[0]
        self.volumes = {}

        if self.name == ".current":
            Preset.current_preset = self
        else:
            Preset.presets[self.name] = self

    def apply(self):
        """
        Apply the preset
        """
        for name, sound in Sound.sounds.items():
            if self.volumes.has_key(name):
                sound.set_volume(self.volumes[name])
            else:
                sound.set_volume(0)

    def save(self):
        """
        Save the current settings to the preset and write it
        """
        # Get the current settings
        for name, sound in Sound.sounds.items():
            if sound.volume > 0:
                self.volumes[name] = sound.volume
            elif self.volumes.has_key(name):
                self.volumes.pop(name)

        # Write them
        if not os.path.exists(os.path.dirname(self.filename)):
            os.makedirs(os.path.dirname(self.filename))
        with open(self.filename, "w") as fileobj:
            json.dump(self.volumes, fileobj)

    def read(self):
        """
        Read the preset from the file
        """
        with open(self.filename, "r") as fileobj:
            self.volumes = json.load(fileobj)

    def remove(self):
        """
        Remove the preset
        """
        os.remove(self.filename)
        del Preset.presets[self.name]

    @staticmethod
    def load(preset_name=None):
        """
        Load the presets from the presets directory
        """
        if os.path.isdir(PRESETS_DIR):
            for filename in os.listdir(PRESETS_DIR):
                if os.path.splitext(filename)[1] == ".json":
                    preset = Preset(os.path.join(PRESETS_DIR, filename))
                    preset.read()

        if preset_name in Preset.presets:
            Preset.presets[preset_name].apply()
        elif Preset.current_preset != None:
            Preset.current_preset.apply()

    @staticmethod
    def save_as(name):
        """
        Save the current settings in the preset named `name` (create it if it does not exist)
        """
        try:
            preset = Preset.presets[name]
        except KeyError:
            preset = Preset(os.path.join(PRESETS_DIR, name + ".json"))
        preset.save()

    @staticmethod
    def quit():
        """
        Save the current preset for next launch
        """
        preset = Preset.current_preset

        if preset == None:
            preset = Preset(os.path.join(PRESETS_DIR, ".current.json"))

        preset.save()

    @staticmethod
    def sorted():
        """
        Return an iterator over the presets sorted by names
        """
        for name in sorted(Preset.presets):
            yield Preset.presets[name]
