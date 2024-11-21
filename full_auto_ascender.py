import threading
import time
import pyautogui
import os
from pathlib import Path
import keyboard
from tkinter import *
from tkinter import ttk, filedialog
import auxiliary_functions

def close_application():
    global root, stop_threads
    stop_threads.set()
    root.destroy()

def get_root_filepath():
    global root_folder
    root_folder = filedialog.askdirectory( title='Select folder', initialdir=os.path.join( os.environ['USERPROFILE'], 'Desktop', 'clicker' ) )
    root_folder_label_return.config( text=root_folder )
    
def start_threads():
    # Getting settings
    global root_folder_label_return, entry_screen_type
    global logger
    global threads_list
    global configs

    # Setting logging
    l_root_folder = root_folder_label_return.cget('text')
    logger = auxiliary_functions.set_logging( l_root_folder, log_file_name='auto_ascender' )
    
    l_entry_screen_type = entry_screen_type.get()
    if l_entry_screen_type == 'Monitor':
        images_folder = os.path.join(l_root_folder, 'searched_images', 'monitor', 'ascender')
    else:
        images_folder = os.path.join(l_root_folder, 'searched_images', 'default', 'ascender')
    
	# Setting and starting thread
    t = threading.Thread( target=auto_ascender, args=( images_folder, ), daemon=True ) # Using daemon=True as added security
    t.start()
    threads_list.append( t )
    t = threading.Thread(target=check_stop_key, daemon=True)
    t.start()
    threads_list.append( t )
    return threads_list

def auto_ascender(images_folder):
    global logger, hk
    
    target_images = [ os.path.join(images_folder, imgs) for imgs in os.listdir( images_folder ) if os.path.isfile( os.path.join(images_folder, imgs) ) ]
    sorted_target_images = sorted(target_images)
    prestige_check_images = [ os.path.join(images_folder, 'prestige_check', imgs) for imgs in os.listdir(os.path.join(images_folder, 'prestige_check')) if os.path.isfile( os.path.join(images_folder, 'prestige_check', imgs) ) ]
    
    click_coordinates = [pyautogui.locateCenterOnScreen(img) for img in sorted_target_images]

    logger.info( 'Starting run' )
    count_ascensions = 0
    i = 0
    ascend_button = (used_coordinates_x[i].get(), used_coordinates_y[i].get())
    i += 1
    reincarnate_button = (used_coordinates_x[i].get(), used_coordinates_y[i].get())
    i += 1
    confirm_button = (used_coordinates_x[i].get(), used_coordinates_y[i].get())
    i += 1
    buy_all_button = (used_coordinates_x[i].get(), used_coordinates_y[i].get())
    while not stop_threads.is_set():
        for coords in click_coordinates:
            pyautogui.click( coords, clicks=5 )
            for img in prestige_check_images:
                should_ascend = pyautogui.locateCenterOnScreen(img)
                if should_ascend:
                    pyautogui.click( should_ascend )
                    time.sleep(0.05)
                    pyautogui.click( ascend_button )
                    time.sleep(0.1)
                    keyboard.send('esc')
                    time.sleep(0.05)
                    pyautogui.click( reincarnate_button )
                    time.sleep(0.05)
                    pyautogui.click( confirm_button )
                    time.sleep(0.05)
                    pyautogui.moveTo( buy_all_button )
                    count_ascensions += 1
                    logger.info( 'Number of ascensions this run: %d' % count_ascensions )
        time.sleep(0.05)
    logger.debug( 'Leaving thread loop' )
    return

def check_stop_key():
    while not stop_threads.is_set():
        if keyboard.is_pressed(hk.get()) and not stop_threads.is_set():
            close_application()
        time.sleep(0.05)
    return 0

def read_config_file_and_update_dialogs():
    global root_folder_label_return
    global logger
    global configs
    config_file = filedialog.askopenfilename( title='Select folder', initialdir=INITIAL_DIRECTORY, filetypes=[('Configuration files', '*.cfg')] )
    try: configs = auxiliary_functions.read_configs( config_file )
    except: print( f'Error: couldn\'t read file\nResponse from dialog was {config_file}' )
    i = 0
    for coords in configs.values():
        used_coordinates_x[i].set( coords['x'] )
        used_coordinates_y[i].set( coords['y'] )
        i += 1
        
def save_configs():
    global used_coordinates_x, used_coordinates_y
    keys = [
        'legacy_button_coords'
		,'ascend_button_coords'
		,'reincarnate_button_coords'
		,'confirm_button_coords'
		,'buy_all_button_coords'
	]
    config_file = filedialog.asksaveasfilename( title='Select file to save', initialdir=INITIAL_DIRECTORY, filetypes=[('Configuration files', '*.cfg')] )
    confs = {}
    i = 0
    for key in keys:
        confs[key] = { 'x': used_coordinates_x[i].get(), 'y': used_coordinates_y[i].get() }
        i += 1
    auxiliary_functions.save_configs_to_file( config_file, confs )

