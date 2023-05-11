import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg


class MPLPlotManager:

    def __init__(self, ax_refs, canvs) -> None:

        self.canvs = canvs
        self.plots = {'average_time': {'ax': ax_refs['average_time'], 'lines': {"chA": None, "chB": None}},
                      'last_time': {'ax': ax_refs['last_time'], 'lines': {"chA": None, "chB": None}}}

        self.init_plots()

    def init_plots(self) -> None:

        # Initialise average_time plot axes
        self.plots['average_time']['ax'].set_title('Signal from SDR14')
        self.plots['average_time']['ax'].set_xlabel('Sample number')
        self.plots['average_time']['ax'].set_ylabel('Signal')

        # Initialise frq plot axes
        self.plots['last_time']['ax'].set_title('Spectrum')
        self.plots['last_time']['ax'].set_xlabel('Frequency (Hz)')
        self.plots['last_time']['ax'].set_ylabel('Intensity (arb.)')

        # Initialise line refs
        for k in self.plots.keys():
            self.plots[k]['lines']['chA'] = self.plots[k]['ax'].plot([], [], c="r", label="Ch A")
            self.plots[k]['lines']['chB'] = self.plots[k]['ax'].plot([], [], c="b", label="Ch B")

    def update_plots(self, y_data: np.ndarray, line: str) -> None:

        x_data = np.arange(0, y_data.size)

        self.plots['average_time']['lines'][line][0].set_xdata(x_data)
        self.plots['average_time']['lines'][line][0].set_ydata(y_data)

        self.plots['average_time']['ax'].set_xlim(0, x_data.size)
        self.plots['average_time']['ax'].set_ylim(0, 1)
        self.canvs['average_time'].draw()


# noinspection PyTypeChecker
class PyqtgraphPlotManager:

    def __init__(self, plot_widgets: dict) -> None:

        self.plots = {k: {'plot_ref': plot_widgets[k],
                          'lines': self.initialise_lines(k, plot_widgets)} for k in plot_widgets.keys()}

        # x-axis
        self.fs = 800e6
        self.Ts = 1/self.fs
        self.N = 2 ** 16
        self.xt = np.arange(0, self.N) * self.Ts

        self.initialise_plot_widgets()

    def initialise_plot_widgets(self) -> None:

        styles = {'color': "#000000", 'font-size': "14px"}

        for k in self.plots.keys():
            self.plots[k]['plot_ref'].setBackground("w")
            self.plots[k]['plot_ref'].setLabel("left", "signal", **styles)
            self.plots[k]['plot_ref'].setLabel("bottom", "t (us)", **styles)

        self.plots['average_time']['plot_ref'].setTitle("Averaged SDR14 signal", color='k')
        self.plots['last_time']['plot_ref'].setTitle("Last scan SDR14 signal", color='k')

    def initialise_lines(self, key: str, plot_widgets: dict) -> dict[pg.PlotItem]:

        return {'ch1': plot_widgets[key].plot([], [], pen='r'),
                'ch2': plot_widgets[key].plot([], [], pen='b')}

    def update_plot(self, data: np.ndarray, plot: str, channel: str) -> None:
        self.plots[plot]['lines'][channel].setData(self.xt, data)

