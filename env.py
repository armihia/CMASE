import copy

import threading
import time

import dill
import numpy as np

from MapMaker import MapMaker
import pygame
import pygame_gui

from agent import cg_status
from agents import Agents
from event import EventController
from popup import Popup
from statistics import *

pygame.init()

class Env:
    def __init__(self,map_file,agents_param,file=None,max_round=None,only_read=False):
        self.file=file
        if(file!=None):
            with open(file, "rb") as f:
                file_load = dill.load(f)
            self.round = file_load["round"]
            self.group_log=file_load["group_log"]
            self.mm = MapMaker(file=file_load["mm"],only_read=only_read)
            self.event=file_load["event"]
            self.agents = Agents(load=file_load["agents"],only_read=only_read)

        else:
            self.mm = MapMaker(file=map_file)
            self.round = 0
            self.event = EventController()
            self.group_log = []
            self.agents = Agents()

        self.mm.relative_size=48

        self.screen = None

        self.fps = pygame.time.Clock()

        # self.controller = True
        # self.controller_round = True
        self.controller = False
        self.controller_round = False
        self.controlling=False

        self.map_window=pygame.surface.Surface((0,0))
        self.map_window_rect=None
        self.msg_window = pygame.surface.Surface((0, 0))
        self.window_ratio=0.8
        self.msg_x=(1 - self.window_ratio) * self.mm.screen_size[0]

        self.manager = pygame_gui.UIManager(self.mm.screen_size)
        self.text_box = None
        self.button1 = None
        self.button2 = None
        self.button3 = None

        self.msg_window_mode=1
        self.statistics_fig=None

        self.perceive_show=None

        self.click_pos=(-1,-1)
        self.click_block=self.mm.blocks.get_elem(name="area").material

        self.max_round=max_round
        self.end=False
        self.time=0

        if(not only_read):
            self.popup = Popup()
            self.init(agents_param)


    def init(self,agents_param):
        if(self.file==None):
            self.agents.agents_init(self.mm,agents_param)

        self.map_window = pygame.transform.scale(self.mm.map_window,
                                                    ((self.mm.screen_size[0] * self.window_ratio, self.mm.screen_size[1])))
        self.map_window_rect=self.map_window.get_rect()
        self.msg_window = pygame.transform.scale(self.mm.map_window,
                                                    ((self.msg_x, self.msg_x)))

    def draw(self,n, map, bias=(0,0),desc=""):
        if(n!=self.agents.agent_list[self.agents.current_see].number):
            return
        mm = self.mm
        shape = map.shape
        screen = pygame.Surface((shape[1] * mm.relative_size, shape[2] * mm.relative_size))
        # map
        screen.fill("black")
        for i in range(shape[1]):
            for j in range(shape[2]):
                for l in range(4):
                    if (map[l, i, j] != int(map[l, i, j])):
                        sub_num = int(map[l, i, j])
                        draw_texture = mm.textures.get_elem(num=round((map[l, i, j] - sub_num) * 100000))
                        img = draw_texture.submaterials[sub_num]
                        screen.blit(pygame.transform.scale(img, (mm.relative_size, mm.relative_size)),
                                    (i * mm.relative_size, j * mm.relative_size))
                        continue
                    if (not (l != 0 and map[l, i, j] == 0)):
                        t = mm.textures.get_elem(num=map[l, i, j])
                        if (t == None):
                            continue
                        if (t.shape[0] != 1 or t.shape[1] != 1):
                            material = t.submaterials[0]
                        else:
                            material = t.material
                        w = mm.relative_size
                        h = mm.relative_size

                        screen.blit(pygame.transform.scale(material, (w, h)),
                                    (i * mm.relative_size, j * mm.relative_size))

        # agents
        p_shape=map.shape
        for i in self.agents.agent_list:
            if ((i.pos[0] - bias[0] in range(0, p_shape[1])) and (i.pos[1] - bias[1] in range(0, p_shape[2]))):
                if (map[0, i.pos[0] - bias[0], i.pos[1] - bias[1]] != 0):
                    screen.blit(
                        pygame.transform.scale(i.materials[i.toward][i.motion_n], (mm.relative_size, mm.relative_size)),
                        ((i.pos[0] - bias[0]) * mm.relative_size, (i.pos[1] - bias[1]) * mm.relative_size))

        #msg_window
        screen_raw_pos=screen.get_size()

        if(screen_raw_pos[0]>screen_raw_pos[1]):
            screen_x=self.mm.screen_size[0] * (1 - self.window_ratio)
            screen_y=screen_raw_pos[1]/screen_raw_pos[0]*screen_x
        else:
            screen_y = self.mm.screen_size[0] * (1 - self.window_ratio)
            screen_x = screen_raw_pos[0] / screen_raw_pos[1] * screen_y
        screen = pygame.transform.scale(screen,((screen_x,screen_y )))
        self.perceive_show=(screen,desc)
        # pygame.image.save(screen, "./test.png")

    def update_map(self,mm):
        # map
        self.mm.map.fill("gray")
        self.map_window.fill("gray")
        self.msg_window.fill("white")
        self.screen.fill((255, 255, 255))
        for i in range(self.mm.size[0]):
            for j in range(self.mm.size[1]):
                for l in range(4):
                    if (self.mm.map_list[l, i, j] != int(self.mm.map_list[l, i, j])):
                        sub_num = int(self.mm.map_list[l, i, j])
                        draw_texture = self.mm.textures.get_elem(num=round((self.mm.map_list[l, i, j] - sub_num) * 100000))
                        img = draw_texture.submaterials[sub_num]
                        self.mm.map.blit(pygame.transform.scale(img, (self.mm.relative_size, self.mm.relative_size)),
                                      (i * self.mm.relative_size, j * self.mm.relative_size))
                        continue
                    if (not (l != 0 and self.mm.map_list[l, i, j] == 0)):
                        t = self.mm.textures.get_elem(num=self.mm.map_list[l, i, j])
                        if (t.shape[0] != 1 or t.shape[1] != 1):
                            material = t.submaterials[0]
                        else:
                            material = t.material
                        w = self.mm.relative_size
                        h = self.mm.relative_size

                        self.mm.map.blit(pygame.transform.scale(material, (w, h)),
                                      (i * self.mm.relative_size, j * self.mm.relative_size))

        if(self.click_pos[0]>=0 and self.click_pos[1]>=0):
            self.mm.map.blit(pygame.transform.scale(self.click_block, (self.mm.relative_size, self.mm.relative_size)),
                             (self.click_pos[0] * self.mm.relative_size, self.click_pos[1] * self.mm.relative_size))

        #agents
        for i in self.agents.agent_list:
            self.mm.map.blit(pygame.transform.scale(i.materials[i.toward][i.motion_n], (self.mm.relative_size, self.mm.relative_size)),
                             (i.pos[0] * self.mm.relative_size, i.pos[1] * self.mm.relative_size))

        # screen rendering
        self.mm.map = pygame.transform.scale(self.mm.map,(self.mm.size[0] * self.mm.relative_size, self.mm.size[1] * self.mm.relative_size))

        self.map_window.blit(self.mm.map, self.mm.map_window_pos)
        self.screen.blit(self.map_window, (0,0))

        if(self.msg_window_mode==1 and self.perceive_show!=None):
            self.msg_window.blit(self.perceive_show[0], (0, 0))
            self.msg_window.blit(self.perceive_show[0], (0, 0))

            if (self.perceive_show[1]!=self.text_box.html_text):
                text=self.perceive_show[1]
                self.text_box.html_text=text
                self.text_box.rebuild()
        elif (self.msg_window_mode == 2):

            if(self.statistics_fig!=None):
                self.msg_window.blit(self.statistics_fig, (0, 0))

            text="\n".join(self.group_log)
            if (text!=self.text_box.html_text):
                self.text_box.html_text=text
                self.text_box.rebuild()
        self.manager.draw_ui(self.screen)
        self.screen.blit(self.msg_window, (self.mm.screen_size[0] * self.window_ratio, 0))

        # self.mm.map = pygame.transform.scale(self.mm.map, (self.mm.size[0] * self.mm.relative_size, self.mm.size[1] * self.mm.relative_size))
        # self.screen.blit(self.mm.map, self.mm.map_window_pos)
        pygame.display.flip()

    def pos2block(self,pos):
        clicked_block = (
            int((pos[0] - self.mm.map_window_pos[0]) / self.mm.relative_size),
            int((pos[1] - self.mm.map_window_pos[1]) / self.mm.relative_size))
        return clicked_block

    def add_group_log(self,*log):
        self.group_log=[" ".join([str(i) for i in log])]+self.group_log
        with open("logs.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(self.group_log))

    def find_area_obj_by_name(self,name):
        name=name.lower().replace(" ","")
        for t in self.mm.description.keys():
            for i in self.mm.description[t]:
                if (t == "area"):
                    desc = self.mm.description[t][i]
                    type_ = t
                    range0 = self.mm.areas[i]
                    index = i
                else:
                    desc = self.mm.description[t][i]["description"]
                    type_ = t
                    range0 = self.mm.description[t][i]["area"]
                    index = i
                n = re.findall(r"Name: (.*?)\n", desc)[0]
                if (n.lower().replace(" ","") == name):

                    return {"name":n,"range":range0,"type":type_,"desc":desc,"index":index}
        return None

    def controller_action(self):
        self.controlling=True
        if(not self.controller):
            self.popup.msgbox("Currently not in control mode!", 'ERROR')
            self.controlling = False
            return
        self.agents.agent_list[self.agents.current_see].perceive(self)
        action_space=self.agents.agent_list[self.agents.current_see].action_space
        msg="Enter the action you want to execute as the main control character."
        text="The actions you can choose to take include:\n"+str(action_space)+"\n___________\n\n"+"action: \nshort-term situational cognition: \nshort-term goal: \ninteractive object cognitive description: \nchat content (Optional, if you choose the action of chat with, it is required): "
        asw = self.popup.textbox(msg=msg, title='Action', text=text, run=True)
        if(asw != None):
            # try:
                asw=asw.split("\n___________\n\n")[-1]

                action = asw.split("\n")[0].split("action: ")[1]
                if ("change " in action):
                    to_ = action.split("change ")[1]
                    try:
                        n=int(to_)
                    except:
                        n=None
                        to_0=to_.lower()
                        for i in range(len(self.agents.agent_list)):
                            if(to_0 in self.agents.agent_list[i].name.lower()):
                                n=i
                    if(n==None):
                        self.popup.msgbox("Can't find this agent!", 'ERROR')
                    else:
                        n_0=self.agents.current_see
                        self.agents.current_see=n
                        self.agents.agent_list[n_0].action_running = False
                else:
                    self.agents.agent_list[self.agents.current_see].action_generation(self,asw_raw_0=asw,control=True)
                    _,jdg,desc=self.agents.agent_list[self.agents.current_see].last_action_situation

                    print(jdg,desc)
                self.agents.agent_list[self.agents.current_see].perceive(self)
            # except Exception as e:
            #     print(e)
            #     self.popup.msgbox("Format Error!", 'ERROR')

        self.controlling = False

    def event_detect(self):
        events=self.event.event_jdg(self)
        if(len(events)!=0):
            for e in events:
                agents, objs = self.event.range_detect(self,e)

                desc_="Function: ["+e.type+"]"+e.desc+"\n"
                for n in agents:
                    cg_status(self, desc_, n, "agent",event=True)
                for n in objs:
                    cg_status(self, desc_, n, "obj",event=True)

                self.add_group_log("Event: [pos:",e.pos," range:",e.range,"desc:",e.desc,"]")

    def round_action(self,max_thread=10000):
        basic_agents_list=[i for i in range(len(self.agents.agent_list))]

        while(True):
            t=time.time()
            self.round += 1
            self.add_group_log("Round ",self.round,"Begin")

            self.event_detect()

            agents_list0=copy.copy(basic_agents_list)

            batch = int(len(agents_list0) / max_thread)
            if(len(agents_list0)%max_thread!=0):
                batch+=1

            for i in range(batch):
                agents_list=agents_list0[i*max_thread:(i+1)*max_thread]

                for i in agents_list:
                    if((self.controller and self.agents.current_see!=i) or (not self.controller)):
                        self.agents.agent_list[i].round_action(self)
                if(self.controller and self.controller_round):
                    self.agents.agent_list[self.agents.current_see].action_running=True
                while (True):
                    if(len(agents_list)==0):
                        break
                    for i in agents_list:
                        if(not self.agents.agent_list[i].action_running):
                            self.add_group_log(self.agents.agent_list[i].name+": "+self.agents.agent_list[i].action)
                            agents_list.remove(i)
                            self.agents.agent_list[i].event_influence = []

            try:
                self.statistics_fig=statistics(self)
            except:
                pass
            print("round end")
            self.add_group_log("Round ", self.round, "total time consumption: ",str(int(time.time()-t)),"s")
            # if(not (self.controller and not self.controller_round)):

            self.save("auto_save_"+str(self.round))
            if(self.max_round!=None and self.round>=self.max_round):
                self.add_group_log("Round Finish")
                self.end=True
                break


    def update(self):
        map_window_pos = (0, 0)
        drag = (0, 0)
        self.screen=pygame.display.set_mode(self.mm.screen_size)
        self.text_box = pygame_gui.elements.UITextBox(
            html_text="",
            relative_rect=pygame.Rect(self.mm.screen_size[0] * self.window_ratio, self.msg_x, self.msg_x,
                                      self.msg_x * 1.5),
            manager=self.manager
        )
        self.button1 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.mm.screen_size[0] * self.window_ratio,
                                      self.mm.screen_size[1] - self.msg_x * 0.2, self.msg_x / 3, self.msg_x * 0.2),
            text="Individual",
            manager=self.manager
        )
        self.button2 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.mm.screen_size[0] * self.window_ratio + self.msg_x / 3,
                                      self.mm.screen_size[1] - self.msg_x * 0.2, self.msg_x / 3, self.msg_x * 0.2),
            text="Group",
            manager=self.manager
        )

        self.button3 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.mm.screen_size[0] * self.window_ratio + self.msg_x / 3 * 2,
                                      self.mm.screen_size[1] - self.msg_x * 0.2, self.msg_x / 3, self.msg_x * 0.2),
            text="Action",
            manager=self.manager
        )

        threading.Thread(target=self.round_action).start()
        self.time=time.time()
        while (True):
            self.update_map(self.mm)
            events = pygame.event.get()
            pygame.event.pump()
            status = "drag"
            for event in events:
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.button1:
                        self.msg_window_mode=1
                    if event.ui_element == self.button2:
                        self.msg_window_mode=2
                    if event.ui_element == self.button3:
                        if(not self.controlling):
                            threading.Thread(target=self.controller_action, daemon=True).start()
                self.manager.process_events(event)

                pos = pygame.mouse.get_pos()

                if (event.type == pygame.KEYDOWN):
                    if event.key == pygame.K_s and (event.mod & pygame.KMOD_CTRL) and not (
                            event.mod & pygame.KMOD_SHIFT):
                        self.save(choose_=True)
                    elif(event.key in range(pygame.K_0,pygame.K_0+9)):
                        self.click_pos = (-1, -1)
                        # self.agents.current_see=event.key-pygame.K_1
                        mode=event.key-pygame.K_0
                        if(mode==0): #Press the number 0 to cancel the control mode
                            self.controller=False
                            self.agents.agent_list[self.agents.current_see].action_running = False
                        else:
                            self.controller = True
                            if(mode==1): #Press the number 1 to move freely
                                self.controller_round=False
                                self.agents.agent_list[self.agents.current_see].action_running = False
                            elif(mode==2): #Press the number 2 to take action in rounds
                                self.controller_round=True
                                self.agents.agent_list[self.agents.current_see].action_running=False

                if(self.map_window_rect.collidepoint(pos)):
                    if(not self.controller_round):
                        if (event.type == pygame.MOUSEBUTTONDOWN and event.button==3):
                            self.click_pos=self.pos2block(pos)
                            goal = self.pos2block(pos)
                            self.agents.agent_move(goal,self)

                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button in [4, 5]):
                        if (event.button == 4):
                            self.mm.resize(element_size=self.mm.relative_size + 1 if self.mm.relative_size < 80 else 80)
                        elif (event.button == 5):
                            self.mm.resize(element_size=self.mm.relative_size - 1 if self.mm.relative_size > 5 else 5)

                    if (status == "drag"):
                        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                            drag = event.pos
                            map_window_pos = self.mm.map_window_pos
                        elif (event.type == pygame.MOUSEMOTION and event.buttons[0] == 1):
                            map_window_pos_x = map_window_pos[0] - (drag[0] - event.pos[0])
                            map_window_pos_y = map_window_pos[1] - (drag[1] - event.pos[1])

                            self.mm.map_window_pos = ((map_window_pos_x if map_window_pos_x > self.mm.map_window_border[0] else
                                                  self.mm.map_window_border[0]) if map_window_pos_x < 0 else 0,
                                                 (map_window_pos_y if map_window_pos_y > self.mm.map_window_border[1] else
                                                  self.mm.map_window_border[1]) if map_window_pos_y < 0 else 0)
                        elif (event.type == pygame.MOUSEBUTTONUP):
                            drag = (0, 0)

            self.manager.update(self.fps.tick(60)/ 1000.0)

            if(self.end):
                msg="round finish, Total time consumption: "+str(int(time.time()-self.time))+"s"
                print(msg)
                self.popup.msgbox(msg,"")
                break

    def save(self,file_name=None,choose_=False):
        base_url="./env file/"
        if(choose_):
            file_path = self.popup.filesavebox(default="./env file/saved model")
            if(file_path==None):
                return
        else:
            if(file_name==None):
                file_name="env"
                file_path = self.popup.filesavebox(default=base_url+file_name)
            else:
                file_path=base_url+file_name
        self.mm.save(file_path+"_map.dill")

        a=[]

        for i in self.agents.agent_list:
            holding={}
            for j in i.holding.keys():
                holding_0 = {}
                for k in i.holding[j].keys():
                    if(k not in ["include"]):
                        holding_0[k]=i.holding[j][k]
                holding[j]=holding_0
            param={"name":i.name,"param":i.param,"long_term_goal":i.long_term_goal,"short_term_goal":i.short_term_goal,"pos":i.pos,"status":i.status,
                   "toward":i.toward,"motion_n":i.motion_n,"holding":holding,
                   "perception_desc":i.perception_desc,"action_space_prompt":i.action_space_prompt,"action_space":i.action_space,"action_his":i.action_his,
                   "number":i.number,"action":i.action,"vad":i.vad,"long_term_self_awareness":i.long_term_self_awareness,"memory":i.memory.memory,
                   "short_term_situational_cognition":i.short_term_situational_cognition,
                   "condition":i.condition,"object_cognitive":i.object_cognitive,"last_action_situation":i.last_action_situation,"event_influence":i.event_influence}
            a.append(param)

        agent = {"agent_name_list": self.agents.agent_name_list, "current_see": self.agents.current_see,"agent_list":a}
        s={"mm":file_path+"_map.dill","group_log":self.group_log,"round":self.round,"event":self.event,"agents":agent}

        with open(file_path+".dill", "wb") as f:
            dill.dump(s, f)
