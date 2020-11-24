from multigrids import MultiGrid, tools
import os
import numpy as np
import matplotlib.pyplot as plt

from bokeh.io import curdoc
from bokeh.layouts import column, row, layout, Spacer
from bokeh.plotting import figure, output_file, show
from bokeh import palettes
from bokeh.transform import linear_cmap

from bokeh.models import TextInput, ColumnDataSource, FileInput, Div, Dropdown, Slider,ColorBar, LinearColorMapper, Title


## TEST DATA setup
# path = "/Volumes/scarif/data/V2/datasets/derived/fdd_ACP_CRU_v3/tiff/"
# load_params = {
#     "method": "tiff",
#     "directory": path
# }
# create_params = {
#     'start_timestep':1901,
#     'raster_metadata': tools.get_raster_metadata(os.path.join(path, "freezing_degree-day_1901.tif"))
# }

# test_data = tools.load_and_create(load_params, create_params)

# UTQ = test_data.zoom_to((70.9, -156), location_format="WGS84")
# PRU = test_data.zoom_to((70, -151), location_format="WGS84")

# print (UTQ.config['grid_shape'])
# print (PRU.config['grid_shape'])


## TEST DATA setup












import plots, constants, maps, colors
import data_sources

# from sites import LOCATIONS


def app():

    sites = data_sources.GLOBAL_SITE_DATA

    current_region = "Utqiaġvik"
    

    start_year = sites[current_region]['data']['cp'].config['start_timestep']
    end_year = start_year + sites[current_region]['data']['cp'].config['num_timesteps']
    

    current_display = ColumnDataSource()
    current_display.data = data_sources.create_data(sites[current_region], start_year + 1)

    

    timeseries = ColumnDataSource()
    timeseries.data = {
        "years": range(start_year,end_year), 
        "average": data_sources.create_area_average_data(
            sites[current_region]['data']['cp']
        )
    }

    current_year = current_display.data['current_year'][0]
    display_average = timeseries.data['average'][current_year  -start_year]
    current_display.data['current_average'] = [display_average]
    current_display.data['region'] = [current_region ]
    

    cp_map = maps.create_cp_map(current_display)




    average_plot = plots.create_average_plot(current_display, timeseries, start_year)

    hidden_plot = figure(
        plot_width=100, plot_height=constants.WIDTH*2, 
        tools=[],
        title = "CLIMATE PRIMING VAL",title_location="right",
        toolbar_location=None, min_border=0, 
        outline_line_color=None
    )
    hidden_plot.toolbar.logo = None
    hidden_plot.toolbar_location = None
    hidden_plot.title.align="center"
    hidden_plot.title.text_font_size = '12pt'

    color_mapper = linear_cmap(
        field_name='average',palette=colors.blue_red, 
        low=constants.CP_MIN, high=constants.CP_MAX
    )
    color_bar = ColorBar(color_mapper=color_mapper['transform'], width=8,  location=(0,0))
    hidden_plot.add_layout(color_bar, 'right')
    

    current_year = current_display.data['current_year'][0]
    last_year = str(current_year - 1)
    current_year = str(current_year)
    tdd_last_map = maps.create_met_map(
        current_display, "tdd_last", 1,
        palettes.Reds256[::-1], constants.TDD_MIN, constants.TDD_MAX
    )
    tdd_last_map.add_layout(Title(text=last_year, name='title'), 'above')
    tdd_last_map.add_layout(Title(text="Thawing Degree Days "), 'above')

    fdd_map = maps.create_met_map(current_display, "fdd", 1,
        palettes.Blues256, constants.FDD_MIN, constants.FDD_MAX
    )
    fdd_map.add_layout(Title(text=last_year + '-' + current_year, name='title'), 'above')
    fdd_map.add_layout(Title(text="Freezing Degree Days "), 'above')

    tdd_map = maps.create_met_map(
        current_display, "tdd", 0,
        palettes.Reds256[::-1], constants.TDD_MIN, constants.TDD_MAX
    )
    tdd_map.add_layout(Title(text=current_year, name='title'), 'above')
    tdd_map.add_layout(Title(text="Thawing Degree Days "), 'above')

    ewp_map = maps.create_met_map(
        current_display, "ewp", 1,
        palettes.Greens256[::-1], constants.EWP_MIN, constants.EWP_MAX
    )
    ewp_map.add_layout(Title(text="Oct "+ last_year+" - Nov " + last_year, name='title'), 'above')
    ewp_map.add_layout(Title(text="Early Winter Precipitation [mm]"), 'above')

    fwp_map = maps.create_met_map(
        current_display, "fwp", 1,
        palettes.Greens256[::-1], constants.FWP_MIN, constants.FWP_MAX
    )
    fwp_map.add_layout(Title(text="Oct "+ last_year +" - Mar " + current_year, name='title'), 'above')
    fwp_map.add_layout(Title(text="Total Winter Precipitation [mm]"), 'above')

    # fwp_map.add_layout() Div(text="<div>Total winter precipitation<div></div>  + "</div>")


    options = [(sites[r]['name'], r) for r in sites]
    region_dropdown = Dropdown(label="region", menu=options)

    year_slider = Slider(
        start=start_year+1, end=end_year - 1, 
        value=current_display.data['current_year'][0], step=1, title="Year"
    )

    def change_display_year(attrname, old, new):

        current_region = current_display.data['region'][0]
       
        current_display.data['cp']  = [sites[current_region]['data']['cp'][int(new)][::-1]]
        display_average = timeseries.data['average'][new-start_year]
        current_display.data['current_average'] = [display_average ]
        current_display.data['current_year'] = [new]
        
        current_display.data['tdd_last'] = [sites[current_region]['data']['tdd'][new - 1][::-1]]
        current_display.data['tdd'] = [sites[current_region]['data']['tdd'][new ][::-1]]
        current_display.data['fdd'] = [sites[current_region]['data']['fdd'][new  - 1][::-1]]
        current_display.data['ewp'] = [sites[current_region]['data']['ewp'][new  - 1][::-1]]
        current_display.data['fwp'] = [sites[current_region]['data']['fwp'][new  - 1][::-1]]

        last_year = str(new - 1)
        current_year = str(new)

        tdd_last_map.select(name="title").text = last_year
        fdd_map.select(name="title").text = last_year + '-' + current_year
        tdd_map.select(name="title").text = current_year
        ewp_map.select(name="title").text = "Oct "+ last_year+" - Nov " + last_year
        fwp_map.select(name="title").text = "Oct "+ last_year +" - Mar " + current_year

        

    def change_region(event):
       
        current_region = event.item
        current_display.data['region'] = [current_region]

        new = current_display.data['current_year'][0]
        
        current_display.data['cp']  = [sites[current_region]['data']['cp'][int(new)][::-1]]
        

        timeseries.data['average'] = data_sources.create_area_average_data(
            sites[current_region]['data']['cp']
        )

        display_average = timeseries.data['average'][new-start_year]
        current_display.data['current_average'] = [display_average ]
        current_display.data['current_year'] = [new]
        
        current_display.data['tdd_last'] = [sites[current_region]['data']['tdd'][new - 1][::-1]]
        current_display.data['tdd'] = [sites[current_region]['data']['tdd'][new ][::-1]]
        current_display.data['fdd'] = [sites[current_region]['data']['fdd'][new  - 1][::-1]]
        current_display.data['ewp'] = [sites[current_region]['data']['ewp'][new  - 1][::-1]]
        current_display.data['fwp'] = [sites[current_region]['data']['fwp'][new  - 1][::-1]]
        cp_map.title.text = sites[current_region]['name']

   

       
    year_slider.on_change('value_throttled', change_display_year)
    region_dropdown.on_click(change_region)

    inputs = column([region_dropdown, year_slider])

    title = Div(text="<H1>CLIMATE PRIMING EXPLORER<H1>", width=1000)
    from copy import deepcopy
    dd_row = row([tdd_last_map, fdd_map, tdd_map])
    precip_row = row( [Spacer(width=100, height = 100), ewp_map, fwp_map])
    met_col = column(dd_row, precip_row)

    curdoc().add_root(
        layout([
            [title],
            [inputs, cp_map, hidden_plot, met_col  ] ,
            [average_plot]
        ]) 
        
    )
    curdoc().title = "Climate Priming Explorer"

    

    

# if __name__=="__main__":
app() 
