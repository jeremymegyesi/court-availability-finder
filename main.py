import asyncio
import asyncio.base_futures
from async_tkinter_loop import async_handler, async_mainloop, async_tkinter_loop
import threading
import time
import ctypes
import tkinter as tk
import _tkinter
import ttkbootstrap as ttk
from tkcalendar import Calendar, DateEntry
from PIL import Image, ImageTk
from ui_elements import *
from court_finder import CourtFinder
import sys

class CustomGUIColors:
    TEA_GREEN = '#CCF1C7'

FIELD_FRAME_PAD = 20
FIELD_LABEL_PAD = 15
FIELD_ENTRY_PAD = 5
BUTTON_BELOW_PAD = (0, 10)

FIELD_ENTRY_LEFT_PAD = (15, FIELD_ENTRY_PAD)
FIELD_LEFT_PAD = (30, FIELD_ENTRY_PAD)
LEFT_INDENT_1_PAD = (40, FIELD_FRAME_PAD)

# Enable DPI awareness (fix blurry text in Windows)
ctypes.windll.shcore.SetProcessDpiAwareness(1)

style = ttk.Style(theme='solar')
style.configure('TLabelframe.Label', font=HEADER_1_FONT)
style.configure('TLabel', font=HEADER_1_FONT)
style.configure('TMenubutton', font=BODY_1_FONT)
style.configure('TButton', font=BUTTON_FONT)

root = style.master
root.option_add('*Menu*Font', ('Arial', 12))
root.geometry('1400x800')
root.title('Court Finder')
root.columnconfigure(0, weight=1)

inputs_frame = ttk.LabelFrame(root, text='Enter your availability', style='primary')
# put frame at center
inputs_frame.grid(row=0, column=0, sticky='w', padx=20, pady=20)

inputs_r1_frame = ttk.Frame(inputs_frame)
inputs_r1_frame.grid(row=0, column=0, sticky='w')

# availability inputs
dur_menu_params = {
    'menu_options': ['30', '60', '90', '120'],
    'default_value': '90'
}
dur_menu_button = FieldInput(inputs_r1_frame, 0, 0, type=FieldInputType.DROPDOWN, label_text='Duration:',
                                         suffix='mins', params=dur_menu_params)

loc_menu_params = {
    'menu_options': ['Any', 'Oak Bay Recreation', 'Panorama Recreation'],
    'default_value': 'Any'
}
loc_field_button = FieldInput(inputs_r1_frame, 0, 1, type=FieldInputType.DROPDOWN, label_text='Location:',
                                          params=loc_menu_params)

# datetime ranges
availability_frame = ttk.Frame(inputs_frame)
availability_frame.grid(row=1, column=0, sticky='w', padx=FIELD_FRAME_PAD)
availability_label = ttk.Label(availability_frame, text='Available times:', font=HEADER_1_FONT)
availability_label.grid(row=0, column=0, sticky='w',
                padx=FIELD_LABEL_PAD, pady= FIELD_LABEL_PAD)
row1 = DatetimeWindow(availability_frame, style.lookup('TFrame', 'background'), 1)
# TODO: add functionality for multiple availability windows
windows = [row1]

def get_user_inputs():
    user_inputs = {}
    user_inputs['duration'] = int(dur_menu_button.get())
    user_inputs['location'] = loc_field_button.get()
    user_inputs['availability'] = [window.get() for window in windows]
    return user_inputs

broker = CourtFinder()
async def search_courts():
    user_input = get_user_inputs()
    await broker.find_courts(user_input)

search_icon = tk.PhotoImage(file='imgs/search-icon.png')
search_button = ttk.Button(root, text='Search ', image=search_icon, compound='right', command=async_handler(search_courts))
search_button.grid(row=1, column=0, sticky='w', padx=FIELD_FRAME_PAD, pady=BUTTON_BELOW_PAD)

async_mainloop(root)