# -*- coding: utf-8 -*-
'''
@Time          : 2020/04/26 15:48
@Author        : Tianxiaomo
@File          : camera.py
@Noice         :
@Modificattion :
    @Author    :
    @Time      :
    @Detail    :

'''
from __future__ import division
import cv2
import argparse
from Yolov4_KL_demo.tool.utils import *
from Yolov4_KL_demo.tool.torch_utils import *
from easydict import EasyDict
from Yolov4_KL_demo.models import Yolov4, Yolov4_KL


def arg_parse():
    """
    Parse arguements to the detect module

    """

    # parser = argparse.ArgumentParser(description='YOLO v3 Cam Demo')
    # parser.add_argument("--confidence", dest="confidence", help="Object Confidence to filter predictions", default=0.25)
    # parser.add_argument("--nms_thresh", dest="nms_thresh", help="NMS Threshhold", default=0.4)
    # parser.add_argument("--reso", dest='reso', help=
    # "Input resolution of the network. Increase to increase accuracy. Decrease to increase speed",
    #                     default="160", type=str)
    # args = parser.parse_args()

    args = EasyDict()

    arguments = {
        # 'video_file'        : '../data/videos/gta/fir_2.mp4',
        'video_file'        : '../data/videos/bdd/bdd_4.mov',
        # 'video_file'        : '../data/videos/Breaking Bad Trailer (First Season).avi',
        # 'weightsfile'         : "../weights/yolov4.pth",
        'weightsfile'        : "../weights/bdd/kl/good_models/Yolov4_epoch14.pth",
        # 'weightsfile'       : "../checkpoints/kl/bdd/3e4_new/Yolov4_epoch9.pth",
        'confidence'        : 0.15,
        'nms_thresh'        : 0.4,
        'reso'              : '608',
        'height'            : 416,
        'width'             : 416,
        'num_classes'       : 10,
        'kl'                : True,
        'class_names_path'  : '../data/bdd.names'
    }

    args.update(arguments
                )
    return args


if __name__ == '__main__':
    cfgfile = "../cfg/yolov4.cfg"

    args = arg_parse()
    weightsfile = args.weightsfile
    confidence = float(args.confidence)
    nms_thesh = float(args.nms_thresh)
    CUDA = torch.cuda.is_available()
    bbox_attrs = 5 + args.num_classes
    class_names = load_class_names(args.class_names_path)

    # model = Darknet(cfgfile)
    # model.load_weights(weightsfile)

    if args.kl:
        get_vars = True
        model = Yolov4_KL(yolov4conv137weight=None, n_classes=args.num_classes, inference=True, get_vars=get_vars)
    else:
        model = Yolov4(yolov4conv137weight=None, n_classes=args.num_classes, inference=True)


    pretrained_dict = torch.load(weightsfile, map_location=torch.device('cuda'))
    model.load_state_dict(pretrained_dict)

    if CUDA:
        model.cuda()

    model.eval()
    # cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture(args.video_file)
    cap.set(3, 1080)
    cap.set(4, 1920)

    assert cap.isOpened(), 'Cannot capture source'

    frames = 0
    start = time.time()
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            if args.video_file.endswith('mov'):
                frame = np.swapaxes(frame, 0, 1)
                frame = cv2.flip(frame, 0)
            sized = cv2.resize(frame, (args.width, args.height))
            sized = cv2.cvtColor(sized, cv2.COLOR_BGR2RGB)
            boxes = do_detect(model, sized, 0.5, 0.4, CUDA)

            if args.kl and get_vars:
                orig_im = plot_boxes_cv2_kl(frame, boxes[0], class_names=class_names)
            else:
                orig_im = plot_boxes_cv2(frame, boxes[0], class_names=class_names)


            cv2.imshow("frame", orig_im)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
            frames += 1
            print("FPS of the video is {:5.2f}".format(frames / (time.time() - start)))
        else:
            break
