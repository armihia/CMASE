import random
import re
import time

import names

from BaseLLM import LLM
from MapMaker import create_random_index
from astar import astar
from avatar_generator import Avatar_generator
from bresenham import find_points
import pygame
import numpy as np
import copy
import threading

from memory import Memory
from vad import VAD


def cg_status(env, desc, target, target_type,event=False):
    desc += "\n"
    func = re.findall(r"Function: (.*?)\n", desc)
    if (len(func) != 0):
        func = "[".join(func[0].replace("(optional)", "").split("[")[1:]).split("]")
        func_type = func[0].lower().replace(" ", "")
        func_desc = "]".join(func[1:]).replace("+", "")
        if (func_type == "goal"):
            if (target_type == "agent"):
                if (func_desc not in target.condition):
                    target.short_term_goal+=" "+func_desc
        if (func_type == "add"):
            if (target_type == "obj"):
                target_desc = env.mm.description[target["type"]][target["index"]]["description"] + "\n"
                try:
                    target_status = re.findall(r"Status: (.*?)\n", target_desc)[0]
                    if (func_desc in target_status):
                        pass
                    else:
                        target_status += " // " + func_desc
                        env.mm.description[target["type"]][target["index"]]["description"] = \
                            re.sub("Status: (.*?)", target_status,
                                   env.mm.description[target["type"]][target["index"]]["description"])

                except:
                    target_status = func_desc
                    env.mm.description[target["type"]][target["index"]][
                        "description"] += "\nStatus: " + target_status

            elif (target_type == "agent"):
                if (func_desc not in target.condition):
                    target.condition.append(func_desc)
                    target.action_his.append("You have been added condition: "+func_desc)
                    if(event):
                        target.event_influence.append(func_desc)
        elif (func_type == "remove"):
            func_desc = func_desc.lower().replace(" ", "").replace("+", "")
            if (func_desc in ["*", "all"]):
                if (target_type == "obj"):
                    env.mm.description[target["type"]][target["index"]]["description"] = \
                        re.sub("Status: (.*?)", "",
                               env.mm.description[target["type"]][target["index"]]["description"] + "\n")[:-1]
                elif (target_type == "agent"):
                    target.condition = []
                    target.action_his.append("Your condition has been cleared")
                    if (event):
                        target.event_influence.append("Your condition has been cleared")
            else:
                if (target_type == "obj"):
                    target_desc = env.mm.description[target["type"]][target["index"]][
                                      "description"] + "\n"
                    try:
                        target_status = re.findall(r"Status: (.*?)\n", target_desc)[0].split(" // ")
                        target_status_0 = []
                        for i in target_status:
                            i0 = i.lower().replace(" ", "")
                            if (i0 not in func_desc and func_desc not in i0):
                                target_status_0.append(i)

                            target_status = " // ".join(target_status_0)
                            env.mm.description[target["type"]][target["index"]]["description"] = \
                                re.sub("Status: (.*?)\n", "Status: " + target_status,
                                       env.mm.description[target["type"]][target["index"]][
                                           "description"] + "\n")[:-1]

                    except:
                        pass
                elif (target_type == "agent"):
                    for i in copy.copy(target.condition):
                        i0 = i.lower().replace(" ", "")
                        if (i0 in func_desc or func_desc in i0):
                            target.condition.remove(i)
                            target.action_his.append("Your condition '" + i+"' has been removed")
                            if (event):
                                target.event_influence.append("Your condition '" + i+"' has been removed")

