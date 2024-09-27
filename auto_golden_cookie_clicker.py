import ctypes
import threading
import time
import pyautogui
import os
import logging
import datetime
from pathlib import Path

def find_and_click_golden_cookie(img_file_path):
    clicks = 0
    logger.info( 'Starting run' )
    while not stop_thread.is_set():
        logger.debug( 'Looking for cookie' )
        search = pyautogui.locateCenterOnScreen( img_file_path )

        if search != None:
            x, y = search
            pyautogui.click( x=x, y=y )
            clicks += 1
            logger.info( 'Cookie found. Number of clicks this run: %d' % clicks)
        else:
            logger.debug( 'Cookie hasn\'t spawned yet' )
        time.sleep( 5 )

# Setting stable variables
COOKIE_IMAGE_MONITOR = 'golden_cookie_monitor.png'
COOKIE_IMAGE_DEFAULT = 'golden_cookie_default.png'
current_dir = os.path.dirname( __file__ )

img_file_name = COOKIE_IMAGE_MONITOR # If you want to use a different image, change this line

# Asking for the path for the images to be searched
user_img_input = input( 'Paste the full folder path where your golden cookie images are. The folder and images must exist prior to the execution.\nWill default to desktop/clicker/searched_images if left empty\n')
if user_img_input is None or user_img_input == '':
    img_folder = os.path.join( os.path.join( os.environ['USERPROFILE'] ), 'Desktop', 'clicker', 'searched_images' )
else:
    img_folder = user_img_input
img_file_path = os.path.join( img_folder, img_file_name )

#Setting logging path and file
now = datetime.datetime.now()
dt = now.strftime( "%Y%m%d_%H%M" )

# Asking for the path where logs will be saved
user_logger_input = input( 'Paste the full folder path you want to save your logs. Will default to desktop/clicker/logs if left empty\n')
if user_logger_input is None or user_logger_input == '':
    logger_folder = os.path.join( os.path.join( os.environ['USERPROFILE'] ), 'Desktop', 'clicker', 'logs' )
else:
    logger_folder = user_logger_input

logging_path = os.path.join( logger_folder, dt + '_golden_cookie_clicker.log' )

# Creating logging file if it doesn't exist
Path( logger_folder ).mkdir( parents=True, exist_ok=True )
file = open( logging_path, 'a' )
file.close()

# Setting loggers
logger = logging.getLogger( 'Logger' )
logger.setLevel( 'DEBUG' )
formatter = logging.Formatter( fmt="{asctime} - {levelname} - {message}"
                              ,style="{"
                              ,datefmt="%Y-%m-%d %H:%M"
                              )

console_handler = logging.StreamHandler()
console_handler.setLevel( 'DEBUG' )
console_handler.setFormatter( formatter )
logger.addHandler( console_handler )

file_handler = logging.FileHandler( filename=logging_path, mode='a', encoding='utf-8' )
file_handler.setLevel( 'INFO' )
file_handler.setFormatter( formatter )
logger.addHandler( file_handler )

# Setting golden cookie file path



stop_thread = threading.Event()

# Setting and starting thread
t = threading.Thread( target=find_and_click_golden_cookie, args=( img_file_path, ), daemon=True ) # Using daemon=True as added security
t.start()

# This will hold the program on standby until you close the message box, then it will set the thread event to stop it
ctypes.windll.user32.MessageBoxW(0, "Auto Golden Cookie clicker still running\nPress OK or close this window to stop it", "Golden Cookie auto clicker", 0)
stop_thread.set()

t.join()
logger.info( 'Golden Cookie auto clicker has been stopped' )
ctypes.windll.user32.MessageBoxW(0, "Auto Golden Cookie clicker has been stopped\n", "Golden Cookie auto clicker", 0)