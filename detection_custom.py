#================================================================
#
#   File name   : detection_custom.py
#   Author      : PyLessons
#   Created date: 2020-09-17
#   Website     : https://pylessons.com/
#   GitHub      : https://github.com/pythonlessons/TensorFlow-2.x-YOLOv3
#   Description : object detection image and video example
#
#================================================================
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
import cv2
import numpy as np
import tensorflow as tf
from keras.applications.vgg16 import VGG16
from yolov3.utilscopy import detect_image, detect_realtime, detect_video, Load_Yolo_model, detect_video_realtime_mp
from yolov3.configs import *
from keras.models import load_model

def test(path):
    image_path   = path
    video_path   = "./IMAGES/test.mp4"

    yolo = Load_Yolo_model()
    bounded_img_path = "./IMAGE/"+path[-15:-4]+".jpg"
    # return detect_image(yolo, image_path, r"C:\Users\TibaMe\Desktop\linebot\IMAGE\GGGG.jpg", input_size=YOLO_INPUT_SIZE, show=False, CLASSES=TRAIN_CLASSES, rectangle_colors=(255,0,0))
    return detect_image(yolo, image_path, bounded_img_path, input_size=YOLO_INPUT_SIZE, show=False, CLASSES=TRAIN_CLASSES, rectangle_colors=(255,0,0))

#detect_video(yolo, video_path, './IMAGES/detected.mp4', input_size=YOLO_INPUT_SIZE, show=False, CLASSES=TRAIN_CLASSES, rectangle_colors=(255,0,0))
#detect_realtime(yolo, '', input_size=YOLO_INPUT_SIZE, show=True, CLASSES=TRAIN_CLASSES, rectangle_colors=(255, 0, 0))

#detect_video_realtime_mp(video_path, "Output.mp4", input_size=YOLO_INPUT_SIZE, show=True, CLASSES=TRAIN_CLASSES, rectangle_colors=(255,0,0), realtime=False)




# pathq = '.\img\\image03122021175958.jpg'
# pathq ='.\img\\image03112021164717.jpg'
def pred(path):
    image_path=path
    a,b,c=test(image_path)
    ans=[]
    # print(c)
    if c == 'None':
        for i in b:
            x1,y1,x2,y2= i[0][0],i[0][1],i[1][0],i[1][1]
            pic_x = int(x1)
            pic_y = int(y1)
            pic_x2 = int(x2)
            pic_y2 = int(y2)
            IMAGE_SIZE = (224, 224)
            original_image = cv2.imread(image_path)
            original_image = original_image[pic_y:pic_y2, pic_x:pic_x2]
            original_image = cv2.resize(original_image, IMAGE_SIZE)
            image = original_image.reshape(1,224,224,3)
            re_image = image/255
            model1 = load_model('my_vggmodel.h5')
            test_features = model1.predict(re_image)
            mode2 = load_model('my_cnnmodel.h5')
            predictions = mode2.predict(test_features)
            pred_labels = np.argmax(predictions, axis = 1)
            ans.append(pred_labels)
            # print(ans)
            # print(pred_labels)
    else:
        return c
        # return "BBBB"
    # print(np.array(ans))
    return np.array(ans)[0]
    # return "Gggg"
# a=int(pred(pathq)[0])
# print(a)