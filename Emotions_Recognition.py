import cv2
import time
from datetime import datetime
import tkinter
from tkinter import Tk, ttk, Image
from threading import Thread
from PIL import Image, ImageTk
import webbrowser
from bokeh.plotting import figure, show, output_file
import numpy as np

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

smile_cascade = cv2.CascadeClassifier('haarcascade_smile.xml')

class app:

    def __init__(self, classifier, video_capture, gui):
        #Todo: Create class video capture
        self._classifier = classifier
        self._time_line = []
        self._emotion_axis = []
        self._video_capture = video_capture
        self._num_of_times = [0, 0, 0]
        self._canvas = np.zeros([480, 640, 3], dtype=np.uint8)
        self.gui = gui #Todo: implement class gui

    def detect(self):
        pass

    def start(self, gui):
        #Todo: this is the buttons the start controls :show_camera, close_camera, plot, exit
        pass

    def run(self):
        pass




def detect(gray, frame):
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    emotion = None
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_gray1 = gray[y:y + h, x:x + w]
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + w]
        resized_image = cv2.resize(roi_gray1, (350, 350))
        emotion, c = fisher_face.predict(resized_image)
        smiles = smile_cascade.detectMultiScale(roi_gray, 1.7, 22)
        for (sx, sy, sw, sh) in smiles:
            emotion = 2
            cv2.rectangle(roi_color, (sx, sy), (sx + sw, sy + sh), (0, 0, 255), 2)
    return frame, emotion



# Globales



##############################################################Plots#####################################################
data = {}



########################################################################################################################


# Start function: backstage code
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


# When Grided will show the frame which is caputerd
def showFrame():
    frame = cv2.flip(canvas, 1)
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(10, showFrame)


# Griding the frame to the video
def showCamera():
    imageFrame.grid(row=4, column=0, columnspan=5, padx=6, pady=6, sticky='ew')


# Ungriding the showFrame
def closeCamera():
    imageFrame.grid_remove()


# Creating the Plots for the data
def plotBokeh(typePlot, ):
    output_file("Plot.html", title="Analyzed Data")
    f = figure()
    if (typePlot == "LinePlot"):
        f = linePlot()
    if (typePlot == "Histogram"):
        f = histogram()
    if (typePlot == "Pie"):
        f = pie()
    show(f)


# closing Tkinter
def onClosing():
    cv2.destroyAllWindows()
    root.destroy()
    try:
        video_capture.release()
    except:
        print("close")


# Exit button
def Exit():
    cv2.destroyAllWindows()
    root.destroy()
    try:
        video_capture.release()
    except:
        print("close")


# plot the instructions for App
def openPdf():
    webbrowser.open_new(r'writeup_group54.pdf')


# Open new Thread for startFunc
def threadFunc():
    t = Thread(target=startFunc, args=[button2, button3, button4, button5])
    t.daemon = True
    t.start()


##################################################GUI###################################################################


# Init of texts
type1 = "LinePlot"
type2 = "Histogram"
type3 = "Pie"
instruct_plot = "Choose the data you\n want to analyze:"
title = "Emotions Recognition"

# Tkinter init
root = Tk()
root.config(background="#FFFFFF")
root.title(title)
style = ttk.Style(root)
style.theme_use("clam")

# Create Image
imageFrame = ttk.Frame(root, width=600, height=600)
lmain = ttk.Label(imageFrame)
lmain.grid(row=0, column=0)

# Buttons
button2 = ttk.Button(root, text="Show Camera", command=showCamera).grid(row=1, column=0, padx=4, pady=4, sticky='ew')

button3 = ttk.Button(root, text="Close Camera", command=closeCamera).grid(row=2,
                                                                          column=0, padx=4, pady=4, sticky='ew')

button4 = ttk.Button(root, text="Plot", command=lambda: plotBokeh(PlotChosen.get())).grid(row=1, column=3,
                                                                                          columnspan=5, padx=4, pady=4,
                                                                                          sticky='wnse')

button5 = ttk.Button(root, text="Exit", command=Exit).grid(row=0, column=3,
                                                           columnspan=5, padx=4, pady=4, sticky='wnse')

button6 = ttk.Button(root, text="Instructions", command=openPdf).grid(row=2,
                                                                      column=1, columnspan=6, padx=6, pady=6,
                                                                      sticky='we')

# CheckBox + Button1 + Label
PlotType = tkinter.StringVar()
PlotChosen = ttk.Combobox(root, width=20, textvariable=PlotType)
PlotChosen['values'] = (type1, type2, type3)
PlotChosen.grid(row=1, column=1, columnspan=2, padx=6, pady=6, sticky="wnse")
PlotChosen.current(0)

ttk.Label(root, text=instruct_plot).grid(row=0, column=1, columnspan=2, padx=6, pady=6, sticky="wnse")
button1 = ttk.Button(root, text="Start", command=threadFunc).grid(row=0, column=0, padx=4, pady=4, sticky='ew')

if __name__ == '__main__':
    create_classifier()
    # Running GUI
    showFrame()
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", onClosing)
    root.mainloop()
