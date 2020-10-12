import torch
from torch.utils.data import DataLoader
from tqdm import tqdm
from deeplearning_tools.networks import centernet
from deeplearning_tools.utils.image import to_rgb
from deeplearning_tools.utils import box as bounding_box
import torchvision.transforms as T
import torch.nn.functional as F
import numpy as np
import cv2

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

IMAGE_WIDTH_HEIGHT = 256
STRIDE = 4
HM_WIDTH_HEIGHT = IMAGE_WIDTH_HEIGHT / STRIDE

class CenterPosition():
    def __init__(self,image_size=(256,256),images_path=None,images_txt=None,batch_size=64,model_name='test.model',test_model=True):
        self.transform = T.Compose([
            to_rgb,
            T.ToPILImage(),
            T.Resize(image_size),
            T.ToTensor(),
        ])
        self.model_name = model_name
        if not test_model:
            train_set = centernet.dataset.CenterNetDataset(
                path=images_path,
                path_txt=images_txt,
                transform=self.transform
            )
            self.train_loader = DataLoader(dataset=train_set, batch_size=batch_size, shuffle=True, num_workers=2)
        if test_model:
            self.model = centernet.model.CenterNet()
            self.model.load_state_dict(torch.load(self.model_name,map_location=torch.device(device)))
            self.model = self.model.to(device)
            self.model.eval()  # 转入测试模式, 更新BN计算方法
        # import cv2
        # im, _, _, _ = train_set.__getitem__(2)
        # cv2.imshow("128x128", im.permute(1, 2, 0).detach().numpy())
        # cv2.waitKey()
        # exit()

    def train(self):
        model = centernet.model.CenterNet()
        model.load_state_dict(torch.load(self.model_name,map_location=torch.device(device)))
        model = model.to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        reg_loss = centernet.loss.RegL1Loss()
        focal_loss = centernet.loss.FocalLoss()
        for epoch in range(0, 10000):
            bar = tqdm(self.train_loader, 'Training')
            try:
                for image, hm, ltrb, ltrb_mask in bar:
                    image = image.to(device)
                    hm = hm.to(device)
                    ltrb = ltrb.to(device)
                    ltrb_mask = ltrb_mask.to(device)
                    # print(image)
                    predict = model(image)
                    predict_hm, predict_ltrb = torch.split(predict, [1, 4], 1)
                    loss0 = reg_loss(predict_ltrb, ltrb, ltrb_mask)
                    loss1 = focal_loss(predict_hm, hm)
                    loss = loss0 + loss1
                    # 快乐三步曲
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                    lr = optimizer.param_groups[0]['lr']
                    bar.set_description("Train epoch %d, loss %.4f, lr %.6f" % (
                        epoch, loss.detach().cpu().numpy(), lr
                    ))
                    # predict_hm_slice = predict_hm[0].cpu().squeeze().detach().numpy()
                    # cv2.imshow("HeatMap", predict_hm_slice)
                    # cv2.waitKey(10)
            except Exception as e:
                print(e)
            torch.save(model.state_dict(),self.model_name)

    def load(self,path_or_bytes, size=None):
        """
        加载图片
        :param path_or_bytes: 图片目录 / 字节
        :param size: 缩放图片 (width, height)
        :return: 图片 np.array (height, width, dim)
        """
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

    def predict(self,bytes=None,show_images=True):
        img1 = self.load(bytes)
        img1 = self.transform(img1).unsqueeze(0)
        image = img1.to(device)
        predict = self.model(image)
        predict_hm, predict_ltrb = torch.split(predict, [1, 4], 1)
        # MaxPool
        predict_hm_pool = F.max_pool2d(predict_hm, 3, 1, 1)
        points = (predict_hm_pool.flatten() > 0.4).nonzero().flatten()
        boxes = []
        for point in points:
            x = point % HM_WIDTH_HEIGHT
            y = point // HM_WIDTH_HEIGHT
            ltrb = predict_ltrb[0, :, int(y), int(x)]
            l, t, r, b = (
                int(x / HM_WIDTH_HEIGHT * IMAGE_WIDTH_HEIGHT - ltrb[0] / HM_WIDTH_HEIGHT * IMAGE_WIDTH_HEIGHT),
                int(y / HM_WIDTH_HEIGHT * IMAGE_WIDTH_HEIGHT - ltrb[1] / HM_WIDTH_HEIGHT * IMAGE_WIDTH_HEIGHT),
                int(x / HM_WIDTH_HEIGHT * IMAGE_WIDTH_HEIGHT + ltrb[2] / HM_WIDTH_HEIGHT * IMAGE_WIDTH_HEIGHT),
                int(y / HM_WIDTH_HEIGHT * IMAGE_WIDTH_HEIGHT + ltrb[3] / HM_WIDTH_HEIGHT * IMAGE_WIDTH_HEIGHT)
            )
            box = (l, t, r, b)
            boxes.append(box)
        if not boxes:return
        boxes = bounding_box.nms(boxes)
        if show_images:
            draw_image = image[0].permute(1, 2, 0).cpu().detach().numpy()
            draw_image = bounding_box.draw_boxes(draw_image, boxes)
            cv2.imshow("Visualize", draw_image)
            cv2.waitKey(0)
        return boxes

if __name__ == '__main__':
    k = CenterPosition(image_size=(256,256),images_path=None,images_txt=None,batch_size=64,model_name='test.model',test_model=True)
    #训练
    k.train()
    #调用
    k.predict('1.jpg')

