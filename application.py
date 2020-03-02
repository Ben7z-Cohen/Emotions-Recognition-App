import time
import tkinter
import webbrowser
from threading import Thread
from tkinter import Image
from tkinter import Tk, ttk

import cv2
from PIL import Image, ImageTk
from bokeh.plotting import output_file

from plots.plot import Plot, PlotType
from plots.plot_strategy import PlotStrategy
from singleton import Singleton


class Application(metaclass=Singleton):
    def __init__(self, engine):
        self.init_texts()
        self.init_tkinter()
        self.create_image()
        self.buttons()
        self.combobox()
        self.engine = engine
        self.plot = Plot(self.engine)
        self.plot_strategy = PlotStrategy(self.plot)

    def init_texts(self):
        self.plot_type_line = PlotType.Line.value
        self.plot_type_histogram = PlotType.Histogram.value
        self.plot_type_pie = PlotType.Pie.value
        self.instruction_plot = "Choose the type of data you\n want to analyze:"
        self.title = "Emotions Recognition"

    def init_tkinter(self):
        self.root = Tk()
        self.root.config(background="#FFFFFF")
        self.root.title(self.title)
        style = ttk.Style(self.root)
        style.theme_use("clam")

    def create_image(self):
        self.image_frame = ttk.Frame(self.root, width=600, height=600)
        self.lmain = ttk.Label(self.image_frame)
        self.lmain.grid(row=0, column=0)

    def combobox(self):
        plot_type = tkinter.StringVar()
        self.plot_chosen = ttk.Combobox(self.root, width=20, textvariable=plot_type)
        self.plot_chosen['values'] = (self.plot_type_line, self.plot_type_histogram, self.plot_type_pie)
        self.plot_chosen.grid(row=1, column=1, columnspan=2, padx=6, pady=6, sticky="wnse")
        self.plot_chosen.current(0)

    def buttons(self):
        ttk.Label(self.root, text=self.instruction_plot). \
            grid(row=0,
                 column=1,
                 columnspan=2,
                 padx=6, pady=6,
                 sticky="wnse")
        self.show_camera_button = ttk.Button(self.root, text="Show Camera",
                                             command=self.show_camera). \
            grid(row=1,
                 column=0,
                 padx=4, pady=4,
                 sticky='ew')
        self.close_camera_button = ttk.Button(self.root, text="Close Camera",
                                              command=self.close_camera).\
            grid(row=2,
                 column=0,
                 padx=4,
                 pady=4,
                 sticky='ew')
        self.plot_button = ttk.Button(self.root, text="Plot",
                                      command=lambda:
                                      self.handle_plot(self.plot_chosen.get())). \
            grid(row=1,
                 column=3,
                 columnspan=5,
                 padx=4,
                 pady=4,
                 sticky='wnse')
        self.exit_button = ttk.Button(self.root, text="Exit", command=self.exit). \
            grid(row=0,
                 column=3,
                 columnspan=5,
                 padx=4,
                 pady=4,
                 sticky='wnse')

        self.instruction_button = ttk.Button(self.root, text="Instructions",
                                             command=self.open_instructions). \
            grid(row=2,
                 column=1,
                 columnspan=6,
                 padx=6,
                 pady=6,
                 sticky='we')

        self.start_button = ttk.Button(self.root, text="Start",
                                       command=self.handle_thread). \
            grid(row=0,
                 column=0,
                 padx=4,
                 pady=4,
                 sticky='ew')

    @staticmethod
    def open_instructions():
        webbrowser.open_new(r'Instructions.pdf')

    def show_frame(self):
        frame = cv2.flip(self.engine.canvas, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)
        self.lmain.after(10, self.show_frame)

    def show_camera(self):
        self.image_frame.grid(row=4, column=0, columnspan=5,
                              padx=6, pady=6, sticky='ew')

    def close_camera(self):
        self.image_frame.grid_remove()

    def handle_plot(self, plot_type):
        output_file("Plot.html", title="Analyzed Data")
        plot = self.plot.factory(plot_type)
        self.plot_strategy.strategy = plot
        self.plot_strategy.plot()

    def handle_thread(self):
        thread = Thread(target=self.main, args=[self.show_camera_button,
                                                self.close_camera_button,
                                                self.plot_button, self.exit_button])
        thread.daemon = True
        thread.start()

    def on_closing(self):
        cv2.destroyAllWindows()
        self.root.destroy()
        try:
            self.engine.video_capture.release()
        except:
            print("close")

    def exit(self):
        cv2.destroyAllWindows()
        self.root.destroy()
        try:
            self.engine.video_capture.release()
        except:
            print("close")

    def main(self, show_camera_button,
             close_camera_button, plot_button, exit_button):
        t0 = time.time()
        th = 1
        self.engine.video_capture = cv2.VideoCapture(0)
        while True:
            ts = time.time()
            tr = ts - t0
            ret, frame = self.engine.video_capture.read()
            if ret is True:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                self.engine.canvas, emotion = self.engine.model.detect(gray, frame)
                if emotion is not None:
                    if tr > th:
                        self.engine.time_line.append(th)
                        th += 1
                        self.engine.emotion_axis.append(emotion)
                        self.engine.num_of_appearance[emotion] += 1

            else:
                continue
            if show_camera_button is not None:
                show_camera_button.invoke()
            if close_camera_button is not None:
                close_camera_button.invoke()
            if plot_button is not None:
                plot_button.invoke()
            if exit_button is not None:
                exit_button.invoke()
                break
        self.engine.video_capture.release()
        cv2.destroyAllWindows()

    def run(self):
        self.engine.model.load_classifier()
        self.show_frame()
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

