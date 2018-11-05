import sys
import os
import time

import numpy as np
np.random.seed(1)
#import pandas as pd
import datetime

from bokeh.layouts import row, column, gridplot
from bokeh.models import ColumnDataSource, Slider, Select, DatetimeTickFormatter
from bokeh.models import Range1d, LinearAxis
from bokeh.plotting import curdoc, figure
from bokeh.driving import count

from sht31 import SHT31
import smbus2 as smbus
import RPi.GPIO as GPIO                                                                                                                 


source = ColumnDataSource(dict(
    idx=[], time=[], T=[], RH=[]
))

p = figure(tools="xpan,xwheel_zoom,xbox_zoom,reset")#, x_axis_type='datetime', y_axis_location="right")
#p.width = 200 # height and width is set below when it is added to the layout with add_root
p.x_range.follow = "end"
p.x_range.follow_interval = 5*60*1000 # ms
p.x_range.range_padding = 0
p.xaxis.formatter=DatetimeTickFormatter(
        microseconds = ['%F %T.%3N'],
        milliseconds = ['%F %T.%3N'],
        seconds = ['%F %T'],
        minsec = ['%F %T'],
        minutes = ['%F %T'],
        hourmin = ['%F %T'],
        hours = ['%F %T'],
        days = ['%F %T'],
        months = ['%F %T'],
        years = ['%F %T'],
        )
p.xaxis.major_label_orientation = 0.7 #1.571 #math.pi/2

p.xaxis.axis_label = "T"
p.extra_y_ranges = {'RH': Range1d(bounds=(0,100), start=0, end=100)}
p.add_layout(LinearAxis(y_range_name='foo', axis_label='RH'), 'right')

p.line(x='time', y='T', alpha=0.5, line_width=1, color='red', source=source)
p.line(x='time', y='RH', alpha=0.5, line_width=1, color='blue', source=source, y_range_name='foo')

def _read_sensor():
    timeval = datetime.datetime.now() #pd.to_datetime('now')
#int(time.time()*1000000)
    #T = np.random.normal(0, 1)
    #RH = np.random.normal(0, 1)
    try:
        T, RH = sht.read(rep='high')
    except ConnectionError as e:
        print("FAILED:", e)
    except OSError as e:
        if e.errno == 121: # 121 is Remote I/O Error
            print("FAILED:", e)
    return timeval,T, RH

@count()
def update(cnt):
    timeval,T,RH = _read_sensor()

    new_data = dict(
        idx=[cnt],
        time=[timeval],
        T=[T],
        RH=[RH],
    )
    source.stream(new_data, 300)


def main():
    # Setup
    # GPIO boilerplate
    GPIO.setmode(GPIO.BCM) # GPIO.BCM is numbers like 17 for GPIO17
    GPIO.setwarnings(True)

    global sht
    sht = SHT31(smbus.SMBus(1), addr_gpio=4)

    # Layout
    curdoc().add_root(column(gridplot([[p]], toolbar_location="left", plot_width=300, plot_height=300)))
    curdoc().title = "PIHVAC"

    # add the main update callback (effectively an event loop)
    curdoc().add_periodic_callback(update, 500)


def on_server_unloaded(server_context):
    ''' If present, this function is called when the server shuts down. '''
    GPIO.cleanup()



# Run main
main()
