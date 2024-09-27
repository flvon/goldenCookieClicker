import ctypes
import threading
import time
import pyautogui
import os
import logging
import datetime

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

img_file_path = os.path.join( current_dir, 'img_searches', img_file_name )

#Setting logging path and file
now = datetime.datetime.now()
dt = now.strftime( "%Y%m%d_%H%M" )
logging_path = os.path.join( current_dir, 'logs', dt + '_golden_cookie_clicker.log' )

# Creating logging file if it doesn't exist
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