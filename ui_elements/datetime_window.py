import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
# add directory to python path to run script directly with ui_elements imports
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from ui_elements.constants import *
from ui_elements.field_input import FieldInput, FieldInputType
from ui_elements.time_entry import TimeEntry
import date_utils

DATE_PICKER_WIDTH = 12
BORDER_WIDTH = 3
TIME_RANGE_OFFSET = 40
WINDOW_BOTTOM_PAD = 20

class DatetimeWindow(ttk.Frame):
    '''Date and time pickers to allow date and time ranges to be specified.'''
    
    def __init__(self, parent, parent_bg_color, row, **kwargs):
        super().__init__(parent, **kwargs)

        bg_color = self._lighten_color(parent_bg_color)
        style_prefix = 'DTW'
        style = ttk.Style()
        style.configure(style_prefix + '.Bordered.TFrame', background=bg_color, borderwidth=BORDER_WIDTH, relief='solid')
        style.configure(style_prefix + '.TFrame', background=bg_color)
        style.configure(style_prefix + '.TLabel', background=bg_color, font=BODY_1_FONT)

        datetime_window_frame = ttk.Frame(parent, style=(style_prefix + '.Bordered.TFrame'))
        datetime_window_frame.grid(row=row, column=0, sticky='nswe', padx=FIELD_FRAME_PAD, pady=(0, WINDOW_BOTTOM_PAD))
        # date picker inputs
        date_window_frame = ttk.Frame(datetime_window_frame, style=(style_prefix + '.TFrame'))
        date_window_frame.grid(row=0, column=0, sticky='nswe', padx=BORDER_WIDTH, pady=BORDER_WIDTH)
        self._from_date_select = FieldInput(date_window_frame, 0, 0, type=FieldInputType.DATE, label_text='From',
                   input_width=DATE_PICKER_WIDTH, style_prefix=style_prefix, padx=0, pady=0)
        self._to_date_select = FieldInput(date_window_frame, 0, 1, type=FieldInputType.DATE, label_text='To', suffix=',',
                   input_width=DATE_PICKER_WIDTH, style_prefix=style_prefix, padx=0, pady=0)
        # time inputs
        time_window_frame = ttk.Frame(datetime_window_frame, style=(style_prefix + '.TFrame'))
        time_window_frame.grid(row=0, column=1, sticky='e', padx=(TIME_RANGE_OFFSET, BORDER_WIDTH), pady=BORDER_WIDTH)
        self._from_time_entry = TimeEntry(time_window_frame, 0, 0)
        time_until_label = ttk.Label(time_window_frame, text='-', style=(style_prefix + '.TLabel'))
        time_until_label.grid(row=0, column=1, padx=10)
        self._to_time_entry = TimeEntry(time_window_frame, 0, 2)


    def get(self):
        '''Get the combined inputs of date and time fields.'''
        user_input = {
            'start_date': date_utils.extract_date(self._from_date_select.get()),
            'end_date': date_utils.extract_date(self._to_date_select.get()),
            'start_time': date_utils.extract_time(self._from_time_entry.get()),
            'end_time': date_utils.extract_time(self._to_time_entry.get())
        }
        return user_input

    def _lighten_color(self, color, factor=0.2):
        '''Lightens an RGB color by blending it with white.'''
        hex_color = color.strip("#")
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        # Lighten color by blending with white (255, 255, 255)
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
        # Convert back to Tkinter format (#RRGGBB)
        return f'#{r:02x}{g:02x}{b:02x}'

# Example usage
def test():
    root = ttk.Window(themename='darkly')
    win = DatetimeWindow(root, root.style.lookup('TFrame', 'background'), 0)
    root.mainloop()

if __name__ == '__main__':
    test()