import numpy as np
from classifier_handler import ClassifierHandler


class AppEngine:
    EMOTIONS = ["sadness", "surprise"]

    def __init__(self):
        self.time_line = []
        self.emotion_axis = []
        self.num_of_appearance = [0] * (len(self.EMOTIONS) + 1)
        self.emotions = ['others']
        self.emotions = self.emotions + AppEngine.EMOTIONS
        self.video_capture = None
        self.canvas = np.zeros([480, 640, 3], dtype=np.uint8)
        self._model = ClassifierHandler(self)

    @property
    def model(self):
        return self._model
