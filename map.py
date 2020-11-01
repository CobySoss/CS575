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
from covid_data import get_percentage_cases_by_month

df = pd.read_csv (r'WHO-COVID-19-global-data.csv')

percent_cases = get_percentage_cases_by_month(df, 6)
print(percent_cases)
shapefile = 'mapfiles/ne_110m_admin_0_countries.shp'
#Read shapefile using Geopandas
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
#Rename columns.
gdf.columns = ['country', 'country_code', 'geometry']
print(gdf.head())

print(gdf[gdf['country'] == 'Antarctica'])
#Drop row corresponding to 'Antarctica'
gdf = gdf.drop(gdf.index[159])

obesity_file = 'data/obesity.csv'

#Read csv file using pandas
df = pd.read_csv(obesity_file, names = ['entity', 'code', 'year', 'per_cent_obesity'], skiprows = 1)
print(df.head())


def json_data(selectedYear):
    yr = selectedYear
    df_yr = df[df['year'] == yr]
    merged = gdf.merge(df_yr, left_on = 'country_code', right_on =     'code', how = 'left')
    merged.fillna('No data', inplace = True)
    merged_json = json.loads(merged.to_json())
    json_data = json.dumps(merged_json)
    return json_data


#Input GeoJSON source that contains features for plotting.
geosource = GeoJSONDataSource(geojson = json_data(2016))
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
year = 2016
def update_plot(attr, old, new):
    yr = new
    new_data = json_data(yr)
    geosource.geojson = new_data
    p.title.text = 'Share of adults who are obese, %d' %yr
    
def thread_safe_update():
    global year
    if year == 1975:
        year = 2016
    yr = year
    new_data = json_data(yr)
    print(year)
    geosource.geojson = new_data
    p.title.text = 'Share of adults who are obese, %d' %yr
    year = year - 1

def on_click_handler():
    curdoc().add_periodic_callback(thread_safe_update, 4000)

 #Make a slider object: slider
button = Button(label = "The Button")
button.on_click(on_click_handler)
slider = Slider(title = 'Year',start = 1975, end = 2016, step = 1, value = 2016)
slider.on_change('value', update_plot)
 #Make a column layout of widgetbox(slider) and plot, and add it to the current document
layout = column(p,widgetbox(slider), widgetbox(button))
curdoc().add_root(layout)
#Display plot inline in Jupyter notebook
#output_notebook()
#Display plot

#show(p)
#i = 0
