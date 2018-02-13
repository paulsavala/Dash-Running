import pandas as pd
import numpy as np
from app import app

def haversine_np(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.

    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    return km * 1000

def prep_df(df):
    """
    Parses, cleans and formats the data coming from the converted csv file.
    """
    # Compute time elapsed in seconds
    start_time = pd.to_datetime(df['Timestamp'].iloc[0])
    current_time = pd.to_datetime(df['Timestamp'])
    df['sec_elapsed'] = (current_time - start_time) / np.timedelta64(1, 's')

    # Compute distance delta in meters
    df['dist_delta_meters'] = haversine_np(df.Longitude.shift(), df.Latitude.shift(), \
                                 df.loc[1:, 'Longitude'], df.loc[1:, 'Latitude']).fillna(0.0)

    # Compute the elevation difference (in meters) between successive points
    df['elev_delta_meters'] = df['Elevation'].diff().fillna(0.0)

    # Compute the time difference (in seconds) between successive points (NEEDS SPEED-UP WORK DONE)
    df['time_delta_sec'] = pd.to_datetime(df['Timestamp']).diff().fillna(0.0) / np.timedelta64(1, 's')

    # Compute instantaneous speed (in meters per second)
    df['speed_meters_sec'] = df['dist_delta_meters'] / df['time_delta_sec']
    df['speed_meters_sec'] = df['speed_meters_sec'].fillna(0.0)

    # Compute gradient (unitless)
    df['gradient'] = df['elev_delta_meters'] / df['dist_delta_meters']
    df['gradient'].fillna(0.0, inplace=True)
    df['gradient_100'] = 100*df['gradient']

    df.drop(['Latitude', 'Longitude'], axis=1, inplace=True)

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

    max_speed = {int(name): max(group['speed_meters_sec'].values) \
                            for name, group in rolling_groupby}
    return max_speed

def compute_max_speed_df(df):
    minutes = app.config['MAX_MINUTES']
    time_interval = np.arange(60*minutes + 1)
    min_gradient = app.config['MIN_GRADIENT']
    max_gradient = app.config['MAX_GRADIENT']
    gradient_interval = np.arange(min_gradient, max_gradient + 1)
    df = prep_df(df)
    # Compute the maximum speed over all gradients which appear...
    max_speed_matrix = pd.DataFrame([rolling_max_speed(t, df) \
                                    for t in time_interval]).fillna(0)

    # ... then fill in those gradients which don't appear with zero max speed
    df_data = max_speed_matrix
    df = pd.DataFrame(0, index=time_interval, columns=gradient_interval)
    df.update(df_data)

    max_speed_df = df[gradient_interval].iloc[time_interval]
    return max_speed_df
