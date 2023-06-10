
import pandas as pd
import geopandas as gpd
# import matplotlib.pyplot as plt
from urllib.request import urlopen
import json
from jinja2 import Template

from bokeh.io import show, curdoc
from bokeh.models import (BoxZoomTool, ColorBar, CustomJS, CustomJSFilter,
                          GeoJSONDataSource, HoverTool,
                          LinearColorMapper, Slider, Range1d)
from bokeh.layouts import column, row
from bokeh.palettes import brewer, varying_alpha_palette, interp_palette
from bokeh.plotting import figure, output_file
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.util.browser import view

template = Template(
'''<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Programming Final</title>
    <link rel="stylesheet" href="css/style.css">
    <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-3.1.1.min.js"></script>
    {{ script }}
</head>
<body>
    <h1 class="page-title">Data Programming Final</h1>
    <div class="embed-wrapper">
        {% for key in div.keys() %}
            {{ div[key] }}
        {% endfor %}
    </div>
</body>
</html>
''')


def import_data(filename, encoding=None):
    return pd.read_csv(filename) if encoding is None else pd.read_csv(filename, encoding=encoding)


def import_map(filename):
    return gpd.read_file(filename)


def create_graph(map, name="Plot", data="POPESTIMATE2018"):
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
    """
    pass


def create_html(map, filename="index", data="POPESTIMATE2018", open_file=True):

    geosource = GeoJSONDataSource(geojson=map.to_json())

    max_data = map[data].max()

    filename += '.html'

    s = 0.75
    # Create figure object.
    plot1 = figure(
        # sizing_mode='stretch_both',
        # id="map_fig",
        height=int(s * 600),
        width=int(s * 950),
        # title="Honestly Don't Know What Goes Here",
        # x_range=(-182, -59),
        # y_range=(14, 74),
        x_range=(-128, -64),
        y_range=(22, 52),
        # toolbar_location='below',
        tools="pan, wheel_zoom, reset",
        active_scroll="wheel_zoom"
    )

    # Define color palettes
    palette_blue = brewer['Blues'][8]
    # palette_blue = palette_blue[::-1]  # reverse the order of the color palette
    palette = interp_palette(palette_blue, 256)
    color_mapper = LinearColorMapper(palette=palette, low=0, high=max_data)

    tick_labels = {
        0: '0',
        2_000_000: '2,000,000',
        4_000_000: '4,000,000',
        6_000_000: '6,000,000',
        8_000_000: '8,000,000',
        10_000_000: '10,000,000',
        15_000_000: '15,000,000',
        20_000_000: '20,000,000',
        25_000_000: '25,000,000',
        30_000_000: '30,000,000',
        35_000_000: '35,000,000',
        40_000_000: '40,000,000+'
    }

    color_bar = ColorBar(
        color_mapper=color_mapper,
        label_standoff=8,
        width=500,
        height=20,
        location=(0, 0),
        background_fill_alpha=1,
        background_fill_color='#121212',
        orientation='horizontal',
        major_label_overrides=tick_labels
    )

    plot1.xgrid.grid_line_color = None
    plot1.ygrid.grid_line_color = None

    plot1.border_fill_color = '#121212'

    # Add patch renderer to figure.
    counties = plot1.patches(
        'xs',
        'ys',
        source=geosource,
        fill_color={'field': data, 'transform': color_mapper},
        line_color='gray',
        line_width=0.25,
        fill_alpha=1
    )

    # Add separate tools and layouts
    plot1.add_tools(
        HoverTool(
            renderers=[counties],
            tooltips=[
                ('State', '@STATEFP'),
                ('County', '@NAME'),
                ('Population', '@POPESTIMATE2018'),
                ('Crimes per 1,000 People', '@Crimes_per_thousand')
            ]
        ),
        BoxZoomTool(match_aspect=True)
    )

    plot1.add_layout(color_bar, 'below')

    plots = dict(Crimes=plot1)

    doc = curdoc()
    doc.theme = 'dark_minimal'
    doc.add_root(plot1)

    script, div = components(plots)

    resources = INLINE.render()

    html = template.render(
        resources=resources,
        script=script,
        div=div
    )

    with open(filename, mode="w", encoding="utf-8") as file:
        file.write(html)

    if open_file:
        view(filename)


def convert_columns_to_floats(data, columns=[]):
    for col in columns:
        data[col] = data[col].str.replace(',', '').astype(float)


def main_small():
    print('Opening Data')
    washington_map = import_map('./src/data/washington.json')
    washington_map.head()

    print('Showing')


def main():

    print('Importing Data')
    # washington_map = import_map('./src/data/washington.json')
    county_map = import_map('./src/data/5m-US-counties.json')
    crime_data = import_data('./src/data/US_Offense_Type_by_Agency_2018-trim.csv')
    pop_data = import_data('./src/data/popest2018-trim.csv', encoding='latin-1')
    fips_codes = import_data('./src/data/statefipscodes.csv')

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

    # Find the number of crimes per 1,000 people by coutny
    merged_final['Crimes_per_thousand'] = 1000 * merged_final['Total Offenses'] / merged_final['POPESTIMATE2018']

    print('Graphing data')

    create_html(merged_final, filename='index', open_file=True, data='Crimes_per_thousand')

    print('Finished.')


if __name__ == "__main__":
    main()
    # main_small()
