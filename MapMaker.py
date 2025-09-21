import random
import re

import pygame
import numpy as np
import os
import dill
import copy

from popup import Popup

popup=Popup()
pygame.init()

def create_random_index(raw_list=None):
    n=str(random.random()).split(".")[1]
    if(raw_list==None):
        raw_list=[]
    while(True):
        if (n not in raw_list):
            break
        n=str(random.random()).split(".")[1]
    return n

class UI:
    def __init__(self,name):
        self.name = name
        self.w=48
        self.h = 48
        self.x=0
        self.y=0
        self.ratio=1
        self.material = pygame.image.load(r"./source material/base/base.png")  # .convert_alpha()
        self.shape=(1,1)
        self.submaterials={}
        self.submaterials_index={}

    def resize(self,scale):
        size=self.material.get_size()

        self.shape=(int(size[0]/24),int(size[1]/24))
        self.ratio=int(self.shape[1] / self.shape[0])

        self.w,self.h=size
        if(self.ratio>1):
            self.w=self.w/self.h*scale
            self.h = scale
        elif (self.ratio < 1):
            self.h = self.h / self.w * scale
            self.w = scale
        else:
            self.w=scale
            self.h=scale
        self.material=pygame.transform.scale(self.material, (self.w,self.h))

        if (self.shape[0] != 1 or self.shape[1]!=1):

            base_len=self.material.get_size()[0]/self.shape[0]#min(self.material.get_size()[0],self.material.get_size()[1])
            for i in range(self.shape[0]):
                for j in range(self.shape[1]):
                    subsurface = self.material.subsurface((i*base_len, j*base_len, base_len, base_len))
                    k=str(i)+"-"+str(j)
                    index=len(self.submaterials)
                    self.submaterials[index] = subsurface
                    self.submaterials_index[index]=k

    def get_submaterials_index(self,i,j):
        k = str(i) + "-" + str(j)
        for key, value in self.submaterials_index.items():
            if value == k:
                return key
        return None

    def pos(self,pos):
        self.x=pos[0]
        self.y=pos[1]

    def collidepoint(self,pos):
        if(pos[0]>=self.x and pos[0]<=self.x+self.w and pos[1]>=self.y and pos[1]<=self.y+self.h):
            return True
        else:
            return False

class ObjArray:
    def __init__(self):
        self.elem=[]

    def get_elem(self,num=None,name=None):
        if(num!=None):
            for e in self.elem:
                if(e.num==num):
                    return e
        elif (name != None):
            for e in self.elem:
                if (e.name == name):
                    return e
        else:
            return None
        return None

class Tool(UI):

    def __init__(self,name,num):
        super().__init__(name)
        self.num = num
        self.material = pygame.image.load(r"./source material/ui/" + self.name + ".png")#.convert_alpha()


class Tools(ObjArray):
    def __init__(self):
        super().__init__()

    def add(self,name):
        self.elem.append(Tool(name,len(self.elem)))

class Block:
    def __init__(self,name,num):
        self.name=name
        self.num=num
        self.material=pygame.image.load(r"./source material/base/"+self.name+".png")#.convert_alpha()

    def copy(self):
        return Block(self.name,self.num)

class Blocks(ObjArray):
    def __init__(self):
        super().__init__()

    def add(self,name,n=None):
        if(n==None):
            n=-len(self.elem)
        self.elem.append(Block(name,n))

    def export(self):
        elem = []
        for j in self.elem:
            try:
                elem.append([j.name,j.num])
            except:
                elem=[j.name, j.num]
        return {"elem":elem}

class Texture(UI):
    def __init__(self,name,type_,num,button_size=(0,0)):
        super().__init__(name)
        self.num=num

        if(str(type(type_))=="<class 'str'>"):
            if(name=="null"):
                self.material = pygame.image.load(r"./source material/base/base.png")  # .convert_alpha()
            else:
                self.material = pygame.image.load(r"./source material/" + type_ + "/" + self.name + ".png")  # .convert_alpha()
            self.type = type_

            self.w = 48
            self.h = 48
        else:
            self.type = "button"
            self.material = type_
            self.w = button_size[0]
            self.h = button_size[1]
        self.texture=None
    def copy(self):
        return Texture(self.name,self.type,self.num,(self.w,self.h))

