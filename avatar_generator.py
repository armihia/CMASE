import copy
import os
import random
import re

import numpy as np
from PIL import Image

import matplotlib.pyplot as plt

class Avatar_generator:
    def __init__(self):
        self.base_url = "./source material/agent/TV/"
        self.gradients = Image.open("./source material/agent/gradients.png").convert("RGB")

        self.require_param = {"gender": ["Male", "Female"],"skin tone":["light skin tone","medium skin tone","dark skin tone"]}
        self.order=[["Body"],["Clothing1"],['RearHair1',"FrontHair1"]]
        self.optional_order = [["AccA"],["AccB"],["Glasses"]]
        self.optional_rate=0.2
        self.body_color = {"light skin tone": [[245, 255], [210, 230], [190, 210]],
            "medium skin tone": [[220, 240], [180, 200], [140, 160]],
             "dark skin tone": [[80, 100], [50, 70], [30, 50]]}

    def random_color(self,body=""):
        if(body!=""):
            while (True):
                r = random.randint(self.body_color[body][0][0], self.body_color[body][0][1])
                g = random.randint(self.body_color[body][1][0], self.body_color[body][1][1])
                b = random.randint(self.body_color[body][2][0], self.body_color[body][2][1])

                if (r > 80 and g > 40 and b > 30) and (r > g and r > b) and (r - g > 15):
                    break
            color = (r, g, b)
        else:
            width, height = self.gradients.size

            random_x = random.randint(0, width - 1)
            random_y = random.randint(0, height - 1)

            color = self.gradients.getpixel((random_x, random_y))

        return color

    def color_change(self, original, color_mask, color):
        original = original.convert("RGBA")
        color_mask = color_mask.convert("RGB")

        result = Image.new("RGBA", original.size)

        for x in range(original.width):
            for y in range(original.height):
                r_orig, g_orig, b_orig, a_orig = original.getpixel((x, y))
                r_mask, g_mask, b_mask = color_mask.getpixel((x, y))

                new_color = (r_orig - r_mask + color[0], g_orig - g_mask + color[1], b_orig - b_mask + color[2], a_orig)

                result.putpixel((x, y), new_color)

        return result

    def generate_avatar(self,param,avatar_param=None):
        require_check=False
        for p in self.require_param.keys():
            try:
                param[p]=self.require_param[p][[i.lower() for i in self.require_param[p]].index(param[p].lower())]
            except:
                require_check = True
                break
        if(require_check):
            print("Required parameters are missing")
            return None

        if(avatar_param==None):
            avatar_param={}

        url=self.base_url+param["gender"]
        data={}
        for root, dirs, files in os.walk(url):
            for file in files:
                file_0=file.split("_")
                if(file_0[-1]!="c.png"):
                    try:
                        data[file_0[1]].append(os.path.join(root, file))
                    except:
                        data[file_0[1]]=[os.path.join(root, file)]

        img = Image.new('RGBA', (144, 192), (0,0,0,0))
        if("order" in avatar_param.keys()):
            order=avatar_param["order"]
        else:
            order=copy.copy(self.order)
            for o in self.optional_order:
                if(random.random()<self.optional_rate):
                    order.append(o)
        avatar_param["order"]=order

        for t1 in order:
            color=self.random_color()
            for t in t1:
                if(t+"_color" in avatar_param.keys()):
                    color=avatar_param[t+"_color"]
                avatar_param[t + "_color"]=color

                if(t=="Body"):
                    color = self.random_color(body=param["skin tone"])
                if (len(data[t]) != 0):
                    material_url = random.choice(data[t])
                    if(t in avatar_param.keys()):
                        for i in data[t]:
                            if(avatar_param[t] in i):
                                material_url = i


                    t_list = [material_url]

                    avatar_param[t]=material_url.split("\\")[-1]
                    try:
                        t_n=int(re.findall(r'\d+', t)[-1])
                        t_text = t.replace(str(t_n), "")
                        while(True):
                            t_n += 1
                            t_tmp = t_text + str(t_n)
                            tmp_url=material_url.replace(t,t_tmp)
                            if(t_tmp in data.keys() and tmp_url in data[t_tmp]):
                                t_list.append(tmp_url)
                                avatar_param[t_tmp] = tmp_url.split("\\")[-1]
                            else:
                                break
                    except:
                        pass

                    for url in t_list:
                        material=self.color_change(Image.open(url),Image.open(url.replace(".png","_c.png")),color)
                        img=Image.alpha_composite(img, material)

        return (img,avatar_param)

    def show(self,img):
        plt.figure()
        ax = plt.subplot(1, 1, 1)
        ax.imshow(img)
        plt.show()


# param={"gender":"female","skin tone":"medium skin tone"}
# avatar_param={'Body': 'TV_Body_p01.png', 'Clothing1': 'TV_Clothing1_p08.png', 'RearHair1': 'TV_RearHair1_p08.png', 'RearHair2': 'TV_RearHair2_p08.png', 'FrontHair1': 'TV_FrontHair1_p11.png', 'FrontHair2': 'TV_FrontHair2_p11.png', 'Body_color': (243, 243, 240), 'Clothing1_color': (237, 231, 227), 'RearHair1_color': (125, 135, 64), 'FrontHair1_color': (125, 135, 64), 'order': [['Body'], ['Clothing1'], ['RearHair1', 'FrontHair1'], ['Glasses']], 'Glasses_color': (180, 206, 225), 'Glasses': 'TV_Glasses_p04.png'}
# avatar_param=None
# ag=Avatar_generator()
# img,avatar_param=ag.generate_avatar(param,avatar_param)
# print(avatar_param)
# ag.show(img)
