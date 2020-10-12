# encoding=utf8
import torch
import os
import random
import cv2
from PIL import Image
import numpy as np
from tqdm import tqdm
from torch.utils import data
from io import BytesIO
from efficientnet_pytorch import EfficientNet
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torchvision import transforms
from albumentations.pytorch import ToTensor
from collections import Counter
from albumentations import (
    HorizontalFlip, IAAPerspective, ShiftScaleRotate, CLAHE, RandomRotate90,
    Transpose, ShiftScaleRotate, Blur, OpticalDistortion, GridDistortion, HueSaturationValue,
    IAAAdditiveGaussianNoise, GaussNoise, MotionBlur, MedianBlur, RandomBrightnessContrast, IAAPiecewiseAffine,
    IAASharpen, IAAEmboss, Flip, OneOf, Compose, Resize
)


class Transform:
    def __init__(self, image_size):
        self.image_size = image_size

    def albumentations_transform(self, image):
        transform = self.strong_aug_Single_category(p=1, image_size=self.image_size)
        image_np = np.array(image)
        augmented = transform(image=image_np)
        image = augmented['image']
        return image

    def strong_aug_Single_category(self, p=1, image_size=None):
        return Compose([
            Resize(image_size[0], image_size[1]),
            # RandomRotate90(),
            # Flip(),
            # Transpose(),
            OneOf([
                IAAAdditiveGaussianNoise(),
                GaussNoise(),
            ], p=0.2),
            OneOf([
                MotionBlur(p=.2),
                MedianBlur(blur_limit=3, p=0.1),
                Blur(blur_limit=3, p=0.1),
            ], p=0.2),
            ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.2, rotate_limit=45, p=0.2),
            OneOf([
                OpticalDistortion(p=0.3),
                GridDistortion(p=.1),
                IAAPiecewiseAffine(p=0.3),
            ], p=0.2),
            OneOf([
                CLAHE(clip_limit=2),
                IAASharpen(),
                IAAEmboss(),
                RandomBrightnessContrast(),
            ], p=0.3),
            HueSaturationValue(p=0.3),
            ToTensor()
        ], p=p)

    def transform_model(self, model='single',test_model=False, mean=(), std=()):
        if model.lower() == 'single':
            if test_model:
                transform = transforms.Compose([
                    transforms.Resize(self.image_size),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=mean, std=std)
                ])
            else:
                transform = transforms.Compose([
                    transforms.Lambda(self.albumentations_transform),
                    transforms.Normalize(mean=mean, std=std)
                ])
        elif model.lower() == 'multiple':
            transform = transforms.Compose([
                transforms.Resize(self.image_size),
                transforms.ToTensor(),
                transforms.Normalize(mean=mean, std=std)
            ])
        else:
            raise TypeError('please choice a train type! "multiple" or "single"')
        return transform


