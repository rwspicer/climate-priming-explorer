import numpy as np



from bokeh.plotting import figure
from bokeh.transform import linear_cmap


import constants, colors



def create_average_plot(current_display, timeseries, start_year):

    

    average_plot = figure(
        plot_width= constants.WIDTH*4, plot_height= constants.WIDTH+100, 
        x_range=(1900, 2016), y_range=( constants.CP_MIN,  constants.CP_MAX), 
        tools=[],
        title="Yearly Average for Area"
    )


    average = timeseries.data['average']
    ## 1901-1950 average_line
    average_plot.ray(
        x=[start_year-1], y=[np.nanmean(average[:1950-start_year])], 
        length=0, angle=0, line_width=3, alpha=0.5, color="blue",
        legend_label="1901-1950 regional average"
    )


    color_mapper = linear_cmap(
        field_name='average',palette=colors.blue_red, 
        low=constants.CP_MIN, high=constants.CP_MAX
    )
    average_plot.circle(
        'years', 'average', size=10, color=color_mapper,
        alpha=1, source = timeseries
    )
    
    average_plot.circle(
        x='current_year', y='current_average', size=20, color="green", 
        alpha=.5, source=current_display,
        legend_label="Current Year"
    )

    average_plot.legend.location = "bottom_left"
    average_plot.legend.click_policy="hide"

    return average_plot
