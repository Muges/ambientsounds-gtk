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
Module handling the interface
"""

from gi.repository import Gtk, Gdk, Gio, GObject
from .sounds import Sound, Preset

from constants import ICON_PATH

Gtk.IconTheme.get_default().append_search_path(ICON_PATH)

Gtk.Window.set_default_icon_name("ambientsounds-gtk")

def main():
    """
    Start the interface
    """
    Sound.load()
    Preset.load()

    StatusIcon()

    Gtk.main()

class StatusIcon(Gtk.StatusIcon):
    """
    Object handling the tray icon
    """
    def __init__(self):
        Gtk.StatusIcon.__init__(self)
        self.set_icon()
        self.connect("activate", self.on_activate)
        self.connect("popup-menu", self.on_menu)
        self.set_tooltip_text("AmbientSounds")
        self.window = MainWindow()

        self.set_visible(True)

    def set_icon(self):
        """
        Set the icon, depending on the state of the application
        """
        if Sound.muted:
            pixbuf = Gtk.IconTheme.get_default().load_icon("ambientsounds-gtk-muted", 16,
                                                           Gtk.IconLookupFlags.USE_BUILTIN)
        else:
            pixbuf = Gtk.IconTheme.get_default().load_icon("ambientsounds-gtk", 16,
                                                           Gtk.IconLookupFlags.USE_BUILTIN)
        self.set_from_pixbuf(pixbuf)

    def on_activate(self, icon):
        """
        Method called when the user left-clicks on the icon, mute or unmute the sounds
        """
        Sound.toggle_mute()
        self.set_icon()

    def on_menu(self, icon, button, activate_time):
        """
        Method called when the user right-clicks on the icon, displays the main window
        """
        self.window.toggle()

class MainWindow(Gtk.Window):
    """
    Object handling the main window
    """
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(380, 500)
        self.set_title("AmbientSounds")
        self.connect("delete-event", self.on_close)

        vbox = Gtk.VBox()
        self.add(vbox)

        toolbar = self.create_toolbar()
        vbox.pack_start(toolbar, False, True, 0)

        self.stack = Gtk.Stack()
        vbox.pack_start(self.stack, True, True, 0)

        scrolledwindow = Gtk.ScrolledWindow()
        self.stack.add_named(scrolledwindow, "sounds")

        listbox = Gtk.ListBox()
        scrolledwindow.add_with_viewport(listbox)

        for sound in Sound.sorted():
            listbox.add(SoundBox(sound))

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.add_with_viewport(AboutBox())
        self.stack.add_named(scrolledwindow, "about")

        self.savebox = SaveBox()
        self.savebox.connect("saved", self.on_saved)
        self.stack.add_named(self.savebox, "save")

    def create_toolbar(self):
        """
        Create the toolbar, containing the master volume slider and a menu button
        """
        toolbar = Gtk.Toolbar()
        context = toolbar.get_style_context()
        context.add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)

        master = Gtk.HScale.new_with_range(0, 100, 1)
        master.set_draw_value(False)
        master.set_value(Sound.master_volume)
        master.set_tooltip_text("Master volume")
        master.connect("value-changed", self.on_master_changed)

        toolitem = Gtk.ToolItem()
        toolitem.add(master)
        toolitem.set_expand(True)
        toolbar.insert(toolitem, 0)

        menu_button = Gtk.ToggleToolButton()
        menu_button.set_icon_name("emblem-system-symbolic")
        menu_button.connect("toggled", self.on_menu_toggled)
        toolbar.insert(menu_button, 1)

        self.back_button = Gtk.ToolButton()
        self.back_button.set_icon_name("go-previous-symbolic")
        self.back_button.connect("clicked", self.on_back_clicked)
        toolbar.insert(self.back_button, 2)

        return toolbar

    def create_menu(self, button):
        """
        Create the menu allowing the user to handle the presets
        """
        menu = Gtk.PopoverMenu()
        menu.set_relative_to(button)
        menu.connect("closed", lambda _: button.set_active(False))

        menu.set_border_width(10)

        grid = Gtk.Grid()
        menu.add(grid)

        y = 0
        for preset in Preset.sorted():
            preset_button = Gtk.ModelButton()
            preset_button.set_property("text", preset.name)
            preset_button.connect("clicked", self.on_apply, preset)
            grid.attach(preset_button, 0, y, 1, 1)

            remove_button = Gtk.ModelButton()
            icon = Gio.ThemedIcon.new("window-close-symbolic")
            remove_button.set_property("icon", icon)
            remove_button.connect("clicked", self.on_remove, preset)
            grid.attach(remove_button, 1, y, 1, 1)
            y += 1

        save_button = Gtk.ModelButton()
        save_button.set_property("text", "Save preset")
        save_button.connect("clicked", self.on_save)
        grid.attach(save_button, 0, y, 2, 1)
        y += 1

        about_button = Gtk.ModelButton()
        about_button.set_property("text", "About")
        about_button.connect("clicked", self.on_about)
        grid.attach(about_button, 0, y, 2, 1)
        y += 1

        quit_button = Gtk.ModelButton()
        quit_button.set_property("text", "Quit")
        quit_button.connect("clicked", self.on_quit)
        grid.attach(quit_button, 0, y, 2, 1)
        y += 1

        return menu

    def show_all(self, *args, **kwargs):
        self.stack.set_visible_child_name("sounds")
        Gtk.Window.show_all(self, *args, **kwargs)
        self.back_button.hide()

    def toggle(self):
        """
        Toggle the visibility of the window
        """
        if self.is_visible():
            self.hide()
        else:
            self.show_all()

    def on_master_changed(self, scale):
        """
        Change the master volume
        """
        Sound.set_master_volume(scale.get_value())

    def on_menu_toggled(self, button):
        """
        Show the menu
        """
        if button.get_active():
            menu = self.create_menu(button)
            menu.show_all()

    def on_back_clicked(self, button):
        """
        Return to the sounds view
        """
        self.back_button.hide()
        self.stack.set_visible_child_name("sounds")

    def on_close(self, window, event):
        """
        Hide the window instead of destroying it on closing
        """
        self.hide()
        return True

    def on_apply(self, button, preset):
        """
        Load a preset
        """
        preset.apply()

        for soundbox in SoundBox.soundboxes:
            soundbox.update()

    def on_remove(self, button, preset):
        """
        Remove a preset
        """
        preset.remove()

    def on_save(self, button):
        """
        Show the save view
        """
        self.back_button.show()
        self.savebox.update()
        self.stack.set_visible_child_name("save")

    def on_saved(self, savebox):
        """
        Return to the sounds view
        """
        self.back_button.hide()
        self.stack.set_visible_child_name("sounds")

    def on_about(self, button):
        """
        Show the about view
        """
        self.back_button.show()
        self.stack.set_visible_child_name("about")

    def on_quit(self, button):
        """
        Quit the application
        """
        Preset.quit()
        Gtk.main_quit()

class AboutBox(Gtk.VBox):
    """
    Box displaying the credits
    """
    def __init__(self):
        Gtk.VBox.__init__(self)
        self.set_border_width(10)
        self.set_spacing(10)

        # For some reason this gives a small icon :
        #icon = Gtk.Image.new_from_icon_name("ambientsounds", 128)
        pixbuf = Gtk.IconTheme.get_default().load_icon("ambientsounds-gtk", 128,
                                                       Gtk.IconLookupFlags.USE_BUILTIN)
        icon = Gtk.Image.new_from_pixbuf(pixbuf)
        self.pack_start(icon, False, True, 0)

        label = Gtk.Label()
        label.set_markup("<big><b>AmbientSounds</b></big>")
        self.pack_start(label, False, True, 0)

        label = Gtk.Label()
        label.set_markup("<b>by Muges</b>")
        self.pack_start(label, False, True, 0)

        label = Gtk.Label("Ambient sounds player inspired by Noizio, A Soft Murmur, etc...")
        label.set_line_wrap(True)
        label.set_xalign(0)
        self.pack_start(label, False, True, 0)

        label = Gtk.Label()
        label.set_markup("The source code of this application is available on " +
                         "<a href=\"https://github.com/Muges/ambientsounds-gtk\">Github</a> " +
                         "under MIT License.")
        label.set_line_wrap(True)
        label.set_xalign(0)
        self.pack_start(label, False, True, 0)

        label = Gtk.Label()
        label.set_markup("I would like to thank <a href=\"http://snwh.org/moka/\">Sam Hewitt</a> " +
                         "for the application's icon, and the authors of the original sound " +
                         "files which are listed below :")
        label.set_line_wrap(True)
        label.set_xalign(0)
        self.pack_start(label, False, True, 0)

        label = Gtk.Label()
        label.set_markup("\n".join([sound.infos.as_html() for sound in Sound.sorted()]))
        label.set_line_wrap(True)
        label.set_xalign(0)
        self.pack_start(label, False, True, 0)

class SoundBox(Gtk.ListBoxRow):
    """
    Box displaying the name of a sound and a slider to change its volume
    """

    soundboxes = []

    def __init__(self, sound):
        Gtk.ListBoxRow.__init__(self)

        self.sound = sound

        vbox = Gtk.VBox()
        vbox.set_border_width(5)
        vbox.set_spacing(5)
        self.add(vbox)

        label = Gtk.Label(sound.infos.name)
        label.set_xalign(0)
        vbox.pack_start(label, False, True, 0)

        self.volume = Gtk.HScale.new_with_range(0, 100, 1)
        self.volume.set_draw_value(False)
        self.volume.connect("value-changed", self.on_volume_changed)
        vbox.pack_start(self.volume, False, True, 0)

        self.update()

        SoundBox.soundboxes.append(self)

    def update(self):
        """
        Update the volume
        """
        self.volume.set_value(self.sound.volume)

    def on_volume_changed(self, volume):
        """
        Change the volume
        """
        self.sound.set_volume(volume.get_value())

class SaveBox(Gtk.VBox):
    """
    Box displaying a list of preset names and an entry
    """
    def __init__(self):
        Gtk.VBox.__init__(self)
        self.set_border_width(10)
        self.set_spacing(10)

        self.store = Gtk.ListStore(str)

        treeview = Gtk.TreeView(self.store)
        treeview.set_headers_visible(False)
        treeview.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        treeview.get_selection().connect("changed", self.on_selection_changed)
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.add_with_viewport(treeview)
        self.pack_start(scrolledwindow, True, True, 0)

        cellrenderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Preset name", cellrenderer, text=0)
        treeview.append_column(column)

        hbox = Gtk.HBox()
        hbox.set_spacing(10)
        self.pack_start(hbox, False, True, 0)

        label = Gtk.Label()
        label.set_markup("<b>Preset name:</b>")
        hbox.pack_start(label, False, True, 0)

        self.entry = Gtk.Entry()
        hbox.pack_start(self.entry, True, True, 0)
        #self.pack_start(self.entry, False, True, 0)

        buttonbox = Gtk.HButtonBox()
        buttonbox.set_layout(Gtk.ButtonBoxStyle.END)
        self.pack_start(buttonbox, False, True, 0)

        savebutton = Gtk.Button.new_with_label("Save")
        savebutton.connect("clicked", self.on_save)
        buttonbox.pack_start(savebutton, False, True, 0)

    def update(self):
        """
        Update the list of presets
        """
        self.store.clear()

        for preset in Preset.sorted():
            self.store.append([preset.name])

    def on_selection_changed(self, selection):
        """
        Update the entry text when the treeview's selection change
        """
        (store, treeiter) = selection.get_selected()

        if store != None and treeiter != None:
            self.entry.set_text(store.get_value(treeiter, 0))

    def on_save(self, button):
        """
        Method called when the user clicks on the save button
        """
        name = self.entry.get_text()

        if name != "":
            Preset.save_as(name)
            self.emit("saved")

GObject.signal_new("saved", SaveBox, GObject.SIGNAL_RUN_FIRST, None, [])
