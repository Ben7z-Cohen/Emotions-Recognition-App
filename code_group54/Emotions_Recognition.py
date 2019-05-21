import cv2
import glob as gb
import random
import numpy as np
import time
from datetime import datetime
import tkinter
from tkinter import Tk, ttk, Image
from threading import Thread
from PIL import Image ,ImageTk
import webbrowser
from math import pi
import pandas as pd
from bokeh.transform import cumsum
from bokeh.transform import factor_cmap
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show, output_file





# Loading the cascades
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
smile_cascade = cv2.CascadeClassifier('haarcascade_smile.xml')

# Emotion list 123 + 123



emojis = ["sadness","surprise"]
# Initialize fisher face classifier
fisher_face = cv2.face.FisherFaceRecognizer_create()
data = {}

###############################################Training#################################################################

# Function definition to get file list, randomly shuffle it and split 67/33
def getFiles(emotion):
    files = gb.glob("final_dataset/%s/*" % emotion)
    random.shuffle(files)
    training = files[:int(len(files) * 0.67)]  # get first 67% of file list
    prediction = files[-int(len(files) * 0.33):]  # get last 33% of file list
    return training, prediction


def makeTrainingAndValidationSet():
    training_data = []
    training_labels = []
    prediction_data = []
    prediction_labels = []
    for emotion in emojis:
        training, prediction = getFiles(emotion)
        # Append data to training and prediction list, and generate labels 0-7
        for item in training:
            image = cv2.imread(item)  # open image
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # convert to grayscale
            training_data.append(gray)  # append image array to training data list
            training_labels.append(emojis.index(emotion))

        for item in prediction:  # repeat above process for prediction set
            image = cv2.imread(item)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            prediction_data.append(gray)
            prediction_labels.append(emojis.index(emotion))
    return training_data, training_labels, prediction_data, prediction_labels

########################################################################################################################

##################################################Detecting Funcs#######################################################

#Activate Training
def runClassifier():
    training_data, training_labels, prediction_data, prediction_labels = makeTrainingAndValidationSet()

    print("training fisher face classifier suing the training data")
    print("size of training set is:", len(training_labels), "images")
    fisher_face.train(training_data, np.asarray(training_labels))
    print("classification prediction")
    counter = 0
    right = 0
    wrong = 0
    for image in prediction_data:
        pred, conf = fisher_face.predict(image)
        print(pred)
        if pred == prediction_labels[counter]:
            right += 1
            counter += 1
        else:
            wrong += 1
            counter += 1
    return ((100 * right) / (right + wrong))


#Creating Canvas for Detections
def detect(gray, frame):
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    emotion = None
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        roi_gray1 = gray[y:y+h, x:x+w]
        roi_gray = gray[y:y + h , x:x + w ]
        roi_color = frame[y:y+h, x:x+w]
        resized_image = cv2.resize(roi_gray1, (350, 350))
        emotion, c = fisher_face.predict(resized_image)
        smiles = smile_cascade.detectMultiScale(roi_gray, 1.7, 22)
        for (sx, sy, sw, sh) in smiles:
            emotion = 2
            cv2.rectangle(roi_color, (sx, sy), (sx+sw, sy+sh), (0, 0, 255), 2)
    return frame, emotion



# Creating the Classfier
def Create_Classfier():
    # Run the trainer & validator to get ready to do the emotion recognition
    metascore = []
    for i in range(0, 10):
        right = runClassifier()
        print("got", right, "percent right!")
        metascore.append(right)
    print("\n\nend score:", np.mean(metascore), "percent right!")

#######################################################################################################################



############################################# Function Used by Buttons##################################################

#Globales
time_line = []
emotion_axis = []
num_of_times=[0,0,0]
canvas = np.zeros([480, 640, 3], dtype=np.uint8)
##############################################################Plots#####################################################

def Pie():
    x = {
        'Other': num_of_times[0],
        'Sadness':  num_of_times[1],
        'Happy': num_of_times[2]
    }

    data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'Emotion'})
    data['angle'] = data['value'] / data['value'].sum() * 2 * pi
    data['color'] = ['#1f77b4', '#aec7e8', '#ff7f0e']

    p = figure(plot_height=350, title="Pie Chart", toolbar_location=None,
               tools="hover", tooltips="@Emotion: @value", x_range=(-0.5, 1.0))

    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend='Emotion', source=data)

    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None

    return p

def Histogram():
    emotion = ['Other', 'Sadness','Happy']
    counts = [num_of_times[0], num_of_times[1], num_of_times[2]]

    source = ColumnDataSource(data=dict(emotion=emotion, counts=counts))

    p = figure(x_range=emotion, plot_height=350, toolbar_location=None, title="Emotion's")
    p.vbar(x='emotion', top='counts', width=0.9, source=source, legend="emotion",
           line_color='white', fill_color=factor_cmap('emotion', palette=["#3288bd", "#99d594", "#e6f598",
                                                                          "#fee08b", "#fc8d59", "#d53e4f"]
    , factors=emotion))

    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.y_range.end = max(num_of_times)
    p.legend.orientation = "horizontal"
    p.legend.location = "top_left"
    return p