class Textures:
    def __init__(self,raw_elem=None):
        self.elem={}
        self.raw_elem = raw_elem
        if(raw_elem!=None):
            self.type=self.raw_elem["type"]
            for i in self.type:
                self.elem[i]=[]
            for i in self.type:
                for j in self.raw_elem["elem"][i]:
                    self.add(i,j[0],n=j[1])
        else:
            self.type=["wall","ground","furniture","item"]

            for i in self.type:
                self.elem[i]=[]
        for i in self.type:
            self.add(i, "null", 0)

        self.button=pygame.image.load(r"./source material/base/base.png")#.convert_alpha()
        self.button_w = 0
        self.button_h = 0
        self.button_text_bias=5
        self.buttons=[]

        self.show_type=self.type[0]

    def add(self,type,name,n=None):
        if(self.get_elem(name=name,type=type)!=None):
            return
        if(n==None):
            n=sum([len(self.elem[t]) for t in self.type])
        self.elem[type].append(Texture(name,type,n))

    def add_button(self,name,n=None):
        if (n == None):
            n=len(self.buttons)
        b=Texture(name,self.button,n,button_size=(self.button_w,self.button_h))
        b.x=n*self.button_w
        b.y=0
        self.buttons.append(b)

    def get_elem(self,num=None,name=None,type=None):

        if(type==None):
            for t in self.type:
                for e in self.elem[t]:
                    if(num!=None and e.num==num):
                        return e
                    elif (name != None and e.name == name):
                        return e
        else:
            for e in self.elem[type]:
                if (num != None and e.num == num):
                    return e
                elif (name != None and e.name == name):
                    return e

        return None

    def export(self):
        type=copy.copy(self.type)
        elem = {}
        for i in self.elem.keys():
            for j in self.elem[i]:
                try:
                    elem[i].append([j.name,j.num])
                except:
                    elem[i]=[[j.name, j.num]]
        return {"type":type,"elem":elem}


