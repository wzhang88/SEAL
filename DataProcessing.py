import os
import numpy as np
import pandas as pd
from scipy import stats


def read_data_combine(data_path: str):
    data_files = []
    for f in os.listdir(data_path):
        if not f.startswith('.'):
            data_files.append(f)
    data_array = []
    device_names = []

    for d in data_files:
        device_name = d.split('.')[0]
        device_names.append(device_name)
        data_df = pd.read_csv(data_path + d, skiprows=1)
        data_df.columns = data_df.columns.str.replace(' ', '')
        data_df['Device'] = device_name
        data_array.append(data_df)

    all_device_data = pd.concat(data_array)
    all_device_data['Datetime'] = pd.to_datetime(all_device_data['Date'] + ' ' + all_device_data['Time'])
    to_numeric_cols = all_device_data.columns.drop(
        ['Time', 'Date', 'Battery', 'Fix', 'Longitude', 'Latitude', 'Temp(C)', 'RH(%)', 'P(hPa)', 'Alti(m)', 'Device',
         'Datetime'])
    all_device_data[to_numeric_cols] = all_device_data[to_numeric_cols].apply(pd.to_numeric, errors='coerce',
                                                                              downcast='float').astype(float)
    # only keep relevant columns
    all_device_data = all_device_data[['Datetime', 'Date', 'Time', 'Dp>0.3',
                                       'Dp>0.5', 'Dp>1.0', 'Dp>2.5', 'Dp>5.0', 'Dp>10.0', 'PM1_Std',
                                       'PM2.5_Std', 'PM10_Std', 'PM1_Env', 'PM2.5_Env', 'PM10_Env', 'Device']]
    return all_device_data


def round_time_and_linear_interpolate(data, period: str):
    period = period + 's'
    rounded = pd.DataFrame(data['Datetime'].dt.round(period))
    data['Datetime_round'] = rounded
    data_rounded = data.groupby(['Datetime_round', 'Device']).mean().reset_index()
    # Add interpolation
    data_rounded.select_dtypes(include=['float64']).interpolate(method='linear', limit_direction='both',
                                                                inplace=True, axis=0)
    return data_rounded


def drop_numerical_outliers(df, conf_level):
    # two-sided, taken confidence level from 0 to 100
    z_thresh = stats.norm.ppf((1 + conf_level / 100) / 2)
    constrains = df.select_dtypes(include=['float64']) \
        .apply(lambda x: np.abs(stats.zscore(x)) < z_thresh).all(axis=1)
    idx = df.index[constrains == False].tolist()
    new_df = df.drop(idx)
    return new_df


def get_data_in_range(df, start, end):
    return df[(df['Datetime_round'] >= start) & (df['Datetime_round'] <= end)]
