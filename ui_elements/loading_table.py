import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview
import tkinter as tk
from tkinter import font as tkFont
import asyncio
import webbrowser
from async_tkinter_loop import async_mainloop, async_handler
from ttkbootstrap.constants import *
from PIL import Image, ImageTk, ImageSequence  # Ensure you have Pillow installed
# add directory to python path to run script directly with ui_elements imports
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from constants import *
from ui_elements.ui_utils import *

class LoadingTable(Tableview):
    '''Table widget that displays a loading spinner when searching for data and a label when no data is present.'''
    
    def __init__(self, parent, column_config, **kwargs):
        style = ttk.Style()
        style.configure('LT.TLabel', font=TABLE_MSG_FONT)
        table_background = style.lookup('Treeview', 'fieldbackground', default='gray')
        super().__init__(parent, stripecolor=(lighten_color(table_background, 0.1), None), **kwargs)
        
        self._loading = False
        self._column_config = column_config
        self._no_data_msg = 'No data'
        self._no_data_found_msg = 'No available time slots found'
        self._overlay_msg = ttk.StringVar(value=self._no_data_msg)

        # Load the GIF
        self._loading_gif = Image.open(os.path.join(SCRIPT_DIR, '../imgs/loading.gif'))
        self._loading_frames = self._prepare_frames(self._loading_gif)
        self._loading_gif = self._loading_frames[0]
        self._current_frame = 0
        self._overlay = ttk.Label(parent, textvariable=self._overlay_msg, background=table_background, style='LT.TLabel')

        self.grid(row=0, column=0, padx=FIELD_FRAME_PAD, pady=FIELD_FRAME_PAD, sticky='nsew')
        self._center_overlay()
        self.view.bind('<ButtonRelease-1>', self._open_link)

    def clear_url_map(self):
        self._url_map = {}

    def add_to_url_map(self, path, url):
        self._url_map[path] = url

    def _prepare_frames(self, gif):
        frames = []
        for frame in ImageSequence.Iterator(gif):
            frame = frame.convert('RGBA')
            frame = frame.resize((50, 50))
            transparent_frame = Image.new('RGBA', frame.size)
            transparent_frame = Image.alpha_composite(transparent_frame, frame)
            frames.append(ImageTk.PhotoImage(transparent_frame))
        return frames
        
    def _open_link(self, event):
        ''' Open the hyperlink only if the clicked column is 'hyperlink' '''
        item_id = self.view.identify_row(event.y)  # Get the clicked row
        column_id = self.view.identify_column(event.x)  # Get the clicked column (e.g., '#1', '#2')

        # get column name from column id
        col_index = int(column_id[1:]) - 1  # Convert to zero-based index
        columns = self.get_columns()
        col_name = columns[col_index].headertext
        def get_column_value(col_name):
            values = self.view.item(item_id, 'values')
            col_index = next(i for i, col in enumerate(columns) if col.headertext == col_name)
            return values[col_index].strip(' 🔗')
        if item_id and self._column_config[col_name]['hyperlink']:
            path = '.'.join([get_column_value(x) for x in self._column_config[col_name]['hyperlink_params']])
            url = self._url_map[path]
            webbrowser.open(url)
    
    # Example function to get font height from Style
    def _get_font_height(self, style_name):
        style = ttk.Style()
        font_name = style.lookup(style_name, 'font')
        if font_name:
            font = tkFont.Font(font=font_name)
            return font.metrics('linespace')
        else:
            # get system default if none set
            font = tkFont.nametofont('TkDefaultFont')
            return font.metrics('linespace')

    def _center_overlay(self):
        self.update_idletasks()  # Ensure layout is updated
        tree_height = self.winfo_height()
        if tree_height <= 1:
            self.after(100, self._center_overlay)
            return
        scrollbar_height = tree_height - self.view.winfo_height()
        header_height = self._get_font_height('Treeview.Heading')
        body_height = tree_height - header_height  # Height of the table body
        self._overlay.place(relx=0.5, rely=header_height/tree_height + body_height/(2*tree_height) - scrollbar_height/tree_height, anchor='center')

    def is_loading(self):
        return self._loading

    def start_loading(self):
        self._loading = True
        self._overlay_msg.set(None)
        self._center_overlay()
        self._animate_gif()

    def stop_loading(self):
        self._loading = False
        if len(self.get_rows()) == 0:
            self._overlay.configure(image='')
            del self._overlay.image
            self._overlay_msg.set(self._no_data_found_msg)
        else:
            self._overlay.place_forget()

    def _animate_gif(self):
        if self._loading:
            self._current_frame = (self._current_frame + 1) % len(self._loading_frames)
            self._overlay.configure(image=self._loading_frames[self._current_frame])
            self._overlay.image = self._loading_frames[self._current_frame] # Keep a reference to avoid garbage collection
            self.after(100, self._animate_gif)  # Adjust the delay as needed

# Example usage
def test():
    root = ttk.Window(themename='darkly')
    table = LoadingTable(root, column_config={'Name': {'weight': 2}, 'Age': {'weight': 1}, 'Occupation': {'weight': 3}},
                         coldata=['Name', 'Age', 'Occupation'])
    async def load_3_seconds():
        table.start_loading()
        await asyncio.sleep(3)
        table.insert_rows(tk.END, [
                ['John Doe', 30, 'Software Engineer'],
                ['Jane Doe', 25, 'Data Scientist'],
                ['John Smith', 40, 'Project Manager']
        ]
        )
        table.load_table_data()
        table.stop_loading()
    async_handler(load_3_seconds)
    btn = ttk.Button(root, text='Search', command=async_handler(load_3_seconds))
    btn.grid(row=1, column=0)
    async_mainloop(root)

if __name__ == '__main__':
    test()