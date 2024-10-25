import os
import logging
import datetime
from pathlib import Path
import json

def set_logging(root_folder, filename_timestamp_level='minute', log_file_name='execution_log' ):
    #Setting logging path and file
    now = datetime.datetime.now()
    if filename_timestamp_level == 'year':
        dt = now.strftime( "%Y" )
    elif filename_timestamp_level == 'month':
        dt = now.strftime( "%Y%m" )
    elif filename_timestamp_level == 'day':
        dt = now.strftime( "%Y%m%d" )
    elif filename_timestamp_level == 'hour':
        dt = now.strftime( "%Y%m%d_%H" )
    elif filename_timestamp_level == 'second':
        dt = now.strftime( "%Y%m%d_%H%M%S" )
    else:
        dt = now.strftime( "%Y%m%d_%H%M" )
    log_folder = os.path.join( root_folder, 'logs' )
    log_file_path = os.path.join( log_folder, dt + '_' + log_file_name + '.log' )

    # Creating logging file if it doesn't exist
    Path( log_folder ).mkdir( parents=True, exist_ok=True )
    file = open( log_file_path, 'a' )
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

    file_handler = logging.FileHandler( filename=log_file_path, mode='a', encoding='utf-8' )
    file_handler.setLevel( 'INFO' )
    file_handler.setFormatter( formatter )
    logger.addHandler( file_handler )

    return logger
    
def read_configs(filepath):
    configs = {}
    corrected_path = Path( filepath )
    with open( corrected_path, 'r' ) as f:
        config_json = json.load( f )
    for k, v in config_json.items():
        configs[k] = v
    f.close()
    return configs

	# Example on how to read the result for app_name = auto_ascender
    # x, y = cfgs['legacy_button_coords']['x'], cfgs['legacy_button_coords']['y']

def save_configs_to_file( filepath, configs ):
    corrected_path = Path( filepath )
    with open( corrected_path, 'w' ) as f:
        json.dump( configs, f )

def create_folder_structure( root_folder ):
    print( 'entering create folder function' )
    print( f'folder is {root_folder}')
    if root_folder is not None and root_folder != '':
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

        folder_path = os.path.join( root_folder, folder_list_level1[0] )
        Path( folder_path ).mkdir( parents=True, exist_ok=True )
        folder_path = os.path.join( root_folder, folder_list_level1[1] )
        for level2 in screen_type:
            for level3 in seasons:
                directory = os.path.join( folder_path, level2, level3 )
                Path( directory ).mkdir( parents=True, exist_ok=True )
    else: print( 'No path given' )