# Imports
import serial
import re
from serial.tools.list_ports import comports
import numpy as np
import time
import tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt, animation
import time

# ===================================================================
# Helper functions
def serial_connection():
    for port, _, hwid in comports():
        if re.match("USB VID:PID=2341:0043", hwid):
            serial_object = serial.Serial(port, baudrate = 115200)
            if serial_object.is_open:
                return serial_object
    raise ConnectionError("No valid connection to the manometer found!")

def modified_relu(val):
    if val > 1750:
        return 1700
    elif val > 50:
        return val
    else:
        return 50

def plot_data(i, t_array, p_array, s_array, serial_object, axis):
    
    while True:
        try:
            data = serial_object.read_all().decode()
            complete_line = data.split("\n")[-2]
            line = complete_line.split(";")
            if len(line) == 4:
                rel_time, mode, speed, pressure = [x.strip() for x in line]
                break
        except IndexError:
            time.sleep(0.01)
            continue
        
    if SAVING:
        with open(f"./{DATA_NAME}.csv", "a") as fo:
            fo.write(f"{rel_time}, {mode}, {speed}, {pressure}\n")
            fo.close()
    
    t_array.append((time.time() - START))
    p_array.append(modified_relu(float(pressure)))
    
    if mode == "U" or mode == "F":
        s_array.append(0)
    elif mode == "T":
        s_array.append(int(speed))
    
    t_array = t_array[-100:]
    p_array = p_array[-100:]
    s_array = s_array[-100:]
    
    axis.clear()
    axis.set_ylim(0, 1750)
    axis.plot(t_array, p_array, label="Pressure")
    axis.plot(t_array, s_array, label="Pump activity")
    axis.legend(loc='lower left')
    
def main():
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True

    t_array, p_array, s_array = list(), list(), list()
    serial_object = serial_connection()

    root = tkinter.Tk()
    root.wm_title("Realtime manometer measurements")

    fig = plt.Figure(dpi=100)
    ax = fig.add_subplot(1, 1, 1)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()

    button = tkinter.Button(master=root, text="Quit", command=root.quit)
    button.pack(side=tkinter.BOTTOM)
        
    def save_data():
        global DATA_NAME
        DATA_NAME = tkinter.simpledialog.askstring("Document name", "Please provide a name for the .csv file.")
        if not DATA_NAME:
            DATA_NAME = "recording"
        fo = open(f"./{DATA_NAME}.csv", "w")
        fo.write(f"timestamp, pump_mode, pump_speed, pressure\n")
        fo.close()
        global SAVING; SAVING = True
        
    def stop_data():
        global SAVING; SAVING = False
    
    button2 = tkinter.Button(master = root, text = "Record", command=save_data)
    button2.pack(side = tkinter.BOTTOM)
    
    button3 = tkinter.Button(master = root, text= "Stop", command=stop_data)
    button3.pack(side = tkinter.BOTTOM)

    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
    ani = animation.FuncAnimation(fig, plot_data, fargs=(t_array, p_array, s_array, serial_object, ax), interval = INTERVAL, cache_frame_data=False)

    tkinter.mainloop()
    
# ===================================================================
# File execution
if __name__ == "__main__":
    SAVING = False
    INTERVAL = 50
    START = time.time()

    main()
