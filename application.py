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
        self._engine = engine
        self._plot = Plot(self._engine)
        self._plot_strategy = PlotStrategy(self._plot)

    def init_texts(self):
        self._plot_type_line = PlotType.Line.value
        self._plot_type_histogram = PlotType.Histogram.value
        self._plot_type_pie = PlotType.Pie.value
        self._instruction_plot = "Choose the type of data you\n want to analyze:"
        self._title = "Emotions Recognition"

    def init_tkinter(self):
        self._root = Tk()
        self._root.config(background="#FFFFFF")
        self._root.title(self._title)
        style = ttk.Style(self._root)
        style.theme_use("clam")

    def create_image(self):
        self._image_frame = ttk.Frame(self._root, width=600, height=600)
        self._lmain = ttk.Label(self._image_frame)
        self._lmain.grid(row=0, column=0)

    def combobox(self):
        plot_type = tkinter.StringVar()
        self._plot_chosen = ttk.Combobox(self._root, width=20, textvariable=plot_type)
        self._plot_chosen['values'] = (self._plot_type_line, self._plot_type_histogram, self._plot_type_pie)
        self._plot_chosen.grid(row=1, column=1, columnspan=2, padx=6, pady=6, sticky="wnse")
        self._plot_chosen.current(0)

    def buttons(self):
        ttk.Label(self._root, text=self._instruction_plot). \
            grid(row=0,
                 column=1,
                 columnspan=2,
                 padx=6, pady=6,
                 sticky="wnse")
        self._show_camera_button = ttk.Button(self._root, text="Show Camera",
                                              command=self.show_camera). \
            grid(row=1,
                 column=0,
                 padx=4, pady=4,
                 sticky='ew')
        self._close_camera_button = ttk.Button(self._root, text="Close Camera",
                                               command=self.close_camera). \
            grid(row=2,
                 column=0,
                 padx=4,
                 pady=4,
                 sticky='ew')
        self._plot_button = ttk.Button(self._root, text="Plot",
                                       command=lambda:
                                       self.handle_plot(self._plot_chosen.get())). \
            grid(row=1,
                 column=3,
                 columnspan=5,
                 padx=4,
                 pady=4,
                 sticky='wnse')
        self._exit_button = ttk.Button(self._root, text="Exit", command=self.exit). \
            grid(row=0,
                 column=3,
                 columnspan=5,
                 padx=4,
                 pady=4,
                 sticky='wnse')

        self._instructions_button = ttk.Button(self._root, text="Instructions",
                                               command=self.open_instructions). \
            grid(row=2,
                 column=1,
                 columnspan=6,
                 padx=6,
                 pady=6,
                 sticky='we')

        self._start_button = ttk.Button(self._root, text="Start",
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
        frame = cv2.flip(self._engine.canvas, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self._lmain.imgtk = imgtk
        self._lmain.configure(image=imgtk)
        self._lmain.after(10, self.show_frame)

    def show_camera(self):
        self._image_frame.grid(row=4, column=0, columnspan=5,
                               padx=6, pady=6, sticky='ew')

    def close_camera(self):
        self._image_frame.grid_remove()

    def handle_plot(self, plot_type):
        output_file("Plot.html", title="Analyzed Data")
        plot = self._plot.factory(plot_type)
        self._plot_strategy.strategy = plot
        self._plot_strategy.plot()

    def handle_thread(self):
        thread = Thread(target=self.main, args=[self._show_camera_button,
                                                self._close_camera_button,
                                                self._plot_button, self._exit_button])
        thread.daemon = True
        thread.start()

    def on_closing(self):
        cv2.destroyAllWindows()
        self._root.destroy()
        try:
            self._engine.video_capture.release()
        except:
            print("close")

    def exit(self):
        cv2.destroyAllWindows()
        self._root.destroy()
        try:
            self._engine.video_capture.release()
        except:
            print("close")

    def main(self, show_camera_button,
             close_camera_button, plot_button, exit_button):
        t0 = time.time()
        th = 1
        self._engine.video_capture = cv2.VideoCapture(0)
        while True:
            ts = time.time()
            tr = ts - t0
            ret, frame = self._engine.video_capture.read()
            if ret is True:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                self._engine.canvas, emotion = self._engine.model.detect(gray, frame)
                if emotion is not None:
                    if tr > th:
                        self._engine.time_line.append(th)
                        th += 1
                        self._engine.emotion_axis.append(emotion)
                        self._engine.num_of_appearance[emotion] += 1

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
        self._engine.video_capture.release()
        cv2.destroyAllWindows()

    def run(self):
        self._engine.model.load_classifier()
        self.show_frame()
        self._root.resizable(False, False)
        self._root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._root.mainloop()