class MydataSet():
    def __init__(self, images_path, transform, encode_list, train_class_len, classification_scheme, size):
        self.images_path_list = [os.path.join(images_path, i) for i in os.listdir(images_path)]
        self.encode_list = encode_list
        self.train_class_len = train_class_len
        self.transform = transform
        self.classification_scheme = classification_scheme
        self.image_size = size

    def __getitem__(self, item):
        path = self.images_path_list[item]
        image = Image.open(path)
        image = image.convert('RGB')
        image = self.transform(image)
        name = os.path.basename(path).replace('.jpg', '').replace('.png', '').split('_')[0]
        label = [self.encode_list[i] for i in name]
        if self.classification_scheme.lower() == 'single':
            label = label[0]
            return image, label
        label2 = torch.tensor(label, dtype=torch.long)
        eye = torch.eye(self.train_class_len)
        ret = eye[label2]
        label = ret.view(-1)
        return image, label

    def __len__(self):
        return len(self.images_path_list)

    def load(self, path_or_bytes, size=None):
        """
        加载图片
        :param path_or_bytes: 图片目录 / 字节
        :param size: 缩放图片 (width, height)
        :return: 图片 np.array (height, width, dim)
        """
        # path_or_bytes = Image.open(path_or_bytes).convert('RGB')
        # cv2.imread(img_path)
        # im = np.array(path_or_bytes)
        # return im
        if isinstance(path_or_bytes, str):
            im = np.fromfile(path_or_bytes, dtype=np.uint8)
        elif isinstance(path_or_bytes, bytes):
            im = np.frombuffer(path_or_bytes, dtype=np.uint8)
        else:
            raise TypeError("image must be path or bytes")
        im = cv2.imdecode(im, -1)
        if size is not None:
            im = cv2.resize(im, size, interpolation=cv2.INTER_AREA)
        return im

    def get_mean_std(self):
        mean = np.array([0, 0, 0], dtype=np.float)
        std = np.array([0, 0, 0], dtype=np.float)
        for i in tqdm(range(len(self)), desc="Evaluating Mean & Std"):
            if len(self) > 100000:
                if i > 100000: break
                im = self.load(random.choice(self.images_path_list))
            else:
                im = self.load(self.images_path_list[i])
            im = im.astype(np.float32) / 255.
            for j in range(3):
                mean[j] += im[:, :, j].mean()
                std[j] += im[:, :, j].std()
        mean, std = mean / len(self), std / len(self)
        mean = tuple(eval(','.join(str(mean).replace("  ", " ").split(' '))))
        std = tuple(eval(','.join(str(std).replace("  ", " ").split(' '))))
        return mean, std


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class Train_Captcha:
    def __init__(self,
                 images_train_path: str = None,
                 images_test_path: str = None,
                 train_class: str or list = None,
                 image_size: tuple = (60, 60),
                 batch_size: int = 64,
                 Max_length: int = 1,
                 Model_name: str = 'test.model',
                 test_model: bool = False,
                 train_continue: bool = True,
                 show_train_images_demo: int = 10,
                 Normalize: bool = True
                 ):
        '''
        :param images_path: 训练图片文件夹路径
        :param train_class: 训练类别
        :param Max_length: 单个验证码标签最大长度
        :param Model_name: 模型保存路径
        '''
        # train_class -> number
        if Max_length == 1:
            classification_scheme = 'single'
        else:
            classification_scheme = 'multiple'
        if isinstance(train_class, list):
            train_class = train_class
        elif isinstance(train_class, str):
            train_class = list(train_class)
        else:
            raise TypeError('train_class must be list or str !')
        # number -> train_class
        self.decode_list = dict(zip(range(0, len(train_class)), train_class))
        self.train_class_len = len(train_class)
        self.Max_length = Max_length
        self.classification_scheme = classification_scheme
        self.image_size = image_size
        self.Model_name = Model_name
        self.images_test_path = images_test_path
        if Normalize:
            mean, std = MydataSet(images_train_path, None, None, self.train_class_len, classification_scheme,
                                  image_size).get_mean_std()
        else:
            # mean,std = [0.485, 0.456, 0.406],[0.229, 0.224, 0.225] #常用均方差
            mean, std = [0.471, 0.448, 0.408], [0.234, 0.239, 0.242]  # 常用均方差
        print(f'mean: {mean} std: {std}')
        self.transform = Transform(image_size=image_size).transform_model(model=classification_scheme,test_model=test_model, mean=mean,
                                                                          std=std)
        if not test_model:
            self.encode_list = dict(zip(train_class, range(0, len(train_class))))
            self.images_path = images_train_path
            train_data = MydataSet(images_train_path, self.transform, self.encode_list, self.train_class_len,
                                   classification_scheme, image_size)
            self.train_data_loader = torch.utils.data.DataLoader(train_data, batch_size=batch_size, shuffle=True,
                                                                 num_workers=0,
                                                                 pin_memory=True)
            images_train_path_len = len(os.listdir(images_train_path))
            if show_train_images_demo and show_train_images_demo != 0:
                import cv2, random
                for i in [random.randint(1, images_train_path_len) for _ in range(show_train_images_demo)]:
                    im, _ = train_data.__getitem__(i)
                    cv2.imshow("128x128", im.permute(1, 2, 0).detach().numpy())
                    cv2.waitKey()

            if images_test_path:
                test_data = MydataSet(images_test_path, self.transform, self.encode_list, self.train_class_len,
                                      classification_scheme, image_size)
                self.test_data_loader = torch.utils.data.DataLoader(test_data, batch_size=16, shuffle=False,
                                                                    num_workers=0, pin_memory=True)

        self.model = EfficientNet.from_pretrained('efficientnet-b4').to(device)
        in_fea = self.model._fc.in_features
        self.model._fc = torch.nn.Linear(in_features=in_fea, out_features=self.train_class_len * Max_length,
                                         bias=True).to(device)
        if test_model:
            self.model.load_state_dict(torch.load(Model_name, map_location=torch.device(device)))
            self.model.eval()
        if train_continue:
            try:
                self.model.load_state_dict(torch.load(Model_name))
                print(f"loading {Model_name} model Successful，continue training based on the model!")
            except:
                print(f"loading {Model_name} model failed. Train from the beginning!")
        if classification_scheme.lower() == 'single':
            self.loss_func = torch.nn.CrossEntropyLoss()
        elif classification_scheme.lower() == 'multiple':
            self.loss_func = torch.nn.MultiLabelSoftMarginLoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        print(
            f"【pre training model】: efficientnet-b4 【model_name】: {self.Model_name} 【train_type】: {classification_scheme} 【Max_length】: {Max_length} 【image_size】: {image_size} 【batch_size】: {batch_size}")

    def decode(self, tgt):
        tgt = tgt.view(self.Max_length, self.train_class_len)
        idx = tgt.max(1)[1]
        ret = []
        for i in idx:
            num = self.decode_list[i.item()]
            ret.append(str(num))
        return ''.join(ret)

    def train(self):
        scheduler = ReduceLROnPlateau(self.optimizer, 'max', patience=3, min_lr=0.00001)
        loss = None
        for epoch in range(200000):
            bar = tqdm(self.train_data_loader)
            for i, (image, label) in enumerate(bar):
                # 获取最后输出
                out = self.model(image.to(device))  # torch.Size([128,10])
                # 获取损失
                loss = self.loss_func(out, label.to(device))
                # 使用优化器优化损失
                self.optimizer.zero_grad()  # 清空上一步残余更新参数值
                loss.backward()  # 误差反向传播，计算参数更新值
                self.optimizer.step()  # 将参数更新值施加到net的parmeters上
                lr = self.optimizer.param_groups[0]['lr']
                bar.set_description("Train epoch %d, loss %.4f, lr %.6f" % (
                    epoch, loss.detach().cpu().numpy(), lr
                ))
            acc = None
            if self.images_test_path:
                correct = 0
                total = 0
                bar = tqdm(self.test_data_loader, 'Validating')
                for image, labels in bar:
                    out = self.model(image.to(device))
                    for i in range(out.shape[0]):
                        total += 1
                        pred = self.decode(out[i])
                        if self.classification_scheme.lower() == 'single':
                            label = self.decode_list[labels[i]]
                        else:
                            label = self.decode(labels[i])
                        if pred == label:
                            correct += 1
                        print(f"predict: {pred}  true: {label}")
                    loss = self.loss_func(out, labels.to(device))
                    lr = self.optimizer.param_groups[0]['lr']
                    acc = correct / total
                    bar.set_description("Valid epoch %d, acc %.4f, loss %.4f, lr %.6f" % (
                        epoch, acc, loss.detach().cpu().numpy(), lr
                    ))
            scheduler.step(loss)
            torch.save(self.model.state_dict(), self.Model_name)
            if acc and acc > 0.95:
                break

    def predecit(self, images):
        if isinstance(images, bytes):
            images = BytesIO(images)
        img = Image.open(images)
        image = img.convert('RGB')
        img = self.transform(image).unsqueeze(0)
        out = self.model(img.to(device))
        pred = self.decode(out[0])
        return pred


if __name__ == '__main__':
    # encoding=utf8
    from CNN.CnnNetModule import Train_Captcha
    chinese = []
    # multiple:训练定长验证码1个字符以上 Max_length>=1   single：训练单个字符验证码 Max_length=1
    s = Train_Captcha(
        images_train_path=r'D:\data\dx\1',
        images_test_path=r'D:\data\dx\1',
        image_size=(50, 50),
        Max_length=1,
        batch_size=32,
        Model_name='test4.pt',
        train_class=chinese,
        classification_scheme='single',
        test_model=True,
        train_continue=False,
        show_train_images_demo=False
    )
    s.train()
    m = s.predecit(r'D:\Captcha_Net\CNN\1.jpg')
    print(m)




