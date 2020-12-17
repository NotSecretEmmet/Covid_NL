import sys
import datetime
import pandas as pd
from statsmodels.formula.api import ols

def set_target_regression_variables(type_var):
    ''' Returns the variable names depending on the regression of 
    interest (type_var).

    Parameters:
    type_var: string containing name of the variable of interest.

    Returns:
    day_var_name: Name of the variable by day.
    week_var_name: Name of the variable by week.
    y_var_name: Name of the independent variable on which 
        the regression will be ran.

    '''
    if type_var == 'infection':
        day_var_name = 'infection_day'
        week_var_name = 'infection_week'
        y_var_name = 'infect_pct_of_week'
    elif type_var == 'hospital':
        day_var_name = 'hospital_day'
        week_var_name = 'hospital_week'
        y_var_name = 'hosp_pct_of_week'
    elif type_var == 'deaths':
        day_var_name = 'dead_day'
        week_var_name = 'dead_week'
        y_var_name = 'dead_pct_of_week'
    else:
        print('Unknown type variable inputted to regress.')
        sys.exit()
    return day_var_name , week_var_name , y_var_name

def day_contrib_reg(df_input, type_var):
    ''' Performs on OLS regressions with catagorial/dummy variables for each week day 
    in order to investigate whether some days systemically over/under rapport
    cases. First retreives the variable names depending on which rapporting variable
    is under investigation, and drops unnecessary variables.
    Next, determines ISO week numbers, and drops non-complete weeks.
    Then it caclulates the ratio of day to week total of the rapporting
    variable, and runs the regression. 

    Parameters:
    df_input: Pandas dataframe containing the data on which the regression will be ran.
    type_var: String of the varirable name of the variable of interest

    Returns:
    regression_result: OLS Regression Results 

    '''
    day_var_name, week_var_name, y_var_name = set_target_regression_variables(type_var)
    cols_to_keep = ['date', 'week_number', day_var_name, week_var_name]
    df = df_input[cols_to_keep].copy()
    
    df['date'] = pd.to_datetime(df.date, dayfirst=True)
    df['weekday'] = df.date.dt.day_name() 
    week_count = df.week_number.value_counts()
    to_remove = week_count[week_count < 7].index
    df = df[~df.week_number.isin(to_remove)].copy()
    df[y_var_name] = df[day_var_name] / df[week_var_name]

    fit = ols(f'{y_var_name} ~ C(weekday)', data=df).fit()
    regression_result = fit.summary() 
    return regression_result

def export_regression_results(results):
    with open('reg_results.txt', 'w') as f:
        f.write(results.as_text()) 