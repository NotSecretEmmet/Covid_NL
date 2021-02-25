import requests
import json
import pandas as pd
import os
import isoweek
import datetime

def calc_week(row):
    return isoweek.Week.withdate(datetime.datetime.strptime(row['date'], '%Y-%m-%d')).isoformat()

df = pd.read_csv('export.csv')

df['w'] = df.apply(calc_week, axis=1)
print(df)
print(df.w.min())