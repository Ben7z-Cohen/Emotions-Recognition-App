from abc import abstractmethod
from math import pi
import pandas as pd
from bokeh.transform import cumsum
from bokeh.transform import factor_cmap
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show
from enum import Enum


class PlotType(Enum):
    Pie = "Pie",
    Line = "Line",
    Histogram = "Histogram"


class Plot:

    def __init__(self, app_engine):
        self.app_engine = app_engine

    @abstractmethod
    def plot(self):
        pass

    def emotions_dict(self):
        emotions_dict = {}
        for i in range(len(self.app_engine.emotions)):
            emotions_dict[self.app_engine.emotions[i]] = self.app_engine.num_of_appearance[i]
        return emotions_dict

    def create_names_string(self):
        names_string = ''
        for index, name in enumerate(self.app_engine.emotions):
            names_string += str(index) + '-' + name + '\n'
        return names_string

    @property
    def num_of_appearance(self):
        return self.app_engine.num_of_appearance

    @property
    def time_line(self):
        return self.app_engine.time_line

    @property
    def emotion_axis(self):
        return self.app_engine.emotion_axis

    @property
    def emotions(self):
        return self.app_engine.emotions

    def factory(self, plot_type):
        if plot_type == PlotType.Pie.value[0]:
            return Pie(self.app_engine)
        if plot_type == PlotType.Line.value[0]:
            return Line(self.app_engine)
        if plot_type == PlotType.Histogram.value:
            return Histogram(self.app_engine)

        assert 0, "Bad plot creation: " + plot_type


class Pie(Plot):

    def __init__(self, app_engine):
        super().__init__(app_engine)

    @property
    def name(self):
        return PlotType.Pie.value[0]

    def plot(self):
        data = pd.Series(self.emotions_dict()).reset_index(name='value') \
            .rename(columns={'index': 'Emotion'})
        data['angle'] = data['value'] / data['value'].sum() * 2 * pi
        data['color'] = ['#1f77b4', '#aec7e8', '#ff7f0e']
        f = figure(plot_height=350, title="Pie Chart", toolbar_location=None,
                   tools="hover", tooltips="@Emotion: @value", x_range=(-0.5, 1.0))
        f.wedge(x=0, y=1, radius=0.4,
                start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                line_color="white", fill_color='color', legend='Emotion', source=data)
        f.axis.axis_label = None
        f.axis.visible = False
        f.grid.grid_line_color = None
        show(f)


class Histogram(Plot):

    def __init__(self, app_engine):
        super().__init__(app_engine)

    @property
    def name(self):
        return PlotType.Histogram.value

    def plot(self):
        counts = [x for x in self.num_of_appearance]
        source = ColumnDataSource(data=dict(emotion=self.emotions, counts=counts))
        f = figure(x_range=self.emotions, plot_height=350, toolbar_location=None,
                   title="Emotions")
        f.vbar(x='emotion', top='counts', width=0.9, source=source, legend="emotion",
               line_color='white', fill_color=factor_cmap('emotion',
                                                          palette=["#3288bd", "#99d594",
                                                                   "#e6f598", "#fee08b",
                                                                   "#fc8d59", "#d53e4f"]
                                                          , factors=self.emotions))
        f.xgrid.grid_line_color = None
        f.y_range.end = max(self.num_of_appearance)
        f.legend.orientation = "horizontal"
        f.legend.location = "top_left"
        show(f)


class Line(Plot):

    def __init__(self, app_engine):
        super().__init__(app_engine)

    @property
    def name(self):
        return PlotType.Line.value[0]

    def plot(self):
        name = self.create_names_string()
        f = figure(title="Emotions Vs Time")
        f.xaxis.axis_label = 'Time'
        f.yaxis.axis_label = 'Emotion'
        f.line(self.time_line, self.emotion_axis, alpha=0.8, color="blue", legend=name)
        f.legend.location = "top_left"
        show(f)