def LinePlot():
    name = "0-Other\n 1-Sadness \n 2-Happy"
    color = ["red"]
    f = figure(title="Emotions Vs Time")
    f.xaxis.axis_label = 'Time'
    f.yaxis.axis_label = 'Emotion'
    f.line(time_line, emotion_axis,alpha=0.8,color="blue", legend=name)
    f.legend.location = "top_left"
    return f

########################################################################################################################




#Start Function: Running the backstage code
def Start(button1,button2,button3,button4):
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
        sec =(datetime.now()-start  ).seconds
        if ret is True:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            global canvas
            canvas, emotion = detect(gray, frame)
            if (emotion != None ):#and emotion != 0):
                if (tr > th):
                    time_line.append(th)
                    th += 1
                    emotion_axis.append(emotion)
                    num_of_times[emotion]=num_of_times[emotion]+1

        else:
            continue
        #Buttons Actions
        if button1!=None:
            button1.invoke()
        if button2 != None:
            button2.invoke()
        if button3 != None:
            print("3 is Alive")
            button3.invoke()
        if button4!= None:
            button4.invoke()
            break
    video_capture.release()
    cv2.destroyAllWindows()



#Whene Grided will show the frame which is caputerd
def show_frame():
    frame = cv2.flip(canvas, 1)
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(10, show_frame)

#Griding the Show_frame to this the video
def Show_camera():
    imageFrame.grid(row=4, column=0 ,columnspan = 5, padx=6, pady=6, sticky='ew')

#Ungriding the show_frame
def Close_camera():
    imageFrame.grid_remove()


#Creating the Plots for the data
def Plot_Bokeh(typePlot,):
    output_file("Plot.html",title="Analyzed Data")
    f = figure()
    if(typePlot=="LinePlot"):
        f =LinePlot()
    if(typePlot=="Histogram"):
        f=Histogram()
    if (typePlot == "Pie"):
        f = Pie()
    show(f)


#Whene closing Tkinter
def on_closing():
    cv2.destroyAllWindows()
    root.destroy()
    try:
        video_capture.release()
    except:
        print("close")
#Pressing the Exit button on Tkinter
def Exit():
    cv2.destroyAllWindows()
    root.destroy()
    try:
        video_capture.release()
    except:
        print("close")
#plot the instroctions for App
def OpenPdf():
    webbrowser.open_new(r'writeup_group54.pdf')

#Open new Thread for Start Function
def ThreadFunc():
    t = Thread(target=Start,args =[button2,button3,button4,button5])
    t.daemon = True
    t.start()

########################################################################################################################

##################################################GUI###################################################################



#Init of Text's
type1 = "LinePlot"
type2 = "Histogram"
type3 = "Pie"
InstructPLot = "Choose the Data you\n Want to Analyze:"
title = "Emotions Recognition"

#Tkinter init
root = Tk()
root.config(background="#FFFFFF")
root.title(title)
style = ttk.Style(root)
style.theme_use("clam")

#Create Image
imageFrame = ttk.Frame(root, width=600, height=600)
lmain = ttk.Label(imageFrame)
lmain.grid(row=0, column=0)


#Buttons
button2 = ttk.Button(root, text="Show Camera", command=Show_camera).grid(row=1, column=0,padx=4, pady=4, sticky='ew')

button3 =ttk.Button(root, text="Close Camera", command=Close_camera).grid(row=2,
                                                                          column=0,padx=4, pady=4, sticky='ew')

button4=ttk.Button(root,text = "Plot",command=lambda: Plot_Bokeh(PlotChosen.get())).grid(row=1, column=3,
                                                                         columnspan =5,padx=4, pady=4, sticky='wnse')

button5 =ttk.Button(root, text="Exit", command=Exit).grid(row=0, column=3,
                                                          columnspan =5,padx=4, pady=4, sticky='wnse')

button6 = ttk.Button(root, text="Instructions", command=OpenPdf).grid(row=2,
                                                              column=1, columnspan =6,padx=6, pady=6, sticky='we')

#CheckBox + Button1 + Label
PlotType = tkinter.StringVar()
PlotChosen = ttk.Combobox(root,width=20,textvariable = PlotType)
PlotChosen['values']= (type1,type2,type3)
PlotChosen.grid(row=1, column=1,columnspan=2, padx=6, pady=6, sticky="wnse")
PlotChosen.current(0)

ttk.Label(root, text=InstructPLot).grid(row=0, column=1,columnspan=2, padx=6, pady=6, sticky="wnse")
button1 =ttk.Button(root, text="Start", command= ThreadFunc).grid(row=0, column=0,padx=4, pady=4, sticky='ew')


if __name__ == '__main__':

    #Start the Classfier
    Create_Classfier()



    # Running GUI
    show_frame()
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()




