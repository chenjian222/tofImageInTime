import queue
import threading

import matplotlib
import numpy as np
import serial
import matplotlib.colors
from matplotlib import pyplot as plt, animation
from scipy.interpolate import RectBivariateSpline, interp2d

matplotlib.use('TkAgg')
ser = serial.Serial('COM12', 115200)  # Change baud rate if needed
cmap = plt.cm.get_cmap('viridis')
reversed_cmap = cmap.reversed()
q = queue.Queue()


# 绘图代码
def calculate(final_array):

    data_4x4 = final_array

    # 创建一个行列向量，用于表示4x4图像数据的坐标
    x = np.linspace(0, 1, 4)
    y = np.linspace(0, 1, 4)

    # 创建一个网格，用于表示10x10的目标图像数据的坐标
    x_new = np.linspace(0, 1, 20)
    y_new = np.linspace(0, 1, 20)

    # 创建一个二维样条插值对象并拟合数据
    interp = RectBivariateSpline(x, y, data_4x4)

    # 使用插值对象对新的网格进行插值
    data_20x20 = interp(x_new, y_new)
    return data_20x20

def get_data():
    global change_array
    try:

        final_array = []
        while True:
            if ser.in_waiting > 0:
                # Read bytes from the serial port
                data = ser.readline().decode('utf-8').strip()
                data = data.split("\t")
                num = 0
                # 判断一个4*4的起始位置
                if not data[0].isdigit() and num % 4 == 0:
                    num = 0
                    # 获取4*4的矩阵，先判断arrayd的长度是不是4
                    if final_array.__len__() == 4:
                        # 绘图前准备

                        final_array = calculate(final_array)
                        # print(final_array)
                        q.put(final_array.tolist())
                    final_array = []

                if data[0].isdigit():
                    array = []
                    for i in data:
                        array.append(int(i))
                    num += 1
                    final_array.append(array)


    except KeyboardInterrupt:
        ser.close()  # Close the serial port on Ctrl+C interrupt

def update(frame):
    global q
    print(q.qsize())
      # Clear the current axes
    if q.get() != None:
        plt.cla()
        data = q.get()  # Get new data for this frame
        plt.imshow(data, cmap=reversed_cmap, vmin=300, vmax=1000)  # Plot the new data with a color map
        plt.title(f'Frame: {frame}')  # Set title for each frame
        print(data)


def draw():
    fig, ax = plt.subplots()


    # Set up the initial plot (empty for animation)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()
    data = np.random.rand(10, 10)  # Generating some initial random data as placeholder

    # Plot the initial data and create colorbar
    ax.imshow(data, cmap=reversed_cmap, vmin=300, vmax=1000)
    # Create the animation
    ani = animation.FuncAnimation(fig, update, frames=100, interval=0.001)  # 100 frames, each lasting 200 milliseconds

    plt.show()


if __name__ == '__main__':
    thread1 = threading.Thread(target=draw)
    thread2 = threading.Thread(target=get_data)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
