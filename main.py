from multigrids import MultiGrid, tools

from spicebox import transforms
import os
import numpy as np
import matplotlib.pyplot as plt

from bokeh.io import curdoc
from bokeh.layouts import column, row, layout, Spacer
from bokeh.plotting import figure, output_file, show
from bokeh import palettes
from bokeh.transform import linear_cmap

from bokeh.models import TextInput, ColumnDataSource, FileInput, Div, Dropdown, Slider,ColorBar, LinearColorMapper, Title, Toggle, Button
from bokeh.events import Tap

from copy import deepcopy
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


def refresh_display():
    pass


def met_filter(data, year, toggle):
    if toggle:
        mean = data.config['mean']
        grid = data[year]

        diff = ( (grid - mean )/ np.abs(mean) ) * 100

        print("mean", mean[-1,-1], 'val', grid[-1,-1], diff[-1,-1])


        return diff[::-1]
    return data[year][::-1]


loc_div_txt = """
<p> location:  %fN %fW </p>
<p> value:  %f </p>
"""

def app():

    sites = data_sources.GLOBAL_SITE_DATA

    cp_threshold_toggle = False
    cp_threshold = 0

    predisp_toggle = False
    met_toggle = False

    current_region = "Utqiaġvik"
    

    start_year = sites[current_region]['data']['cp'].config['start_timestep']
    end_year = start_year + sites[current_region]['data']['cp'].config['num_timesteps']
    

    current_display = ColumnDataSource()
    current_display.data = data_sources.create_data(sites[current_region], start_year + 1)

    description = Div(text="<h2>Notes for area:</h2><p>"+ sites[current_region]['description'] + "</p>")

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
    
    current_display.data['cp_threshold_toggle'] = [cp_threshold_toggle]
    current_display.data['cp_threshold'] = [cp_threshold]
    current_display.data['predisp_toggle'] = [predisp_toggle]
    current_display.data['met_toggle'] = [met_toggle]

    cp_map = maps.create_cp_map(current_display)

    click_val = Div(text=loc_div_txt % (0, 0 , 0))
   
    def click_clack(event):

        current_region = current_display.data['region'][0]

        current_year = current_display.data['current_year'][0]
        predisp_toggle = current_display.data['predisp_toggle'][0]

        multiplier = 1
        if predisp_toggle: 
            multiplier = sites[current_region]['predisp_model']

        cur_map = sites[current_region]['data']['cp'][current_year][::-1] * multiplier

        col = int((event.x * cur_map.shape[1]) / 10) 
        row = int((event.y * cur_map.shape[0]) / 10) 

        md = sites[current_region]['data']['cp'].config['raster_metadata']

        val = cur_map[row, col]

        wgs_84 = transforms.to_wgs84(transforms.to_geo([row, col], md['transform']), md['projection'])

        click_val.text = loc_div_txt % (wgs_84[0], abs(wgs_84[1]) , val)

        # print(col, row, val)

    cp_map.on_event(Tap, click_clack)

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

    year_next = Button(label="Next Year", width=145)
    year_previous = Button(label="Previous Year", width=145)

    threshold_toggle = Toggle(label="climate priming threshold off")
    threshold_slider = Slider(
        start=-50, end=50, 
        step = .5,
        value=cp_threshold,
        title="Climate Priming Threshold"
    )

    predisp_toggle_button = Toggle(label="predisposition model overlay off")

    met_toggle_button = Toggle(label="Show Met as difference from mean off")

    def change_display_year(attrname, old, new):

        current_region = current_display.data['region'][0]

        current_year = int(new)

        cp_threshold_toggle = current_display.data['cp_threshold_toggle'][0]
        cp_threshold= current_display.data['cp_threshold'][0]

        predisp_toggle = current_display.data['predisp_toggle'][0]

        multiplier = 1
        if predisp_toggle: 
            multiplier = sites[current_region]['predisp_model']
       
        if cp_threshold_toggle:
            th_map =  deepcopy(sites[current_region]['data']['cp'][current_year][::-1]) * multiplier
            th_map[th_map >= cp_threshold] = 49 
            th_map[th_map < cp_threshold] = -49
            th_map[np.isinf(th_map)] = constants.CP_MIN - 10
            current_display.data['cp'] = [th_map]
        else:
            map_ = sites[current_region]['data']['cp'][current_year][::-1] * multiplier
            map_[np.isinf(map_)] = constants.CP_MIN - 10
            current_display.data['cp'] = [map_]

        current_display.data['cp_vals'] = [sites[current_region]['data']['cp'][current_year][::-1] * multiplier]

        display_average = timeseries.data['average'][new-start_year]
        current_display.data['current_average'] = [display_average ]
        current_display.data['current_year'] = [current_year]
        
        met_toggle = current_display.data['met_toggle'][0]
        current_display.data['tdd_last'] = [met_filter(sites[current_region]['data']['tdd'], current_year -1 , met_toggle)]
        current_display.data['tdd'] = [ met_filter(sites[current_region]['data']['tdd'], current_year, met_toggle)]
        current_display.data['fdd'] = [ met_filter(sites[current_region]['data']['fdd'], current_year -1, met_toggle)]
        current_display.data['ewp'] = [ met_filter(sites[current_region]['data']['ewp'], current_year -1, met_toggle)]
        current_display.data['fwp'] = [ met_filter(sites[current_region]['data']['fwp'], current_year -1 , met_toggle)]

        last_year = str(current_year - 1)
        current_year = str(current_year)

        tdd_last_map.select(name="title").text = last_year
        fdd_map.select(name="title").text = last_year + '-' + current_year
        tdd_map.select(name="title").text = current_year
        ewp_map.select(name="title").text = "Oct "+ last_year+" - Nov " + last_year
        fwp_map.select(name="title").text = "Oct "+ last_year +" - Mar " + current_year

    def next_year(event):

        yr = min(int(current_display.data['current_year'][0]) + 1, end_year)
        if yr == end_year:
            return
        change_display_year("", "", yr)
        year_slider.value=current_display.data['current_year'][0]
    
    def previous_year(event):

        yr = max(int(current_display.data['current_year'][0]) - 1, start_year + 1)
        if yr == end_year - 1:
            return
        change_display_year("", "", yr)
        year_slider.value=current_display.data['current_year'][0]

    def change_region(event):
       
        current_region = event.item
        current_display.data['region'] = [current_region]

        current_year = current_display.data['current_year'][0]
        
        cp_threshold_toggle = current_display.data['cp_threshold_toggle'][0]
        cp_threshold= current_display.data['cp_threshold'][0]

        predisp_toggle = current_display.data['predisp_toggle'][0]

        multiplier = 1
        if predisp_toggle: 
            multiplier = sites[current_region]['predisp_model']

        if cp_threshold_toggle:
            th_map = deepcopy(sites[current_region]['data']['cp'][current_year][::-1]) * multiplier
            th_map[th_map >= cp_threshold] = 49 
            th_map[th_map < cp_threshold] = -49
            th_map[np.isinf(th_map)] = constants.CP_MIN - 10
            current_display.data['cp'] = [th_map]
        else:
            map_ = sites[current_region]['data']['cp'][current_year][::-1] * multiplier
            map_[np.isinf(map_)] = constants.CP_MIN - 10
            current_display.data['cp'] = [map_]
        
        current_display.data['cp_vals'] = [sites[current_region]['data']['cp'][current_year][::-1] * multiplier]


        timeseries.data['average'] = data_sources.create_area_average_data(
            sites[current_region]['data']['cp']
        )

        display_average = timeseries.data['average'][current_year-start_year]
        current_display.data['current_average'] = [display_average ]
        current_display.data['current_year'] = [current_year]
        
        met_toggle = current_display.data['met_toggle'][0]
        current_display.data['tdd_last'] = [met_filter(sites[current_region]['data']['tdd'], current_year -1 , met_toggle)]
        current_display.data['tdd'] = [ met_filter(sites[current_region]['data']['tdd'], current_year, met_toggle)]
        current_display.data['fdd'] = [ met_filter(sites[current_region]['data']['fdd'], current_year -1, met_toggle)]
        current_display.data['ewp'] = [ met_filter(sites[current_region]['data']['ewp'], current_year -1, met_toggle)]
        current_display.data['fwp'] = [ met_filter(sites[current_region]['data']['fwp'], current_year -1 , met_toggle)]
        cp_map.title.text = sites[current_region]['name']

        description.text = "<h2>Notes for area:</h2><p>"+ sites[current_region]['description'] + "</p>"

    def toggle_threshold (event):

        cp_threshold_toggle = current_display.data['cp_threshold_toggle'][0]
        cp_threshold_toggle = not cp_threshold_toggle
        current_display.data['cp_threshold_toggle'] = [cp_threshold_toggle]

        current_region = current_display.data['region'][0]
        current_year = current_display.data['current_year'][0]

        predisp_toggle = current_display.data['predisp_toggle'][0]

        multiplier = 1
        if predisp_toggle: 
            multiplier = sites[current_region]['predisp_model']

        if cp_threshold_toggle:
            # print('on',cp_threshold_toggle)
            threshold_toggle.label="climate priming threshold on"
            th_map = deepcopy(sites[current_region]['data']['cp'][current_year][::-1]) * multiplier
            th_map[th_map >= cp_threshold] = 49
            th_map[th_map < cp_threshold] = -49
            th_map[np.isinf(th_map)] = constants.CP_MIN - 10
            current_display.data['cp'] = [th_map]
        else:
            # print('off',cp_threshold_toggle)
            threshold_toggle.label="climate priming threshold off"
            # print(current_region, current_year)
            map_ = sites[current_region]['data']['cp'][current_year][::-1] * multiplier
            map_[np.isinf(map_)] = constants.CP_MIN - 10
            current_display.data['cp'] = [map_]

    def change_threshold_value(attrname, old, new):

        cp_threshold = new
        current_display.data['cp_threshold'] = [cp_threshold]

        current_region = current_display.data['region'][0]
        current_year = current_display.data['current_year'][0]

        cp_threshold_toggle = current_display.data['cp_threshold_toggle'][0]

        predisp_toggle = current_display.data['predisp_toggle'][0]

        multiplier = 1
        if predisp_toggle: 
            multiplier = sites[current_region]['predisp_model']

        if cp_threshold_toggle:
            # print(cp_threshold)
            th_map = deepcopy(sites[current_region]['data']['cp'][current_year][::-1]) * multiplier
            th_map[th_map >= cp_threshold] = 49
            th_map[th_map < cp_threshold] = -49
            th_map[np.isinf(th_map)] = constants.CP_MIN - 10
            current_display.data['cp'] = [th_map]
        else:
            map_ = sites[current_region]['data']['cp'][current_year][::-1] * multiplier
            map_[np.isinf(map_)] = constants.CP_MIN - 10
            current_display.data['cp'] = [map_]

        # current_display.data['cp_vals'] = [sites[current_region]['data']['cp'][current_year][::-1]]

    def toggle_predisp(event): 
        predisp_toggle = current_display.data['predisp_toggle'][0]
        predisp_toggle = not predisp_toggle
        current_display.data['predisp_toggle'] = [predisp_toggle]

        current_region = current_display.data['region'][0]
        current_year = current_display.data['current_year'][0]
        cp_threshold_toggle = current_display.data['cp_threshold_toggle'][0]

        multiplier = 1
        if predisp_toggle: 
            multiplier = sites[current_region]['predisp_model']
            predisp_toggle_button.label="predisposition model overlay on"
        else:
            predisp_toggle_button.label="predisposition model overlay off"
            


        if cp_threshold_toggle:
            # print(cp_threshold)
            th_map = deepcopy(sites[current_region]['data']['cp'][current_year][::-1]) * multiplier
            th_map[th_map >= cp_threshold] = 49 
            th_map[th_map < cp_threshold] = -49
            th_map[np.isinf(th_map)] = constants.CP_MIN - 10
            current_display.data['cp'] = [th_map] 
        else:
            map_ = sites[current_region]['data']['cp'][current_year][::-1] * multiplier
            map_[np.isinf(map_)] = constants.CP_MIN - 10
            # print(map_)
            current_display.data['cp'] = [map_]
            
        current_display.data['cp_vals'] = [sites[current_region]['data']['cp'][current_year][::-1] * multiplier ] 

    def toggle_met(event): 
        met_toggle = current_display.data['met_toggle'][0]
        met_toggle = not met_toggle
        current_display.data['met_toggle'] = [met_toggle]

        current_region = current_display.data['region'][0]
        current_year = current_display.data['current_year'][0]
        cp_threshold_toggle = current_display.data['cp_threshold_toggle'][0]

        multiplier = 1
        if met_toggle: 
            met_toggle_button.label="Show Met as difference from mean on"

            diff_c_map = linear_cmap(
                field_name='average',palette=colors.blue_red, 
                low=-25, high=25, nan_color='white'
            )

            tdd_last_map.renderers[0].glyph.color_mapper = diff_c_map['transform']
            fdd_map.renderers[0].glyph.color_mapper = diff_c_map['transform']
            tdd_map.renderers[0].glyph.color_mapper = diff_c_map['transform']
            ewp_map.renderers[0].glyph.color_mapper = diff_c_map['transform']
            fwp_map.renderers[0].glyph.color_mapper = diff_c_map['transform']



            # fdd_map.select('cb')[0].color_mapper = linear_cmap(
            #     field_name='average',palette=colors.blue_red, 
            #     low=-25, high=25, nan_color='white'
            # )['transform']
        else:
            met_toggle_button.label="Show Met as difference from mean off"
            tdd_last_map.renderers[0].glyph.color_mapper = LinearColorMapper(palettes.Reds256[::-1], 
                low=constants.TDD_MIN, high=constants.TDD_MAX, 
                nan_color='white'
            )

            fdd_cmap=LinearColorMapper(palettes.Blues256, 
                low=constants.FDD_MIN, high=constants.FDD_MAX, 
                nan_color='white'
            )
            fdd_map.renderers[0].glyph.color_mapper = fdd_cmap

            tdd_map.renderers[0].glyph.color_mapper = LinearColorMapper(palettes.Reds256[::-1], 
                low=constants.TDD_MIN, high=constants.TDD_MAX, 
                nan_color='white'
            )
            ewp_map.renderers[0].glyph.color_mapper = LinearColorMapper(palettes.Greens256[::-1], 
                low=constants.TDD_MIN, high=constants.TDD_MAX, 
                nan_color='white'
            )
            fwp_map.renderers[0].glyph.color_mapper = LinearColorMapper(palettes.Greens256[::-1], 
                low=constants.TDD_MIN, high=constants.TDD_MAX, 
                nan_color='white'
            )


            # fdd_map.select('cb')[0].color_mapper = fdd_cmap
            # print(fdd_map.renderers[0])
            # print(dir(fdd_map.renderers[0]))


        
        current_display.data['tdd_last'] = [met_filter(sites[current_region]['data']['tdd'], current_year -1 , met_toggle)]
        current_display.data['tdd'] = [ met_filter(sites[current_region]['data']['tdd'], current_year, met_toggle)]
        current_display.data['fdd'] = [ met_filter(sites[current_region]['data']['fdd'], current_year -1, met_toggle)]
        current_display.data['ewp'] = [ met_filter(sites[current_region]['data']['ewp'], current_year -1, met_toggle)]
        current_display.data['fwp'] = [ met_filter(sites[current_region]['data']['fwp'], current_year -1 , met_toggle)]



        
       
    year_slider.on_change('value_throttled', change_display_year)
    region_dropdown.on_click(change_region)
    threshold_toggle.on_click(toggle_threshold)
    threshold_slider.on_change('value_throttled', change_threshold_value)
    predisp_toggle_button.on_click(toggle_predisp)
    year_next.on_click(next_year)
    year_previous.on_click(previous_year)
    met_toggle_button.on_click(toggle_met)


    inputs = column([region_dropdown, year_slider, row([year_previous, year_next] ), predisp_toggle_button, threshold_toggle,threshold_slider, met_toggle_button, click_val])

    title = Div(text="<H1>CLIMATE PRIMING EXPLORER<H1>", width=1000)
    from copy import deepcopy
    dd_row = row([tdd_last_map, fdd_map, tdd_map])
    precip_row = row( [Spacer(width=100, height = 100), ewp_map, fwp_map])
    met_col = column(dd_row, precip_row)

    

    curdoc().add_root(
        layout([
            [title],
            [inputs, cp_map, hidden_plot, met_col  ] ,
            [average_plot, description]
        ]) 
        
    )
    curdoc().title = "Climate Priming Explorer"

    

    

# if __name__=="__main__":
app() 
