import config_dev as cfg # My own config.py file with configuration parameters
from models import *
import fileIO
import os
from datetime import datetime

gpx_directory = cfg.data_directories['gpx']
csv_directory = cfg.data_directories['csv']
msm_directory = cfg.data_directories['msm']

def runs_by_date(start_date, end_date):
    """
    Return a list containing Run objects for all runs which occurred between the
    given dates.

    Attributes:
        start_date: A string in the format YYYY-MM-DD
        end_date: A string in the format YYYY-MM-DD
    """
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except:
        return 'Invalid dates'

    if start_date > end_date:
        return None

    msm_directory_contents = os.listdir(msm_directory)
    msm_subdirectories = [subdirectory for subdirectory \
                            in msm_directory_contents \
                            if os.path.isdir(msm_directory + subdirectory)]

    # Holds the filenames (without extension) for the files to be returned
    # as runs
    run_filenames = []

    for subdirectory in msm_subdirectories:
        try:
            subdirectory_date = datetime.strptime(subdirectory, '%Y-%m-%d')
        except:
            return 'Invalid directory date'

        if start_date <= subdirectory_date <= end_date:
            all_files = os.listdir(msm_directory + subdirectory)
            valid_files = [individual_file for individual_file \
                            in all_files if individual_file.endswith('.csv')]
            for valid_file in valid_files:
               run_filenames.append(valid_file.replace('.csv', ''))

    runs = [Run(filename) for filename in run_filenames]
    return runs
