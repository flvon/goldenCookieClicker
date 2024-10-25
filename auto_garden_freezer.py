from tkinter import *
from tkinter import ttk, filedialog
import os
from pathlib import Path
import logging
import datetime
import threading
import time
import pyautogui
import auxiliary_functions

def get_root_filepath():
    global root_folder
    root_folder = filedialog.askdirectory( title='Select folder', initialdir=INITIAL_DIRECTORY )
    root_folder_label_return.config( text=root_folder )

def close_application():
    global root, stop_threads
    stop_threads.set()
    root.destroy()

def find_and_click_images(img_file_list):
    global logger
    logger.debug( 'Looking for images' )
    max_attempts = 50
    count = 0
    for img in img_file_list:
        search = pyautogui.locateCenterOnScreen( img )
        if search != None:
            pyautogui.click( search )
            logger.info( 'Button found. Garden has been frozen' )
            pyautogui.moveTo( x=10, y=10 )
        else:
            pyautogui.moveTo( x=10, y=10 )
            while count <= max_attempts and search == None:
                logger.info( 'Button not found. Garden still running, trying again in 5 seconds' )
                time.sleep(5)
                search = pyautogui.locateCenterOnScreen( img )
                if search != None:
                    pyautogui.click( search )
                    logger.info( 'Button found. Garden has been frozen' )
                    pyautogui.moveTo( x=10, y=10 )
                    count = 0
                else:
                    logger.info( 'Button not found. Garden still running, trying again in 5 seconds' )
                    count += 1
    

def calculate_stop_time():
    global logger
    global current_time, soil, entry_soil, ticks_to_wait, security_buffer, started_at, end_at
    
    minutes_per_tick = int( soil[entry_soil.get()] )
    
    logger.info(f'Soil is {entry_soil.get()} ({minutes_per_tick} min/tick)')
    
    if security_buffer.get() == None or security_buffer.get() == '':
        ticks_buffer = 0
    else: ticks_buffer = int( security_buffer.get() )
    
    logger.info('Starting now')
    
    seconds_to_wait = int( 60 * minutes_per_tick * ( int( ticks_to_wait.get() ) - 1 - ticks_buffer ) )
    
    current_time = datetime.datetime.now()
    deadline = current_time + datetime.timedelta( seconds=seconds_to_wait )
    
    logger.info(f'Will wait for {seconds_to_wait} seconds and stop at {deadline.strftime( "%Y-%m-%d %H:%M:%S" )}')
    
    start_text = f'Started at: {current_time.strftime( "%Y-%m-%d %H:%M:%S" )}'
    end_text = f'Will wait until: {deadline.strftime( "%Y-%m-%d %H:%M:%S" )}'
    
    started_at.config( text=start_text )
    end_at.config( text=end_text )
    
    root.update()
    
    return seconds_to_wait

def wait_and_freeze(wait_time, update_frequency, freeze_buttons):
    time_elapsed = 0
    time_elapsed_text = f'Time elapsed: { str( round(time_elapsed) ) }/{ str(wait_time) } seconds'
    time_elapsed_label.config( text=time_elapsed_text )
    root.update()
    while time_elapsed < wait_time and not stop_threads.is_set():
        before = datetime.datetime.now()
        time.sleep(update_frequency)
        after = datetime.datetime.now()
        time_diff = after - before
        time_elapsed += time_diff.total_seconds()
        time_elapsed_text = f'Time elapsed: { str( round(time_elapsed) ) }/{ str(wait_time) } seconds'
        try: time_elapsed_label.config( text=time_elapsed_text )
        except: print( 'Tkinter window not found' )
        else: root.update()
        
    if stop_threads.is_set():
        logger.info( 'Execution cancelled by user')
    elif time_elapsed >= wait_time:
        logger.info( 'Finished waiting, freezing garden' )
        find_and_click_images(freeze_buttons)
    else: logger.info( 'Exception happened' )
    
    

def start_execution():
    # Getting settings
    global root_folder_label_return, entry_screen_type, update_frequency
    global logger

    # Setting logging
    l_root_folder = root_folder_label_return.cget('text')
    logger = auxiliary_functions.set_logging( l_root_folder, log_file_name='garden_freezer' )

    l_screen_type = entry_screen_type.get()

    # Setting image folders
    if l_screen_type == 'Monitor':
        images_folder = os.path.join( l_root_folder, 'searched_images', 'monitor', 'garden' )
    else:
        images_folder = os.path.join( l_root_folder, 'searched_images', 'default', 'garden' )

    target_images = [ os.path.join(images_folder, imgs) for imgs in os.listdir( os.path.join(images_folder) ) if os.path.isfile( os.path.join(images_folder, imgs) ) ]
    
    sleep_time = calculate_stop_time()
    l_update_frequency = int(update_frequency.get())
    
    garden_freezer = threading.Thread( target=wait_and_freeze, args=( sleep_time, l_update_frequency, target_images, ) ) # Using daemon=True as added security
    garden_freezer.start()
    threads_list.append( garden_freezer )



