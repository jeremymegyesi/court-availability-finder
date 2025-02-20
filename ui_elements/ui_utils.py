import ttkbootstrap as ttk
import tkinter as tk

def create_menu_button(self, parent, options, default_value, style, width=None):
    if default_value not in options:
        raise Exception('Default value for menu item is not one of the options')
    self._dropdown_value = tk.StringVar(value=default_value)
    def update_option(option):
        self._dropdown_value.set(option)
    menu_button = ttk.Menubutton(parent, textvariable=self._dropdown_value, style=style, width=width)
    menu = ttk.tk.Menu(menu_button)
    for option in options:
        menu.add_command(label=option, command=lambda opt=option: update_option(opt))
    menu_button['menu'] = menu # associate menu with menubutton

    return menu_button

def create_style_from_existing(old_style, new_style, override_attr):
    style = ttk.Style()
    old_attrs = style.configure(old_style)
    new_attrs = old_attrs.copy()
    old_map = style.map(old_style)
    old_layout = style.layout(old_style)
    for attr, value in override_attr.items():
        new_attrs[attr] = value
    style.configure(new_style, **new_attrs)
    style.map(new_style, **old_map)
    style.layout(new_style, old_layout)