
from mgocr.detection import init_easyocr, load_data, batch_predict
from mgocr.cnocr import CnOcr
from mgocr.cnocr.detect_result import *
import time
from glob import glob
from easyocr.detection import get_detector, get_textbox
from easyocr.imgproc import loadImage
import os
import datetime
import cv2

os.environ['MXNET_CUDNN_AUTOTUNE_DEFAULT'] = '0'
detector = init_easyocr(model_path='./model/craft_mlt_25k.pth', context='cuda')
recognizer = CnOcr(model_name='densenet-lite-gru', context = 'gpu')

def detect(video_dir, key_word):
    pre_dataloaders, org_image_list = load_data(video_dir + '/*', 8, 20)

    begin = time.time()

    text_boxs = batch_predict(detector, pre_dataloaders, 0.7, 0.1, 0.4, False, 'cuda')

    index_result = []
    index_around_result = []
    index = 1
    video_result = []
    for img, text_box in zip(org_image_list, text_boxs):
        print('processing index ', index)
        img_result = {}
        res_result = ''
        for rect in text_box:
            if rect[1] >= rect[5] or rect[0] >= rect[4]:
                continue
            part_img = img[rect[1]:rect[5], rect[0]:rect[4],:]

            if part_img.shape[0] == 0 or part_img.shape[1] == 0:
                continue

            res = recognizer.ocr_for_single_line(part_img)
        
            if res == None:
                continue
        
            if ('刷宝' in res.result) or ('宝藏' in res.result):
                index_result.append(index)
            if ('刷' in res.result) or ('宝' in res.result):
                index_around_result.append(index)

            res_result = res_result + ' ' + res.result
        img_result['index'] = index
        img_result['img_result'] = res_result
        video_result.append(img_result)
        index = index + 1

    end = time.time()
    print("gpu times = ", end - begin)
    return index_result, video_result, index_around_result

if __name__ == '__main__':
    '''
        # ['7690170','7649182','7607348','7568493','7806659','7568493','7846118','7893729','7941325','7987338','8039015','8151700','8205793'] 朋友请听好
        # ['7393555','7420672','7452407','7550197','7589173','7629818','7671011','7712092','7752036','7789032','7831075','7872953','7919446','7964953','8010955','8069719','8125268','8181866','8233482'] 快乐大本营
        # ['7397109','7423700','7452752','7474281','7494990','7523851','7555246','7594196','7635340','7675732','7717605','7756565','7793888','7833156','7876992','7924999','7971424','8021565','8077728','8132615','8187814','8240281'] 天天向上

    '''
# 7589173
    # vid_list = ['7690170','7649182','7607348','7568493','7806659','7568493','7846118','7893729','7941325','7987338','8039015','8151700','8205793', '7393555','7420672','7452407','7550197','7589173','7629818','7671011','7712092','7752036','7789032','7831075','7872953','7919446','7964953','8010955','8069719','8125268','8181866','8233482','7397109','7423700','7452752','7474281','7494990','7523851','7555246','7594196','7635340','7675732','7717605','7756565','7793888','7833156','7876992','7924999','7971424','8021565','8077728','8132615','8187814','8240281'] 
    # vid_list = [8077728]
    vid_list = [5729907]
    total_result = []
    for vid in vid_list:
        index_result, video_result, index_around_result = detect('./data/{}'.format(str(vid)), '刷宝')
        result = {}
        result['vid'] = vid
        result['index_result'] = index_result
        result['index_around_result'] = index_around_result
        result['video_result'] = video_result
        f = open('./result_log.txt', 'a')
        f.write(str(result))
        f.write('\n')
        f.close()



# @app.route('/ocrdetect', methods=['POST'])
# def index():
#     try:
#         if not request.json:
#             abort(400)

#         logger.info('Input Request: {}'.format(str(request.json)))
#         json_obj = request.json
#         executor.submit(detect, json_obj)
#         return jsonify({"msg": "sucess get the task"}),200

#     except Exception as ex:
#         print(ex)
#         abort(400)
#         pass


# def detect_imgs(img_directory_path):
#     pre_dataloaders, org_image_list = load_data(img_path, 8, 20)
#     text_boxs = batch_predict(detector, pre_dataloaders, 0.7, 0.1, 0.4, False, 'cuda')

#     result = []
#     for img, text_box in zip(org_image_list, text_boxs):
#         for rect in text_box:
#             if rect[1] >= rect[5] or rect[0] >= rect[4]:
#                 continue
#             part_img = img[rect[1]:rect[5], rect[0]:rect[4],:]
        
#             res = recognizer.ocr_for_single_line(part_img)
        
#             if res == None:
#                 continue
#             result.append(res.result)
#     return result

# def detect_img(json_obj):
#     img_path = json_obj['imgpath']
#     result = []
#     img = loadImage(img_path)
#     text_box = get_textbox(detector, img, 2560, 1., 0.7,\
#                                     0.01, 0.4, False, 'cuda')
#     image = cv2.imread(img_path)
#     for rect in text_box:
#         part_img = image[rect[1]:rect[5], rect[0]:rect[4],:]
#         res = recognizer.ocr_for_single_line(part_img)
#         result.append(res.result)
#     return result

# def post_result(result):
#     send_json = {}
#     send_json['result'] = result
#     headers ={
#                'Content-Type': 'application/json'
#              }
#     json_data = json.dumps(send_json)

#     print(json_data)
#     logger.info('Result: {}'.format(str(json_data)))

#     response = requests.post(url = "http://10.200.12.152:8088/vrs/api/v1/mosaic/record/positionResult",
#                              headers = headers,
#                              data = json_data)
