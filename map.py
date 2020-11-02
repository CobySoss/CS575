import geopandas as gpd
import pandas as pd
import json
import miditime
from miditime.miditime import MIDITime
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer
from bokeh.io import curdoc, output_notebook
from bokeh.models import Slider, HoverTool, Button
from bokeh.layouts import widgetbox, row, column
from covid_data import get_percentage_cases_by_month, get_monthly_increase_ratios_against_current_total
from sound import build_midi, play_midi, get_midi_scalars

month_str = {1:"January", 2:"February", 3:"March", 4:"April", 5:"May", 6:"June", 7:"July", 8:"August", 9:"September", 10:"October"}
df_who = pd.read_csv (r'WHO-COVID-19-global-data.csv')
monthly_increase_scalars = get_monthly_increase_ratios_against_current_total(df_who)
midi_scalars = get_midi_scalars(monthly_increase_scalars)

shapefile = 'mapfiles/ne_110m_admin_0_countries.shp'
#Read shapefile using Geopandas
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
#Rename columns.
gdf.columns = ['country', 'country_code', 'geometry']
print(gdf.head())

print(gdf[gdf['country'] == 'Antarctica'])
#Drop row corresponding to 'Antarctica'
gdf = gdf.drop(gdf.index[159])

df_month = get_percentage_cases_by_month(df_who, 6)
print(df_month)
merged = gdf.merge(df_month, left_on = 'country_code', right_on = " Country_code", how = 'left')
print(merged)
def json_data(selectedMonth):
    m = selectedMonth
    df_month = get_percentage_cases_by_month(df_who, selectedMonth)
    print(df_month)
    
    merged = gdf.merge(df_month, left_on = 'country_code', right_on = " Country_code", how = 'left')
    print(merged)
    merged.fillna('No data', inplace = True)
    merged_json = json.loads(merged.to_json())
    json_data = json.dumps(merged_json)
    return json_data


#Input GeoJSON source that contains features for plotting.
geosource = GeoJSONDataSource(geojson = json_data(1))
#Define a sequential multi-hue color palette.
palette = brewer['YlOrRd'][8]
#Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]
#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
color_mapper = LinearColorMapper(palette = palette, low = 0, high = 40, nan_color = '#d9d9d9')
#Define custom tick labels for color bar.
tick_labels = {'0': '0%', '5': '5%', '10':'10%', '15':'15%', '20':'20%', '25':'25%', '30':'30%','35':'35%', '40': '>40%'}
#Add hover tool
hover = HoverTool(tooltips = [ ('Country/region','@country'),('% obesity', '@per_cent_obesity')])
#Create color bar. 
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                     border_line_color=None,location = (0,0), orientation = 'horizontal', major_label_overrides = tick_labels)
#Create figure object.
p = figure(title = 'Share of adults who are obese, 2016', plot_height = 600 , plot_width = 950, toolbar_location = None, tools = [hover])
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
#Add patch renderer to figure. 
p.patches('xs','ys', source = geosource,fill_color = {'field' :'per_cent_obesity', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
#Specify layout
p.add_layout(color_bar, 'below')

# Define the callback function: update_plot
month = 1 

def thread_safe_update():
    month_str = {1:"January", 2:"February", 3:"March", 4:"April", 5:"May", 6:"June", 7:"July", 8:"August", 9:"September", 10:"October"}
    global month
    if month == 11:
        month = 1
    m = month
    filename = str(month) + ".midi"
    build_midi(filename, month, midi_scalars[month-1])
    new_data = json_data(m)
    print(m)
    geosource.geojson = new_data
    p.title.text = 'Covid19 perentage of total Cases for ' + month_str[m]
    month = month + 1
    play_midi(filename)

def on_click_handler():
    curdoc().add_periodic_callback(thread_safe_update, 4000)

 #Make a slider object: slider
button = Button(label = "Start")
button.on_click(on_click_handler)
layout = column(p,widgetbox(button))
curdoc().add_root(layout)
#Display plot inline in Jupyter notebook
#output_notebook()
#Display plot
#show(p)
