import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
# add directory to python path to run script directly with ui_elements imports
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from constants import *
from ui_elements.field_input import FieldInput, FieldInputType
from ui_elements.time_entry import TimeEntry
from ui_elements.ui_utils import darken_color
import date_utils

class DatetimeWindow(ttk.Frame):
    '''Date and time pickers to allow date and time ranges to be specified.'''
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        style = ttk.Style()
        bg_color = darken_color(style.lookup('TFrame', 'background'), factor=0.1)
        style_prefix = 'DTWINDOW'
        style.configure(style_prefix + '.Bordered.Info.TFrame', background=bg_color, borderwidth=LT_BORDER_WIDTH, relief='solid', bordercolor=style.colors.get(INFO))
        style.configure(style_prefix + '.TFrame', background=bg_color)
        style.configure(style_prefix + '.TLabel', background=bg_color, font=BODY_1_FONT)

        datetime_window_frame = ttk.Frame(parent, style=(style_prefix + '.Bordered.Info.TFrame'))
        datetime_window_frame.grid(row=0, column=0)
        # date picker inputs
        date_window_frame = ttk.Frame(datetime_window_frame, style=(style_prefix + '.TFrame'))
        date_window_frame.grid(row=0, column=0, sticky='nswe', padx=LT_BORDER_WIDTH, pady=LT_BORDER_WIDTH)
        self._from_date_select = FieldInput(date_window_frame, 0, 0, type=FieldInputType.DATE, label_text='From',
                   input_width=DATE_PICKER_WIDTH, style_prefix=style_prefix, padx=0, pady=0)
        self._to_date_select = FieldInput(date_window_frame, 0, 1, type=FieldInputType.DATE, label_text='To', suffix=',',
                   input_width=DATE_PICKER_WIDTH, style_prefix=style_prefix, padx=0, pady=0)
        # time inputs
        time_window_frame = ttk.Frame(datetime_window_frame, style=(style_prefix + '.TFrame'))
        time_window_frame.grid(row=0, column=1, sticky='e', padx=(TIME_RANGE_OFFSET, LT_BORDER_WIDTH), pady=LT_BORDER_WIDTH)
        self._from_time_entry = TimeEntry(time_window_frame, 0, 0, default='00:00')
        time_until_label = ttk.Label(time_window_frame, text='-', style=(style_prefix + '.TLabel'))
        time_until_label.grid(row=0, column=1, padx=10)
        self._to_time_entry = TimeEntry(time_window_frame, 0, 2, default='23:59', padx=(FIELD_ENTRY_PAD, FIELD_FRAME_PAD))
        self._from_time_entry.set_latter_widget(self._to_time_entry)
        self._from_date_select.bind("<<FieldInputChanged>>", lambda e: self.after(200, self._catch_up_from_date))
        self._to_date_select.bind("<<FieldInputChanged>>", lambda e: self.after(200, self._rollback_to_date))

    def _remove_row(self):
        print('delete')
        self.master.destroy()

    def _catch_up_from_date(self):
        curr = self.get()
        if not curr['start_date'] or not curr['end_date']:
            return
        if curr['end_date'] < curr['start_date']:
            self._to_date_select.set(curr['start_date'])

    def _rollback_to_date(self):
        curr = self.get()
        if not curr['start_date'] or not curr['end_date']:
            return
        if curr['end_date'] < curr['start_date']:
            self._from_date_select.set(curr['end_date'])

    def get(self):
        '''Get the combined inputs of date and time fields.'''
        user_input = {
            'start_date': date_utils.extract_date(self._from_date_select.get()),
            'end_date': date_utils.extract_date(self._to_date_select.get()),
            'start_time': date_utils.extract_time(self._from_time_entry.get()),
            'end_time': date_utils.extract_time(self._to_time_entry.get())
        }
        return user_input

# Example usage
def test():
    root = ttk.Window(themename='darkly')
    DatetimeWindow(root)
    root.mainloop()

if __name__ == '__main__':
    test()