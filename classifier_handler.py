import cv2
import glob as gb
import random
import numpy as np


class ClassifierHandler:

    def __init__(self, app_engine):
        self._fisher_face = cv2.face.FisherFaceRecognizer_create()
        self._data = {}
        self._app_engine = app_engine
        self._face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self._smile_cascade = cv2.CascadeClassifier('haarcascade_smile.xml')

    def get_files(self, emotion):
        files = gb.glob("final_dataset/%s/*" % emotion)
        random.shuffle(files)
        training = files[:int(len(files) * 0.67)]
        prediction = files[-int(len(files) * 0.33):]
        return training, prediction

    def make_training_and_validation_set(self):
        training_data = []
        training_labels = []
        prediction_data = []
        prediction_labels = []
        for emotion in self._app_engine.EMOTIONS:
            training, prediction = self.get_files(emotion)
            for item in training:
                image = cv2.imread(item)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                training_data.append(gray)
                training_labels.append(self._app_engine.EMOTIONS.index(emotion))

            for item in prediction:
                image = cv2.imread(item)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                prediction_data.append(gray)
                prediction_labels.append(self._app_engine.EMOTIONS.index(emotion))
        return training_data, training_labels, prediction_data, prediction_labels


    def train_and_test_classifier(self):
        training_data, training_labels, prediction_data, \
        prediction_labels = self.make_training_and_validation_set()
        print("training fisher face classifier suing the training data")
        print("size of training set is:", len(training_labels), "images")
        self._fisher_face.train(training_data, np.asarray(training_labels))
        self._fisher_face.save('emotions_recognition.xml')
        print("classification prediction")
        counter = 0
        right = 0
        wrong = 0
        for image in prediction_data:
            pred, conf = self._fisher_face.predict(image)
            print(pred)
            if pred == prediction_labels[counter]:
                right += 1
                counter += 1
            else:
                wrong += 1
                counter += 1
        return ((100 * right) / (right + wrong))

    def get_classifier_accuracy(self, num_of_tests):
        metascore = []
        for i in range(0, num_of_tests):
            right = self.train_and_test_classifier()
            print("got", right, "percent right!")
            metascore.append(right)
        print("\n\nend score:", np.mean(metascore), "percent right!")

    def load_classifier(self):
        self._fisher_face.read('emotions_recognition.xml')

    def detect(self, gray, frame):
        faces = self._face_cascade.detectMultiScale(gray, 1.3, 5)
        emotion = None
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray1 = gray[y:y + h, x:x + w]
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = frame[y:y + h, x:x + w]
            resized_image = cv2.resize(roi_gray1, (350, 350))
            emotion, c = self._fisher_face.predict(resized_image)
            smiles = self._smile_cascade.detectMultiScale(roi_gray, 1.7, 22)
            for (sx, sy, sw, sh) in smiles:
                emotion = 2
                cv2.rectangle(roi_color, (sx, sy), (sx + sw, sy + sh), (0, 0, 255), 2)
        return frame, emotion
