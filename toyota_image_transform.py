import numpy as np
import os
import cv2
import tensorflow as tf
from keras.applications.vgg16 import VGG16
from keras.layers import Input, Dense, Conv2D, Activation , MaxPooling2D, Flatten
from keras.models import load_model
def image_transform(path):
    IMAGE_SIZE = (224, 224)
    image = cv2.imread(path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, IMAGE_SIZE)
    image = image.reshape(1,224,224,3)
    re_image = image/255
    model1 = load_model('my_vggmodel.h5')
    test_features = model1.predict(re_image)
    mode2 = load_model('my_cnnmodel.h5')
    predictions = mode2.predict(test_features)
    pred_labels = np.argmax(predictions, axis = 1)
    return pred_labels