INITIAL_DIRECTORY = os.path.join( os.environ['USERPROFILE'], 'Desktop', 'clicker' )

root = Tk()
root.title("Cookie Clicker automations")

default_coordinates = [
	( 960, 610 ) # DEFAULT_ASCEND_BUTTON
	,( 960, 150 ) # DEFAULT_REINCARNATE_BUTTON
	,( 940, 560 ) # DEFAULT_CONFIRM_BUTTON
	,( 1820, 190 ) # DEFAULT_BUY_ALL_BUTTON
]

default_labels = [
    'Ascend button'
    ,'Reincarnate button'
    ,'Confirm button'
    ,'Buy all upgrades button'
]

used_coordinates_x = [
	StringVar()
	,StringVar()
	,StringVar()
	,StringVar()
]

used_coordinates_y = [
	StringVar()
	,StringVar()
	,StringVar()
	,StringVar()
]

threads_list = []
stop_threads = threading.Event()

frame = ttk.Frame(root, padding="5 5 12 12")
frame.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

row_num = 1
column_num = 1

# Read config file
config_label = ttk.Label( frame, text='Open configuration file' )
config_label.grid( row=row_num, column=column_num, sticky=(N, S, W, E))
column_num += 1
config_button = ttk.Button( frame, text='...', command=read_config_file_and_update_dialogs )
config_button.grid( row=row_num, column=column_num, sticky=W )
column_num += 1
save_config_button = Button( frame, text='Save configs', command=save_configs )
save_config_button.grid( row=row_num, column=column_num, sticky=W )

row_num += 1
column_num = 1

# Separator
sep = ttk.Separator( frame, orient='horizontal' )
sep.grid( row=row_num, columnspan=4, sticky=EW )

row_num += 1
column_num = 1

# Select root folder
root_folder_label = ttk.Label( frame, text='Select image root directory' )
root_folder_label.grid( row=row_num, column=column_num, sticky=(N, S, W, E))
column_num += 1
root_folder = StringVar()
default_filepath = os.path.join( os.environ['USERPROFILE'], 'Desktop', 'clicker' )
root_folder_label_return = ttk.Label( frame, padding=(15, 0), text=default_filepath, width=-10, background='white' )
root_folder_label_return.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
root_folder_button = ttk.Button( frame, text='...', command=get_root_filepath )
root_folder_button.grid( row=row_num, column=column_num, sticky=(W, E) )

row_num += 1
column_num = 1

# Select if you're using a monitor or your laptop default screen
screen_type_text = ttk.Label( frame, text='Select the screen type' )
screen_type_text.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
entry_screen_type = ttk.Combobox( frame, values=[ 'Monitor', 'Laptop screen' ] )
entry_screen_type.current( 0 )
entry_screen_type.grid( row=row_num, column=column_num, sticky=W )

row_num += 1
column_num = 1

# Separator
sep = ttk.Separator( frame, orient='horizontal' )
sep.grid( row=row_num, columnspan=4, sticky=EW )

row_num += 1
column_num = 1

# Entry for the button to be checked
static_label = ttk.Label( frame, text='Key that automatically ascends', )
static_label.grid( row=row_num, column=column_num, sticky=W )
column_num += 1
hk = StringVar()
hk_entry = ttk.Entry( frame, textvariable=hk, justify='center' )
hk_entry.insert( index=0, string='q' )
hk_entry.grid( row=row_num, column=column_num, sticky=W )

row_num += 1
column_num = 1

# Separator
sep = ttk.Separator( frame, orient='horizontal' )
sep.grid( row=row_num, columnspan=4, sticky=EW )

row_num += 1
column_num = 1

# Creates the entries for coordinates
column_num = 2
static_label = ttk.Label( frame, text='X', anchor='center' )
static_label.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
static_label = ttk.Label( frame, text='Y', anchor='center' )
static_label.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )

row_num += 1
column_num = 1

labels = []
x_entries = []
y_entries = []
for i in range(len( default_coordinates )):
    x, y = default_coordinates[i]
    label = ttk.Label( frame, text=default_labels[i] )
    label.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
    labels.append( label )
    column_num += 1
    x_entry = ttk.Entry( frame, textvariable=used_coordinates_x[i], justify='center' )
    x_entry.insert( index=0, string=x )
    x_entry.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
    x_entries.append( x_entry )
    column_num += 1
    y_entry = ttk.Entry( frame, textvariable=used_coordinates_y[i], justify='center' )
    y_entry.insert( index=0, string=y )
    y_entry.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
    y_entries.append( y_entry )
    row_num += 1
    column_num = 1

column_num = 2

# Buttons to start and cancel the application
start_button = Button( frame, text='Start', bg='#ccffcc', command=start_threads )
start_button.grid( row=row_num, column=column_num, sticky=E )
column_num += 1
cancel_button = Button( frame, text='Cancel/Stop', bg='#ffcccc', command=close_application )
cancel_button.grid( row=row_num, column=column_num, sticky=W )

for child in frame.winfo_children(): 
    child.grid_configure(padx=5, pady=5)

root.mainloop()