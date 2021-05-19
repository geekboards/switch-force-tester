import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button,TextBox
import serial
from time import sleep
import json

#ser = serial.Serial('COM21', 115200)
sleep(2)

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)

plt.xlabel("travel, mm")
plt.ylabel("weight, g")
plt.grid(color = 'green', linestyle = '--', linewidth = 0.5)

down_plt, = plt.plot([0,4], [10,110], lw=1)
up_plt, = plt.plot([0,4], [0,100], lw=1)
pressed_plt, = plt.plot(2, 60, 'v', color='blue')
release_plt, = plt.plot(2, 50, '^', color='red')

STEPS_PER_MM = 320.0

class Index:
    ind = 0
    export_data = {'x':1}

    def up(self, event):
        ser.write(b'm-3200')
        print(ser.readline())

    def down(self, event):
        ser.write(b'm3200')
        print(ser.readline())

    def save(self,event):
        plt.savefig('results/' + tname.text+'.png', dpi=300, format='png')
        with open('results/' + tname.text+'.json', 'w+') as f:
            f.write(json.dumps(self.export_data))

    def measure(self, event):
        ser.write(b't')
        print(ser.readline())
        ser.write(b'z')
        print(ser.readline())
        ser.write(b'p')
        down_datax = []
        down_datay = []
        up_datax = []
        up_datay = []
        pressPoint = (0,0)
        releasePoint = (0,0)
        while True:
            c = ser.readline()
            print(c)
            if chr(c[0]) == 'p': #plot
                break
            if chr(c[0]) == 'P': #pressed
                pressPoint = (int(c[1:].split(b':')[0])/STEPS_PER_MM, float(c[1:].split(b':')[1]))
                print('pressPoint', pressPoint)
                continue
            if chr(c[0]) == 'R': #relesed
                releasePoint = (int(c[1:].split(b':')[0])/STEPS_PER_MM, float(c[1:].split(b':')[1]))
                print('releasePoint', releasePoint)
                continue
            x = int(c[1:].split(b':')[0])/STEPS_PER_MM
            y = float(c[1:].split(b':')[1])
            if(y > 1):
                if chr(c[0]) == 'd':
                    down_datax.append(x)
                    down_datay.append(y)
                if chr(c[0]) == 'u':
                    up_datax.append(x)
                    up_datay.append(y)

            down_plt.set_xdata(down_datax)
            down_plt.set_ydata(down_datay)
            up_plt.set_xdata(up_datax)
            up_plt.set_ydata(up_datay)
            fig.canvas.draw()
            
        down_plt.set_xdata(down_datax)
        down_plt.set_ydata(down_datay)
        up_plt.set_xdata(up_datax)
        up_plt.set_ydata(up_datay)
        pressed_plt.set_xdata(pressPoint[0])
        pressed_plt.set_ydata(pressPoint[1])
        release_plt.set_xdata(releasePoint[0])
        release_plt.set_ydata(releasePoint[1])
        plt.annotate(str(pressPoint[0]) +'mm, '+str(pressPoint[1])+'g',(pressPoint[0],pressPoint[1]+10))
        plt.annotate(str(releasePoint[0]) +'mm, '+str(releasePoint[1])+'g',(releasePoint[0],releasePoint[1]-10))
        plt.draw()
        ser.write(b'm-3200')
        print(ser.readline())

        self.export_data = {}
        self.export_data['down_x'] = down_datax
        self.export_data['down_y'] = down_datay
        self.export_data['up_x'] = down_datax
        self.export_data['up_y'] = up_datay
        self.export_data['pressPoint'] = pressPoint
        self.export_data['releasePoint'] = releasePoint
        

callback = Index()
axup = plt.axes([0.81, 0.01, 0.1, 0.075])
axdown = plt.axes([0.7, 0.01, 0.1, 0.075])
axmeasure = plt.axes([0.59, 0.01, 0.1, 0.075])
axsave = plt.axes([0.48, 0.01, 0.1, 0.075])
axname = plt.axes([0.20, 0.01, 0.27, 0.075])
bup = Button(axup, 'Up')
bup.on_clicked(callback.up)
bdown = Button(axdown, 'Down')
bdown.on_clicked(callback.down)
bmeasure = Button(axmeasure, 'Measure')
bmeasure.on_clicked(callback.measure)
bsave = Button(axsave, 'Save')
bsave.on_clicked(callback.save)
tname = TextBox(axname, '', 'name')

plt.show()


ser.close()
