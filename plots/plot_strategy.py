from plots.plot import Plot


class PlotStrategy:

    def __init__(self, plots: Plot) -> None:
        self._plot = plots

    @property
    def strategy(self) -> Plot:
        return self._plot

    @strategy.setter
    def strategy(self, plots: Plot):
        self._plot = plots

    def plot(self) -> None:
        self._plot.plot()
