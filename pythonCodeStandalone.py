import miditime
import pandas as pd
import geopandas as geopd
from miditime.miditime import MIDITime
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="my_Dashboard")
import numpy as np

def geolocate(country=None):
    '''
    Inputs city and country, or just country. Returns the lat/long coordinates of 
    either the city if possible, if not, then returns lat/long of the center of the country.
    '''
    try:
            # Geolocate the center of the country
        loc = geolocator.geocode(country)
            # And return latitude and longitude 
        return (loc.latitude, loc.longitude)
        # Otherwise
    except:
            # Return missing value
        return np.nan

# Instantiate the class with a tempo (120bpm is the default) and an output file destination.
mymidi = MIDITime(120, 'myfile.mid')

# Create a list of notes. Each note is a list: [time, pitch, velocity, duration]
midinotes = [
    [0, 60, 127, 3],  #At 0 beats (the start), Middle C with velocity 127, for 3 beats
    [10, 61, 127, 4]  #At 10 beats (12 seconds from start), C#5 with velocity 127, for 4 beats
]

# Add a track with those notes
mymidi.add_track(midinotes)

# Output the .mid file
mymidi.save_midi()

df = pd.read_csv (r'WHO-COVID-19-global-data.csv')
location_data = pd.read_csv(r'lat_lon_for_covid.csv')


print (df)
midi_df = df[['Date_reported',' Country_code',' Country',' New_cases', ' Cumulative_cases',' Cumulative_deaths']]
midi_df_sorted = midi_df.sort_values(by=[' Country_code', 'Date_reported'])

def get_max_cases_per_country(who_df):
    df = who_df[['Date_reported',' Country_code',' Country',' New_cases', ' Cumulative_cases',' Cumulative_deaths']]
    df_sorted = df.sort_values(by=[' Country_code', 'Date_reported'])
    max_cases_by_country = df_sorted.groupby(' Country_code').agg(max_cases = pd.NamedAgg(column=" Cumulative_cases", aggfunc = max))
    return max_cases_by_country

def get_cumulative_cases_by_month(who_df, month_num):
    last_day = {1:31, 2:29, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31}
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
    print(df_max_cases)
    print(df_cumulative_cases_by_month)
    merged = pd.merge(df_max_cases, df_cumulative_cases_by_month, left_index = True, right_on = " Country_code")
    merged['percent_cases'] = merged[' Cumulative_cases'] / merged["max_cases"]
    print(merged)


get_percentage_cases_by_month(df, 6)


#get_percentage_cases_by_month(df)
country = midi_df_sorted[' Country'].unique()
country_df = pd.DataFrame({' Country': country})
#country_df['location'] = country_df[' Country'].apply(geolocate)
print(country_df)
print(location_data)
final_table = pd.merge(midi_df_sorted, location_data)
#country_df.to_csv('lat_lon_for_covid.csv')
print(final_table)


#difference = dataFrame.diff(axis=0)

