import time
import numpy as np
import pyqtgraph as pg

class PlotWidget(pg.PlotWidget):
    def __init__(self):
        super().__init__(name='velocity plot')
        self.plot_pen_width = 3.0
        self.velocity_plot_list = np.zeros(1000)
        self.setMinimumSize(self.minimumWidth(), 300)
        self.setEnabled(False)
        self.velocity_curve = self.plot()
        self.velocity_curve.setPen(color='y', width=self.plot_pen_width)
        self.setYRange(-20, 20)
        self.setLabel('left', 'velocity', '-')
        self.showAxis('bottom', False)
        self.showGrid(x=True, y=True)
        self.plot_text = pg.TextItem(text='test', color='w', anchor=(1, 1.5))
        self.addItem(self.plot_text)

    def update_plot(self, data, recording):
        self.velocity_plot_list[:-1] = self.velocity_plot_list[1:]
        self.velocity_plot_list[-1] = data.velocity
        self.velocity_curve.setData(self.velocity_plot_list)
        self.velocity_curve.setPos(-1000, 0)
        treadmill_time = time.strftime("%M:%S", time.gmtime(int(data.time) / 1000))
        tmp_plot_text = str("time: " + treadmill_time + "\n" +
                          "velocity: " + str(data.velocity) + "\n" +
                          "abs. position: " + str(data.abs_position) + "\n" +
                          "lap: " + str(data.lap) + "\n" +
                          "rel. position: " + str(data.rel_position) + "\n")
        if recording:
            tmp_plot_text = str(tmp_plot_text + "🔴 REC")
        self.plot_text.setText(text=tmp_plot_text)

    def update_color(self, treadmill):
        if treadmill.initialized:
            if treadmill.recording:
                self.velocity_curve.setPen(color='r', width=self.plot_pen_width)
            else:
                self.velocity_curve.setPen(color='w', width=self.plot_pen_width)
        else:
            self.velocity_curve.setPen(color='y', width=self.plot_pen_width)

    def enable(self):
        self.setEnabled(True)
        self.velocity_curve.setData(self.velocity_plot_list)

    def disable(self):
        self.setEnabled(False)
