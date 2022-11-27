from serial.tools.list_ports import comports
import pyqtgraph as pg
import pandas as pd
import threading
import serial

df = pd.DataFrame()
running = True
win = pg.GraphicsLayoutWidget(show=True, title="V5 Data")

win.nextRow()
plot_all = win.addPlot()
plot_all.setDownsampling(mode='peak')
plot_all.setClipToView(True)
curve_all = plot_all.plot()

win.nextRow()
plot_recent = win.addPlot()
plot_recent.setLabel('bottom', 'Time', 's')

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


# main

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


# stop data collection
running = False
collect_thread.join()