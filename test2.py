import pyqtgraph as pg

win = pg.GraphicsLayoutWidget(show=True, title="V5 Data")

win.nextRow()
p1 = win.addPlot()
p1.setDownsampling(mode='peak')
p1.setClipToView(True)
curve_all = p1.plot()