class Agent:
    def __init__(self,name,n,param,pos=None,items=None,object_cognitive=None,long_term_self_awareness=None,file=None,only_read=False):
        self.llm = LLM()
        if(file!=None):
            self.name = file["name"]
            self.param = {}
            for k in file["param"].keys():
                if (k not in ["spacy"]):
                    self.param[k] = copy.deepcopy(file["param"][k])
            spacy_ = param["spacy"]
            self.vad_model = VAD(spacy_)

            self.long_term_goal = file["long_term_goal"]
            self.short_term_goal = file["short_term_goal"]
            self.pos = file["pos"]
            self.status = file["status"]
            self.toward = file["toward"]
            self.motion_n = file["motion_n"]
            self.holding = file["holding"]
            self.perception_desc = file["perception_desc"]
            self.action_space_prompt = file["action_space_prompt"]
            self.action_space = file["action_space"]
            self.action_his = file["action_his"]
            self.event_influence=file["event_influence"]
            self.number = file["number"]
            self.action = file["action"]
            self.vad = file["vad"]
            self.long_term_self_awareness = file["long_term_self_awareness"]
            self.memory = Memory(self.vad_model,file=file["memory"])
            self.short_term_situational_cognition = file["short_term_situational_cognition"]
            self.condition = file["condition"]
            self.object_cognitive = file["object_cognitive"]
            self.last_action_situation = file["last_action_situation"]
        else:
            if(pos==None):
                pos=(0,0)
            if(name=="random"):
                self.name=names.get_full_name(param["gender"])
            else:
                self.name=name
            self.param = {}
            for k in param.keys():
                if (k not in ["spacy"]):
                    self.param[k] = copy.deepcopy(param[k])

            spacy_ = param["spacy"]
            self.vad_model = VAD(spacy_)

            self.long_term_goal = self.param["action_info"]["long_term_goal"]
            self.short_term_goal = "none"
            self.pos = pos
            self.status = "none"
            self.toward = 0
            self.motion_n = 1

            self.holding = {}
            if (items != None):
                for item in items:
                    name, desc, n, material_n = item
                    material = desc["material"]

                    if ("Function" in desc.keys()):
                        desc_0 = "Name: " + name + "\nType: item\nFunction: " + desc[
                            "Function"] + "+\nDescription: \n" + desc["Description"]
                    else:
                        desc_0 = "Name: " + name + "\nType: item\nDescription: \n" + desc["Description"]

                    detail = {"description": desc_0, 'type': 'item', 'include_count': ['1 ' + material],
                              'area': {(0, 0)}, 'material': [[(0, 0), np.float64(material_n)]]}
                    self.holding[n] = detail

            self.perception_desc = ""
            self.action_space_prompt = ""
            self.action_space = None

            self.action_his = []
            self.event_influence=[]

            self.number = n
            self.action = "None"

            self.vad = {'valence': 'medium', 'arousal': 'medium', 'dominance': 'medium'}

            if(long_term_self_awareness==None):
                self.long_term_self_awareness = self.generate_long_term_self_awareness()
            else:
                self.long_term_self_awareness=long_term_self_awareness
            self.memory = Memory(self.vad_model)
            self.short_term_situational_cognition = "I'm not sure about my current situation."
            self.condition = []
            if(object_cognitive==None):
                self.object_cognitive = {}
            else:
                self.object_cognitive = object_cognitive

            self.last_action_situation = None

        self.avatar_generator=Avatar_generator()

        self.path=[]
        if("avatar_info" in self.param.keys()):
            avatar_param=self.param["avatar_info"]
        else:
            avatar_param = None

        self.param["avatar_info"] = avatar_param
        # self.basic_material = pygame.image.load(r"./source material/agent/"+name+".png")  # .convert_alpha()
        self.materials = []  # 0: front, 1:left, 2:right, 3:back

        self.perception_map = None

        self.shape = (3, 4)
        self.w = 48
        self.h = 48

        if(not only_read):
            img, avatar_param = self.avatar_generator.generate_avatar(self.param["individual_info"],avatar_param)
            self.basic_material = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
            self.basic_material = pygame.transform.scale(self.basic_material, (144, 192))
            size = self.basic_material.get_size()
            base_len = int(size[0] / 3)
            for i in range(self.shape[1]):
                self.materials.append([])
                for j in range(self.shape[0]):
                    subsurface = self.basic_material.subsurface((j * base_len, i * base_len, base_len, base_len))
                    self.materials[-1].append(subsurface)

        self.action_running=False

        self.action_list={"go to":["area"],"use":["furniture","item"],"apply→agent/furniture":["item"],"take":["item"],"put→area/furniture":["item"],"give→agent":["item"],"chat with":["agent"]}
        with open("prompt example/action-example.txt", "r", encoding="utf-8") as f:
            self.action_example=[i.split("——") for i in f.read().split("\n+++++\n")]
        with open("prompt example/action-choose-example.txt", "r", encoding="utf-8") as f:
            self.action_choose_example=[i.split("——") for i in f.read().split("\n+++++\n")]
        with open("prompt example/short_term_situational_cognition_example.txt", "r", encoding="utf-8") as f:
            self.short_term_situational_cognition_example = [i.split("——") for i in f.read().split("\n+++++\n")]


    def generate_long_term_self_awareness(self):
        info=copy.deepcopy(self.param["individual_info"])
        info.update({"long_term_goal":self.param["action_info"]["long_term_goal"]})
        qst="Based on the JSON information provided in <<demographic variables>>, write a long-term self-perception description in the first-person perspective that aligns with this information and does not exceed 200 words. You are creating a character for a literary work; therefore, your writing should reflect a multi-dimensional persona that embodies the character's attributes, rather than simply presenting an overly positive image:\n<<"+ \
            str(info) + ">>"
        his=[["Based on the JSON information provided in <<demographic variables>>, write a long-term self-perception description in the first-person perspective that aligns with this information and does not exceed 200 words. You are creating a character for a literary work; therefore, your writing should reflect a multi-dimensional persona that embodies the character's attributes, rather than simply presenting an overly positive image:\n<<{'name': 'Lorina Lefevere', 'long_term_goal': 'none','gender': 'Female', 'skin tone': 'dark skin tone', 'education': 'junior high school', 'age': '24', 'social status': 'murderer'}>>",
            "I’m Lorina Lefevere, 24, and some would say my story ended the night it all happened—but I’m still here. I didn’t finish much school—junior high was as far as I got before life dragged me elsewhere. The world always saw my dark skin and rough edges before they ever saw me. I used to dream like anyone else, but now I drift through time without a clear tomorrow. People call me a murderer, and maybe that’s the only part of me they think they understand. But they don’t know what led up to that night—the noise, the silence, the choices no one should have to make.\n\nI don’t claim innocence. But I carry more than guilt—I carry memories, consequences, and the weight of survival. I don’t think in long-term goals; I think in moments—quiet ones when I can breathe without shaking. I’ve learned to watch everything and trust almost nothing. Sometimes I remember being fifteen and laughing over nothing with my sister, and for a second, I feel human again. Maybe I’m broken. Maybe I’m dangerous. But I’m not simple. I’m still writing my story, even if no one’s left to read it."]]
        r=self.llm.chat(qst,his=his, model="gpt", version="gpt-4o").replace("\n","")
        print("long_term_self_awareness: ",r)
        return r

    def add_path(self,path,env,round=False):
        self.path=path
        if(self.status!="move"):
            self.status="move"
        if(round):
            finish=self.move(env,round)
            return finish
        else:
            threading.Thread(target=self.move,args=(env,round,)).start()

        return True

    def round_action(self,env):
        self.action_running=True
        self.perceive(env,draw=False)

        threading.Thread(target=self.action_generation,args=(env,)).start()
        # self.action_generation(env)

    def get_self_desc(self,action_jdg=True):
        t = ""
        t += "You are a person, and your long-term self-awareness can be seen as shown in /*long-term self-awareness*/：\n/*\n"
        t += self.long_term_self_awareness + "\n*/\n\n"
        t += "Your short-term situational cognition can be seen as shown in  /**short-term situational cognition**/：\n/**\n"
        t += self.memory.get_memory_and_association() + "\n**/\n\n"
        if (action_jdg):
            t += self.perception_desc + "\n"
        else:
            t += "\nYou can see other people in your field of vision. They include:\n"
            t += "Name: interviewer - " + "The action this people is taking is: chat with you\nMy cognitive description of this agent: \n" + \
            self.object_cognitive["interviewer"] if "interviewer" in self.object_cognitive.keys() else ""
            t += "\n\n"
        if (len(self.action_his) != 0):
            t += "!--\nBelow is the chronological sequence of 'actions you performed and actions performed on you by other agents ([passive action])', with the most recent action listed last:\n" + "\n".join(
                [str(a + 1) + ". " + self.action_his[a] for a in range(len(self.action_his))]) + "\n"
            if ("[passive action]" in " ".join(self.action_his[-2:])):
                t += "NOTE THAT AFTER YOUR LAST ACTION, SOME OTHER AGENT PERFORMED AN ACTION " + str(
                    len(self.action_his)) + " ON YOU!\n"
            t += "--!\n"

        t += "\nYour long-term goal is to '" + self.long_term_goal + "'.\n"
        short_term_goal=self.short_term_goal
        if (len(self.event_influence) != 0):
            short_term_goal += " I have NOTICED that some events have just occurred in the environment, and these events have had SOME IMPACTS on me: " + "; ".join(
                self.event_influence)+". I must pay attention to and handle these events."
        t += "Your short-term goal is to '" + short_term_goal + "'\n"
        t += "Your emotional VAD dimension status: " + str(self.vad)[1:-1] + "\n"

        if(action_jdg):
            t += "\n" + self.action_space_prompt + "\n"
        if (self.last_action_situation != None):
            t += "\nThe action you took in the previous moment was: '" + self.last_action_situation[0] + "' "
            if (self.last_action_situation[1]):
                t += self.last_action_situation[2]
            else:
                t += "The task execution failed due to the following reasons: " + self.last_action_situation[2]
            t += "\n"


        return t

    def action_generation(self,env,asw_raw_0=None,control=False):
        debug=False
        t=self.get_self_desc()
        t += "\nPlease decide the action you want to take and reply with the corresponding action. Note that in your chosen action, [TYPE1, TYPE2, ...] needs to be replaced with an object from /----...----/ that matches the description, rather than returning the type name directly. In addition, you are also required to include in your response a description of your awareness of your own short-term situation, a new short-term goal, and a cognitive description of the object with which you interacted during the action you have chosen. Your reply format should be as follows:\n"
        t += "action: 'The action you chose'\n"
        t += "short-term situational cognition: 'Your description of your own short-term situation'\n"
        t += "short-term goal: 'The new short-term goal you have formulated'\n"
        t += "interactive object cognitive description: 'Your new cognitive description of the interactive object involved in the action'\n"
        t += "chat content (Optional, if you choose the action of chat with, it is required): 'What you want to say to your chat partner, the number of words should not exceed " + str(
            self.param["action_info"]["round_speaking_words"]) + ".If you think you are having a conversation with someone in 'actions you have taken and actions others have taken toward you ([passive actions])', then you need to choose to use a declarative sentence to answer the question before asking a new question. Avoid constantly using questions in conversation to keep the conversation going, and end the conversation appropriately.'"

        with open("test.txt", "w",encoding="utf-8") as f:
            f.write(t)

        content = None

        if(debug and asw_raw_0==None):
            action_raw="go to random"
            actions=[["go to","random"]]
        else:
            if(asw_raw_0==None):
                asw_raw = self.llm.chat(t, his=self.action_example, model="gpt", version="gpt-4o")
            else:
                asw_raw=asw_raw_0
            print(asw_raw)
            asw = self.asw_analysis(asw_raw)
            print(asw)
            action_raw=""

            if("action" in asw.keys()):
                action_raw = asw["action"]
            if ("short-term goal" in asw.keys()):
                self.short_term_goal = asw["short-term goal"]
            else:
                self.short_term_goal = "none"
            if ("short-term situational cognition" in asw.keys()):
                self.short_term_situational_cognition = asw["short-term situational cognition"]
            else:
                #self.short_term_situational_cognition = "I'm not sure about my current situation."
                t0=self.get_self_desc()
                t0+="You already chosed the action '"+action_raw+"'. Now you should generate and only generate your short-term situational cognition in this situation. Keep the length within 100 words:"

                self.short_term_situational_cognition = self.llm.chat(t0, his=self.short_term_situational_cognition_example, model="gpt", version="gpt-4o")
            if(len(self.condition)!=0):
                self.short_term_situational_cognition += "\n"+"\n".join(self.condition)

            vad,vec=self.vad_model.analyze_vad(self.short_term_situational_cognition)
            self.vad=self.vad_model.desc(vad)

            # self.action_space.append(action_raw)
            actions,to_,action_raw=self.action_analysis(env,action_raw,control=control)

            self.memory.add(self.short_term_situational_cognition,self.vad,vec,action_raw)

            if ("interactive object cognitive description" in asw.keys() and to_ != None):
                self.object_cognitive[to_] = asw["interactive object cognitive description"]
            if ("chat content" in asw.keys() and to_ != None):
                content = asw["chat content"]


        print(actions)
        jdg,_=self.action_execute(env, actions,content=content,round=True)
        #print(self.name,self.action_his,jdg,_)
        self.last_action_situation=[action_raw,jdg,_]
        self.action_running=False


    def cg_action(self,a,add_his_only=False,l=15):
        if(not add_his_only):
            self.action=a
        self.action_his.append(a)
        if(len(self.action_his)>l):
            self.action_his=self.action_his[l:]

    def asw_analysis(self,asw_raw):
        asw_raw=asw_raw.replace("**","").replace("\n\n","\n").replace("Short-term","short-term").replace("Interviewer","interviewer").replace("Chat","chat")
        asw_raw=asw_raw+"\nchat content"
        patterns = {
            "action": [re.compile(r'action:\s*(.*?)(?=short-term situational cognition:|\Z)', re.DOTALL)],
            "short-term situational cognition": [re.compile(
                r'short-term situational cognition:\s*(.*?)(?=short-term goal:|\Z)',
                re.DOTALL | re.IGNORECASE
            )],
            "short-term goal": [re.compile(
                r'short-term goal:\s*(.*?)(?=interactive object cognitive description:)',
                re.DOTALL | re.IGNORECASE
            ),
                re.compile(
                    r'short-term goal:\s*(.*?)(?=interviewer cognitive description:)',
                    re.DOTALL | re.IGNORECASE
                )
            ],
            "interactive object cognitive description": [re.compile(
                r'interactive object cognitive description:\s*(.*?)(?=chat content)',
                re.DOTALL | re.IGNORECASE
            ),
                re.compile(
                    r'interviewer cognitive description:\s*([^\n]*?)(?=chat content)',
                    re.DOTALL | re.IGNORECASE
                ),
            ],
            "chat content": [re.compile(
                r'chat content:\s*(.*?)(?=chat content|\Z)',
                re.DOTALL | re.IGNORECASE
            ),
                re.compile(
                    r'chat content \(Optional, if you choose the action of chat with, it is required\):\s*(.*?)(?=chat content|\Z)',
                    re.DOTALL | re.IGNORECASE
                )
            ]
        }

        result = {}
        for key, patterns in patterns.items():
            for pattern in patterns:
                match = pattern.search(asw_raw)
                if match:
                    r=match.group(1).strip().replace("\n","")
                    if(len(r.replace(" ",""))!=0):
                        result[key] = r
                        try:
                            if(result[key][0]=="'"):
                                result[key] =result[key][1:]
                            if (result[key][-1] == "'"):
                                result[key] = result[key][:-1]
                        except:
                            pass
                    break

        return result

    def random_choose_pos(self,env,range0=None):
        if(range0==None):
            range0=[]
        range_=[]
        range0 = list(range0)
        shape = env.mm.map_list[1].shape
        if(len(range0)==0):
            print("random walk")
            for i in range(1,self.param["action_info"]["round_move_distance"]):
                x1 = self.pos[0] - i
                x2 = self.pos[0] + i
                for j in range(1,self.param["action_info"]["round_move_distance"]):
                    y1=self.pos[1] - j
                    y2=self.pos[1] + j
                    range0 += [(x1, y1), (x1, y2),(x2, y1), (x2, y2)]

        for i in range(len(range0)):
            if(range0[i][0]>=0 and range0[i][0]<shape[0] and range0[i][1]>=0 and range0[i][1]<shape[1]):
                if (env.mm.map_list[1][range0[i][0]][range0[i][1]] == 0):
                    range_.append(range0[i])
        if (len(range_) == 0):
            return None

        return random.choice(range_)

    def action_execute(self,env,actions,content=None,round=True):
        shape = env.mm.map_list[0].shape

        if(content==None):
            content=""

        for action in actions:
            a=action[0]
            to_=action[1]
            from_=None
            if(str(type(to_))=="<class 'list'>"):
                from_=to_[1]
                to_=to_[0]

            _action = a
            goal=None
            if(a=="go to"):
                if(to_ == "random"):
                    goal = self.random_choose_pos(env)
                else:
                    n=env.find_area_obj_by_name(to_)
                    if (n !=None):
                        goal = self.random_choose_pos(env, n["range"])
                if(goal!=None):
                    _action += " "+to_
                    self.cg_action(_action)
                else:
                    n=env.agents.find_by_name(to_)

                    if (n != None):
                        goal = n.pos
                        _action += " "+to_
                        self.cg_action(_action)
                    else:
                        return False,"You have found that the place you are going to cannot be reached at the moment."
                start = self.pos
                path = astar(copy.deepcopy(env.mm.map_list[1]), start, goal)
                if (path != None):
                    finish=self.add_path(path, env, round=round)
                    if(not finish):
                        break
            elif(a=="chat with"):
                _action+=" "+to_+": '"+content+"'"
                self.cg_action(_action)
                n = env.agents.find_by_name(to_)
                _action="[passive action] chatted up by "+self.name+": '"+content+"'"
                n.cg_action(_action,True)

            elif (a == "give"):
                n = env.agents.find_by_name(from_)
                if (n != None):
                    hold = [[i, re.findall(r"Name: (.*?)\n", self.holding[i]["description"])[0]] for i in
                            self.holding.keys()]
                    m = None
                    for i in range(len(hold)):
                        if (hold[i][1] == to_):
                            m = hold[i][0]
                            break
                    if (m != None):
                        n.holding[m]=copy.deepcopy(self.holding[m])
                        del self.holding[m]

                        _action += " " + to_ + " to " + from_
                        self.cg_action(_action)
                        _action = "[passive action] received "+to_+" from " + self.name
                        n.cg_action(_action, True)

                    else:
                        return False, "You're not holding what you're going to give right now"
                else:
                    return False, "The agent who you want to give the object does not exist."

            elif (a == "take"):
                n = env.find_area_obj_by_name(to_)
                if (n != None):
                    material=[]
                    t=re.findall(r"Type: (.*?)\n", n["desc"])[0]
                    for n_pos in n["range"]:
                        tmp=env.mm.map_list[env.mm.map_list_index[t]][n_pos[0]][n_pos[1]]
                        env.mm.map_list[env.mm.map_list_index[t]][n_pos[0]][n_pos[1]]=0
                        material.append([n_pos,tmp])

                    tmp_d=env.mm.description[n["type"]][n["index"]]
                    if(n["index"] in env.mm.description[n["type"]].keys()):
                        try:
                            del env.mm.description[n["type"]][n["index"]]
                        except:
                            return False,"The object you want to take is no longer here, it has just been taken away by another agent."
                        self.holding[n["index"]]=tmp_d
                        self.holding[n["index"]]["material"]=material

                        _action += " "+to_
                        self.cg_action(_action)
                    else:
                        return False,"The object you want to take is no longer here, it has just been taken away by another agent."
                    
            elif(a=="use"):
                n = env.find_area_obj_by_name(to_)
                desc=None
                if (n != None):
                    desc=n["desc"]
                else:
                    hold = [[i, re.findall(r"Name: (.*?)\n", self.holding[i]["description"])[0]] for i in
                            self.holding.keys()]
                    n = None
                    for i in range(len(hold)):
                        if (hold[i][1] == to_):
                            n = hold[i][0]
                            break
                    if (n != None):
                        desc=self.holding[n]['description']
                    else:
                        return False,"You're not holding what you're going to use right now"

                if(desc!=None):
                    cg_status(env, desc, self, "agent")
                    _action += " "+to_
                    self.cg_action(_action)
            elif (a == "apply"):
                n = env.find_area_obj_by_name(from_)
                target_type="obj"
                if (n == None):
                    n = env.agents.find_by_name(from_)
                    target_type = "agent"
                    if (n == None):
                        return False, "You can't find the object you want to act on"
                target=n

                hold = [[i, re.findall(r"Name: (.*?)\n", self.holding[i]["description"])[0]] for i in
                        self.holding.keys()]
                n = None
                for i in range(len(hold)):
                    if (hold[i][1] == to_):
                        n = hold[i][0]
                        break
                if (n == None):
                    return False, "You're not holding what you're going to apply right now"
                desc = self.holding[n]['description']
                if (desc != None):
                    if (target_type == "agent"):
                        _action = "[passive action] applied " + to_ + " by " + self.name
                        target.cg_action(_action, True)
                    cg_status(env, desc, target, target_type)

                    _action+=" "+to_+" to "+from_
                    self.cg_action(_action)


            elif (a == "put"):
                n = env.find_area_obj_by_name(from_)
                if (n != None):
                    n_pos = self.random_choose_pos(env, n["range"])
                    hold=[[i,re.findall(r"Name: (.*?)\n", self.holding[i]["description"])[0]] for i in self.holding.keys()]
                    m=None
                    for i in range(len(hold)):
                        if(hold[i][1]==to_):
                            m=hold[i][0]
                            break
                    if(m!=None):
                        basic_pos=self.pos
                        jdg=True
                        new_pos_l=[]
                        for i in self.holding[m]["material"]:
                            new_pos=(basic_pos[0]+i[0][0]-self.holding[m]["material"][0][0][0],basic_pos[1]+i[0][1]-self.holding[m]["material"][0][0][1])
                            new_pos_l.append([new_pos,i[1]])
                            if(env.mm.map_list[env.mm.map_list_index[self.holding[m]["type"]]][new_pos[0]][new_pos[1]]!=0):
                                jdg=False
                                break
                        if(jdg):
                            areas=set()
                            for new_p in new_pos_l:
                                new_pos=new_p[0]
                                env.mm.map_list[env.mm.map_list_index[self.holding[m]["type"]]][new_pos[0]][new_pos[1]]=new_p[1]
                                areas.add(new_pos)
                            self.holding[m]["area"]=areas
                            del self.holding[m]["material"]
                            env.mm.description["object"][m]=copy.deepcopy(self.holding[m])
                            del self.holding[m]

                            _action += " "+to_+" in/on "+from_
                            self.cg_action(_action)
                        else:
                            return False,"You cannot put the object here."

                    else:
                        return False,"You're not holding what you're going to put right now"
                else:
                    return False,"The location where you want to put the object does not exist."
        return True,"You have successfully completed the action you wanted to execute."


    def action_analysis(self,env,action_raw,control=False):
        type_=copy.copy(env.mm.textures.type)
        action_list=self.action_list
        holding_list=self.holding

        action=action_raw.split("\n")[0]
        action = action.replace("[", "").replace("]", "").lower()
        for i in type_:
            action = action.replace(i + ": ", "")

        jdg = False
        for i in range(len(self.action_space)):
            if (self.action_space[i].lower() in action.lower()):
                action = self.action_space[i]
                jdg = True
                break

        if (not jdg and not control):
            qst = "Determine which of the following actions corresponds to the answer \"" + action_raw + "\": " + str(
                self.action_space)
            action = self.llm.chat(qst, his=self.action_choose_example, model="llama", version="gpt-4o").replace("'","").replace(
                "\"", "")
            jdg = False
            for i in self.action_space:
                if (i in action):
                    action = i
                    jdg = True
                    break
            if(not jdg):
                print("error",action_raw)
                return [],None,""

        action_raw = action

        action = ""
        for a in action_list.keys():
            if ("←" in a):
                a = a.split("←")[0]
            elif ("→" in a):
                a = a.split("→")[0]
            if (a in action_raw):
                action = a
        obj = action_raw.replace(action + " ", "")
        if (", " in obj):
            obj=obj.split(", ")[0]

        move = None
        to_=None
        if (action in ["chat with"]):
            if(obj=="everyone"):
                to_ = obj
            else:
                move = obj
                to_ = obj
        elif (action in ["go to", "take"]):
            move = obj
            to_ = obj
        elif (action in ["use"]):
            if (obj not in [re.findall(r"Name: (.*?)\n", holding_list[i]["description"])[0] for i in holding_list.keys()]):
                move = obj
                to_ = obj
        elif (action in ["put"]):
            for i in ["in/on", "on/in", "on", "in"]:
                if (" " + i + " " in obj):
                    obj = obj.split(" " + i + " ")
                    move = obj[-1]
                    to_ = obj[0]
                    break
        elif (action in ["give","apply"]):
            if (" to " in obj):
                obj = obj.split(" to ")
                move = obj[-1]
                to_ = obj[0]

        actions = [[action, obj]]
        if (action!="go to" and move != None):
            actions = [["go to", move]] + actions
        if(action=="chat with" and to_=="everyone"):
            actions=[]
            for i in self.action_space:
                if("chat with" in i and " everyone" not in i):
                    actions.append(["chat with",i.replace("chat with ","")])

        return actions,to_,action_raw

    def get_action_space(self,env,area_n,agent_n,obj_n):
        obj={}
        obj_type=copy.copy(env.mm.textures.type)
        obj_type.remove("ground")
        for i in obj_type:
            obj[i]=[]
        for i in obj_n:
            desc=i["description"]
            name=re.findall(r"Name: (.*?)\n", desc)[0]
            type=i["type"]
            range_=list(i["area"])
            obj[type].append({"name":name,"range":range_})

        obj["area"] = []
        for i in area_n:
            if (i in env.mm.description["area"].keys()):
                area_desc = env.mm.description["area"][i]
                name = re.findall(r"Area Name: (.*?)\n", area_desc)[0]
                range_ = list(env.mm.areas[i])
                obj["area"].append({"name": name, "range": range_})

        obj["agent"] = []
        for i in agent_n:
            obj["agent"].append({"name": i.name, "range": [i.pos]})

        actions=[]
        holding_list = self.holding

        action_list=self.action_list

        #LLM GENERATION
        type_with_name=[]

        holding={}
        if(len(holding_list.keys())!=0):
            type_with_name.append("The following are the objects you hold (<type>: obj1, obj2, ...) :")
            for x in holding_list.keys():
                _name = re.findall(r"Name: (.*?)\n", holding_list[x]["description"])[0]
                try:
                    holding[holding_list[x]["type"]].append(_name)
                except:
                    holding[holding_list[x]["type"]]=[_name]

            for t in holding.keys():
                type_with_name.append(t+": "+", ".join([o for o in holding[t]]))
            type_with_name.append("")
        type_with_name.append("The following are the objects you see (<type>: obj1, obj2, ...) :")
        for t in obj.keys():
            if(len(obj[t])==0):
                continue
            type_with_name.append(t+": "+", ".join([o["name"] for o in obj[t]]))
        type_with_name.append("")
        type_with_name="\n".join(type_with_name)

        actions.append("Below are the actions you can choose to execute, where [TYPE1, TYPE2, …] represents the types of objects you can fill in; if a type is preceded by the (ONLY_HOLD) marker, it means you can only choose from the objects you possess:")
        for a_type in action_list.keys():
            from_ = None
            to_ = action_list[a_type]
            temp_desc = ""
            if ("→" in a_type):
                a_type = a_type.split("→")
                from_ = a_type[1].split("/")
                temp_desc = " in/on "

                if(a_type[0] in ["give","apply"]):
                    temp_desc = " to "
                a_type = a_type[0]

            if ("→" in a_type):
                a_type = a_type.split("→")
                from_ = a_type[1].split("/")
                temp_desc = " from "
                a_type = a_type[0]
                to_=["(ONLY_HOLD)"+i for i in to_]
            if (to_[0] == "*"):
                to_ = list(obj.keys())

            action=""
            if (a_type == "go to"):
                to_="["+", ".join(to_+["random"]) +"]"
            else:
                to_="["+", ".join(to_) +"]"
            if(from_!=None):

                from_ = "[" + ", ".join(from_) + "]"
                action=a_type+" "+to_+temp_desc+from_
            else:
                action=a_type+" "+to_

            if("chat with " in action):
                action+=" (The 'agent' can include all the people you see, such as' chat with everyone'.)"
            actions.append(action)

        actions="/----\n"+type_with_name+"\n"+"\n".join(actions)+"\n----/"

        action_space=["go to random"]
        # full action space
        for a_type in action_list.keys():
            from_=None
            to_=action_list[a_type]

            temp_desc=""
            if("→" in  a_type):
                a_type=a_type.split("→")
                from_=a_type[1].split("/")
                temp_desc = " in/on "
                if (a_type[0] in ["give", "apply"]):
                    temp_desc = " to "
                a_type = a_type[0]
                for x in holding_list.keys():
                    if(holding_list[x]["type"] in to_):
                        x_name = re.findall(r"Name: (.*?)\n", holding_list[x]["description"])[0]
                        for t in from_:
                            for o_ in obj[t]:
                                action = a_type + " " + x_name + temp_desc + o_["name"]
                                action_space.append(action)

            else:
                if ("←" in a_type):
                    a_type = a_type.split("←")
                    from_ = a_type[1].split("/")
                    temp_desc = " from "
                    a_type = a_type[0]
                if(to_[0]=="*"):
                    to_=list(obj.keys())

                for t in to_:
                    for o in obj[t]:
                        action=a_type+" "+o["name"]
                        if(from_!=None):
                            if(temp_desc==" from "):
                                from_n=None
                                for p in from_:
                                    for x in range(len(obj[p])):
                                        if(o["range"][0] in obj[p][x]["range"]):
                                            from_n=[p,x]
                                            break
                                    if(from_n!=None):
                                        break
                                if(from_n!=None):
                                    action = a_type + " " + o["name"] +temp_desc+obj[from_n[0]][from_n[1]]["name"]
                        action_space.append(action)
                if(a_type=="chat with" and len(obj['agent'])>1):
                    action_space.append("chat with everyone")
                if(a_type=="use" and len(holding.keys())>0):
                    for t_h in holding.keys():
                        for o_h in holding[t_h]:
                            action_space.append("use "+o_h)


        return actions,action_space

    def move(self,env,round=False):
        n=0
        last=self.pos
        finish=True

        while(True):
            if(len(self.path)==0):
                self.status = "none"
                break
            if(self.status!="move"):
                break
            if(round and n>=self.param["action_info"]["round_move_distance"]):
                finish = False
                break
            self.motion_n=n%len(self.materials[self.toward])
            self.pos=self.path[0]
            del self.path[0]
            if (self.pos[0]!=last[0]):
                if(self.pos[0]>last[0]):
                    self.toward=2
                else:
                    self.toward = 1
            elif (self.pos[1] != last[1]):
                if (self.pos[1] > last[1]):
                    self.toward = 0
                else:
                    self.toward = 3
            last=self.pos
            n+=1

            self.perceive(env)
            time.sleep(0.1)
        self.motion_n=1
        return finish

    def perceive(self,env,draw=True):
        mm=env.mm
        map=copy.deepcopy(mm.map_list)
        x0 = self.pos[0] - self.param["action_info"]["perceived_distance"] if self.pos[0] - self.param["action_info"]["perceived_distance"] > 0 else 0
        x1 = self.pos[0] + self.param["action_info"]["perceived_distance"] if self.pos[0] + self.param["action_info"]["perceived_distance"] < \
                                                               map.shape[1] - 1 else map.shape[1] - 1
        y0 = self.pos[1] - self.param["action_info"]["perceived_distance"] if self.pos[1] - self.param["action_info"]["perceived_distance"] > 0 else 0
        y1 = self.pos[1] + self.param["action_info"]["perceived_distance"] if self.pos[1] + self.param["action_info"]["perceived_distance"] < \
                                                               map.shape[2] - 1 else map.shape[2] - 1
        area=map[-1,self.pos[0],self.pos[1]]


        p_map=map[:,x0:x1,y0:y1]
        center=(self.pos[0]-x0,self.pos[1]-y0)
        path=find_points(p_map[1],center)
        p_map_0=np.zeros(p_map.shape)
        if(len(path)!=0):
            xs, ys = zip(*path)
            p_map_0[:, xs, ys]=p_map[:, xs, ys]

        area_perceived = list(np.unique(p_map_0[-1]))
        try:
            area_perceived.remove(0)
            # area_perceived.remove(area)
        except:
            pass
        p_map_0 = p_map_0[:-1]

        agents=[]
        p_shape=p_map_0.shape
        for i in env.agents.agent_list:
            if ((i.pos[0] - x0 in range(0, p_shape[1])) and (i.pos[1] - y0 in range(0, p_shape[2]))):
                if(p_map_0[0,i.pos[0]-x0,i.pos[1]-y0]!=0 and i.name!=self.name):
                    agents.append(i)

        objs=[]
        shape=p_map_0.shape
        for l in range(1,shape[0]):
            for i in range(shape[1]):
                for j in range(shape[2]):
                    if(p_map_0[l][i][j]==0):
                        continue
                    else:
                        if(int(p_map_0[l][i][j])==p_map_0[l][i][j]):
                            t=env.mm.textures.get_elem(num=p_map_0[l][i][j])
                            objs.append([t,(i+x0,j+y0)])

        objs_desc_index=[]
        objs_desc = []
        objs_no_desc = []
        for o in objs:

            jdg=False
            for i in env.mm.description["object"].keys():
                d=env.mm.description["object"][i]
                type=re.findall(r"Type: (.*?)\n", d["description"])[0]
                if(type==o[0].type and o[1] in d["area"]):
                    jdg = True
                    if(i not in objs_desc_index):
                        d["include"]=[]
                        objs_desc_index.append(i)
                        objs_desc.append(d)
                    objs_desc[objs_desc_index.index(i)]["include"].append(o[0])
                    break
            if(not jdg):
                if(o[0].type!="wall"):
                    objs_no_desc.append(o)

        if(area in env.mm.description["area"].keys()):
            area_desc=env.mm.description["area"][area]
        else:
            area_desc = None
        self.action_space_prompt,self.action_space=self.get_action_space(env, area_perceived, agents, objs_desc)


        desc=""
        desc+="Now you look around and realize you are in the middle of an area. "
        if(area_desc != None):
            desc+="Its description can be found in <<Description>>:\n<<\n"+area_desc+"\n>>\n"
        if (len(agents) != 0):
            desc += "\nYou can also see other people in your field of vision. They include:\n"
            desc += "\n".join(["Name: "+i.name+" - "+"The action this people is taking is: "+i.action+("\nMy cognitive description of this agent: \n"+self.object_cognitive[i.name] if i.name in self.object_cognitive.keys() else "") for i in agents])
            desc += "\n"

        if(len(objs_desc)!=0):
            desc += "\nIn addition to that, you can see some objects, which are described as seen in ## objects1 *** objects2 *** ... ##:\n##\n"
            for i in range(len(objs_desc)):
                obj_count = {}
                for name in [j.name for j in objs_desc[i]["include"]]:
                    try:
                        obj_count[name] += 1
                    except:
                        obj_count[name] = 1
                objs_desc[i]["include_count"]=[str(obj_count[i]) + " " + i for i in obj_count.keys()]
                objs_desc[i]["name"] = re.findall(r"Name: (.*?)\n", objs_desc[i]["description"])[0]
            desc += "\n***\n".join(["Include: "+", ".join(i["include_count"])+"\n"+i["description"]+("\nMy cognitive description of this object: \n"+self.object_cognitive[i["name"]] if i["name"] in self.object_cognitive.keys() else "") for i in objs_desc])
            desc += "\n##\n"

        if (len(objs_no_desc) != 0):
            obj_count={}
            for i in [i[0].name for i in objs_no_desc]:
                try:
                    obj_count[i]+=1
                except:
                    obj_count[i]=1
            desc+="\nIn addition, you can see some objects that are not described, including: "+", ".join([str(obj_count[i]) +" "+ i for i in obj_count.keys()])

        self.perception_desc = desc
        self.perception_map = p_map_0
        if(draw):
            env.draw(self.number,p_map_0,bias=(x0,y0),desc=self.get_self_desc())
            #print(env.mm.description)
