import gpxpy # Used for reading gpx files
import os
import pandas as pd
import numpy as np
import app.dataProcessing
from app import app
from datetime import datetime
from app.dataProcessing import compute_max_speed_df, prep_df
from flask import flash

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def metadata_from_gpx(filename):
    """
    Gets the name, date and time from a gpx file, given the filename. Returns
    all three as strings.
    """
    gpx_directory = app.config['GPX_FOLDER']

    if os.path.isfile(gpx_directory + filename) == False:
        return None, None, None
    else:
        gpstracks = []
        with open(gpx_directory + filename, 'r') as gpxfile:
            gpx = gpxpy.parse(gpxfile)
            name = gpx.tracks[0].name
            timestamp = gpx.tracks[0].segments[0].points[0].time
            date = timestamp.date()
            time = timestamp.time()
        return name, date, time

def gpx_to_csv_to_msm(run, filename):
    df = gpx_to_csv(run, filename)
    max_speed_df = compute_max_speed_df(df)
    date = run.date.isoformat()
    write_max_speed_matrix(max_speed_df, run, date)

    distance = df['dist_delta_meters'].sum()
    elevation_gain = 0 # Still need to compute this

    # It's a little ugly to just randomly return this data from this IO method...
    return distance, elevation_gain

def gpx_to_csv(run, filename):
    """
    Parse a GPX file into a list of dictonaries, convert it to a Pandas data
    frame, then write it to a csv. Takes in a Run object.
    """

    gpx_directory = app.config['GPX_FOLDER']
    csv_directory = app.config['CSV_FOLDER']
    date = run.date.isoformat()
    csv_date_directory = csv_directory + date + r'/'

    gpstracks = []
    with open(gpx_directory + filename, 'r') as gpxfile:
        gpx = gpxpy.parse(gpxfile)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    dict = {'Timestamp' : point.time,
                            'Latitude' : point.latitude,
                            'Longitude' : point.longitude,
                            'Elevation' : point.elevation
                            }
                    gpstracks.append(dict)

    df = pd.DataFrame(gpstracks)

    minutes = 120
    time_interval = np.arange(60*minutes + 1)

    csv_filename = str(run.id)

    os.makedirs(os.path.dirname(csv_date_directory + csv_filename + '.csv'), exist_ok=True)
    with open(csv_date_directory + csv_filename + '.csv', 'a') as csv:
        df.to_csv(csv, index = False)
    return df

def load_csv_to_df(filename, date):
    """
    A helper function to take a converted csv (identified by its filename and
    date), and return a Pandas DataFrame with the contents. Note that the
    filename should *not* include an extension ('.csv').
    """
    csv_directory = app.config['CSV_FOLDER']
    csv_date_directory = csv_directory + date + r'/'

    with open(csv_date_directory + filename + '.csv') as csv:
        rows_to_skip = 0
        line = csv.readline()
        while line.startswith('#'):
            line = csv.readline()
            rows_to_skip += 1

    # Since I've been 'reading lines', the file is not starting at the beginning. So we re-open it and skip lines
    with open(csv_date_directory + filename + '.csv') as csv:
        df = pd.read_csv(csv, skiprows = rows_to_skip)
    return df

def write_max_speed_matrix(df, run, date):

    msm_directory = app.config['MSM_FOLDER']
    msm_date_directory = msm_directory  + date + r'/'
    filename = str(run.id)

    try:
        os.remove(msm_date_directory + filename + '.csv')
    except OSError:
        pass

    os.makedirs(os.path.dirname(msm_date_directory + filename + '.csv'), exist_ok=True)
    with open(msm_date_directory + filename + '.csv', 'a') as msm_csv:
        df.to_csv(msm_csv, index=False)

    return True

def csv_to_msm(filename, date):
    df = load_csv_to_df(filename, date)
    df = dataProcessing.prep_df(df)
    max_speed_df = dataProcessing.compute_max_speed_df(df)
    write_max_speed_matrix(max_speed_df, filename, date)
    return True

def read_max_speed_matrix(filename, date):
    msm_directory = app.config['MSM_FOLDER']
    msm_date_directory = msm_directory + date + r'/'

    with open(msm_date_directory + filename + '.csv', 'r') as msm:
        rows_to_skip = 0
        line = msm.readline()
        while line.startswith('#'):
            line = msm.readline()
            rows_to_skip += 1
    with open(msm_date_directory + filename + '.csv', 'r') as msm:
        max_speed_matrix = pd.read_csv(msm, skiprows = rows_to_skip)

    return max_speed_matrix

def find_unparsed_gpx():
    """
    Go through the gpx directory and find all runs which have not yet between
    converted to csv. Note that, if for some reason the run was converted to
    csv, but not to msm, this function would not see that. Returns a list of
    filenames (including the '.gpx')
    """
    all_files = os.listdir(gpx_directory)
    gpx_files = [gpx_file for gpx_file in all_files if gpx_file.endswith('.gpx')]
    unparsed_gpx = []
    for gpx_file in gpx_files:
        _, date, _ = fileIO.metadata_from_gpx(gpx_file.replace('.gpx', ''))
        csv_date_directory = csv_directory + date + r'/'
        if os.path.isfile(csv_date_directory + gpx_file.replace('.gpx', '.csv')):
            pass
        else:
            unparsed_gpx.append(gpx_file)

    return unparsed_gpx

def parse_unparsed_gpx():
    """
    Finds any unparsed gpx (using the find_unparsed_gpx function) and parses
    them.
    """
    unparsed_gpx = find_unparsed_gpx()
    for gpx in unparsed_gpx:
        try:
            # Retrieve the metadata from the gpx file
            filename = gpx.replace('.gpx', '')
            name, date, time = fileIO.metadata_from_gpx(filename)
        except:
            return None

        csv_date_directory = csv_directory + date + r'/'
        msm_date_directory = msm_directory + date + r'/'

        # First, check if the csv file has already been created (from the gpx),
        # and if not, create it
        if os.path.isfile(csv_date_directory  + filename + '.csv'):
            pass
        else:
            fileIO.gpx_to_csv(filename, date)

        # Next, check if the max speed matrix (msm) has already been created,
        # and if not, create it
        if os.path.isfile(msm_date_directory  + filename + '.csv'):
            pass
        else:
            fileIO.csv_to_msm(filename, date)

def msms_by_date(start_date, end_date):
    """
    Return a list containing msm's for all runs which occurred between the
    given dates.

    Attributes:
        start_date: A string in the format YYYY-MM-DD
        end_date: A string in the format YYYY-MM-DD
    """
    msm_directory = app.config['MSM_FOLDER']

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

    msm_list = []

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
                msm_list.append(pd.read_csv(msm_directory + subdirectory + '/' + valid_file))
    return msm_list
