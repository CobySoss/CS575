import pandas as pd
import geopandas as geopd
import numpy as np
import pycountry as pc
from datetime import datetime as dt
import math

df = pd.read_csv (r'WHO-COVID-19-global-data.csv')
location_data = pd.read_csv(r'lat_lon_for_covid.csv')

#test comment here
print (df)
midi_df = df[['Date_reported',' Country_code',' Country',' New_cases', ' Cumulative_cases',' Cumulative_deaths']]
midi_df_sorted = midi_df.sort_values(by=[' Country_code', 'Date_reported'])

def get_max_new_daily_cases_for_regions(who_df):
    new_daily_cases_per_region = get_new_daily_cases_by_region(who_df)
    max_new_daily_cases_for_regions = new_daily_cases_per_region.agg(max_daily_new_regional_cases = pd.NamedAgg(column="total_new_daily_cases", aggfunc = max))
    print(new_daily_cases_per_region)
    return max_new_daily_cases_for_regions.loc['max_daily_new_regional_cases', 'total_new_daily_cases']


def get_new_daily_cases_by_region(who_df):
    df = who_df[['Date_reported',' WHO_region',' Country_code',' Country',' New_cases']]
    df_sorted = df.sort_values(by=['Date_reported'])
    print(df_sorted)
    new_daily_cases_per_region = df_sorted.groupby(['Date_reported', ' WHO_region']).agg(total_new_daily_cases = pd.NamedAgg(column=" New_cases", aggfunc = sum))
    return new_daily_cases_per_region

def get_max_cases_per_country(who_df):
    df = who_df[['Date_reported',' Country_code',' Country',' New_cases', ' Cumulative_cases',' Cumulative_deaths']]
    df_sorted = df.sort_values(by=[' Country_code', 'Date_reported'])
    max_cases_by_country = df_sorted.groupby(' Country_code').agg(max_cases = pd.NamedAgg(column=" Cumulative_cases", aggfunc = max))
    return max_cases_by_country

def get_cumulative_cases_by_month(who_df, month_num):
    last_day = {1:31, 2:29, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:30}
    day = last_day[month_num]
    date_str = "2020" + '-' + "{:02d}".format(month_num) + '-' + str(day)
    df_sorted = who_df.sort_values(by=[' Country_code', 'Date_reported'])
    print(df_sorted)
    is_monthly_cumulative = df_sorted['Date_reported'] == date_str
    df_sorted_filtered = df_sorted[is_monthly_cumulative]
    print(df_sorted_filtered)
    return df_sorted_filtered[['Date_reported', ' Country_code', ' Cumulative_cases']]

def get_percentage_cases_by_month(who_df, month_num):
    df_max_cases = get_max_cases_per_country(who_df)
    df_cumulative_cases_by_month = get_cumulative_cases_by_month(who_df, month_num)
    total_global_cases = df_max_cases["max_cases"].sum(skipna = True) 
    print(df_max_cases)
    print(df_cumulative_cases_by_month)
    merged = pd.merge(df_max_cases, df_cumulative_cases_by_month, left_index = True, right_on = " Country_code")
    merged['per_cent_covid'] = (merged[' Cumulative_cases'] / total_global_cases) * 100
    merged[' Country_code'] = merged[' Country_code'].apply(lambda x: convert_to_a3_codes(x))
    return merged[[' Country_code', 'per_cent_covid']]

def convert_to_a3_codes(x):
    country = pc.countries.get(alpha_2=x)
    if country != None:
        return country.alpha_3
    return x

def get_percentage_of_total_cases_for_month(who_df, month):
    max_cases_per_country = get_max_cases_per_country(who_df)   
    total_global_cases = max_cases_per_country["max_cases"].sum(skipna = True) 
    cumulative_cases_for_month = get_cumulative_cases_by_month(who_df, month)
    new_monthly_cases =  cumulative_cases_for_month[" Cumulative_cases"].sum(skipna = True)
    if month > 1:
        cumulative_cases_for_prev_month = get_cumulative_cases_by_month(who_df, month - 1)
        last_month_cases =  cumulative_cases_for_prev_month[" Cumulative_cases"].sum(skipna = True)
        new_monthly_cases = new_monthly_cases - last_month_cases
    return new_monthly_cases / total_global_cases

def get_monthly_increase_ratios_against_current_total(who_df):
    monthly_case_contributions = []
    i = 1
    while(i < 11):
        monthly_case_contributions.append(get_percentage_of_total_cases_for_month(who_df, i))
        i = i + 1
    return monthly_case_contributions

def get_daily_velocity_coefficients_by_region(who_df):
    new_daily_cases_by_region = get_new_daily_cases_by_region(df)
    max_new_daily_cases_across_all_regions = get_max_new_daily_cases_for_regions(df)
    new_daily_cases_by_region["velocity_coefficient"] = new_daily_cases_by_region["total_new_daily_cases"]/max_new_daily_cases_across_all_regions
    return new_daily_cases_by_region

def region_to_note(region_name):
    region_map = {
        "AFRO": 65,
        "WPRO": 66,
        "SEARO": 67,
        "EURO": 68,
        "Other": 69,
        "AMRO" : 70,
        "EMRO" : 71
    }
    return region_map[region_name]

def region_to_channel(region_name):
    region_map = {
        "AFRO": 0,
        "WPRO": 1,
        "SEARO": 2,
        "EURO": 3,
        "Other": 4,
        "AMRO" : 5,
        "EMRO" : 6
    }
    return region_map[region_name]

def get_midi_notes():
    newdf = get_daily_velocity_coefficients_by_region(df)
    print(newdf)
    midi_notes = []
    for date_and_region, velocity_coeff in newdf.iterrows():
        date = date_and_region[0]
        region = date_and_region[1]
        date_time_obj = dt.strptime(date, '%Y-%m-%d')
        day_of_year =  date_time_obj.timetuple().tm_yday 
        coefficient = velocity_coeff["velocity_coefficient"]
        velocity = math.floor(127*coefficient)
        if(velocity < 0):
            velocity = 0
        #format: [beat, note, channel, velocity, duration]    
        midi_notes.append([day_of_year, region_to_note(region), region_to_channel(region), velocity, 1])    
        print(date, region, coefficient)
        print(date_and_region, velocity_coeff)
        print()
    return midi_notes

