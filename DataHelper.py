#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 22:25:27 2023

@author: pfox
"""
import pandas as pd

def get_time_of_day(the_time):
    if the_time < 6:
        return 'Night'
    elif the_time < 12: 
        return 'Morning'
    elif the_time < 18:
        return 'Afternoon'
    elif the_time < 24:
        return 'Evening'    


class DataManager():
    
    def __init__(self, file_name='data/hystreet_fussgaengerfrequenzen_seit2021.csv'):

        df = pd.read_csv(file_name)
        
        # prep data   
        df['timestamp_ts']=pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp_ts'].dt.hour
        df['day'] = df['timestamp_ts'].dt.day_name()
        df['month'] = df['timestamp_ts'].dt.month_name()
        df['year'] = df['timestamp_ts'].dt.year
        df['date'] = df['timestamp_ts'].dt.date
        df['month_year'] = df['month'] +" "+df['timestamp_ts'].dt.strftime('%Y')
        df['time_of_day'] = df['hour'].apply(get_time_of_day)  
        df['month'] = pd.Categorical(df['month'],
                                       categories=[ 'October', 'November', 'December','January','February','March','April','May','June', 'July','August', 'September'],
                                       ordered=True)

        Oct1_2021 = pd.Timestamp("2021-10-01", tz="UTC")
        Oct1_2022 = pd.Timestamp("2022-10-01", tz="UTC")
        Oct1_2023 = pd.Timestamp("2023-10-01", tz="UTC")
  
        #remove nord data
        df = df[df['location_name'] != 'Bahnhofstrasse (Nord)']
  
    
        self.DF_PREVIOUS_YEAR = df[(df['timestamp_ts'] > Oct1_2021) & (df['timestamp_ts'] < Oct1_2022 ) ].copy()
        self.DF_LAST_YEAR = df[(df['timestamp_ts'] > Oct1_2022) & (df['timestamp_ts'] < Oct1_2023)].copy()
        
    def location_date_time_last_year(self):
        df_by_date = self.DF_LAST_YEAR.groupby(["month",'time_of_day', 'location_name']).agg(
                {"pedestrians_count": "sum", "adult_pedestrians_count":'sum', 'child_pedestrians_count':'sum' ,"month_year":'first' })
        return df_by_date
        
    def count_by_month(self, df):
        return df.groupby(['month']).agg({'pedestrians_count': 'sum',"month_year":'first'},sort=False)
        
        
    def count_by_month_last_year(self): 
        return self.count_by_month(self.DF_LAST_YEAR)
        
    def count_by_month_previous_year(self): 
        return self.count_by_month(self.DF_PREVIOUS_YEAR)
        
        
    def count_by_day(self, df): 
        return df.groupby(['date']).agg({'pedestrians_count': 'sum', 'day': 'first','month':'first',"month_year":'first' },sort=False)
        
    def count_by_day_last_year(self): 
        return self.count_by_day(self.DF_LAST_YEAR)
        

    def location_day_time(self,df):
        df_by_year = df.groupby(["day",'time_of_day', 'location_name']).agg(
                {"pedestrians_count": "sum" })
        return df_by_year

    def location_day_time_last_year(self):
        return self.location_day_time(self.DF_LAST_YEAR)

    '''
    def year_totals(self):
        previous_total = self.DF_PREVIOUS_YEAR['pedestrians_count'].sum()
        last_total = self.DF_LAST_YEAR['pedestrians_count'].sum()
        
        totals_df = pd.DataFrame(data = {'year': ['last_year', 'previous_year'], 'pedestrians_count': [last_total,previous_total]  })
        
        return totals_df
    '''
    
    def count_by_location(self, df): 
        return df.groupby(['location_name']).agg({'pedestrians_count': 'sum' },sort=False)
    
    def count_by_location_last_year(self):
        return self.count_by_location(self.DF_LAST_YEAR)
        