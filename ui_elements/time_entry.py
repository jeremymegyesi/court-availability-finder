import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
from enum import Enum
# add directory to python path to run script directly with ui_elements imports
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from ui_elements.constants import *
from ui_elements.ui_utils import *
from ui_elements.field_input import FieldInput, FieldInputType

class TimeEntry(ttk.Entry):
    '''Entry that only accepts time values.'''
    placeholder_text = '00:00'
    
    def __init__(self, parent, row, column, padx = FIELD_ENTRY_PAD, pady = FIELD_ENTRY_PAD, **kwargs):
        super().__init__(parent, **kwargs)
        self._value = ttk.StringVar(value=self.placeholder_text)

        time_entry_frame = ttk.Frame(parent)
        time_entry_frame.grid(row=row, column=column, padx=padx, pady=pady)

        validate_cmd = self.register(self._validate_input)
        self._entry = ttk.Entry(time_entry_frame, textvariable=self._value, width=5, validate='key', validatecommand=(validate_cmd, '%P'))
        self._entry.grid(row=0, column=0)

        def focus_in(event):
            self._entry.selection_range(0, ttk.END)

        def focus_out(event):
            if self.get() == '':
                self.set(self.placeholder_text)  # Restore placeholder

        self._entry.bind('<FocusIn>', focus_in)
        self._entry.bind('<FocusOut>', focus_out)
        self._entry.bind('<KeyRelease>', self._format_time_input)

        # Tweak secondary menubutton style
        create_style_from_existing('secondary.TMenubutton', 'TIMEENTRY.TMenubutton', {'font': ('Arial', 10)})
        self._dropdown = create_menu_button(self, time_entry_frame, ['AM', 'PM'], 'AM', 'TIMEENTRY.TMenubutton', width=3)
        self._dropdown.grid(row=0, column=1)

    def get(self):
        '''Get the current text in the Entry field.'''
        return self._value.get()

    def set(self, text):
        '''Set the text of the Entry field.'''
        self._value.set(text)

    # only allow numbers
    def _validate_input(self, text):
        # remove colon
        if len(text) >= 3 and text[2] == ':':
            text = text[:2] + text[3:]
        return (text.isdigit() or text == '') and len(text) <= 4
    
    def _format_time_input(self, event):
        text = self.get().replace(':', '')  # Remove existing colons
        if not text.isdigit():
            return  # Ignore invalid characters

        # Format the text as HH:MM
        if len(text) > 4:
            text = text[:4]  # Limit to max 4 digits

        formatted = ':'.join([text[:2], text[2:]]) if len(text) > 2 else text
        self.set(formatted)
        self._entry.icursor('end')

# Example usage
def test():
    root = ttk.Window(themename='darkly')
    # Create custom FieldInput widget
    time_entry = TimeEntry(root, 0, 0)
    root.mainloop()

if __name__ == '__main__':
    test()