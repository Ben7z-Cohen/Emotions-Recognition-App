import cv2
import glob as gb
import random
import numpy as np


class FisherClassifier:

    def __init__(self, emotions = None):
        if emotions == None:
            self._emotions = ["sadness", "surprise"]
        else:
        self._emotions = emotions
        self.fisher_face = cv2.face.FisherFaceRecognizer_create()
        self.create_classifier()
        return self.fisher_face

    def split_data(self, emotion: str) -> (list, list):
        """
        splitting the images to training set and prediction set for each emotion.
        :parameter: emotion
        """
        files = gb.glob("final_dataset/%s/*" % emotion)
        random.shuffle(files)
        training = files[:int(len(files) * 0.67)]
        prediction = files[-int(len(files) * 0.33):]
        return training, prediction

    def make_training_and_validation_set(self) -> (list, list, list, list):
        training_data = []
        training_labels = []
        prediction_data = []
        prediction_labels = []
        for emotion in self._emotions:
            training, prediction = self.split_data(emotion)
            for item in training:
                image = cv2.imread(item)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                training_data.append(gray)
                training_labels.append(self.emotions.index(emotion))
            for item in prediction:
                image = cv2.imread(item)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                prediction_data.append(gray)
                prediction_labels.append(self.emotions.index(emotion))
        return training_data, training_labels, prediction_data, prediction_labels

    def run_classifier(self) -> float:
        training_data, training_labels, prediction_data, prediction_labels \
            = self.make_training_and_validation_set()
        print("training fisher face classifier suing the training data")
        print("size of training set is:", len(training_labels), "images")
        self.fisher_face.train(training_data, np.asarray(training_labels))
        print("classification prediction")
        counter = 0
        right = 0
        wrong = 0
        for image in prediction_data:
            pred, conf = self.fisher_face.predict(image)
            print(pred)
            if pred == prediction_labels[counter]:
                right += 1
                counter += 1
            else:
                wrong += 1
                counter += 1
        return (100 * right) / (right + wrong)

    def create_classifier(self) -> None:
        metascore = []
        for i in range(0, 10):
            right = self.run_classifier()
            print("got", right, "percent right!")
            metascore.append(right)
        print("\n\nend score:", np.mean(metascore), "percent right!")
