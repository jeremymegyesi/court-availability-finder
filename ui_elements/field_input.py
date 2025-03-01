import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
from enum import Enum
from .constants import *
from .ui_utils import *

FIELD_LABEL_PAD = 15

class FieldInputType(Enum):
    TEXT = 'text'
    DROPDOWN = 'dropdown'
    DATE = 'date'

class FieldInput(ttk.Frame):
    '''Combines a Label and Input.'''
    
    def __init__(self, parent, row, column, type=FieldInputType.TEXT, label_text='Label:', suffix=None,
                 padx=FIELD_FRAME_PAD, pady=FIELD_FRAME_PAD, params={}, input_width=20, style_prefix=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._style_prefix = style_prefix
        self._type = type

        if type not in FieldInputType:
            raise Exception('Unknown field input type specified: ' + str(type))
        
        # Create frame
        field_frame = ttk.Frame(parent, style=self._append_style_prefix('TFrame'))
        field_frame.grid(row=row, column=column, sticky='w', padx=padx, pady=pady)
        
        # Create Label
        self.label = ttk.Label(field_frame, text=label_text, style=self._append_style_prefix('TLabel'))
        self.label.grid(row=0, column=0, padx=FIELD_LABEL_PAD, pady=FIELD_LABEL_PAD)

        # Create Input
        self._input = None
        match type:
            case FieldInputType.TEXT:
                self._input = ttk.Entry(field_frame, width=input_width, style=self._append_style_prefix('TEntry'))
            case FieldInputType.DROPDOWN:
                self._input = create_menu_button(self, field_frame, params['menu_options'], params['default_value'], 'secondary.TMenubutton')
            case FieldInputType.DATE:
                self._input =  ttk.DateEntry(field_frame, width=input_width, dateformat='%Y/%m/%d', bootstyle=SECONDARY)
        
        self._input.grid(row=0, column=1, padx=FIELD_ENTRY_PAD, pady=FIELD_ENTRY_PAD)
        
        if suffix:
            self.suffix = ttk.Label(field_frame, text=suffix, style=self._append_style_prefix('TLabel'))
            self.suffix.grid(row=0, column=2)

    def get(self):
        '''Get the current text in the Entry field.'''
        match self._type:
            case FieldInputType.DROPDOWN:
                return self._dropdown_value.get()
            case FieldInputType.DATE:
                return self._input.entry.get()
            case FieldInputType.TEXT:
                return self._input.get()

    def set(self, text):
        '''Set the text of the Entry field.'''
        self._input.delete(0, 'end')
        self._input.insert(0, text)

    def _append_style_prefix(self, name):
        return (self._style_prefix + '.' if self._style_prefix else '') + name

# Example usage
def test():
    root = ttk.Window(themename='darkly')
    # Create custom FieldInput widget
    custom_entry = FieldInput(root, type='dropdown', label_text='Username:', suffix='Last Name',
                            params={
                                'menu_options': ['mike', 'daniel', 'john'],
                                'default_value': 'john'
                                }
                            )
    root.mainloop()

if __name__ == '__main()__':
    test()