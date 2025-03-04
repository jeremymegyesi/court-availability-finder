import datetime
import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
from enum import Enum
# add directory to python path to run script directly with ui_elements imports
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from constants import *
from ui_elements.ui_utils import *
from ui_elements.field_input import FieldInput, FieldInputType

class Meridiem(Enum):
    AM = 'AM'
    PM = 'PM'

class TimeEntry(ttk.Frame):
    '''Entry that only accepts time values.\n
    Stores time in 24hr format and displays in 12hr format.'''
    
    def __init__(self, parent, row, column, latter_widget=None, latter_gap_var=0, default='00:00', padx = FIELD_ENTRY_PAD, pady = FIELD_ENTRY_PAD, **kwargs):
        super().__init__(parent, **kwargs)
        self._default_value = default
        self._value = ttk.StringVar(value=self._default_value)
        self._entry_value = ttk.StringVar(value=self._value.get())
        self._latter_widget = latter_widget
        self._latter_widget_gap_var = latter_gap_var

        self.grid(row=row, column=column, padx=padx, pady=pady)

        validate_cmd = self.register(self._validate_input)
        self._entry = ttk.Entry(self, textvariable=self._entry_value, width=5, validate='key', validatecommand=(validate_cmd, '%P'))
        self._entry.grid(row=0, column=0)

        def focus_in(event):
            self._entry.selection_range(0, ttk.END)

        def on_focus_out(event):
            if self.get() == '':
                # Restore default value
                self._value.set(self._default_value)
                self._entry_value.set(self._default_value)
                self._display_12hr()
                return
            self._save_display_in_24hr()
            self._display_12hr()
            self.update_latter_widget()

        self._entry.bind('<FocusIn>', focus_in)
        self._entry.bind('<FocusOut>', on_focus_out)
        self._entry.bind('<KeyRelease>', self._format_time_input)

        # Tweak secondary menubutton style
        create_style_from_existing('secondary.TMenubutton', 'TIMEENTRY.TMenubutton', {'font': ('Arial', 10)})
        meridiem_values = [e.value for e in Meridiem]
        self._dropdown = create_menu_button(self, self, meridiem_values, Meridiem.AM.value, 'TIMEENTRY.TMenubutton', width=3)
        self._dropdown.grid(row=0, column=1)
        self._display_12hr()
        
        # set value to 24hr time when dropdown value changes
        self._dropdown_value.trace_add('write', lambda *args: (self._save_display_in_24hr(), self.update_latter_widget()))

    def get(self):
        '''Get the 24hr time.'''
        return self._value.get()

    def set(self, time):
        '''Set the 24hr time and update display.'''
        self._value.set(time)
        self._entry_value.set(time)
        self._display_12hr()

    def set_latter_widget(self, widget):
        '''Set the widget that must have a later value than this widget.'''
        self._latter_widget = widget

    def update_latter_widget(self): 
        if self._latter_widget is None:
            return
        
        # Convert to time object
        def convert_time_str(time_str):
            return datetime.datetime.strptime(time_str, '%H:%M').time()
        try:
            before_time = convert_time_str(self.get())
            after_time = convert_time_str(self._latter_widget.get())
        except ValueError:
            return

        # catch up linked TimeEntry widget
        if before_time > after_time:
            self._latter_widget.set(self.get())

    def _save_display_in_24hr(self):
        display_time = self._entry_value.get()
        if display_time == '' or not ':' in display_time:
            return

        hour, minute = map(int, display_time.split(':'))
        meridiem = self._dropdown_value.get()
        if meridiem == Meridiem.PM.value and hour < 12:
            hour += 12
        elif meridiem == Meridiem.AM.value and hour == 12:
            hour = 0

        self._value.set(f'{hour:02}:{minute:02}')

    def _display_12hr(self):
        time_24hr = self.get()
        if time_24hr == '' or not ':' in time_24hr:
            return
        
        hour, minute = time_24hr.split(':')
        hour = int(hour)
        meridiem = self._dropdown_value.get()
        if hour >= 12:
            meridiem = Meridiem.PM.value
            if hour > 12:
                hour -= 12
        elif hour == 0:
            hour = 12

        self._entry_value.set(f'{hour:02}:{minute}')
        self._dropdown_value.set(meridiem)

    # only allow numbers
    def _validate_input(self, text):
        # remove colon
        if len(text) >= 3 and text[2] == ':':
            text = text[:2] + text[3:]
        return (text.isdigit() or text == '') and len(text) <= 4
    
    def _format_time_input(self, event):
        text = self._entry_value.get().replace(':', '')  # Remove existing colons
        if not text.isdigit():
            return  # Ignore invalid characters

        # Format the text as HH:MM
        if len(text) > 4:
            text = text[:4]  # Limit to max 4 digits

        formatted = ':'.join([text[:2], text[2:]]) if len(text) > 2 else text
        self._entry_value.set(formatted)
        self._entry.icursor('end')

# Example usage
def test():
    root = ttk.Window(themename='darkly')
    # Create custom FieldInput widget
    TimeEntry(root, 0, 0)
    root.mainloop()

if __name__ == '__main__':
    test()