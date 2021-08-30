import time
import numpy as np
import pyqtgraph as pg

class PlotWidget(pg.PlotWidget):
    def __init__(self):
        super(PlotWidget, self).__init__(name='velocity plot')
        self.plotPenWidth = 3.0
        self.velocityPlotList = np.zeros(1000)
        self.setMinimumSize(self.minimumWidth(), 300)
        self.setEnabled(False)
        self.velocityCurve = self.plot()
        self.velocityCurve.setPen(color='y', width=self.plotPenWidth)
        self.setYRange(-20, 20)
        self.setLabel('left', 'velocity', '-')
        self.showAxis('bottom', False)
        self.showGrid(x=True, y=True)
        self.plotText = pg.TextItem(text='test', color='w', anchor=(1, 1.5))
        self.addItem(self.plotText)
    
    def update_plot(self, data, recording):
        self.velocityPlotList[:-1] = self.velocityPlotList[1:]
        self.velocityPlotList[-1] = data.velocity
        self.velocityCurve.setData(self.velocityPlotList)
        self.velocityCurve.setPos(-1000, 0)
        treadmillTime = time.strftime("%M:%S", time.gmtime(int(data.time) / 1000))
        tmpPlotText = str("time: " + treadmillTime + "\n" +
                          "velocity: " + str(data.velocity) + "\n" +
                          "abs. position: " + str(data.absPosition) + "\n" +
                          "lap: " + str(data.lap) + "\n" +
                          "rel. position: " + str(data.relPosition) + "\n")
        if recording:
            tmpPlotText = str(tmpPlotText + "🔴 REC")
        self.plotText.setText(text=tmpPlotText)
    
    def update_color(self, treadmill):
        if treadmill.initialized:
            if treadmill.recording:
                self.velocityCurve.setPen(color='r', width=self.plotPenWidth)
            else:
                self.velocityCurve.setPen(color='w', width=self.plotPenWidth)
        else:
            self.velocityCurve.setPen(color='y', width=self.plotPenWidth)
    
    def enable(self):
        self.setEnabled = True
        self.velocityCurve.setData(self.velocityPlotList)
    
    def disable(self):
        self.setEnabled = False

