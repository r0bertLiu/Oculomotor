import numpy as np
from PIL import Image
from obj_detect import Detector
import time
import os
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)



# open image as ndarray
img_dir = '/home/zx/comp9900/code/2.jpg'
img = Image.open(img_dir)
img = np.array(img)


# initialize a new Detector object
# model = 'yolov3' or 'yolov3_tiny'
detector = Detector(model='yolov3')

# make detection 100 times on same image and print out prcess speed in frame per second.
for _ in range(100):
    t = time.time()
    result = detector.detect_img(img)
    os.system('clear')
    print('fps: ', 1 / (time.time()-t))

# print out result
print(result)
