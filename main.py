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


def met_filter(data, year, toggle):
    if toggle:
        mean = data.config['mean']
        grid = data[year]

        diff = ( (grid - mean )/ np.abs(mean) ) * 100

        print("mean", mean[-1,-1], 'val', grid[-1,-1], diff[-1,-1])


        return diff[::-1]
    return data[year][::-1]

def update_display(sites, maps, timeseries, values):

    cp = sites[values['region']]['data']['cp']
    start_year = cp.config['start_timestep']
    end_year = start_year + cp.config['num_timesteps']

    timeseries.data['average'] = data_sources.create_area_average_data(cp)
    display_average = timeseries.data['average'][ values['year'] -start_year ]
    maps.data['current_average'] = [display_average ]
    maps.data['current_year'] = [values['year']]

    pd_filter = 1
    if values['predisp']['toggle']: 
        pd_filter = sites[values['region']]['predisp_model']
    
    cp_map = \
        sites[values['region']]['data']['cp'][values['year']][::-1] * pd_filter

    maps.data['cp_vals'] = [deepcopy(cp_map)]

    if values['threshold']['toggle']:
        cp_map = deepcopy(cp_map)  # Ensures data is not over written ## check if needed?
        cp_map[cp_map >= values['threshold']['value']] = constants.CP_MAX - 1 
        cp_map[cp_map < values['threshold']['value']] = constants.CP_MIN + 1 
    
    
    cp_map[np.isinf(cp_map)] = constants.CP_MIN - 10    
    maps.data['cp'] = [cp_map]
    
    

    for m_var in ['tdd_last', 'fdd', 'ewp', 'fwp']:
        maps.data[m_var] = [
            met_filter(
                sites[values['region']]['data'][m_var.replace('_last','')],
                values['year'] - 1, 
                values['met']['toggle']
            )
        ]
    maps.data['tdd'] = [
        met_filter(
            sites[values['region']]['data']['tdd'], 
            values['year'], 
            values['met']['toggle']
        )
    ]
       

    





loc_div_txt = """
<p> location:  %fN %fW </p>
<p> value:  %f </p>
"""

