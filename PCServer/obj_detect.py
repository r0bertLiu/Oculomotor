import os
import numpy as np
import tensorflow as tf
import time
from PIL import Image
from yolov3.core.yolo_tiny import YOLOv3_tiny
from yolov3.core.yolo import YOLOv3
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)


def load_class_names(class_names_file):
    """
    Returns a list of string corresonding to class names and it's length
    :param class_names_file: (str) class.name file path
    :return: (list, int) class name list, length of the class list
    """
    with open(class_names_file, 'r') as f:
        class_names = f.read().splitlines()

    return class_names, len(class_names)


class Detector:
    """
    iou_threshold:
    interaction of union, only the boxes with iou score higher than the threshold will be output

    confidence_threshold:
    Only the predicts with confidence higher than threshold will be output

    yolov3_ckpt_path:
    path of weights for YOLOv3

    tiny_ckpt_path:
    path of weights for YOLOv3 Tiny

    class_names_file:
    path of class name file
    """
    def __init__(self, model='yolov3', iou_threshold=0.5, confidence_threshold=0.5,
                 yolov3_ckpt_path='./yolov3//weights/model.ckpt',
                 tiny_ckpt_path='./yolov3/weights/model-tiny.ckpt',
                 class_names_file='./yolov3/data/coco.names'):
        print('Detector: initializing...')
        self.iou_threshold = iou_threshold
        self.confidence_threshold = confidence_threshold
        self.yolov3_ckpt_path = yolov3_ckpt_path
        self.tiny_ckpt_path = tiny_ckpt_path
        self.class_names_file = class_names_file
        self.class_names, self.n_classes = load_class_names(self.class_names_file)

        print('Detector: loading model:', model, '...')
        if model == 'yolov3':
            self.model = YOLOv3(n_classes=self.n_classes,
                                iou_threshold=self.iou_threshold,
                                confidence_threshold=self.confidence_threshold)
        elif model == 'yolov3_tiny':
            self.model = YOLOv3_tiny(n_classes=self.n_classes,
                                     iou_threshold=self.iou_threshold,
                                     confidence_threshold=self.confidence_threshold)
        else:
            print('Error: model name incorrect.')
            exit()

        self.inputs = tf.placeholder(tf.float32, [1, *self.model.input_size, 3])
        self.detections = self.model(self.inputs)
        self.saver = tf.train.Saver(tf.global_variables(scope=self.model.scope))

        print('Detector: loading parameters...')
        self.sess = tf.Session()
        if model == 'yolov3':
            self.saver.restore(self.sess, self.yolov3_ckpt_path)
        elif model == 'yolov3_tiny':
            self.saver.restore(self.sess, self.tiny_ckpt_path)
        else:
            print('Error: model name incorrect.')
            exit()
        print('Detector: loading complate! Ready To Go!')

    def image_preproc(self, np_img):
        """
        resize and increase dimension of the image to fit the model
        :param np_img: (ndarray) image input
        :return: (ndarray) model input
        """
        pil_img = Image.fromarray(np_img)
        pil_img = pil_img.resize(size=self.model.input_size)
        np_img = np.array(pil_img, dtype=np.float32)
        np_img = np.expand_dims(np_img[:, :, :3], axis=0)
        return np_img

    def result_reform(self, orimg, boxes_dict):
        """
        convert detect result into a readable list consists of bounding boxes.
        format:
        [[cls_name_0, confidence_0, x_01, y_01, x_02, y_02],
         [cls_name_1, confodence_2, x_11, y_12, x_11, y_12], ...]
         where x_01, y_01 is the upleft coordinates of the box.
               x_02, y_02 is the bottomright coordinates of the box.
               the original position (0,0) is the upleft corner of the image.

        :param orimg:(ndarray) np_image input to the model
        :param boxes_dict:(dict) detection result[0] from the model
        :return: (list) list consists of bounding boxes information
        """
        result_list = []
        resize_factor = (orimg.shape[1] / self.model.input_size[0], orimg.shape[0] / self.model.input_size[1])
        for cls_num in range(self.n_classes):
            boxes = boxes_dict[cls_num]

            if np.size(boxes) != 0:
                for box in boxes:
                    xy, confidence = box[:4], box[4]
                    for i in range(4):
                        xy[i] *= resize_factor[i % 2]
                    result_list.append([self.class_names[cls_num], confidence,
                                        xy[0], xy[1], xy[2], xy[3]])

        return result_list

    def detect_img(self, np_img):
        """
        detection entrance
        :param np_img: (ndarray) input image in 3d np array format
        :return: (list) list of boxes information
        """
        img = self.image_preproc(np_img)
        result = self.sess.run(self.detections, feed_dict={self.inputs: img})
        return self.result_reform(np_img, result[0])




