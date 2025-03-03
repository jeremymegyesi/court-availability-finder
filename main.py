from async_tkinter_loop import async_handler, async_mainloop
import ctypes
import tkinter as tk
import ttkbootstrap as ttk
from ui_elements import *
from court_finder import CourtFinder
from ttkbootstrap.constants import *
from itertools import accumulate

# Enable DPI awareness (fix blurry text in Windows)
ctypes.windll.shcore.SetProcessDpiAwareness(1)

style = ttk.Style(theme='solar')
style.configure('TLabelframe.Label', font=HEADER_1_FONT)
style.configure('TLabel', font=HEADER_1_FONT)
style.configure('TMenubutton', font=BODY_1_FONT)
style.configure('TButton', font=BUTTON_FONT)
style.configure('Treeview.Heading', font=HEADER_1_FONT)
style.configure('Treeview', font=BODY_1_FONT)

root = style.master
root.option_add('*Menu*Font', ('Arial', 12))
root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')
root.title('Court Finder')
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# center content in middle of window
content_frame = ttk.Frame(root, width=1400)
content_frame.grid(row=0, column=0, sticky='ns')
# set weight for results table, allowing vertical expansion
content_frame.rowconfigure(2, weight=1)

inputs_frame = ttk.LabelFrame(content_frame, text='Enter your availability', style=PRIMARY)
# put frame at center
inputs_frame.grid(row=0, column=0, sticky='nwe', padx=FIELD_FRAME_PAD, pady=FIELD_FRAME_PAD)

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
row1 = DatetimeWindow(availability_frame, 1)
# TODO: add functionality for multiple availability windows
windows = [row1]

def get_user_inputs():
    user_inputs = {}
    user_inputs['duration'] = int(dur_menu_button.get())
    user_inputs['location'] = loc_field_button.get()
    user_inputs['availability'] = [window.get() for window in windows]
    return user_inputs

table_data = []
broker = CourtFinder()

# Results
results_frame = ttk.LabelFrame(content_frame, text='Results', style=PRIMARY)
results_frame.grid(row=2, column=0, sticky='nswe', padx=FIELD_FRAME_PAD, pady=FIELD_FRAME_PAD)
results_frame.rowconfigure(0, weight=1)
results_frame.columnconfigure(0, weight=1)

def create_loc_url(location):
    facility_data = broker.get_facility_data()
    return facility_data[location]['listUrl']

def create_facility_url(location, facility):
    facility_data = broker.get_facility_data()
    facilities = facility_data[location]['facilities']
    facility_id = next((i['facilityId'] for i in facilities if i['name'] == facility), None)
    return f'{facility_data[location]['baseUrl']}/Facility?facilityId={facility_id}'

# Create a Treeview widget (Table)
column_config = {
    'Date': {'width': 250},
    'Start Time': {'width': 200},
    'End Time': {'width': 200},
    'Location': {'width': 300, 'hyperlink': True, 'hyperlink_params': ['Location']},
    'Facility': {'width': 200, 'stretch': True, 'hyperlink': True, 'hyperlink_params': ['Location', 'Facility']}
}
coldata = [{'text': x, 'width': column_config[x].get('width', 200), 'stretch': column_config[x].get('stretch', False)} for x in column_config.keys()]
table = LoadingTable(results_frame, column_config, coldata=coldata, bootstyle=PRIMARY)
external_icon = tk.PhotoImage(file='imgs/external-link-icon.png')

async def populate_table(user_input):
    # Clear rows
    table.delete_rows()
    table.reset_table()
    table.clear_url_map()
    table.start_loading()
    table_data = await broker.find_courts(user_input)
    for row in table_data:
        location = row['location']
        facility = row['facility']
        table.add_to_url_map(f'{location}', create_loc_url(location))
        table.add_to_url_map(f'{location}.{facility}', create_facility_url(location, facility))
        table.insert_row(tk.END,
                values=(
                    row['start_time'].strftime('%a (%b %d)').upper(),
                    row['start_time'].strftime('%I:%M%p'),
                    row['end_time'].strftime('%I:%M%p'),
                    f'{location} 🔗',
                    f'{facility} 🔗'
                )
                )
    table.load_table_data()
    table.stop_loading()

async def search_courts():
    search_button.config(state=tk.DISABLED)
    input = get_user_inputs()
    await populate_table(input)
    search_button.config(state=tk.NORMAL)

search_icon = tk.PhotoImage(file='imgs/search-icon.png')
search_button = ttk.Button(content_frame, text='Search ', image=search_icon, compound='right', command=async_handler(search_courts))
search_button.grid(row=1, column=0, sticky='w', padx=FIELD_FRAME_PAD, pady=BUTTON_BELOW_PAD)

async_mainloop(root)