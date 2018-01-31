import gpxpy # Used for reading gpx files
from geopy.distance import vincenty # Used for calculating distances between (lat, lon) pairs
import os
import pandas as pd
import numpy as np
import dataProcessing
import config_dev as cfg # My own config.py file with configuration parameters

def metadata_from_gpx(filename):
    """
    Gets the name, date and time from a gpx file, given the filename. Returns all three as strings.
    """
    gpx_directory = cfg.data_directories['gpx']

    if os.path.isfile(gpx_directory + filename + '.gpx') == False:
        return None, None, None
    else:
        gpstracks = []
        with open(gpx_directory + filename + '.gpx', 'r') as gpxfile:
            gpx = gpxpy.parse(gpxfile)
            name = gpx.tracks[0].name
            date_time = gpx.tracks[0].segments[0].points[0].time.isoformat()
            date, time = date_time.split('T')
            time = time.replace(':', '-') # A colon is used to indicate a key for metadata, so those must be changed
        return name, date, time

def gpx_to_csv(filename, date):
    """
    Parse a GPX file into a list of dictonaries, convert it to a Pandas data frame, then write to csv, along
    with metadata
    """

    name, _, time = metadata_from_gpx(filename)

    gpx_directory = cfg.data_directories['gpx']
    csv_directory = cfg.data_directories['csv']
    csv_date_directory = csv_directory + date + r'/'

    name, _, time = metadata_from_gpx(filename)

    gpstracks = []
    with open(gpx_directory + filename + '.gpx', 'r') as gpxfile:
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

    # If the converted csv file already exists, remove it so that it can be written again. This avoids
    # appending stuff to the end of an already existing csv file and creating problems
    try:
        os.remove(csv_date_directory + filename + '.csv')
    except OSError:
        pass

    minutes = cfg.minutes
    time_interval = np.arange(60*minutes + 1)

    os.makedirs(os.path.dirname(csv_date_directory + filename + '.csv'), exist_ok=True)
    with open(csv_date_directory + filename + '.csv', 'a') as csv:
        csv.write("#name:" + name + '\n')
        csv.write("#date:" + date + '\n')
        csv.write("#time:" + time + '\n')
        df.to_csv(csv, index = False)
    return True

def load_csv_to_df(filename, date):
    """
    A helper function to take a converted csv (identified by its filename and
    date), and return a Pandas DataFrame with the contents. Note that the
    filename should *not* include an extension ('.csv').
    """
    csv_directory = cfg.data_directories['csv']
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

def write_max_speed_matrix(df, filename, date):
    name, _, time = metadata_from_gpx(filename)

    msm_directory = cfg.data_directories['msm']
    msm_date_directory = msm_directory  + date + r'/'

    try:
        os.remove(msm_date_directory + filename + '.csv')
    except OSError:
        pass

    os.makedirs(os.path.dirname(msm_date_directory + filename + '.csv'), exist_ok=True)
    with open(msm_date_directory + filename + '.csv', 'a') as msm_csv:
        msm_csv.write("#name:" + name + '\n')
        msm_csv.write("#date:" + date + '\n')
        msm_csv.write("#time:" + time + '\n')
        df.to_csv(msm_csv, index=False)

    return True

def read_max_speed_matrix(filename, date):
    msm_directory = cfg.data_directories['msm']
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

def csv_to_msm(filename, date):
    df = load_csv_to_df(filename, date)
    df = dataProcessing.prep_df(df)
    max_speed_df = dataProcessing.compute_max_speed_df(df)
    write_max_speed_matrix(max_speed_df, filename, date)
    return True

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
