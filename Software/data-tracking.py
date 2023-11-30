# Imports
import serial
import re
from serial.tools.list_ports import comports
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ===================================================================
# Helper functions
def serial_connection():
    for port, _, hwid in comports():
        if re.match("USB VID:PID=2341:0043", hwid):
            serial_object = serial.Serial(port, baudrate = 115200)
            if serial_object.is_open:
                return serial_object
    raise ConnectionError("No valid connection to the manometer found!")

def plot_data(i, t_array, p_array, serial_object, axis):
    # Read the data from the serial object
    while True:
        try:
            buffer = ";"
            while buffer[-1] != "\n":
                buffer += serial_object.read().decode()
            rel_time, speed, pressure = [x.strip() for x in buffer.split(";")[1:]]
            break
        except:
            continue
    
    if saving:
        with open("./recording.csv", "a") as fo:
            fo.write(f"{rel_time}, {speed}, {pressure}\n")
    
    t_array.append(rel_time)
    p_array.append(float(pressure))
    
    t_array = t_array[-30:]
    p_array = p_array[-30:]
    
    axis.clear()
    axis.plot(t_array, p_array)
    
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Manometer pressure over time')
    plt.ylabel('Pressure over time')

# ===================================================================
# File execution
if __name__ == "__main__":
    import tkinter
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib import pyplot as plt, animation

    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True

    t_array, p_array = list(), list()
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
        fo.write(f"timestamp, pump_speed, pressure\n")
        fo.close()
        
    def stop_data():
        global saving; saving = False
    
    button2 = tkinter.Button(master = root, text = "Record", command=save_data)
    button2.pack(side = tkinter.BOTTOM)
    
    button3 = tkinter.Button(master = root, text= "Stop", command=stop_data)
    button3.pack(side = tkinter.BOTTOM)

    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
    ani = animation.FuncAnimation(fig, plot_data, fargs=(t_array, p_array, serial_object, ax), interval = 1000)

    tkinter.mainloop()
