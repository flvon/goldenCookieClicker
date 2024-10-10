from tkinter import *
from tkinter import ttk, filedialog
import os
from pathlib import Path
import logging
import datetime
import threading
import time
import pyautogui

def get_root_filepath():
    global root_folder
    root_folder = filedialog.askdirectory( title='Select folder', initialdir=os.path.join( os.environ['USERPROFILE'], 'Desktop', 'clicker' ) )
    root_folder_label_return.config( text=root_folder )
    
def create_folder_structure():
    folder_list_level1 = [
          'logs'
          ,'searched_images'
    ]
    screen_type = [
         'default'
         ,'monitor'
    ]
    seasons = [
         'christmas'
         ,'halloween'
         ,'valentines'
         ,'business_day'
         ,'easter'
    ]
     
    global root_folder
    folder_path = os.path.join( root_folder, folder_list_level1[0] )
    Path( folder_path ).mkdir( parents=True, exist_ok=True )
    folder_path = os.path.join( root_folder, folder_list_level1[1] )
    for level2 in screen_type:
        for level3 in seasons:
            directory = os.path.join( folder_path, level2, level3 )
            Path( directory ).mkdir( parents=True, exist_ok=True )

def close_application():
    global root, stop_threads
    stop_threads.set()
    root.destroy()

def set_logging(root_folder):
    #Setting logging path and file
    now = datetime.datetime.now()
    dt = now.strftime( "%Y%m%d_%H%M" )
    log_folder = os.path.join( root_folder, 'logs' )
    log_file_path = os.path.join( log_folder, dt + '_golden_cookie_clicker.log' )

    # Creating logging file if it doesn't exist
    Path( log_folder ).mkdir( parents=True, exist_ok=True )
    file = open( log_file_path, 'a' )
    file.close()

    # Setting loggers
    global logger
    logger.setLevel( 'DEBUG' )
    formatter = logging.Formatter( fmt="{asctime} - {levelname} - {message}"
                                  ,style="{"
                                  ,datefmt="%Y-%m-%d %H:%M:%S"
                                  )

    console_handler = logging.StreamHandler()
    console_handler.setLevel( 'INFO' ) # Change this to DEBUG if debugging the script is needed
    console_handler.setFormatter( formatter )
    logger.addHandler( console_handler )

    file_handler = logging.FileHandler( filename=log_file_path, mode='a', encoding='utf-8' )
    file_handler.setLevel( 'INFO' )
    file_handler.setFormatter( formatter )
    logger.addHandler( file_handler )

def find_and_click_images(target, img_file_list, wait_time):
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
        time.sleep( wait_time )
    logger.debug( 'Leaving thread loop' )

def start_threads():
    # Getting settings
    global root_folder, entry_screen_type, fortune, fortune_wait, entry_season, cookie_wait, reindeer_wait
    global logger
    global threads_list

    l_root_folder = os.path.abspath(root_folder_label_return.cget('text'))
    l_entry_screen_type = entry_screen_type.get()
    l_fortune = fortune.get()
    l_fortune_wait = float(fortune_wait.get())
    l_entry_season = entry_season.current()
    l_cookie_wait = float(cookie_wait.get())
    l_reindeer_wait = float(reindeer_wait.get())

    logger.info( 'Starting application' )

    season_folder_list = [
        'christmas'
        ,'halloween'
        ,'valentines'
        ,'business_day'
        ,'easter'
    ]

    set_logging( l_root_folder )

    # Setting image folders
    if l_entry_screen_type == 'monitor':
        images_folder = os.path.join( l_root_folder, 'searched_images', 'monitor' )
    else:
        images_folder = os.path.join( l_root_folder, 'searched_images', 'default' )

    if l_entry_season != 0:
        season_folder = season_folder_list[l_entry_season - 1]
    else: season_folder = 'no season'

    logger.info( f"""Configurations:
Root folder: {str(l_root_folder)}
Screen type: {l_entry_screen_type}
Season: {season_folder}
Click fortune cookie: {str(l_fortune)}
Wait times: 
Golden Cookie: {str(l_cookie_wait)}  |  Fortune:{str(l_fortune_wait)}  |  Reindeer: {str(l_reindeer_wait)}""" )


    # Setting thread that clicks on the golden cookie
    logger.info( 'Starting golden cookie clicker' )
    if l_entry_season == 0 or l_entry_season == 1:
        target_images = [ os.path.join( images_folder, 'golden_cookie.png' ) ]
    else:
        target_images = [ os.path.join(images_folder, season_folder, imgs) for imgs in os.listdir( os.path.join(images_folder, season_folder) ) if os.path.isfile( os.path.join(images_folder, season_folder, imgs) ) ]
    golden_cookie_clicker = threading.Thread( target=find_and_click_images, args=( 'Golden Cookie', target_images, l_cookie_wait, ), daemon=True ) # Using daemon=True as added security
    golden_cookie_clicker.start()
    threads_list.append( golden_cookie_clicker )

    # Setting thread that clicks on reindeer if Christmas Season is active
    if l_entry_season == 1:
        logger.info( 'Starting reindeer clicker' )
        target_images = [ os.path.join(images_folder, season_folder, imgs) for imgs in os.listdir( os.path.join(images_folder, season_folder) ) if os.path.isfile( os.path.join(images_folder, season_folder, imgs) ) ]
        reindeer_clicker = threading.Thread( target=find_and_click_images, args=( 'Reindeer', target_images, l_reindeer_wait, ), daemon=True ) # Using daemon=True as added security
        reindeer_clicker.start()
        threads_list.append( reindeer_clicker )

    if l_fortune == 1:
        # Setting thread that clicks on the fortune news ticker
        logger.info( 'Starting fortune news ticker clicker' )
        target_images = [ os.path.join( images_folder, 'fortune_cookie.png' ) ]
        fortune_clicker = threading.Thread( target=find_and_click_images, args=( 'Fortune', target_images, l_fortune_wait, ), daemon=True ) # Using daemon=True as added security
        fortune_clicker.start()
        threads_list.append( fortune_clicker )


