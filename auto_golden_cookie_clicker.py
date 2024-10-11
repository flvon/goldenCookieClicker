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

def find_and_click_images(target, img_file_list, sleep):
    global logger
    clicks = 0
    time.sleep( 5 )
    while not stop_threads.is_set():
        logger.debug( 'Looking for %s' % target )
        for img in img_file_list:
            search = pyautogui.locateCenterOnScreen( img )

            if search != None:
                x, y = search
                pyautogui.click( x=x, y=y )
                clicks += 1
                logger.info( '%s found. Number of clicks this run: %d' % (target, clicks) )
        time.sleep( sleep )
    logger.debug( 'Leaving thread loop' )
    return

def read_config_file_and_update_dialogs():
    global root_folder_label_return, entry_screen_type, fortune, fortune_sleep, entry_season, cookie_sleep, reindeer_sleep
    global logger
    global configs
    config_file = filedialog.askopenfilename( title='Select folder', initialdir=INITIAL_DIRECTORY, filetypes=[('Configuration files', '*.cfg')] )
    try: configs = auxiliary_functions.read_configs( config_file )
    except: print( f'Error: couldn\'t read file\nResponse from dialog was {config_file}' )
    else:
        root_folder_label_return.config( text=configs['root_path'] )
        if configs['screen_type'] == 'Monitor': entry_screen_type.current( 0 )
        else: entry_screen_type.current( 1 )
        fortune.set( configs['click_fortune'] )
        fortune_sleep.set( configs['fortune_sleep'] )
        entry_season.current( configs['season'] )
        cookie_sleep.set( configs['golden_cookie_sleep'] )
        reindeer_sleep.set( configs['reindeer_sleep'] )

def save_configs():
    config_file = filedialog.asksaveasfilename( title='Select file to save', initialdir=INITIAL_DIRECTORY, filetypes=[('Configuration files', '*.cfg')] )
    confs={}
    confs['root_path'] = root_folder_label_return.cget('text')
    confs['screen_type'] = entry_screen_type.get()
    confs['click_fortune'] = fortune.get()
    confs['fortune_sleep'] = fortune_sleep.get()
    confs['season'] = str( entry_season.current() )
    confs['golden_cookie_sleep'] = cookie_sleep.get()
    confs['reindeer_sleep'] = reindeer_sleep.get()
    auxiliary_functions.save_configs_to_file( config_file, confs )

def start_threads():
    # Getting settings
    global root_folder_label_return, entry_screen_type, fortune, fortune_sleep, entry_season, cookie_sleep, reindeer_sleep
    global logger
    global threads_list
    global configs

    # Setting logging
    l_root_folder = root_folder_label_return.cget('text')
    logger = auxiliary_functions.set_logging( l_root_folder, log_file_name='golden_cookie_clicker' )

    l_screen_type = entry_screen_type.get()
    l_click_fortune = fortune.get()
    l_fortune_sleep = float(fortune_sleep.get())
    l_entry_season = entry_season.current()
    l_cookie_sleep = float(cookie_sleep.get())
    l_reindeer_sleep = float(reindeer_sleep.get())


    logger.info( 'Starting application' )

    season_folder_list = [
        'christmas'
        ,'halloween'
        ,'valentines'
        ,'business_day'
        ,'easter'
    ]


    # Setting image folders
    if l_screen_type == 'Monitor':
        images_folder = os.path.join( l_root_folder, 'searched_images', 'monitor' )
    else:
        images_folder = os.path.join( l_root_folder, 'searched_images', 'default' )

    if l_entry_season != 0:
        season_folder = season_folder_list[l_entry_season - 1]
    else: season_folder = 'no season'

    logger.info( f"""Configurations:
Root folder: {str(l_root_folder)}
Screen type: {l_screen_type}
Season: {season_folder}
Click fortune cookie: {str(l_click_fortune)}
Sleep timess: 
Golden Cookie: {str(l_cookie_sleep)}  |  Fortune:{str(l_fortune_sleep)}  |  Reindeer: {str(l_reindeer_sleep)}""" )


    # Setting thread that clicks on the golden cookie
    logger.info( 'Starting golden cookie clicker' )
    if l_entry_season == 0 or l_entry_season == 1:
        target_images = [ os.path.join( images_folder, 'golden_cookie.png' ) ]
    else:
        target_images = [ os.path.join(images_folder, season_folder, imgs) for imgs in os.listdir( os.path.join(images_folder, season_folder) ) if os.path.isfile( os.path.join(images_folder, season_folder, imgs) ) ]
    golden_cookie_clicker = threading.Thread( target=find_and_click_images, args=( 'Golden Cookie', target_images, l_cookie_sleep, ), daemon=True ) # Using daemon=True as added security
    golden_cookie_clicker.start()
    threads_list.append( golden_cookie_clicker )

    # Setting thread that clicks on reindeer if Christmas Season is active
    if l_entry_season == 1:
        logger.info( 'Starting reindeer clicker' )
        target_images = [ os.path.join(images_folder, season_folder, imgs) for imgs in os.listdir( os.path.join(images_folder, season_folder) ) if os.path.isfile( os.path.join(images_folder, season_folder, imgs) ) ]
        reindeer_clicker = threading.Thread( target=find_and_click_images, args=( 'Reindeer', target_images, l_reindeer_sleep, ), daemon=True ) # Using daemon=True as added security
        reindeer_clicker.start()
        threads_list.append( reindeer_clicker )

    if l_click_fortune == 1:
        # Setting thread that clicks on the fortune news ticker
        logger.info( 'Starting fortune news ticker clicker' )
        target_images = [ os.path.join( images_folder, 'fortune_cookie.png' ) ]
        fortune_clicker = threading.Thread( target=find_and_click_images, args=( 'Fortune', target_images, l_fortune_sleep, ), daemon=True ) # Using daemon=True as added security
        fortune_clicker.start()
        threads_list.append( fortune_clicker )

