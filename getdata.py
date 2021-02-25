import requests
import json
import pandas as pd
import os
import isoweek
import datetime

def check_request_response(response):
    if response.raise_for_status() is None:
        return response
    else:
        print(response.raise_for_status())
        sys.exit()

def get_nice_data(headers, nice_url, variable_name):
    ''' Retreives either the amount of current patients in the 
    hospital or in the IC (depending on inputted variable_name)
    JSON data from stichting nice using the requests module, 
    loads the json into a dataframe, and returns said dataframe. '''
    response = requests.get(nice_url, headers=headers)
    if check_request_response(response):
        dframe = pd.DataFrame(json.loads(response.content))
        dframe.rename(columns = {'value' : variable_name}, inplace = True)
        dframe['date'] = pd.to_datetime(dframe.date)
        return dframe

def calculate_week_numer(row):
    ''' Function using the Isoweek module to calculate the week number
    corresponsing with a given date. '''
    return isoweek.Week.withdate(row['date']).isoformat()

def get_rivm_data_main(headers, url):
    ''' Retreives RIVM data using requests. Additionally sets up the 
    date column as datetime and calculates ISO week number. 
    Requests the json file containing the data, and returns it
    as a dataframe. '''
    response = requests.get(url, headers=headers)
    if check_request_response(response):
        try:
            dframe = pd.DataFrame(json.loads(response.content))
            dframe['date'] = pd.to_datetime(dframe.Date_of_publication)
            dframe['week_number'] = dframe.apply(calculate_week_numer, axis=1)
            return dframe
        except ValueError:
            print('None JSON response received from RIVM')
            sys.exit()

def sum_day_and_week_rivm(dframe):
    ''' Takes the raw dataframe and returns a dataframe with 
    the reported infection, hospital admissions, and deaths
    summed by week and by day. '''
    dframe['infection_day'] = dframe.Total_reported.groupby(
        dframe.date).transform('sum')
    dframe['hospital_day'] = dframe.Hospital_admission.groupby(
        dframe.date).transform('sum')
    dframe['dead_day'] = dframe.Deceased.groupby(
        dframe.date).transform('sum')
    dframe['infection_week'] = dframe.Total_reported.groupby(
        dframe.week_number).transform('sum')
    dframe['hospital_week'] = dframe.Hospital_admission.groupby(
        dframe.week_number).transform('sum')
    dframe['dead_week'] = dframe.Deceased.groupby(
        dframe.week_number).transform('sum')  
    return dframe


def drop_redudant(dframe):
    ''' Returns the rivm dataframe with only the relevant
    columns (dropping the others). '''
    dframe.drop_duplicates(subset=['date'], keep='first', inplace=True)
    cols_to_keep = ['date', 'week_number', 'infection_day', 
            'hospital_day', 'dead_day', 'infection_week', 
            'hospital_week', 'dead_week']
    return dframe[cols_to_keep]

def merge_dframes(ic_df, zkh_df, rivm_df):
    ''' Returns the combined NICE dataframes and
    the RIVM dataframe, merged on the date variable. '''
    nice_df = pd.merge(ic_df, zkh_df, how='left', on='date')
    dframe = pd.merge(rivm_df, nice_df, how='left', on='date')
    return dframe

def parse_rivm_df(raw_rivm_df):
    ''' Further processes the rivm dataframe. First
    function sums data by day and week. Second function
    drops duplicates, keeping 1 observation per date.'''
    dframe = sum_day_and_week_rivm(raw_rivm_df)
    dframe = drop_redudant(dframe)
    return dframe

def export_data(dframe):
    ''' Export data retreived from RIVM and NICE to a csv file
    in the current directory. '''
    dframe.to_csv(os.path.join(os.getcwd(), 'export.csv'))

def data_retreival():
    ''' Retreivs the various data sources using the
    requests library. '''
    HEADERS = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) ' \
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')}
    RIVM_URL = 'https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_per_dag.json'
    NICE_URL_IC = 'https://stichting-nice.nl/covid-19/public/intake-count/'
    NICE_URL_ZKH = 'https://stichting-nice.nl/covid-19/public/zkh/intake-count/'
    ic_df = get_nice_data(HEADERS, NICE_URL_IC, 'IC_current')
    zkh_df = get_nice_data(HEADERS, NICE_URL_ZKH, 'ZKH_current')
    raw_rivm_df = get_rivm_data_main(HEADERS, RIVM_URL) 
    return ic_df, zkh_df, raw_rivm_df

def data_main():
    print('Starting data retreival')
    ic_df, zkh_df, raw_rivm_df = data_retreival()
    rivm_df = parse_rivm_df(raw_rivm_df)
    dframe = merge_dframes(ic_df, zkh_df, rivm_df)
    return dframe

