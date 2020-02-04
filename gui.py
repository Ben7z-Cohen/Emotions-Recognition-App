import webbrowser
from threading import Thread
from tkinter import Tk, ttk, Image
import tkinter
import cv2
from PIL import ImageTk
from bokeh.plotting import figure, show, output_file
import time
from datetime import datetime

class Gui:

    def __init__(self, canvas, video_capture):
        self._video_capture = video_capture
        self._plot_instructions = "Choose the data you\n want to analyze:"
        self._title = "Emotions Recognition"
        self.init_root()
        self.init_image()
        self.init_checkbox()
        self.init_label()
        self._canvas = canvas


    def init_root(self):
        self._root = Tk()
        self._root.config(background="#FFFFFF")
        self._root.title(self._title)
        style = ttk.Style(self._root)
        style.theme_use("clam")

    def init_image(self):
        self._imageFrame = ttk.Frame(self._root, width=600, height=600)
        self._lmain = ttk.Label(self._imageFrame)
        self._lmain.grid(row=0, column=0)

    def init_buttons(self):
        self._show_camera_btn = ttk.Button(self._root, text="Show Camera", command=self.showCamera)\
            .grid(row=1, column=0, padx=4, pady=4, sticky='ew')

        self._close_camera_btn = ttk.Button(self._root, text="Close Camera", command=self.closeCamera)\
            .grid(row=2, column=0, padx=4, pady=4, sticky='ew')

        self._plot_btn = ttk.Button(self._root, text="Plot", command=lambda: self.plotBokeh(self.PlotChosen.get()))\
            .grid(row=1, column=3, columnspan=5, padx=4, pady=4, sticky='wnse')

        self._exit_btn = ttk.Button(self._root, text="Exit", command=self.Exit).\
            grid(row=0, column=3, columnspan=5, padx=4, pady=4, sticky='wnse')

        self._instruction_btn = ttk.Button(self._root, text="Instructions", command=self.openPdf)\
            .grid(row=2, column=1, columnspan=6, padx=6, pady=6, sticky='we')

        self._start_btn = ttk.Button(self._root, text="Start", command=self.threadFunc)\
            .grid(row=0, column=0, padx=4, pady=4, sticky='ew')

    def init_label(self):
        ttk.Label(self._root, text=self._plot_instructions).grid(row=0, column=1, columnspan=2, padx=6, pady=6, sticky="wnse")

    def init_checkbox(self):
        PlotType = tkinter.StringVar()
        PlotChosen = ttk.Combobox(self._root, width=20, textvariable=PlotType)
        # PlotChosen['values'] = (type1, type2, type3)#Todo: link the plot types to here
        PlotChosen.grid(row=1, column=1, columnspan=2, padx=6, pady=6, sticky="wnse")
        PlotChosen.current(0)

    # When Grided will show the frame which is caputerd
    def showFrame(self):
        frame = cv2.flip(self._canvas, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self._lmain.imgtk = imgtk
        self._lmain.configure(image=imgtk)
        self._lmain.after(10, self.showFrame)

    # Griding the frame to the video
    def showCamera(self):
        self._imageFrame.grid(row=4, column=0, columnspan=5, padx=6, pady=6, sticky='ew')

    # Ungriding the showFrame
    def closeCamera(self):
        self._imageFrame.grid_remove()


    #Todo: fix this function
    # # Creating the Plots for the data
    # def plotBokeh(self, typePlot ):
    #     output_file("Plot.html", title="Analyzed Data")
    #     f = figure()
    #     if (typePlot == "LinePlot"):
    #         f = linePlot()
    #     if (typePlot == "Histogram"):
    #         f = histogram()
    #     if (typePlot == "Pie"):
    #         f = pie()
    #     show(f)

    # closing Tkinter
    def onClosing(self):
        cv2.destroyAllWindows()
        self._root.destroy()
        try:
            self._video_capture.release()
        except:
            print("close")

    # Exit button
    def Exit(self):
        cv2.destroyAllWindows()
        self._root.destroy()
        try:
            self._video_capture.release()
        except:
            print("close")

    # plot the instructions for App
    def openPdf(self):
        webbrowser.open_new(r'writeup_group54.pdf')

    # Open new Thread for startFunc
    def threadFunc(self):
        start_thread = Thread(target=startFunc, args=[button2, button3, button4, button5])
        start_thread.daemon = True
        start_thread.start()


    def startFunc(button1, button2, button3, button4):
        # Initializing time
        t0 = time.time()
        th = 1
        # Axis
        global time_line
        global emotion_axis
        # Face Recognition with the webcam
        global video_capture
        video_capture = cv2.VideoCapture(0)
        start = datetime.now()
        while True:
            # Sample time
            ts = time.time()
            # Relative time to t0
            tr = ts - t0
            ret, frame = video_capture.read()
            sec = (datetime.now() - start).seconds
            if ret is True:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                global canvas
                canvas, emotion = detect(gray, frame)
                if (emotion != None):  # and emotion != 0):
                    if (tr > th):
                        time_line.append(th)
                        th += 1
                        emotion_axis.append(emotion)
                        num_of_times[emotion] = num_of_times[emotion] + 1
            else:
                continue
            # Buttons Actions
            if button1 != None:
                button1.invoke()
            if button2 != None:
                button2.invoke()
            if button3 != None:
                button3.invoke()
            if button4 != None:
                button4.invoke()
                break
        video_capture.release()
        cv2.destroyAllWindows()
