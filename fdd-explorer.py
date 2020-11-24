from multigrids import MultiGrid, tools
import os
import numpy as np
import matplotlib.pyplot as plt

from bokeh.io import curdoc
from bokeh.layouts import column, row, layout
from bokeh.plotting import figure, output_file, show
from bokeh import palettes
from bokeh.transform import linear_cmap

from bokeh.models import TextInput, ColumnDataSource, FileInput, Div, Dropdown, Slider,ColorBar, LinearColorMapper


## TEST DATA setup
path = "/Volumes/scarif/data/V2/datasets/derived/fdd_ACP_CRU_v3/tiff/"
load_params = {
    "method": "tiff",
    "directory": path
}
create_params = {
    'start_timestep':1901,
    'raster_metadata': tools.get_raster_metadata(os.path.join(path, "freezing_degree-day_1901.tif"))
}

test_data = tools.load_and_create(load_params, create_params)

UTQ = test_data.zoom_to((70.9, -156), location_format="WGS84")
PRU = test_data.zoom_to((70, -151), location_format="WGS84")

print (UTQ.config['grid_shape'])
print (PRU.config['grid_shape'])


## TEST DATA setup

WIDTH = 200

palette_opts = {
    "viridis": palettes.Viridis[256],
    "magma": palettes.Magma[256]
}

def create_data(multigrid, year):

    # # print('a')
    # to_x_geo = lambda x, y, gt: gt[0] + (x + .5)*gt[1] + (y + .5)*gt[2]
    # to_y_geo = lambda x, y, gt: gt[3] + (x + .5)*gt[4] + (y + .5)*gt[5]
    # md =  multigrid.config['raster metadata']
    init = multigrid[year]

    # in_crs = CRS.from_wkt(md.projection)
    # gps = CRS.from_epsg(4326)
    # transformer = Transformer.from_crs(in_crs, gps)
    # # print('b')
    # x = np.zeros(init.shape)
    # y = np.zeros(init.shape)
    # x[:] = range(init.shape[1])
    # y.T[:] = range(init.shape[0])

    # # print('c')

    # x_geo = to_x_geo(x,y,md.transform)
    # y_geo = to_y_geo(x,y,md.transform)
    # print('d')
    data = dict(
        image=[init[::-1]], 
        # x_geo = [x_geo[::-1]],
        # y_geo = [y_geo[::-1]],
        # lat = [transformer.transform(x_geo,y_geo)[0] [::-1]],
        # long = [transformer.transform(x_geo,y_geo)[1] [::-1]],
        # raster_metadata = [md]
    )
    # print('e')
    return data

def create_figure(data):
    TOOLTIPS = [
        ("(x,y)", "($x, $y)"),
        # ("(x map, y map)", "(@x_geo{0,0.000}, @y_geo{0,0.000})"),
        # ("(lat, long)", "(@lat{0,0.000}, @long{0,0.000})"),
        ("value", "@image{0,0.000}")
    ]
    img_shape = data.data['image'][0].shape
    p = figure(
        tooltips= TOOLTIPS,
        plot_height = img_shape[0] * WIDTH*2//img_shape[1],
        plot_width = WIDTH *2 ,
        tools=[],
        title="Utqiaġvik and Point Barrow"
        )

    p.toolbar.logo = None
    p.toolbar_location = None
    p.x_range.range_padding = p.y_range.range_padding = 0
    # p.sizing_mode = 'scale_height'
    # must give a vector of image data for image parameter

    cmapper = LinearColorMapper(palettes.Viridis[256], low=-6000, high=-3500, nan_color='white')

    p.image(
        image='image', x=0, y=0, dw=10, dh=10, 
        color_mapper=cmapper,
        # palette=palettes.linear_palette(palette_opts[data.data['current_palette'][0]],data.data['current_colors'][0] ), 
        level="image",
        source=data,
    )
    # p.grid.grid_line_width = 0.5
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.axis.visible = False

    return p


def create_area_average_data(multigrid):

    average = []
    for yr in range(multigrid.config['num_timesteps']):
        # print(multigrid.grids[yr])
        average.append(np.nanmean(multigrid.grids[yr]))
    return average


def app():

    start_year = UTQ.config['start_timestep']
    end_year = start_year + UTQ.config['num_timesteps']
    years = range(start_year,end_year)
    
    current_palette = 'viridis'
    current_colors = 256
    display_year = start_year
    # print(display_year)

    display_region = ColumnDataSource()
    display_region.data = create_data(UTQ, display_year )
    display_region.data['current_palette'] = [current_palette]
    display_region.data['current_colors'] = [current_colors]
    display_region.data['current_year'] = [display_year ]
    cp_map = create_figure(display_region)

    average = create_area_average_data(UTQ)
    # print(average)


    average_plot = figure(
        plot_width=WIDTH*4, plot_height=WIDTH, 
        x_range=(1900, 2016), y_range=(-6000, -3500), tools=[],
        title="Yearly Average for Area"
    )

    ## 1901-1950 average_line
    average_plot.ray(x=[start_year-1], y=[np.nanmean(average[:1950-start_year])], length=0, angle=0, line_width=3, alpha=0.5, color="blue",legend_label="1901-1950 regional average")
    # average_plot.ray(x=[start_year], y=[np.nanmean(average[:1950-start_year])], length=0, angle=np.pi, line_width=3,alpha=0.5, color="blue", legend_label="1901-1950 regional average")


    timeseries = ColumnDataSource()
    color_mapper = linear_cmap(field_name='average',palette=palettes.Viridis[256], low=-6000, high=-3500)
    timeseries.data = {"years": years, "average": average}
    average_plot.circle('years', 'average', size=10, color=color_mapper , alpha=0.75, source = timeseries)
    

    display_average = average[display_year-start_year]

    display_region.data['current_average'] = [display_average ]
    average_plot.circle(x='current_year', y='current_average', size=20, color="red", alpha=.5, source=display_region )

    average_plot.legend.location = "top_left"
    average_plot.legend.click_policy="hide"

    hidden_plot = figure(
        plot_width=100, plot_height=WIDTH*2, 
        tools=[],
        title = "Degree-days",title_location="right",
        toolbar_location=None, min_border=0, 
        outline_line_color=None
    )
    hidden_plot.toolbar.logo = None
    hidden_plot.toolbar_location = None
    hidden_plot.title.align="center"
    hidden_plot.title.text_font_size = '12pt'

    color_bar = ColorBar(color_mapper=color_mapper['transform'], width=8,  location=(0,0))
    hidden_plot.add_layout(color_bar, 'right')
    


    year_slider = Slider(
        start=start_year, end=end_year, value=display_year, step=1, title="Year"
    )
    def change_display_year(attrname, old, new):
       
        display_region.data['image']  = [UTQ[int(new)][::-1]]
        display_average = average[new-start_year]
        display_region.data['current_average'] = [display_average ]
        display_region.data['current_year'] = [new]

       
    year_slider.on_change('value_throttled', change_display_year)

    inputs = column(year_slider)

    title = Div(text="<H1>FREEZING DEGREE-DAY EXPLORER<H1>", width=1000)
    
    curdoc().add_root(
        layout([
            [title],
            [inputs, cp_map, hidden_plot],
            [average_plot]
        ]) 
        
    )
    curdoc().title = "Freezing Degree-day Priming Explorer"

    

    

# if __name__=="__main__":
app() 
