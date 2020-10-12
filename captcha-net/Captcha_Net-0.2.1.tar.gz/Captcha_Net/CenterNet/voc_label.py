import xml.etree.ElementTree as ET
import os,shutil
import json

classes = ['target']  # 自己训练的类别

def convert(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)

def convert_annotation(image_id,xml_path):
    in_file = open(f'{xml_path}/%s.xml' % (image_id),encoding='utf8')
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    if w!=0:
        for obj in root.iter('object'):
            difficult = obj.find('difficult').text
            cls = obj.find('name').text
            cls = 'target'
            if cls not in classes or int(difficult) == 1:
                continue
            cls_id = classes.index(cls)
            xmlbox = obj.find('bndbox')
            b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text),
                 float(xmlbox.find('ymax').text))
            print(b)
            print(image_id)
            save_path = os.path.join(labels_save_path,image_id+'.txt')
            with open(save_path,'a')as f:
                f.write(json.dumps(b,ensure_ascii=False)+'\n')

def main(images_path,xml_path,labels_save_path):
    images_unuse = os.path.join(os.path.dirname(images_path), 'unuseimages')
    if not os.path.exists(labels_save_path):
        os.mkdir(labels_save_path)
    xml_list = [i.replace('.jpg', '').replace('.png', '').replace('.xml', '') for i in os.listdir(xml_path)]
    for images in os.listdir(images_path):
        images_name = images.replace('.jpg', '').replace('.png', '').replace('.xml', '')
        if images_name not in xml_list:
            if not os.path.exists(images_unuse):
                os.mkdir(images_unuse)
            shutil.move(os.path.join(images_path, images), images_unuse)
            print(f'{images} 图片移动至 {images_unuse} 目录！')

    for xmlid in xml_list:
        convert_annotation(xmlid, xml_path)


if __name__ == '__main__':
    images_path = r'C:\Users\admin\Desktop\test\images'
    xml_path = r'C:\Users\admin\Desktop\test\xml'
    labels_save_path = r'labels'
    main(images_path,xml_path,labels_save_path)






