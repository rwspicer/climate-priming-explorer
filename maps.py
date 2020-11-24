
from bokeh.plotting import figure

import constants,colors

from bokeh.models import LinearColorMapper, ColorBar



def create_cp_map(data):
    TOOLTIPS = [
        ("(x,y)", "($x, $y)"),
        # ("(x map, y map)", "(@x_geo{0,0.000}, @y_geo{0,0.000})"),
        # ("(lat, long)", "(@lat{0,0.000}, @long{0,0.000})"),
        ("value", "@cp{0,0.000}")
    ]
    img_shape = data.data['cp'][0].shape
    p = figure(
        tooltips= TOOLTIPS,
        plot_height = img_shape[0] * constants.WIDTH*2//img_shape[1],
        plot_width = constants.WIDTH *2 ,
        tools=[],
        title="Utqiaġvik and Point Barrow"
        )

    p.toolbar.logo = None
    p.toolbar_location = None
    p.x_range.range_padding = p.y_range.range_padding = 0
    # p.sizing_mode = 'scale_height'
    # must give a vector of image data for image parameter

    cmapper = LinearColorMapper(
        colors.blue_red , 
        low=constants.CP_MIN, high=constants.CP_MAX, 
        nan_color='white'
    )

    p.image(
        image='cp', x=0, y=0, dw=10, dh=10, 
        color_mapper=cmapper,
        # level="image",
        source=data,
    )
    # p.grid.grid_line_width = 0.5
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.axis.visible = False

    return p



def create_met_map(data, met_name, offset, color, c_min, c_max):
    TOOLTIPS = [
        ("(x,y)", "($x, $y)"),
        # ("(x map, y map)", "(@x_geo{0,0.000}, @y_geo{0,0.000})"),
        # ("(lat, long)", "(@lat{0,0.000}, @long{0,0.000})"),
        ("value", "@"+met_name+"{0,0.000}")
    ]
    met_map = figure(
        tooltips= TOOLTIPS,
        plot_height = 200,
        plot_width = 200 ,
        tools=[],
        title=""
        )
    
    cmapper = LinearColorMapper(
        color, 
        low=c_min, high=c_max, 
        nan_color='white'
    )

    met_map.image(
        image=met_name, x=0, y=0, dw=10, dh=10, 
        color_mapper=cmapper,
        # level="image",
        source=data,
    )
    # p.grid.grid_line_width = 0.5
    met_map.xgrid.grid_line_color = None
    met_map.ygrid.grid_line_color = None
    met_map.axis.visible = False

    met_map.toolbar.logo = None
    met_map.toolbar_location = None
    met_map.x_range.range_padding = met_map.y_range.range_padding = 0

    color_bar = ColorBar(color_mapper=cmapper, border_line_color=None, location=(0,0), width=10)

    met_map.add_layout(color_bar, 'right')

    return met_map