class MapMaker:
    def __init__(self,file=None,size=(50,50),only_read=False):
        self.map_list = None
        self.blocks = Blocks()
        self.textures = Textures()
        self.block_type=["base", "base_click","area","areaselect","areacurrent"]
        self.load_blocks(self.block_type)

        self.basic_size = 20#48
        self.relative_size = self.basic_size

        self.screen_size=(1280,960)
        self.map_window_size_scale=(0.6,1)
        self.map_window_size=((int(self.screen_size[0]*self.map_window_size_scale[0]),
                               int(self.screen_size[1]*self.map_window_size_scale[1])),
                              (int(self.screen_size[0]*(1-self.map_window_size_scale[0])),
                               int(self.screen_size[1]*(1-self.map_window_size_scale[1]))))
        self.map_window_pos=(0,0)
        self.map_window_border=(0,0)



        self.map_list_undo_his = []
        self.map_list_redo_his = []
        self.undo_redo_len=10


        self.tool_window_size_scale=(0.05,1)
        self.tools = Tools()

        self.workspace_window_size_scale = (0.35, 1)

        self.areas={}
        self.current_area = 0

        self.selected_obj = set()
        self.description={"area":{},"object":{}}

        self.operation_tool = ["new","open","save","undo", "redo"]
        self.area_tool=["areaedit","areaset","areatext"]
        self.edit_tool=["text","drag","fill","frameselect"]

        self.load_tools(self.operation_tool+self.area_tool+self.edit_tool)
        self.size = (0, 0)
        self.screen=None

        self.font=pygame.font.SysFont("times new roman",20)


        self.fill_block=self.blocks.get_elem(name="base_click")

        if (file != None):
            self.reload(file,only_read=only_read)
        else:
            self.initialization(size)

    def init(self,size=(50,50)):
        self.map_list = None
        self.basic_size = 20  # 48
        self.relative_size = self.basic_size
        self.map_list_undo_his = []
        self.map_list_redo_his = []

        self.blocks = Blocks()
        self.textures = Textures()
        self.load_blocks(self.block_type)

        self.initialization(size)

    def new_map(self):
        size = popup.enterbox('New Map Size', 'New Map',default="50x50")
        if(size!=None):
            try:
                size=size.split("x")
                size=(int(size[0]),int(size[1]))
                self.init(size)
            except:
                popup.msgbox("ERROR! Illegal input!", 'ERROR')

    def find_area_by_name(self,name):
        name="".join(re.findall(r'[a-zA-Z]', name)).lower()
        for i in self.description["area"].keys():
            n = re.findall(r"Area Name: (.*?)\n", self.description["area"][i])[0]
            n = "".join(re.findall(r'[a-zA-Z]', n)).lower()
            if(n==name):
                return i
        return None


    def reload(self,file,only_read=False):
        with open(file, "rb") as f:
            file_load = dill.load(f)
        self.map_list = file_load["map_list"]
        size = self.map_list.shape[1:]
        self.blocks = Blocks()
        self.textures = Textures(file_load["textures"])
        for i in file_load["blocks"]["elem"]:
            self.blocks.add(i[0], i[1])

        self.areas = file_load["areas"]
        self.description=file_load["description"]

        if(not only_read):
            self.initialization(size)

    def save(self,file_path=None):
        blocks=self.blocks.export()
        textures=self.textures.export()
        map_list = copy.deepcopy(self.map_list)
        areas = copy.deepcopy(self.areas)
        description=copy.deepcopy(self.description)
        for i in description["object"].keys():
            if("include" in description["object"][i].keys()):
                del description["object"][i]["include"]
        s={"map_list":map_list,"blocks":blocks,"textures":textures,"areas":areas,"description":description}

        if(file_path==None):
            file_path = popup.filesavebox(default="./maps/map.dill")
        if(file_path!=None):
            try:
                #print(s)
                with open(file_path, "wb") as f:
                    dill.dump(s, f)
                if (file_path == None):
                    popup.msgbox(file_path+" saved!", 'Finish')
            except Exception as e:
                popup.msgbox("ERROR! "+str(e), 'ERROR')


    def open(self):
        file_path = popup.fileopenbox(default="./maps/*.dill",filetypes="*.dill")
        if (file_path != None):
            try:
                self.reload(file_path)
            except Exception as e:
                popup.msgbox("ERROR! " + str(e), 'ERROR')


    def load_blocks(self,names):
        for i in names:
            self.blocks.add(i)
    def load_tools(self,names):
        for i in names:
            self.tools.add(i)

    def load_textures(self,type_name):
        folder_path = "./source material/"+type_name+"/"
        file_list = os.listdir(folder_path)
        for file in file_list:
            texture_name=file.split(".")[0]
            if(self.textures.get_elem(name=texture_name)==None):
                self.textures.add(type_name,texture_name)

    def resize(self,map_size=None,element_size=None):
        if(map_size!=None):
            self.size = map_size
        elif(element_size!=None):
            self.relative_size=element_size
        map_window_border_x=self.map_window_size[0][0] - self.size[0] * self.relative_size
        map_window_border_y=self.map_window_size[0][1] - self.size[1] * self.relative_size
        self.map_window_border = (map_window_border_x if map_window_border_x<0 else 0,
                                  map_window_border_y if map_window_border_y<0 else 0)

    def operation(self,op):
        if(op=="undo"):
            if(len(self.map_list_undo_his)>0):
                tmp_map_list=self.map_list
                self.map_list=self.map_list_undo_his[-1]
                self.map_list_redo_his.append(tmp_map_list)
                self.map_list_undo_his=self.map_list_undo_his[:-1]
                if (len(self.map_list_redo_his) > self.undo_redo_len):
                    self.map_list_redo_his = self.map_list_redo_his[-self.undo_redo_len:]
        elif(op=="redo"):
            if (len(self.map_list_redo_his) > 0):
                tmp_map_list = self.map_list
                self.map_list = self.map_list_redo_his[-1]
                self.map_list_undo_his.append(tmp_map_list)
                self.map_list_redo_his = self.map_list_redo_his[:-1]
                if (len(self.map_list_undo_his) > self.undo_redo_len):
                    self.map_list_undo_his = self.map_list_undo_his[-self.undo_redo_len:]
        elif(op=="save"):
            self.save()
        elif(op=="open"):
            self.open()
        elif(op=="new"):
            self.new_map()


    def initialization(self,size=(5,5)):
        self.resize(map_size=size)

        #init map
        if(str(type(self.map_list))!="<class 'numpy.ndarray'>"):
            self.map_list = np.zeros((5,)+self.size) #0:ground, 1:wall, 2:furniture, 3:item, -1:area
        self.map_list_index={"ground":0, "wall":1, "furniture":2, "item":3, "area":-1}
        self.map_window = pygame.Surface(self.map_window_size[0])
        self.map = pygame.Surface((self.size[0] * self.relative_size, self.size[1] * self.relative_size))

        #init tools
        self.tool_window = pygame.Surface((self.screen_size[0] * self.tool_window_size_scale[0], self.screen_size[1]))
        tool_size = self.screen_size[0] * self.tool_window_size_scale[0]
        for tool in self.tools.elem:
            tool.resize(tool_size)

        #init workspace
        self.workspace_window = pygame.Surface((self.screen_size[0] * self.workspace_window_size_scale[0], self.screen_size[1]))
        self.textures.button_w=int(self.screen_size[0] * self.workspace_window_size_scale[0] / len(self.textures.type))
        self.textures.button_h =self.screen_size[1]*0.03
        self.textures.button=pygame.transform.scale(self.textures.button,(self.textures.button_w ,
                                                                           self.textures.button_h))
        for i in range(len(self.textures.type)):
            self.textures.add_button(self.textures.type[i])


        #init texture in workspace
        self.workspace_texture_window = pygame.Surface((self.workspace_window_size_scale[0]*self.screen_size[0],self.screen_size[1]-self.textures.button_h))
        line_num=4
        texture_scale=0.8
        t_size=int(self.screen_size[0] * self.workspace_window_size_scale[0] / line_num)
        for k in self.textures.elem.keys():
            if(self.textures.raw_elem!=None):
                for raw_texture in self.textures.raw_elem["elem"][k]:
                    self.textures.add(k,raw_texture[0],raw_texture[1])
            self.load_textures(k)

            t_n=0
            for t in self.textures.elem[k]:
                t.resize(t_size * texture_scale)
                t.texture = pygame.Surface((t_size,t_size))
                t.texture.fill("white")
                t.texture.blit(t.material,(0,0))
                text = self.font.render(t.name, True, "gray")
                t.texture.blit(text, (0,t_size*0.8))

                t.pos((int(t_n%line_num)*t_size,int(t_n/line_num)*t_size))

                t_n+=1

        pygame.display.set_caption("MapMaker")

    def get_material_by_index(self,l,i,j):

        n=self.map_list[l,i,j]
        if(n>0):
            return self.textures.get_elem(num=n).material
        else:
            return self.blocks.get_elem(num=n).material

    def add_area(self,pos):
        if(self.current_area not in self.areas.keys()):
            self.areas[self.current_area]=set()
        self.areas[self.current_area].add((pos[0], pos[1]))

    def search_obj_area(self,pos):
        types=copy.deepcopy(self.textures.type)
        types.remove("ground")
        r={}
        l=list(self.description["object"].keys())
        l.reverse()
        for i in l:
            if(self.description["object"][i]["type"] not in types):
                continue
            elif(pos in self.description["object"][i]["area"]):
                r[self.description["object"][i]["type"]]=i
                types.remove(self.description["object"][i]["type"])
                if(len(types)==0):
                    break
        if(len(r.keys())==0):
            return None
        else:
            return r


    def change_map(self,t,pos,pos0=None):
        i0,j0=pos
        try:
            type_=t.type
            shape=t.shape
            n = t.num
        except:

            type_="block"
            shape=(1,1)
            if (t == None):
                if(self.map_list[-1,pos[0],pos[1]]!=self.current_area):
                    return
                else:
                    n=0
            else:
                n = self.current_area

        if (type_ in ["ground"]):
            layer=0
        elif (type_ in ["wall",]):
            layer=1
        elif (type_ in ["furniture"]):
            layer=2
        elif (type_ in ["item"]):
            layer=3
        elif (type_ in ["block"]):
            layer=-1
        else:
            layer=0

        self.map_list_undo_his.append(np.copy(self.map_list))

        try:
            if(pos0!=None):
                i1,j1=pos0
                for i in range(i0, i1):
                    for j in range(j0, j1):
                        if (shape[0]!=1 or shape[1]!=1):
                            for k0 in range(shape[0]):
                                for k1 in range(shape[1]):
                                    index=t.get_submaterials_index(k0,k1)
                                    self.map_list[layer, i+k0, j + k1] = index + n / 100000
                        self.map_list[layer, i, j] = n
                        self.add_area((i, j))
            else:
                if (shape[0] != 1 or shape[1] != 1):
                    for k0 in range(shape[0]):
                        for k1 in range(shape[1]):
                            index = t.get_submaterials_index(k0, k1)
                            self.map_list[layer, i0 + k0, j0 + k1] = index + n / 100000
                self.map_list[layer, i0, j0] = n
                self.add_area((i0, j0))
            self.map_list_redo_his = []
            if (len(self.map_list_undo_his) > self.undo_redo_len):
                self.map_list_undo_his = self.map_list_undo_his[-self.undo_redo_len:]
        except Exception as e:
            print(e)

    def update_map(self,area_edit=False):
        #UI
        self.tool_window.fill("gray")
        tool_size=self.screen_size[0] * self.tool_window_size_scale[0]
        for tool in self.tools.elem:
            self.tool_window.blit(tool.material,(0, tool_size*tool.num))
            tool.pos((0, tool_size*tool.num))

        #workspace
        self.workspace_window.fill("white")
        for i in self.textures.buttons:
            self.workspace_window.blit(i.material, (i.x, i.y))
            text = self.font.render(i.name, True, "gray")
            self.workspace_window.blit(text, (i.x + self.textures.button_text_bias, i.y+self.textures.button_text_bias))
        self.workspace_texture_window.fill("white")
        for i in self.textures.elem[self.textures.show_type]:
            self.workspace_texture_window.blit(i.texture, (i.x, i.y))

        #map
        self.map_window.fill("gray")
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                for l in range(4):
                    if(self.map_list[l,i,j]!=int(self.map_list[l,i,j])):
                        sub_num=int(self.map_list[l, i, j])
                        draw_texture=self.textures.get_elem(num=round((self.map_list[l, i, j] - sub_num) * 100000))
                        img=draw_texture.submaterials[sub_num]
                        self.map.blit(pygame.transform.scale(img, (self.relative_size, self.relative_size)),(i * self.relative_size, j * self.relative_size))
                        continue
                    if(not (l!=0  and self.map_list[l,i,j]==0)):
                        t=self.textures.get_elem(num=self.map_list[l,i,j])
                        if(t.shape[0]!=1 or t.shape[1]!=1):
                            material=t.submaterials[0]
                        else:
                            material = t.material
                        w = self.relative_size
                        h = self.relative_size

                        self.map.blit(pygame.transform.scale(material, (w, h)), (i * self.relative_size, j * self.relative_size))

        area = self.blocks.get_elem(name="area")
        if(area_edit):
            areaselect = self.blocks.get_elem(name="areaselect")
            areacurrent = self.blocks.get_elem(name="areacurrent")
            for i in range(self.size[0]):
                for j in range(self.size[1]):
                    if(self.map_list[-1,i,j]==0):
                        self.map.blit(pygame.transform.scale(area.material, (self.relative_size,self.relative_size)),
                                      (i * self.relative_size, j * self.relative_size))
                    elif (self.map_list[-1, i, j] == self.current_area):
                        self.map.blit(pygame.transform.scale(areacurrent.material, (self.relative_size, self.relative_size)),
                                      (i * self.relative_size, j * self.relative_size))
                    else:
                        self.map.blit(pygame.transform.scale(areaselect.material, (self.relative_size, self.relative_size)),
                                      (i * self.relative_size, j * self.relative_size))

        for s_obj in self.selected_obj:
            self.map.blit(pygame.transform.scale(area.material, (self.relative_size, self.relative_size)),
                          (s_obj[0] * self.relative_size, s_obj[1] * self.relative_size))

        self.map=pygame.transform.scale(self.map, (self.size[0] * self.relative_size, self.size[1] * self.relative_size))
        self.map_window.blit(self.map,self.map_window_pos)

        #screen rendering
        self.screen.blit(self.map_window, self.map_window_size[1])
        self.screen.blit(self.tool_window, (0, 0))
        workspace_x=self.screen_size[0] * self.tool_window_size_scale[0]
        self.screen.blit(self.workspace_window, (workspace_x, 0))
        self.screen.blit(self.workspace_texture_window, (workspace_x, self.textures.button_h*1.1))


        pygame.display.flip()


    def update(self):
        fps = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.flip()
        drag=(0,0)
        map_window_pos = (0,0)
        last_select=(-1,-1)


        status="drag"
        while (True):
            if(status in self.area_tool):
                self.update_map(area_edit=True)
            else:
                self.update_map()
            events = pygame.event.get()
            pygame.event.pump()
            for event in events:
                pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT:
                    pygame.quit()

                click_button = False
                #UI Click
                if (event.type == pygame.MOUSEBUTTONUP and event.button==1):
                    for tool in self.tools.elem:
                        if (click_button):
                            break
                        if(tool.collidepoint(pos)):
                            self.current_area = 0
                            if(tool.name in self.operation_tool):
                                self.operation(tool.name)
                            else:
                                status=tool.name

                            if (tool.name in self.area_tool):
                                self.current_area = len(self.areas.keys()) + 1

                            last_select = (-1, -1)
                            click_button=True
                            self.selected_obj = set()

                    pos_0=(pos[0]-self.screen_size[0] * self.tool_window_size_scale[0],pos[1])
                    for workspace_button in self.textures.buttons:
                        if (click_button):
                            break
                        if(workspace_button.collidepoint(pos_0)):
                            self.textures.show_type=workspace_button.name
                            click_button = True

                    pos_1 = (pos[0] - self.screen_size[0] * self.tool_window_size_scale[0], pos[1]-self.textures.button_h)
                    for workspace_texture in self.textures.elem[self.textures.show_type]:
                        if (click_button):
                            break
                        if (workspace_texture.collidepoint(pos_1)):
                            self.fill_block=workspace_texture
                            click_button = True
                            last_select=(-1,-1)
                    if (click_button):
                        break



                #Map operation
                if (status == "fill"):
                    if((event.type == pygame.MOUSEBUTTONDOWN and event.button==1) or (event.type == pygame.MOUSEMOTION and event.buttons[0]==1)):

                        clicked_block = (int((pos[0]-self.map_window_size[1][0]-self.map_window_pos[0]) / self.relative_size),
                                         int((pos[1]-self.map_window_size[1][1]-self.map_window_pos[1]) / self.relative_size))
                        if(clicked_block[0]>=0 and clicked_block[1]>=0):
                            self.change_map(self.fill_block,clicked_block)
                elif(status=="drag"):
                    if(event.type == pygame.MOUSEBUTTONDOWN and event.button==1):
                        drag=event.pos
                        map_window_pos=self.map_window_pos
                    elif(event.type == pygame.MOUSEMOTION and event.buttons[0]==1):
                        map_window_pos_x = map_window_pos[0] - (drag[0] - event.pos[0])
                        map_window_pos_y = map_window_pos[1] - (drag[1] - event.pos[1])

                        self.map_window_pos=((map_window_pos_x if map_window_pos_x>self.map_window_border[0] else self.map_window_border[0]) if map_window_pos_x<0 else 0,
                                             (map_window_pos_y if map_window_pos_y>self.map_window_border[1] else self.map_window_border[1]) if map_window_pos_y<0 else 0)
                    elif(event.type == pygame.MOUSEBUTTONUP):
                        drag=(0,0)

                    #desc area
                    self.selected_obj=set()
                    clicked_block = (
                        int((pos[0] - self.map_window_size[1][0] - self.map_window_pos[0]) / self.relative_size),
                        int((pos[1] - self.map_window_size[1][1] - self.map_window_pos[1]) / self.relative_size))
                    areas=None
                    areas_show=set()

                    if (clicked_block[0] >= 0 and clicked_block[1] >= 0 and clicked_block[0] <= self.size[0] and
                            clicked_block[1] <= self.size[1]):
                        areas = self.search_obj_area(clicked_block)
                        if (areas != None):
                            for a in areas.keys():
                                areas_show= areas_show | self.description["object"][areas[a]]["area"]
                    if (event.type == pygame.MOUSEMOTION):
                        if(areas != None):
                            self.selected_obj=areas_show

                    #Press the middle mouse button to delete this description
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 2 and areas != None):
                        delete_jdg = True
                        if (len(areas.keys()) > 1):
                            ret = popup.choicebox(
                                "There are multiple types of descriptions in this block, please select the type you want to DELETE.",
                                'DELETE DESCCRIPTION!',
                                list(areas.keys()))
                            if (ret != None):
                                areas = areas[ret]
                            else:
                                delete_jdg = False
                        else:
                            bool_ = popup.boolbox(
                                "Do you want to DELETE this description?",
                                'DELETE DESCCRIPTION!')
                            if (bool_):
                                areas = areas[list(areas.keys())[0]]
                            else:
                                delete_jdg = False
                        if(delete_jdg):
                            del self.description["object"][areas]

                    #Press the right mouse button to view this description
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and areas != None):
                        show_jdg=True
                        if(len(areas.keys())>1):
                            ret = popup.choicebox("There are multiple types of areas in this block, please select the type you want to view.", 'Type',
                                                    list(areas.keys()))
                            if (ret != None):
                                areas=areas[ret]
                            else:
                                show_jdg=False
                        else:
                            areas=areas[list(areas.keys())[0]]
                        if(show_jdg):
                            msg = "The description for " + str(self.description["object"][areas]["type"])+" in this area."
                            try:
                                text = self.description["object"][areas]["description"]
                            except:
                                text = "There is currently no description available for this area."
                            desc=popup.textbox(msg=msg, title='Description', text=text, run=True)
                            if(desc!=None and desc!=text):
                                if(popup.boolbox(msg="Detected a change in description, do you want to execute the change?", title='')):
                                    if ("Name: " not in desc):
                                        popup.msgbox("ERROR! 'Name: ' is required", 'ERROR')
                                    elif ("Type: " not in desc):
                                        popup.msgbox("ERROR! 'Type: ' is required", 'ERROR')
                                    elif ("Function: " in desc and "Function: [" not in desc):
                                        popup.msgbox(
                                            "ERROR! Function type [add/remove] needs to be added to 'Function: ' attribute",
                                            'ERROR')
                                    elif ("Description: " not in desc):
                                        popup.msgbox("ERROR! 'Description: ' is required", 'ERROR')
                                    else:
                                        self.description["object"][areas]["description"] = desc

                elif(status=="frameselect"):
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                        clicked_block = (int((pos[0] - self.map_window_size[1][0] - self.map_window_pos[0]) / self.relative_size),int((pos[1] - self.map_window_size[1][1] - self.map_window_pos[1]) / self.relative_size))
                        if (clicked_block[0] >= 0 and clicked_block[1] >= 0):
                            if (last_select[0] == -1 and  last_select[0]==-1):
                                last_select =clicked_block
                                self.change_map(self.fill_block,clicked_block)
                            else:
                                self.change_map(self.fill_block, (min(last_select[0],clicked_block[0]), min(last_select[1], clicked_block[1])),
                                                (max(last_select[0],clicked_block[0])+1,max(last_select[1], clicked_block[1])+1))
                                last_select = (-1, -1)
                elif (status == "text"):
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 2):
                        self.selected_obj=set()
                        last_select = (-1, -1)
                    elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                        clicked_block = (
                        int((pos[0] - self.map_window_size[1][0] - self.map_window_pos[0]) / self.relative_size),
                        int((pos[1] - self.map_window_size[1][1] - self.map_window_pos[1]) / self.relative_size))


                        if (clicked_block[0] >= 0 and clicked_block[1] >= 0):
                            if (last_select[0] == -1 and last_select[0] == -1):
                                last_select = clicked_block
                                self.selected_obj.add(clicked_block)
                            else:
                                i0, j0 = (min(last_select[0], clicked_block[0]), min(last_select[1], clicked_block[1]))
                                i1, j1 = (max(last_select[0], clicked_block[0]) + 1, max(last_select[1], clicked_block[1]) + 1)
                                for i in range(i0, i1):
                                    for j in range(j0, j1):
                                        self.selected_obj.add((i,j))
                                last_select = (-1, -1)
                    elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and len(self.selected_obj)):
                        type_tmp=copy.deepcopy(self.textures.type)
                        type_tmp.remove("ground")
                        ret = popup.choicebox("In this area, the type of object to be described is:", 'Type', type_tmp)
                        if(ret!=None):
                            msg = "Enter a description for " + str(ret)+" in this area."
                            text = "Name: ...\nType: " + str(ret) + "\nFunction: (optional)[add/remove]...\nDescription: \n..."
                            desc = popup.textbox(msg=msg, title='Description Input', text=text, run=True)
                            if (desc != None):
                                if("Name: " not in desc):
                                    popup.msgbox("ERROR! 'Name: ' is required", 'ERROR')
                                elif ("Type: " not in desc):
                                    popup.msgbox("ERROR! 'Type: ' is required", 'ERROR')
                                elif ("Function: " in desc and "Function: [" not in desc):
                                    popup.msgbox("ERROR! Function type [add/remove] needs to be added to 'Function: ' attribute", 'ERROR')
                                elif ("Description: " not in desc):
                                    popup.msgbox("ERROR! 'Description: ' is required", 'ERROR')
                                else:
                                    self.description["object"][create_random_index(self.description["object"].keys())] = {"description":desc,"type":ret,"area":copy.deepcopy(self.selected_obj)}
                                    self.selected_obj=set()
                                last_select = (-1, -1)
                elif (status == "areaset"):#Reset area per button click, right mouse button to switch target area, middle mouse button to delete area

                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3):
                        clicked_block = (
                        int((pos[0] - self.map_window_size[1][0] - self.map_window_pos[0]) / self.relative_size),
                        int((pos[1] - self.map_window_size[1][1] - self.map_window_pos[1]) / self.relative_size))
                        if (clicked_block[0] >= 0 and clicked_block[1] >= 0 and pos[0] - self.map_window_size[1][0]>0):
                            self.current_area = self.map_list[-1, clicked_block[0], clicked_block[1]]
                    elif (event.type == pygame.MOUSEBUTTONDOWN and event.button in [1,2]):
                        if(event.button==1):
                            block=self.blocks.get_elem(name="areaselect")
                        else:
                            block=None
                        clicked_block = (
                        int((pos[0] - self.map_window_size[1][0] - self.map_window_pos[0]) / self.relative_size),
                        int((pos[1] - self.map_window_size[1][1] - self.map_window_pos[1]) / self.relative_size))
                        if (clicked_block[0] >= 0 and clicked_block[1] >= 0):
                            if (last_select[0] == -1 and last_select[0] == -1):
                                last_select = clicked_block
                                self.change_map(block, clicked_block,)
                            else:
                                self.change_map(block, (
                                min(last_select[0], clicked_block[0]), min(last_select[1], clicked_block[1])),
                                                (max(last_select[0], clicked_block[0]) + 1,
                                                 max(last_select[1], clicked_block[1]) + 1))
                                last_select = (-1, -1)

                elif (status == "areaedit"):
                    area_ = 0
                    clicked_block = (
                        int((pos[0] - self.map_window_size[1][0] - self.map_window_pos[0]) / self.relative_size),
                        int((pos[1] - self.map_window_size[1][1] - self.map_window_pos[1]) / self.relative_size))
                    try:
                        if (clicked_block[0] > 0 and clicked_block[1] > 0 and pos[0] - self.map_window_size[1][0]>0):
                            area_ = self.map_list[-1, clicked_block[0], clicked_block[1]]
                    except:
                        area_ = 0

                    if (event.type == pygame.MOUSEMOTION):
                        if (clicked_block[0] >= 0 and clicked_block[1] >= 0):
                            self.current_area = area_
                    elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and area_ != 0):
                        msg = "The description of the area " + str(area_)
                        try:
                            text = self.description["area"][area_]
                        except:
                            text = "There is currently no description available for this area."
                        popup.textbox(msg=msg, title='Description', text=text, run=True)

                elif (status == "areatext"):
                    area_ = 0
                    clicked_block = (
                        int((pos[0] - self.map_window_size[1][0] - self.map_window_pos[0]) / self.relative_size),
                        int((pos[1] - self.map_window_size[1][1] - self.map_window_pos[1]) / self.relative_size))
                    try:
                        if(clicked_block[0]>0 and clicked_block[1]>0 and pos[0] - self.map_window_size[1][0]>0):
                            area_ = self.map_list[-1, clicked_block[0], clicked_block[1]]
                    except:
                        area_=0

                    if(event.type == pygame.MOUSEMOTION):

                        if(clicked_block[0]>=0 and clicked_block[1]>=0):
                            self.current_area=area_
                    elif (event.type == pygame.MOUSEBUTTONDOWN and event.button==1 and area_!=0):
                        msg="Enter a description for area "+str(area_)
                        try:
                            text=self.description["area"][area_]
                        except:
                            text="Area Name: "+str(area_)+"\nDescription: \n..."
                        desc = popup.textbox(msg=msg, title='Description Input', text=text, run=True)
                        if(desc!=None):
                            if ("Area Name: " not in desc):
                                popup.msgbox("ERROR! 'Area Name: ' is required", 'ERROR')
                            elif ("Description: " not in desc):
                                popup.msgbox("ERROR! 'Description: ' is required", 'ERROR')
                            else:
                                self.description["area"][area_]=desc


                if (event.type == pygame.MOUSEBUTTONDOWN and event.button in [4,5]):
                    if (event.button == 4):
                        self.resize(element_size=self.relative_size + 1 if self.relative_size < 80 else 80)
                    elif (event.button == 5):
                        self.resize(element_size=self.relative_size - 1 if self.relative_size > 5 else 5)

                #shortcut
                if(event.type == pygame.KEYDOWN):
                    if event.key == pygame.K_z and (event.mod & pygame.KMOD_CTRL) and not (event.mod & pygame.KMOD_SHIFT):
                        self.operation("undo")
                        last_select = (-1, -1)
                    elif event.key == pygame.K_z and (event.mod & pygame.KMOD_CTRL) and (event.mod & pygame.KMOD_SHIFT):
                        self.operation("redo")
                        last_select=(-1,-1)
                    elif event.key == pygame.K_s and (event.mod & pygame.KMOD_CTRL) and not (event.mod & pygame.KMOD_SHIFT):
                        self.operation("save")


            fps.tick(60)



