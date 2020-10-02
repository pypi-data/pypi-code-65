from PIL import Image

class imascii():
    def __init__(self, path, file_name='out', new_width=100):
        self.path = path
        self.ASCII_CHARS = ['@', '#', '$', '%', '?', "*", "+", ";", ":", ',', '.']
        self.new_width = new_width
        self.file_name = file_name

    def resize_image(self, image):
        width, height = image.size
        ratio = height/width
        new_height = int(self.new_width*ratio)
        resize_image = image.resize((self.new_width, new_height))
        return resize_image

    def convet_to_gray_scale(self, image):
        gray_image = image.convert("L")
        return gray_image

    def pix_toAscii(self, image):
        pixels = image.getdata()
        characters = "".join([self.ASCII_CHARS[pixel//25] for pixel in pixels])
        return characters

    def convert(self):
        try:
            image = Image.open(self.path)
        except Exception as e:
            return e
        new_image_data = self.pix_toAscii(self.convet_to_gray_scale(self.resize_image(image)))
        pixel_count = len(new_image_data)
        img_array = (new_image_data[i:(i+self.new_width)] for i in range(0, pixel_count, self.new_width))
        ascii_image = "\n".join(img_array)
        
        with open(f"{self.file_name}.txt", "w") as f:
            f.write(ascii_image)

