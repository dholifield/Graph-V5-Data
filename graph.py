from serial.tools.list_ports import comports
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
import pandas as pd
import threading
import serial

# change to True to enable scrolling graph
scrolling = True

df = pd.DataFrame()
running = True

class KeyPressWindow(pg.GraphicsLayoutWidget):
    sigKeyPress = QtCore.pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, ev):
        self.scene().keyPressEvent(ev)
        self.sigKeyPress.emit(ev)

def keyPressed(evt):
    global scrolling

    if evt.text() == "r":
        df.drop(df.index, inplace=True) 
    if evt.text() == "s":
        scrolling = not scrolling

win = KeyPressWindow(show=True)
win.sigKeyPress.connect(keyPressed)

win.nextRow()
p_all = win.addPlot()
p_all.addLegend()
p_all.disableAutoRange(axis=pg.ViewBox.XAxis)
chunk_size = 10000
p_all.setXRange(0, chunk_size)


def find_port():
    for port in comports():
        if "V5 User Port" in port.description:
            V5port = port.device
            print("\n" + "V5 found (" + V5port + ")")
            return V5port
    
    print("V5 not found")
    return 0
# end find_port

def collect_data(ser):
    global df
    while running:
            line = ser.readline().decode('ascii')
            # if data needs to be graphed
            if "graph_data" in line:
                line = ser.readline().decode('ascii')[6:].strip('\n')
                columns = line.split('|')[0].split(',')
                data = map(float, line.split('|')[1].split(','))
                data = pd.DataFrame([data], columns=columns)

                # concat data to dataframe
                df = pd.concat([df, data], ignore_index=True)

                # print data
                #print("\n" + data.to_string(index=False))
# end collect_data

curves = []
start = 0
end = chunk_size
def update_graph():
    global df, curves, start, end
    if (df.shape[1] - 1 > len(curves)):
        p_all.setLabel('bottom', df.columns[0])
        for i in range(len(curves), df.shape[1] - 1):
            curve = p_all.plot(x=df.iloc[:,0], y=df.iloc[:,i + 1], name=df.columns[i + 1], pen=(i,df.shape[1]))
            curves.append(curve)
    else:
        for i in range(len(curves)):
            curves[i].setData(x=df.iloc[:,0], y=df.iloc[:,i + 1])
    
    if (df.shape[0] > 0 and df.iloc[-1,0] > end):
        if not scrolling:
            end = end * 2
            p_all.setXRange(0, end)
        else:
            end = df.iloc[-1,0]
            p_all.setXRange(end - chunk_size, end)
# end update_graph

# timer for updating graph
timer = pg.QtCore.QTimer()
timer.timeout.connect(update_graph)
timer.start(50)

# main
if __name__ == '__main__':
    # find V5 port
    port = find_port()
    if port == 0:
        exit()

    # open serial port
    ser = serial.Serial(port, 115200, timeout=0.1)
    print("Starting data collection...\n")
    # start data collection thread
    collect_thread = threading.Thread(target=collect_data, args=(ser,))
    collect_thread.start()

    # graph data
    pg.exec()

    # stop data collection
    running = False
    collect_thread.join()