# Imports
import serial
import re
from serial.tools.list_ports import comports
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
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
    # Read the data from the serial object
    while True:
        try:
            serial_object.read_all()
            buffer = ";"
            while buffer[-1] != "\n":
                buffer += serial_object.read().decode()
            rel_time, mode, speed, pressure = [x.strip() for x in buffer.split(";")[1:]]
            break
        except:
            continue
    
    if saving:
        with open("./recording.csv", "a") as fo:
            fo.write(f"{rel_time}, {mode}, {speed}, {pressure}\n")
            fo.close()
    
    t_array.append((time.time() - START))
    p_array.append(modified_relu(float(pressure)))
    
    if mode == "U" or mode == "F":
        s_array.append(0)
    elif mode == "T":
        s_array.append(int(speed))
    
    t_array = t_array[-100:]  # TODO: Choose optimal amount
    p_array = p_array[-100:]
    s_array = s_array[-100:]
    
    axis.clear()
    axis.set_ylim(0, 1750)
    axis.plot(t_array, p_array, label="Pressure")
    axis.plot(t_array, s_array, label="Pump activity")
    axis.legend(loc='lower left')
    
# ===================================================================
# File execution
if __name__ == "__main__":
    import tkinter
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib import pyplot as plt, animation
    
    INTERVAL = 50
    START = time.time()
    
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
    
    saving = False
    
    def save_data():
        global saving; saving = True
        fo = open("./recording.csv", "w")
        fo.write(f"timestamp, pump_mode, pump_speed, pressure\n")
        fo.close()
        
    def stop_data():
        global saving; saving = False
    
    button2 = tkinter.Button(master = root, text = "Record", command=save_data)
    button2.pack(side = tkinter.BOTTOM)
    
    button3 = tkinter.Button(master = root, text= "Stop", command=stop_data)
    button3.pack(side = tkinter.BOTTOM)

    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
    # TODO: Choose corret interval
    ani = animation.FuncAnimation(fig, plot_data, fargs=(t_array, p_array, s_array, serial_object, ax), interval = INTERVAL, cache_frame_data=False)

    tkinter.mainloop()
