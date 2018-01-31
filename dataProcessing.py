import gpxpy # Used for reading gpx files
from geopy.distance import vincenty # Used for calculating distances between (lat, lon) pairs
import pandas as pd
import numpy as np
import config as cfg

def prep_df(df):
    """
    Parses, cleans and formats the data coming from the converted csv file.
    """
    # Compute time elapsed in seconds
    start_time = pd.to_datetime(df['Timestamp'].iloc[0])
    current_time = pd.to_datetime(df['Timestamp'])
    df['sec_elapsed'] = (current_time - start_time) / np.timedelta64(1, 's')

    # Compute the distance (in meters) between successive points
    df['lat_lon'] = list(zip(df['Latitude'], df['Longitude']))

    lat_lon_offset = list(df['lat_lon'])
    lat_lon_offset.insert(0,lat_lon_offset[0])
    lat_lon_offset = lat_lon_offset[:-1]

    df['lat_lon_offset'] = lat_lon_offset

    df['lat_lon_pairs'] = list(zip(df['lat_lon'], df['lat_lon_offset']))

    df['dist_delta_meters'] = df['lat_lon_pairs'].apply(lambda x: vincenty(x[0], x[1]).meters)

    # Compute the elevation difference (in meters) between successive points
    elev_offset = list(df['Elevation'])
    elev_offset.insert(0,elev_offset[0])
    elev_offset = pd.Series(elev_offset[:-1])
    df['elev_delta_meters'] = df['Elevation'] - elev_offset

    # Compute the time difference (in seconds) between successive points (NEEDS SPEED-UP WORK DONE)
    time_offset = list(df['Timestamp'])
    time_offset.insert(0,time_offset[0])
    time_offset = pd.Series(time_offset[:-1])
    df['time_delta_sec'] = (pd.to_datetime(df['Timestamp']) - pd.to_datetime(time_offset)) / np.timedelta64(1, 's')

    # Compute instantaneous speed (in meters per second)
    df['speed_meters_sec'] = df['dist_delta_meters'] / df['time_delta_sec']
    df['speed_meters_sec'] = df['speed_meters_sec'].fillna(0.0)

    # Compute gradient (unitless)
    df['gradient'] = df['elev_delta_meters'] / df['dist_delta_meters']
    df['gradient'].fillna(0.0, inplace=True)
    df['gradient_100'] = 100*df['gradient']

    df.drop(['Latitude', 'Longitude', 'lat_lon_offset', 'lat_lon_pairs'], axis=1, inplace=True)

    max_gradient = 1 # Set a maximum gradient of 1 (45 degrees)
    bad_index = df['gradient'].loc[np.abs(df['gradient']) > max_gradient].index
    if len(bad_index) == 0:
        pass
    else:
        df['gradient'].loc[bad_index] = np.median(df['gradient'].values)

    return df

def rolling_max_speed(rolling_window, df):
    rolling_df = df[['speed_meters_sec', 'gradient_100']].rolling(window=rolling_window).mean().fillna(0)
    rolling_df['rounded_gradient_100'] = rolling_df['gradient_100'].apply(np.round)
    rolling_groupby = rolling_df.groupby('rounded_gradient_100')

    max_speed = {int(name): max(group['speed_meters_sec'].values) for name, group in rolling_groupby}
    return max_speed

def compute_max_speed_df(df):
    minutes = cfg.minutes
    time_interval = np.arange(60*minutes + 1)
    minimum_gradient = cfg.minimum_gradient
    maximum_gradient = cfg.maximum_gradient
    gradient_interval = np.arange(minimum_gradient, maximum_gradient + 1)
    # Compute the maximum speed over all gradients which appear...
    max_speed_matrix = pd.DataFrame([rolling_max_speed(t, df) for t in time_interval]).fillna(0)

    # ... then fill in those gradients which don't appear with zero max speed
    df_data = max_speed_matrix
    df = pd.DataFrame(0, index=time_interval, columns=gradient_interval)
    df.update(df_data)

    max_speed_df = df[gradient_interval].iloc[time_interval]
    return max_speed_df
