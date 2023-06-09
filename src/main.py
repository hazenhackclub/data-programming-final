
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from urllib.request import urlopen
import json
from bokeh.io import show
from bokeh.models import (CDSView, ColorBar, ColumnDataSource,
                          CustomJS, CustomJSFilter, 
                          GeoJSONDataSource, HoverTool,
                          LinearColorMapper, Slider, Range1d)
from bokeh.layouts import column, row
from bokeh.palettes import brewer
from bokeh.plotting import figure
import plotly.express as px
import plotly.io as pio


def import_data(filename):
    return pd.read_csv(filename)


def import_map(filename):
    return gpd.read_file(filename)


def create_graph(map, name="Plot", data="POPESTIMATE2018"):
    """

    """

    fig, ax = plt.subplots(1)

    map.plot(ax=ax, color='#bababa')
    map.plot(ax=ax, column=data, legend=True, linewidth=10)

    plt.xlabel('This is the longitude')
    plt.ylabel('This is the latitude')
    plt.title("This is a graph with resolution of 400 dpi")
    # plt.axis([-128, -64, 22, 52])
    plt.axis([-182, -59, 14, 74])  # other territories included
    plt.savefig(name + '.png', dpi=700)


def create_html(map, data="POPESTIMATE2018", open=True):

    geosource = GeoJSONDataSource(geojson=map.to_json())

    # Create figure object.
    fig = figure(
        title="Honestly Don't Know What Goes Here",
        # plot_height=600,
        # outer_height=600,
        height=600,
        # min_height=600,
        # plot_width=950,
        # outer_width=950,
        width=950,
        # min_width=950,
        x_range=(0, 20),
        y_range =(0, 20),
        toolbar_location='below',
        tools="pan, wheel_zoom, box_zoom, reset")
    fig.xgrid.grid_line_color = None
    fig.ygrid.grid_line_color = None
    # Add patch renderer to figure.
    states = fig.patches(
        'xs',
        'ys',
        source=geosource,
        fill_color=None,
        line_color='gray',
        line_width=0.25,
        fill_alpha=1
    )

    # Create hover tool
    fig.add_tools(HoverTool(renderers=[states], tooltips=[('State', '@NAME'), ('Population', '@' + data)]))

    if open:
        show(fig)

def convert_columns_to_floats(data, columns=[]):
    for col in columns:
        data[col] = data[col].str.replace(',', '').astype(float)


def main2():
    print('Opening Data')
    washington_map = import_map('./src/data/washington.json')
    washington_map.head()

    print('Showing')


def main():

    print('Importing Data')
    # washington_map = import_map('./src/data/washington.json')
    county_map = import_map('./src/data/5m-US-counties.json')
    crime_data = import_data('./src/data/US_Offense_Type_by_Agency_2018-trim.csv')
    fips_codes = import_data('./src/data/statefipscodes.csv')
    pop_data = pd.read_csv('./src/data/popest2018-trim.csv', encoding='latin-1')

    # Regularize the data
    convert_columns_to_floats(crime_data, ['Total Offenses', 'Population1'])
    agency_type_county = crime_data['Agency Type'].str.lower().str.contains("count")
    crime_data = crime_data[agency_type_county]

    county_county = pop_data['CTYNAME'].str.lower().str.contains("count")
    pop_data = pop_data[county_county]
    pop_data['CTYNAME'] = pop_data['CTYNAME'].str.replace(' County', '')

    county_map['STATEFP'] = county_map['STATEFP'].astype(int)
    merged_map = county_map.merge(fips_codes, left_on='STATEFP', right_on='FIPS', how='right')

    # Combines state and county names for merging
    crime_data['state_county'] = crime_data['State'].str.upper() + '-' + crime_data['Agency Name'].str.upper()
    pop_data['state_county'] = pop_data['STNAME'].str.upper() + '-' + pop_data['CTYNAME'].str.upper()
    merged_map['state_county'] = merged_map['State'].str.upper() + '-' + merged_map['NAME'].str.upper()

    # Merging data
    print('Merging data')
    merged_data = pop_data.merge(crime_data, left_on='state_county', right_on='state_county', how='outer')

    merged_final = merged_map.merge(merged_data, left_on='state_county', right_on='state_county', how='left')

    # pandas.set_option('display.max_rows', 500)
    # pandas.set_option('display.max_columns', 500)
    # print('merged_final', merged_final)

    # Find the number of crimes per 1,000 people by coutny
    merged_final['Crimes_per_thousand'] = 1000 * merged_final['Total Offenses'] / merged_final['POPESTIMATE2018']

    """
    county_map columns: ['id', 'STATEFP', 'COUNTYFP', 'COUNTYNS', 'AFFGEOID', 'GEOID', 'NAME', 'LSAD', 'ALAND', 'AWATER', 'geometry']
    crime_data columns: ['State', 'Agency Type', 'Agency Name,' 'Population1', 'Total Offenses', ...]

    Info:

    washington_map length: 39
    county_map length: 3233

    crime_data length: 5962
        regularized length: 1184
    pop_data length: 3193
        regularized length: 3007
    merged_data length: 6540

    counties: 1184

    ARIZONA Crimes Per Thousand: 47.934547
    """

    print('Graphing data')

    # create_graph(merged_final, data='STATEFP')
    create_html(merged_final, open=True)

    print('Finished.')


if __name__ == "__main__":
    main()