INITIAL_DIRECTORY = os.path.join( os.environ['USERPROFILE'], 'Desktop', 'clicker' )
DEFAULT_SCREEN_TYPE = "Monitor"

# Setting soil types
soil = {
    "Dirt": "5"
    ,"Fertilizer": "3"
	,"Clay": "15"
    ,"Pebbles": "5"
    ,"Wood chips": "5"
}

root = Tk()
root.title("Cookie Clicker automations")

frame = ttk.Frame( root, padding=(5, 5) )
frame.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

row_num = 1
column_num = 1

# Select root folder
root_folder_label = ttk.Label( frame, text='Select image root directory' )
root_folder_label.grid( row=row_num, column=column_num, sticky=(N, S, W, E))
column_num += 1
default_filepath = INITIAL_DIRECTORY
root_folder_label_return = ttk.Label( frame, padding=(20, 0), text=default_filepath, width=-10, background='white' )
root_folder_label_return.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
root_folder_button = ttk.Button( frame, text='...', command=get_root_filepath )
root_folder_button.grid( row=row_num, column=column_num, sticky=W )

row_num += 1
column_num = 1

# Separator
sep = ttk.Separator( frame, orient='horizontal' )
sep.grid( row=row_num, columnspan=4, sticky=EW )

row_num += 1
column_num = 1

# Select if you're using a monitor or your laptop default screen
static_label = ttk.Label( frame, text='Select the screen type' )
static_label.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
entry_screen_type = ttk.Combobox( frame, values=[ 'Monitor', 'Laptop screen' ] )
entry_screen_type.current( 0 )
entry_screen_type.grid( row=row_num, column=column_num, sticky=W )

row_num += 1
column_num = 1

# Separator
sep = ttk.Separator( frame, orient='horizontal' )
sep.grid( row=row_num, columnspan=4, sticky=(N, S, W, E) )

row_num += 1
column_num = 1

# Select soil
static_label = ttk.Label( frame, text='Select the soil' )
static_label.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
entry_soil = ttk.Combobox( frame, values=list( soil.keys() ) )
entry_soil.current( 0 )
entry_soil.grid( row=row_num, column=column_num, sticky=W )

row_num += 1
column_num = 1

# Enter how many ticks until the plant will take to reach maturity
static_label = ttk.Label( frame, text='How many ticks until maturity?' )
static_label.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
ticks_to_wait = StringVar()
ticks_entry = ttk.Entry( frame, textvariable=ticks_to_wait, justify='center' )
ticks_entry.grid( row=row_num, column=column_num, sticky=W )

row_num += 1
column_num = 1

static_label = ttk.Label( frame, text='How many ticks\nof security buffer?' )
static_label.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
security_buffer = StringVar()
buffer_entry = ttk.Entry( frame, textvariable=security_buffer, justify='center' )
buffer_entry.insert( index=0, string="2" )
buffer_entry.grid( row=row_num, column=column_num, sticky=W )
row_num += 1
column_num = 1
static_label = ttk.Label( frame, text='If left empty or zero, garden will freeze before the last tick, but some plants reach maturity before expected' )
static_label.grid( row=row_num, column=column_num, sticky=(N, S, W, E), columnspan=3 )

row_num += 1
column_num = 1

# Separator
sep = ttk.Separator( frame, orient='horizontal' )
sep.grid( row=row_num, columnspan=4, sticky=(N, S, W, E) )

row_num += 1
column_num = 1

# Update frequency
static_label = ttk.Label( frame, text='Update frequency (seconds)' )
static_label.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
update_frequency = StringVar()
frequency_entry = ttk.Entry( frame, textvariable=update_frequency, justify='center' )
frequency_entry.insert( index=0, string="10" )
frequency_entry.grid( row=row_num, column=column_num, sticky=W )

row_num += 1
column_num = 1

# Separator
sep = ttk.Separator( frame, orient='horizontal' )
sep.grid( row=row_num, columnspan=4, sticky=(N, S, W, E) )

row_num += 1
column_num = 2

# Buttons to start and cancel the applications
start_button = Button( frame, text='Start', bg='#ccffcc', command=start_execution )
start_button.grid( row=row_num, column=column_num, sticky=E )
column_num += 1
cancel_button = Button( frame, text='Cancel/Stop', bg='#ffcccc', command=close_application )
cancel_button.grid( row=row_num, column=column_num, sticky=W )

row_num += 1
column_num = 1

# Run information entry
started_at = ttk.Label( frame, text='Time started:' )
started_at.grid( row=row_num, column=column_num, sticky=W )
column_num += 1
end_at = ttk.Label( frame, text='Will wait until:' )
end_at.grid( row=row_num, column=column_num, sticky=W )
column_num += 1
time_elapsed_label = ttk.Label( frame, text='' )
time_elapsed_label.grid( row=row_num, column=column_num, sticky=W )

for child in frame.winfo_children(): 
    child.grid_configure(padx=5, pady=5)
    
threads_list = []
stop_threads = threading.Event()

root.mainloop()

for t in threads_list:
	t.join()