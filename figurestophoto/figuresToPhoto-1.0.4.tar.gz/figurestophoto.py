from PIL import Image, ImageDraw, ImageFont

class figures():
    def __init__(self,name):
        self.img = Image.open(name)
        self.idraw = ImageDraw.Draw(self.img)
    
    def squareToJpg(self,a:int,b:int,c:int,d:int,color:str,filename):
        self.idraw.rectangle((a,b,c,d), fill= color)
        img = self.img.convert("RGB")
        img.save(f"{filename}.jpg","jpeg")

    def squareToPng(self,a:int,b:int,c:int,d:int,color:str,filename):
        self.idraw.rectangle((a,b,c,d), fill= color)
        img = self.img.convert("RGBA")
        img.save(f"{filename}.png","png")

    def circleToPng(self,a:int,b:int,c:int,d:int,color:str,filename):
        self.idraw.ellipse((a,b,c,d), fill= color)
        img = self.img.convert("RGBA")
        img.save(f"{filename}.png","png")

    def circleToJpg(self,a:int,b:int,c:int,d:int,color:str,filename):
        self.idraw.ellipse((a,b,c,d), fill= color)
        img = self.img.convert("RGB")
        img.save(f"{filename}.jpg","jpeg")
    
    def polygonToJpg(self,a:int,b:int,c:int,d:int,e: int, f: int, color:str,filename):
        self.idraw.polygon([(a,b),(c,d),(e,f)], fill= color)
        img = self.img.convert("RGB")
        img.save(f"{filename}.jpg","jpeg")

    def polygonToPng(self,a:int,b:int,c:int,d:int,e: int, f: int, color:str,filename):
        self.idraw.polygon([(a,b),(c,d),(e,f)], fill= color)
        img = self.img.convert("RGBA")
        img.save(f"{filename}.png","png")

class canvas():
    def canvasToPng(self,a: int, b:int, color: str,filename):
        img = Image.new("RGBA",(a,b), color)
        img.save(f"{filename}.png","png")

    def canvasToJpg(self,a: int, b:int, color: str,filename):
        img = Image.new("RGB",(a,b), color)
        img.save(f"{filename}.jpg","jpeg")

class text():
    def __init__(self,name):
        self.img = Image.open(name)
        self.idraw = ImageDraw.Draw(self.img)


    def textToPng(self, arg, a: int, b: int, fontSize: int, color: str,filename):
        head = ImageFont.truetype('arial.ttf', size=fontSize)
        text = arg
        self.idraw.text((a,b), text, font=head, fill=color)
        img = self.img.convert("RGBA")
        img.save(f"{filename}.png","png")

    def textToJpg(self, arg, a: int, b: int, fontSize: int, color: str,filename):
        head = ImageFont.truetype('arial.ttf', size=fontSize)
        text = arg
        self.idraw.text((a,b), arg, text, font=head, fill=color)
        img = self.img.convert("RGB")
        img.save(f"{filename}.jpg","jpeg")