INITIAL_DIRECTORY = os.path.join( os.environ['USERPROFILE'], 'Desktop', 'clicker' )
DEFAULT_SCREEN_TYPE = "Monitor"
DEFAULT_CLICK_FORTUNE = "0"
DEFAULT_FORTUNE_SLEEP = "5.0"
DEFAULT_SEASON = "0"
DEFAULT_GOLDEN_COOKIE_SLEEP = "5.0"
DEFAULT_REINDEER_SLEEP = "5.0"

# Initializing config
configs = {}


root = Tk()
root.title("Cookie Clicker automations")

frame = ttk.Frame( root, padding=(5, 5) )
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

# Create folder structure if you want to
folder_structure = ttk.Label( frame, text='If you haven\'t done it before,\ncreate the folder structure now' )
folder_structure.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
folder_structure_button = ttk.Button( frame, text='Create', command=lambda: auxiliary_functions.create_folder_structure( root_folder_label_return.cget('text') ) )
folder_structure_button.grid( row=row_num, column=column_num, sticky=W )

row_num += 1
column_num = 1

# Separator
sep = ttk.Separator( frame, orient='horizontal' )
sep.grid( row=row_num, columnspan=4, sticky=EW )

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
sep.grid( row=row_num, columnspan=4, sticky=(N, S, W, E) )

row_num += 1
column_num = 1

# Select if you want the program to click on fortune cookie news tickers
fortune = IntVar()
fortune_cookie = ttk.Checkbutton( frame, variable=fortune, text='Click fortune news tickers' )
fortune_cookie.grid( row=row_num, column=column_num, sticky=W )
column_num += 1
fortune_cookie_sleep = ttk.Label( frame, text='Sleep times (seconds)' )
fortune_cookie_sleep.grid( row=row_num, column=column_num, sticky=E )
column_num += 1
fortune_sleep = StringVar()
fortune_sleep_entry = ttk.Entry( frame, textvariable=fortune_sleep, justify='center' )
fortune_sleep_entry.insert( index=0, string=DEFAULT_FORTUNE_SLEEP )
fortune_sleep_entry.grid( row=row_num, column=column_num, sticky=W )

row_num += 1
column_num = 1

# Select the season
season_text = ttk.Label( frame, text='Select the season' )
season_text.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
entry_season = ttk.Combobox( frame, justify='center' , values=[ 'No season', 'Christmas', 'Halloween', 'Valentine\'s', 'Business Day', 'Easter' ] )
entry_season.current( 0 )
entry_season.grid( row=row_num, column=column_num, sticky=W )

row_num += 1
column_num = 1

# Sleep times for golden cookie in seconds
cookie_sleep_text = ttk.Label( frame, text='Sleep times for golden cookie (seconds)' )
cookie_sleep_text.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
cookie_sleep = StringVar()
cookie_sleep_entry = ttk.Entry( frame, textvariable=cookie_sleep, justify='center' )
cookie_sleep_entry.insert( index=0, string=DEFAULT_GOLDEN_COOKIE_SLEEP )
cookie_sleep_entry.grid( row=row_num, column=column_num, sticky=W )

row_num += 1
column_num = 1

# Sleep times for reindeer in seconds
reindeer_sleep_text = ttk.Label( frame, text='Sleep times for reindeer (seconds)' )
reindeer_sleep_text.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
reindeer_sleep = StringVar()
reindeer_sleep_entry = ttk.Entry( frame, textvariable=reindeer_sleep, justify='center' )
reindeer_sleep_entry.insert( index=0, string=DEFAULT_REINDEER_SLEEP )
reindeer_sleep_entry.grid( row=row_num, column=column_num, sticky=W )

row_num += 1
column_num = 2

# Buttons to start and cancel the applications
start_button = Button( frame, text='Start', bg='#ccffcc', command=start_threads )
start_button.grid( row=row_num, column=column_num, sticky=E )
column_num += 1
cancel_button = Button( frame, text='Cancel/Stop', bg='#ffcccc', command=close_application )
cancel_button.grid( row=row_num, column=column_num, sticky=W )

for child in frame.winfo_children(): 
    child.grid_configure(padx=5, pady=5)

threads_list = []
stop_threads = threading.Event()

root.mainloop()