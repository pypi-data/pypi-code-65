import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from pathlib import Path
import numpy as np
import cv2 as cv
import os


class EmotionRecognition(object):
    def __init__(self, gpu_id=0):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_model = tf.keras.applications.MobileNetV2(include_top=False, weights='imagenet', input_shape=(48, 48, 3))
        self.gap = layers.GlobalMaxPooling2D()
        self.dense = layers.Dense(128, activation='relu')
        self.classifier = layers.Dense(7, activation='sigmoid')
        self.latest_checkpoint = tf.train.latest_checkpoint(os.path.join(self.base_dir, 'model'))
        self.model = self._make_transfer_model()
        self.model.load_weights(self.latest_checkpoint)
        self.haar_file = os.path.join(self.base_dir, 'xml_files', 'haarcascade_frontalface_default.xml')
        self.face_cascade = cv.CascadeClassifier(self.haar_file)
        self.label2emotion = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5: 'Surprise', 6: 'Neutral'}

    def _make_transfer_model(self):
        return keras.Sequential([
            self.base_model,
            self.gap,
            self.dense,
            self.classifier
        ])

    def _detect_face(self, image):
        gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray_image, 1.3, 4)
        if faces is not None:
            return faces
        else:
            return None

    def recognize(self, image, return_type="rgb"):
        h_i, w_i, _ = image.shape
        clone = np.copy(image)
        faces = self._detect_face(image)
        gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        if faces is not None:
            for (x, y, w, h) in faces:
                face = gray_image[y:y+h, x:x+w]
                face = cv.resize(face, (48, 48))
                required_face = np.concatenate((face[:, :, np.newaxis], face[:, :, np.newaxis], face[:, :, np.newaxis]), axis=2)
                tensor = tf.expand_dims(((required_face / 127.5) - 1), axis=0)
                prediction = self.model.predict(tensor)
                emotion = self.label2emotion[np.argmax(prediction)]
                clone = cv.rectangle(clone, (x, y), (x+w, y+h), (0, 255, 0), 1)
                clone = cv.rectangle(clone, (x, y-((15*h_i)//480)), (x+w, y), color=[0, 255, 0], thickness=-1)
                cv.putText(clone, emotion, org=(x+1, y-1),
                           fontFace=cv.FONT_HERSHEY_COMPLEX,
                           fontScale=(0.5*(h_i*w_i)/(640*480)),
                           color=[0, 0, 0],
                           thickness=1,
                           )
            if return_type.lower() == "rgb":
                return cv.cvtColor(clone, cv.COLOR_BGR2RGB)
            elif return_type.lower() == "bgr":
                return clone
        else:
            print('No face detected!')
            return None


if __name__ == "__main__":
    er = EmotionRecognition()
    cap = cv.VideoCapture(0)
    if cap.isOpened():
        print("Camera connected!")

    success, frame = cap.read()

    while success:
        success, frame = cap.read()
        frame = np.flip(frame, 1)
        face_frame = er.recognize(frame)
        if face_frame is not None:
            frame = face_frame
        cv.imshow('frame', frame)
        key = cv.waitKey(1)
        if key & 0xFF == 27:
            cv.destroyAllWindows()
            break