logger = logging.getLogger( 'Logger' )

root = Tk()
root.title("Cookie Clicker automations")

frame = ttk.Frame(root, padding="5 5 12 12")
frame.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

row_num = 1
column_num = 1


# Select root folder
root_folder_label = ttk.Label( frame, text='Select image root directory' )
root_folder_label.grid( row=row_num, column=column_num, sticky=(N, S, W, E))
column_num += 1
root_folder = StringVar()
default_filepath = os.path.join( os.environ['USERPROFILE'], 'Desktop', 'clicker' )
root_folder_label_return = ttk.Label( frame, padding=(5, 0), text=default_filepath, width=-10, background='white' )
root_folder_label_return.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
root_folder_button = ttk.Button( frame, text='...', command=get_root_filepath )
root_folder_button.grid( row=row_num, column=column_num, sticky=(W, E) )

row_num += 1
column_num = 1

# Create folder structure if you want to
folder_structure = ttk.Label( frame, text='If you haven\'t done it before,\ncreate the folder structure now' )
folder_structure.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
folder_structure_button = ttk.Button( frame, text='Create', command=create_folder_structure )
folder_structure_button.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )

row_num += 1
column_num = 1

# Separator
sep = ttk.Separator( frame, orient='horizontal' )
sep.grid( row=row_num, columnspan=4, sticky=EW )

row_num += 1
column_num = 1

# Select if you're using a monitor or your laptop default screen
screen_type = StringVar()
screen_type_text = ttk.Label( frame, text='Select the screen type' )
screen_type_text.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
entry_screen_type = ttk.Combobox( frame, values=[ 'Monitor', 'Laptop screen' ] )
entry_screen_type.current( 0 )
entry_screen_type.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )

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
fortune_cookie.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
fortune_cookie_wait = ttk.Label( frame, text='Wait time (seconds)' )
fortune_cookie_wait.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
fortune_wait = StringVar()
fortune_wait_entry = ttk.Entry( frame, textvariable=fortune_wait, justify='center' )
fortune_wait_entry.insert( index=0, string='5.0' )
fortune_wait_entry.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )

row_num += 1
column_num = 1

# Select the season
season_text = ttk.Label( frame, text='Select the season' )
season_text.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
entry_season = ttk.Combobox( frame, justify='center' , values=[ 'No season', 'Christmas', 'Halloween', 'Valentine\'s', 'Business Day', 'Easter' ] )
entry_season.current( 0 )
entry_season.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )

row_num += 1
column_num = 1

# Wait time for golden cookie in seconds
cookie_wait_text = ttk.Label( frame, text='Wait time for golden cookie (seconds)' )
cookie_wait_text.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
cookie_wait = StringVar()
cookie_wait_entry = ttk.Entry( frame, textvariable=cookie_wait, justify='center' )
cookie_wait_entry.insert( index=0, string='5.0' )
cookie_wait_entry.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )

row_num += 1
column_num = 1

# Wait time for reindeer in seconds
reindeer_wait_text = ttk.Label( frame, text='Wait time for reindeer (seconds)' )
reindeer_wait_text.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
reindeer_wait = StringVar()
reindeer_wait_entry = ttk.Entry( frame, textvariable=reindeer_wait, justify='center' )
reindeer_wait_entry.insert( index=0, string='5.0' )
reindeer_wait_entry.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )

row_num += 1
column_num = 2

# Buttons to start and cancel the applications
start_button = Button( frame, text='Start', bg='#ccffcc', command=start_threads )
start_button.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )
column_num += 1
cancel_button = Button( frame, text='Cancel/Stop', bg='#ffcccc', command=close_application )
cancel_button.grid( row=row_num, column=column_num, sticky=(N, S, W, E) )

for child in frame.winfo_children(): 
    child.grid_configure(padx=5, pady=5)

threads_list = []
stop_threads = threading.Event()

root.mainloop()

for t in threads_list:
    t.join()

logger.info( 'Ending run' )