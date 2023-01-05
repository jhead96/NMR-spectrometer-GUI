import matplotlib.pyplot as plt
import numpy as np

class MPLPlotManager():

    def __init__(self, ax_refs, canvs) -> None:

        self.canvs = canvs
        self.plots = {'time': {'ax': ax_refs['time'], 'lines': {"chA": None, "chB": None}},
                      'fft': {'ax': ax_refs['fft'], 'lines': {"chA": None, "chB": None}}}

        self.init_plots()


    def init_plots(self) -> None:

        # Initialise time plot axes
        self.plots['time']['ax'].set_title('Signal from SDR14')
        self.plots['time']['ax'].set_xlabel('Sample number')
        self.plots['time']['ax'].set_ylabel('Signal')

        # Initialise frq plot axes
        self.plots['fft']['ax'].set_title('Spectrum')
        self.plots['fft']['ax'].set_xlabel('Frequency (Hz)')
        self.plots['fft']['ax'].set_ylabel('Intensity (arb.)')

        # Initialise line refs
        for k in self.plots.keys():
            self.plots[k]['lines']['chA'] = self.plots[k]['ax'].plot([], [], c="r", label="Ch A")
            self.plots[k]['lines']['chB'] = self.plots[k]['ax'].plot([], [], c="b", label="Ch B")


    def update_plots(self, y_data: np.ndarray, line: str) -> None:

        x_data = np.arange(0, y_data.size)

        self.plots['time']['lines'][line][0].set_xdata(x_data)
        self.plots['time']['lines'][line][0].set_ydata(y_data)

        self.plots['time']['ax'].set_xlim(0, x_data.size)
        self.plots['time']['ax'].set_ylim(0, 1)
        self.canvs['time'].draw()


