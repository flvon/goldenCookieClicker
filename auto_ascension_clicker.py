import ctypes
import threading
import time
import pyautogui
import os
import logging
import datetime
from pathlib import Path
import keyboard

LEGACY_BUTTON = ( 1540, 90 )
ASCEND_BUTTON = ( 960, 600 )
REINCARNATE_BUTTON = ( 960, 135 )
CONFIRM_BUTTON = ( 940, 550 )
BUY_ALL_BUTTON = ( 1820, 170 )

def auto_ascender():
    logger.info( 'Starting run' )
    count_ascensions = 0
    while not stop_thread.is_set():
        if keyboard.is_pressed('q'):
            pyautogui.click( LEGACY_BUTTON )
            time.sleep(0.05)
            pyautogui.click( ASCEND_BUTTON )
            time.sleep(0.1)
            keyboard.send('esc')
            time.sleep(0.05)
            pyautogui.click( REINCARNATE_BUTTON )
            time.sleep(0.05)
            pyautogui.click( CONFIRM_BUTTON )
            time.sleep(0.05)
            pyautogui.moveTo( BUY_ALL_BUTTON )
            count_ascensions += 1
            logger.info( 'Number of ascensions this run: %d' % count_ascensions )
            time.sleep(3)
    logger.debug( 'Leaving thread loop' )



#Setting logging path and file
now = datetime.datetime.now()
dt = now.strftime( "%Y%m%d_%H%M" )



# Asking for the path where logs will be saved
user_logger_input = input( 'Paste the full folder path you want to save your logs. Will default to desktop/clicker/logs if left empty\n')
if user_logger_input is None or user_logger_input == '':
    logger_folder = os.path.join( os.path.join( os.environ['USERPROFILE'] ), 'Desktop', 'clicker', 'logs' )
else:
    logger_folder = user_logger_input

logging_path = os.path.join( logger_folder, dt + '_auto_ascender.log' )



# Creating logging file if it doesn't exist
Path( logger_folder ).mkdir( parents=True, exist_ok=True )
file = open( logging_path, 'a' )
file.close()



# Setting loggers
logger = logging.getLogger( 'Logger' )
logger.setLevel( 'DEBUG' )
formatter = logging.Formatter( fmt="{asctime} - {levelname} - {message}"
                              ,style="{"
                              ,datefmt="%Y-%m-%d %H:%M:%S"
                              )

console_handler = logging.StreamHandler()
console_handler.setLevel( 'INFO' ) # Change this to DEBUG if debugging the script is needed
console_handler.setFormatter( formatter )
logger.addHandler( console_handler )

file_handler = logging.FileHandler( filename=logging_path, mode='a', encoding='utf-8' )
file_handler.setLevel( 'INFO' )
file_handler.setFormatter( formatter )
logger.addHandler( file_handler )



# Setting and starting thread
stop_thread = threading.Event()
t = threading.Thread( target=auto_ascender, daemon=True ) # pyinsUsing daemon=True as added security
t.start()

# This will hold the program on standby until you close the message box, then it will set the thread event to stop it
ctypes.windll.user32.MessageBoxW(0, "Auto ascender still running\nPress OK or close this window to stop it", "Auto ascender", 0)
stop_thread.set()

t.join()
logger.info( 'Golden Cookie auto clicker has been stopped' )
ctypes.windll.user32.MessageBoxW(0, "Auto ascender has been stopped\n", "Auto ascender", 0)