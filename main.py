import ctypes
import tkinter as tk
import ttkbootstrap as ttk
from async_tkinter_loop import async_handler, async_mainloop
from constants import *
from ui_elements import *
from court_finder import CourtFinder
from ttkbootstrap.constants import *
import uuid

class App:
    def __init__(self, root):
        self.root = root
        self.style = ttk.Style('courteous')
        self.avail_rows = []
        self.broker = CourtFinder()
        self.configure_styles()
        self.setup_ui()

    def configure_styles(self):
        self.style.configure('TLabelframe.Label', font=HEADER_1_FONT)
        self.style.configure('TLabel', font=HEADER_1_FONT)
        self.style.configure('TMenubutton', font=BODY_1_FONT)
        self.style.configure('secondary.Outline.TButton', font=BODY_1_FONT, relief=FLAT, borderwidth=0)
        self.style.map('secondary.Outline.TButton', background=[('active', self.style.lookup('TFrame', 'background'))])
        self.style.configure('TButton', font=BUTTON_FONT)
        self.style.configure('Treeview.Heading', font=HEADER_1_FONT)
        self.style.configure('Treeview', font=BODY_1_FONT)

    def setup_ui(self):
        self.root.option_add('*Menu*Font', BODY_1_FONT)
        self.root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')
        self.root.title('Court Finder')
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Center content in middle of window
        self.content_frame = ttk.Frame(self.root, width=1400)
        self.content_frame.grid(row=0, column=0, sticky='ns')
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(2, weight=1)

        self.setup_inputs()
        self.setup_results()
        self.setup_buttons()

    def setup_inputs(self):
        self.inputs_frame = ttk.LabelFrame(self.content_frame, text='Enter your availability', style=INFO)
        self.inputs_frame.grid(row=0, column=0, sticky='nwe', padx=FIELD_FRAME_PAD, pady=FIELD_FRAME_PAD)

        self.inputs_r1_frame = ttk.Frame(self.inputs_frame)
        self.inputs_r1_frame.grid(row=0, column=0, sticky='w')

        # Availability inputs
        self.dur_menu_params = {
            'menu_options': ['30', '60', '90', '120'],
            'default_value': '90'
        }
        self.dur_menu_button = FieldInput(self.inputs_r1_frame, 0, 0, type=FieldInputType.DROPDOWN, label_text='Duration:',
                                          suffix='mins', params=self.dur_menu_params)

        self.loc_menu_params = {
            'menu_options': ['Any', 'Oak Bay Recreation', 'Panorama Recreation'],
            'default_value': 'Any'
        }
        self.loc_menu_button = FieldInput(self.inputs_r1_frame, 0, 1, type=FieldInputType.DROPDOWN, label_text='Location:',
                                          params=self.loc_menu_params)

        # Datetime ranges
        self.availability_frame = ttk.Frame(self.inputs_frame)
        self.availability_frame.grid(row=1, column=0, sticky='w', padx=FIELD_FRAME_PAD)
        self.availability_label = ttk.Label(self.availability_frame, text='Available times:', font=HEADER_1_FONT)
        self.availability_label.grid(row=0, column=0, sticky='w', padx=FIELD_LABEL_PAD, pady=FIELD_LABEL_PAD)

        # Availability windows
        self.avail_windows_frame = ttk.Frame(self.availability_frame)
        self.avail_windows_frame.grid(row=1, column=0)
        self._delete_icon = tk.PhotoImage(file='imgs/trash-icon.png')
        self.add_avail_row()
        self.add_window_button = ttk.Button(self.availability_frame, text='+ Add Availability', style='secondary.Outline.TButton',
                                            command=self.add_avail_row)
        self.add_window_button.grid(row=2, column=0, sticky='w', padx=FIELD_FRAME_PAD, pady=(0, FIELD_FRAME_PAD))

    def setup_results(self):
        self.results_frame = ttk.LabelFrame(self.content_frame, text='Results', style=INFO)
        self.results_frame.grid(row=2, column=0, sticky='nswe', padx=FIELD_FRAME_PAD, pady=FIELD_FRAME_PAD)
        self.results_frame.rowconfigure(0, weight=1)
        self.results_frame.columnconfigure(0, weight=1)

        # Create a Treeview widget (Table)
        column_config = {
            'Date': {'width': 250},
            'Start Time': {'width': 200},
            'End Time': {'width': 200},
            'Location': {'width': 300, 'hyperlink': True, 'hyperlink_params': ['Location']},
            'Facility': {'width': 200, 'stretch': True, 'hyperlink': True, 'hyperlink_params': ['Location', 'Facility']}
        }
        coldata = [{'text': x, 'width': column_config[x].get('width', 200), 'stretch': column_config[x].get('stretch', False)} for x in column_config.keys()]
        self.table = LoadingTable(self.results_frame, column_config, coldata=coldata, bootstyle=PRIMARY)
        self._external_icon = tk.PhotoImage(file='imgs/external-link-icon.png')

    def setup_buttons(self):
        self.input_buttons_frame = ttk.Frame(self.content_frame)
        self.input_buttons_frame.grid(row=1, column=0, sticky='w', padx=FIELD_FRAME_PAD, pady=BUTTON_BELOW_PAD_Y)

        self.search_icon = tk.PhotoImage(file='imgs/search-icon.png')
        self.search_button = ttk.Button(self.input_buttons_frame, text=' Search', image=self.search_icon, compound='left', command=async_handler(self.search_courts))
        self.search_button.grid(row=0, column=0, padx=(0, FIELD_LABEL_PAD))

        self.reset_icon = tk.PhotoImage(file='imgs/reset-icon.png')
        self.reset_inputs_button = ttk.Button(self.input_buttons_frame, text=' Reset', image=self.reset_icon, compound='left', style=SECONDARY, command=self.reset_inputs)
        self.reset_inputs_button.grid(row=0, column=1)

    def add_avail_row(self):
        row_frame = ttk.Frame(self.avail_windows_frame)
        row_frame.grid(row=len(self.avail_rows), column=0, sticky='nswe', padx=FIELD_FRAME_PAD, pady=(0, FIELD_FRAME_PAD))
        window = DatetimeWindow(row_frame)
        row_id = uuid.uuid4()
        delete_button = ttk.Button(row_frame, image=self._delete_icon, compound='left', style=DANGER, command=lambda row=row_id: self.remove_row(row))
        delete_button.grid(row=0, column=1, sticky='w', padx=DELETE_BUTTON_PAD_X)
        self.avail_rows.append({'row_id': row_id, 'row_frame': row_frame, 'window': window, 'delete_button': delete_button})
        # Check if delete should be disabled
        if len(self.avail_rows) == 1:
            delete_button.grid_remove()
        else:
            # Make sure previous row's delete is reenabled
            self.avail_rows[-2]['delete_button'].grid_configure(row=0, column=1)

    def remove_row(self, row_id):
        index = next((i for i, row in enumerate(self.avail_rows) if row['row_id'] == row_id), None)
        if index is not None:
            self.avail_rows[index]['row_frame'].destroy()
            del self.avail_rows[index]
        # Reconfigure grid rows
        for i, row in enumerate(self.avail_rows):
            row['row_frame'].grid_configure(row=i)
        # Check if delete should be disabled
        if len(self.avail_rows) == 1:
            self.avail_rows[0]['delete_button'].grid_remove()

    def get_user_inputs(self):
        user_inputs = {}
        user_inputs['duration'] = int(self.dur_menu_button.get())
        user_inputs['location'] = self.loc_menu_button.get()
        user_inputs['availability'] = [row['window'].get() for row in self.avail_rows]
        return user_inputs

    def reset_inputs(self):
        self.dur_menu_button.set(self.dur_menu_params['default_value'])
        self.loc_menu_button.set(self.loc_menu_params['default_value'])
        for row in self.avail_rows:
            row['row_frame'].destroy()
        self.avail_rows = []
        self.add_avail_row()

    async def populate_table(self, user_input):
        # Clear rows
        self.table.delete_rows()
        self.table.reset_table()
        self.table.clear_url_map()
        self.table.start_loading()
        table_data = await self.broker.find_courts(user_input)
        for row in table_data:
            location = row['location']
            facility = row['facility']
            self.table.add_to_url_map(f'{location}', self._create_loc_url(location))
            self.table.add_to_url_map(f'{location}.{facility}', self._create_facility_url(location, facility))
            self.table.insert_row(tk.END,
                    values=(
                        row['start_time'].strftime('%a (%b %d)').upper(),
                        row['start_time'].strftime('%I:%M%p'),
                        row['end_time'].strftime('%I:%M%p'),
                        f'{location} 🔗',
                        f'{facility} 🔗'
                    )
                    )
        self.table.load_table_data()
        self.table.stop_loading()

    async def search_courts(self):
        self.search_button.config(state=tk.DISABLED)
        input = self.get_user_inputs()
        await self.populate_table(input)
        self.search_button.config(state=tk.NORMAL)

    def _create_loc_url(self, location):
        facility_data = self.broker.get_facility_data()
        return facility_data[location]['listUrl']

    def _create_facility_url(self, location, facility):
        facility_data = self.broker.get_facility_data()
        facilities = facility_data[location]['facilities']
        facility_id = next((i['facilityId'] for i in facilities if i['name'] == facility), None)
        return f'{facility_data[location]["baseUrl"]}/Facility?facilityId={facility_id}'

if __name__ == '__main__':
    # Enable DPI awareness (fix blurry text in Windows)
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

    root = ttk.Window(themename='solar')
    app = App(root)
    async_mainloop(root)