def app():

    sites = data_sources.GLOBAL_SITE_DATA

    # cp_threshold_toggle = False
    # cp_threshold = 0

    # predisp_toggle = False
    # met_toggle = False

    init_region = "Utqiaġvik"
    init = sites[init_region]['data']['cp']
    start_year = init.config['start_timestep']
    end_year = start_year + init.config['num_timesteps']
    
    current_values = {
        'region': init_region,
        'year': start_year + 1,
        'met': {'toggle': False},
        'threshold': {'toggle': False, 'value':0},
        'predisp': {'toggle': False},
    }

    
    
    display = ColumnDataSource()
    display.data = data_sources.create_data(
        sites[current_values['region']], 
        current_values['year']
    )

    description = Div(text="<h2>Notes for area:</h2><p>"+ sites[ current_values['region'] ]['description'] + "</p>")

    timeseries = ColumnDataSource()
    timeseries.data = {
        "years": range( start_year, end_year ), 
        "average": data_sources.create_area_average_data(
            sites[ current_values['region'] ]['data']['cp']
        )
    }

    # current_year =current_values['year']

    display_average = timeseries.data['average'][current_values['year'] - start_year]

    # display.data['current_average'] = [display_average]
    # display.data['region'] = [current_region ]
    
    # display.data['cp_threshold_toggle'] = [cp_threshold_toggle]
    # display.data['cp_threshold'] = [cp_threshold]
    # display.data['predisp_toggle'] = [predisp_toggle]
    # display.data['met_toggle'] = [met_toggle]

    update_display(sites, display, timeseries, current_values)
    
    cp_map = maps.create_cp_map(display)

    click_val = Div(text=loc_div_txt % (0, 0 , 0))
   
    def click_clack(event):

        current_region = current_values['region']

        current_year =current_values['year']
        predisp_toggle = current_values['predisp']['toggle']

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

    average_plot = plots.create_average_plot(display, timeseries, start_year)

    


    ### COLOR BAR
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
    

    current_year  =current_values['year']
    last_year = str(current_year - 1)
    current_year = str(current_year)
    
    
    ### MET MAPS
    tdd_last_map = maps.create_met_map(
        display, "tdd_last", 1,
        palettes.Reds256[::-1], constants.TDD_MIN, constants.TDD_MAX
    )
    tdd_last_map.add_layout(Title(text=last_year, name='title'), 'above')
    tdd_last_map.add_layout(Title(text="Thawing Degree Days "), 'above')

    fdd_map = maps.create_met_map(display, "fdd", 1,
        palettes.Blues256, constants.FDD_MIN, constants.FDD_MAX
    )
    fdd_map.add_layout(Title(text=last_year + '-' + current_year, name='title'), 'above')
    fdd_map.add_layout(Title(text="Freezing Degree Days "), 'above')

    tdd_map = maps.create_met_map(
        display, "tdd", 0,
        palettes.Reds256[::-1], constants.TDD_MIN, constants.TDD_MAX
    )
    tdd_map.add_layout(Title(text=current_year, name='title'), 'above')
    tdd_map.add_layout(Title(text="Thawing Degree Days "), 'above')

    ewp_map = maps.create_met_map(
        display, "ewp", 1,
        palettes.Greens256[::-1], constants.EWP_MIN, constants.EWP_MAX
    )
    ewp_map.add_layout(Title(text="Oct "+ last_year+" - Nov " + last_year, name='title'), 'above')
    ewp_map.add_layout(Title(text="Early Winter Precipitation [mm]"), 'above')

    fwp_map = maps.create_met_map(
        display, "fwp", 1,
        palettes.Greens256[::-1], constants.FWP_MIN, constants.FWP_MAX
    )
    fwp_map.add_layout(Title(text="Oct "+ last_year +" - Mar " + current_year, name='title'), 'above')
    fwp_map.add_layout(Title(text="Total Winter Precipitation [mm]"), 'above')

    # fwp_map.add_layout() Div(text="<div>Total winter precipitation<div></div>  + "</div>")


    ##### CONTROLS ---------

    options = [(sites[r]['name'], r) for r in sites]
    region_dropdown = Dropdown(label="region", menu=options)

    year_slider = Slider(
        start=start_year+1, end=end_year - 1, 
        value=current_values['year'], step=1, title="Year"
    )
    year_next = Button(label="Next Year", width=145)
    year_previous = Button(label="Previous Year", width=145)

    threshold_toggle = Toggle(label="climate priming threshold off")
    threshold_slider = Slider(
        start=constants.CP_MIN, end=constants.CP_MAX, 
        step = .5,
        value=current_values['threshold']['value'],
        title="Climate Priming Threshold"
    )

    predisp_toggle_button = Toggle(label="predisposition model overlay off")

    met_toggle_button = Toggle(label="Show Met as difference from mean off")

    ##### CALLBACKS

    def change_display_year(attrname, old, new):
     
        current_values['year'] = new
  

        update_display(
            sites, 
            display, timeseries, 
            current_values
        )

        last_year = str(current_values['year'] - 1)
        year = str(current_values['year'])

        tdd_last_map.select(name="title").text = last_year
        fdd_map.select(name="title").text = last_year + '-' + year
        tdd_map.select(name="title").text = year
        ewp_map.select(name="title").text = "Oct "+ last_year+" - Nov " + last_year
        fwp_map.select(name="title").text = "Oct "+ last_year +" - Mar " + year


    def next_year(event):

        yr = min(current_values['year'] + 1, end_year)
        if yr == end_year:
            return
        change_display_year("", "", yr)
        year_slider.value = current_values['year']
    
    def previous_year(event):

        yr = max(current_values['year'] - 1, start_year + 1)
        if yr == start_year :
            return
        change_display_year("", "", yr)
        year_slider.value = current_values['year']

    def change_region(event):
       
        current_values['region'] = event.item

        update_display(sites, display, timeseries, current_values)

        description.text = "<h2>Notes for area:</h2><p>"+ \
            sites[current_values['region']]['description'] + "</p>"

    def toggle_threshold (event):

        current_values['threshold']['toggle'] = not current_values['threshold']['toggle']
        update_display(sites, display, timeseries, current_values)

        if current_values['threshold']['toggle']: 
            predisp_toggle_button.label="climate priming threshold on"
        else:
            predisp_toggle_button.label='climate priming threshold off'

    def change_threshold_value(attrname, old, new):

        current_values['threshold']['value'] = new
        if current_values['threshold']['toggle']:
            update_display(sites, display, timeseries, current_values)

        

    def toggle_predisp(event): 

        current_values['predisp']['toggle'] = not current_values['predisp']['toggle']
        update_display(sites, display, timeseries, current_values)

        if current_values['predisp']['toggle']: 
            predisp_toggle_button.label="predisposition model overlay on"
        else:
            predisp_toggle_button.label="predisposition model overlay off"
            
            

    def toggle_met(event): 

        current_values['met']['toggle'] = not current_values['met']['toggle']
        update_display(sites, display, timeseries, current_values)
        
        if current_values['met']['toggle']: 
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
