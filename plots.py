from __future__ import generators
from typing import List
from math import pi
import pandas as pd
from bokeh.transform import cumsum
from bokeh.transform import factor_cmap
from bokeh.models import ColumnDataSource
import numpy as np
from bokeh.plotting import figure
from enum import Enum, auto

time_line = []
emotion_axis = []
num_of_times = [0, 0, 0]
canvas = np.zeros([480, 640, 3], dtype=np.uint8)


class PlotType(Enum):
    PIE = auto()
    HISTOGRAM = auto()
    LINE = auto()


class Plots:
    def plot(self):
        pass


class Pie(Plots):

    # x = { #Todo: shold be inizalized
    #     'Other': num_of_times[0],
    #     'Sadness': num_of_times[1],
    #     'Happy': num_of_times[2]
    # }
    def __init__(self, x=None):
        self._x = x

    def plot(self):
        data = pd.Series(self._x).reset_index(name='value').rename(columns={'index': 'Emotion'})
        data['angle'] = data['value'] / data['value'].sum() * 2 * pi
        data['color'] = ['#1f77b4', '#aec7e8', '#ff7f0e']

        p = figure(plot_height=350, title="Pie Chart", toolbar_location=None,
                   tools="hover", tooltips="@Emotion: @value", x_range=(-0.5, 1.0))

        p.wedge(x=0, y=1, radius=0.4,
                start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                line_color="white", fill_color='color', legend='Emotion', source=data)

        p.axis.axis_label = None
        p.axis.visible = False
        p.grid.grid_line_color = None

        return p


class Histogram(Plots):
    #Todo: should be initizaled: emotion = ['Other', 'Sadness', 'Happy']
    def __init__(self, emotion=None):
        self._emotion = emotion

    def plot(self):
        counts = [num_of_times[0], num_of_times[1], num_of_times[2]] #Todo: Counts shouold be added as well, maybe to plot or maybe init
        source = ColumnDataSource(data=dict(emotion=self._emotion, counts=counts))
        p = figure(x_range=self._emotion, plot_height=350,
                   toolbar_location=None, title="Emotion's")
        p.vbar(x='emotion', top='counts', width=0.9, source=source,
               legend="emotion",
               line_color='white', fill_color=factor_cmap('emotion',
                                                          palette=["#3288bd",
                                                                   "#99d594", "#e6f598",
                                                                              "#fee08b",
                                                                   "#fc8d59", "#d53e4f"]
                                                          , factors=self._emotion))
        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        p.y_range.end = max(num_of_times)
        p.legend.orientation = "horizontal"
        p.legend.location = "top_left"
        return p


class LinePlot(Plots):
    #Todo: should be initalized: name = "0-Other\n 1-Sadness \n 2-Happy"
    def __init__(self, name=None):
        self._name = name

    def plot(self):
        color = ["red"]
        f = figure(title="Emotions Vs Time")
        f.xaxis.axis_label = 'Time'
        f.yaxis.axis_label = 'Emotion'
        f.line(time_line, emotion_axis, alpha=0.8, color="blue", legend=self._name)
        f.legend.location = "top_left"
        return f


class PlotFactory:

        @staticmethod
        def create(type):
            if type in PlotFactory.choice:
                return PlotFactory.choice[type]()

            assert 0, "Bad plot creation: " + type

        choice = {PlotType.PIE: Pie,
                  PlotType.HISTOGRAM: Histogram,
                  PlotType.Line: LinePlot
                  }

def plot_name_gen():

    types: List[PlotFactory] = list(PlotFactory)

    for i in range(len(types)):
        yield types[i]


    # shapes = \
    #     [ShapeFactory.create(i) for i in shapeNameGen(7)]