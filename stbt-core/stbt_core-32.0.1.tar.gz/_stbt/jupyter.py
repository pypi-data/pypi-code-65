import cv2

from .imgutils import load_image


def imshow(img):
    from IPython.core.display import Image, display
    img = load_image(img)
    _, data = cv2.imencode('.png', img)
    display(Image(data=bytes(data.data), format='png'))
