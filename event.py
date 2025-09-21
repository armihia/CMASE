import re

import numpy as np


class Event:
    def __init__(self,type_,desc,time,pos,range_,target):

        self.type=type_ #add/remove/goal
        self.desc=desc

        # When 'time' is an int, it is a round number, and when it is a dict, it is a triggering condition
        if (str(type(time)) == "<class 'int'>"):
            self.pattern = "schedule"
        elif (str(type(time)) == "<class 'dict'>"):
            #{"trigger mode":"exist"/"action","trigger object":["item","furniture","agent"],"trigger condition":"..."/"*"/"all","trigger condition detail":"..."/"*"/"all"}
            self.pattern = "trigger"
        self.time=time

        self.pos=pos
        self.range=range_
        range_=set()
        if (str(type(self.pos)) == "<class 'tuple'>"):
            for i in range(self.range):
                for j in range(self.range):
                    range_.add((self.pos[0] + i, self.pos[1] + j))
                    range_.add((self.pos[0] - i, self.pos[1] + j))
                    range_.add((self.pos[0] + i, self.pos[1] - j))
                    range_.add((self.pos[0] - i, self.pos[1] - j))
        self.range_detail=range_
        self.target=target

class EventController:
    def __init__(self):
        self.events=[]

    def add_event(self,type,desc,time,pos,range_,target):
        self.events.append(Event(type,desc,time,pos,range_,target))

    def event_jdg(self,env):
        e=[]
        for ev in self.events:
            if(ev.pattern== "schedule" and ev.time<=env.round):
                e.append(ev)
            elif(ev.pattern== "trigger"):
                agents, objs = self.range_detect(env,ev)
                trigger=ev.time
                if(trigger["trigger mode"]=="exist"):
                    obj=trigger["trigger object"]
                    condition = trigger["trigger condition"].lower()

                    if(condition in ["*","all"]):
                        e.append(ev)
                        continue

                    trigger_jdg=False
                    for o in obj:
                        if(o=="agent"):
                            for a in agents:
                                if(condition in a.short_term_situational_cognition.lower() or condition in " ".join(a.condition).lower()):
                                    e.append(ev)
                                    trigger_jdg = True
                                    break
                        elif (o in ["item","furniture"]):
                            for a in objs:
                                if(env.mm.description["object"][a["index"]]["type"]==o):
                                    if(condition in a["desc"]):
                                        e.append(ev)
                                        trigger_jdg = True
                                        break
                        if(trigger_jdg):
                            break
                elif (trigger["trigger mode"] == "action"):
                    condition = trigger["trigger condition"].lower()
                    condition_detail = ""
                    if("trigger condition" in trigger.keys() and trigger["trigger condition"] not in ["*","all"]):
                        condition_detail = trigger["trigger condition"].lower()
                    if(len(agents)!=0):
                        if (condition in ["*", "all"]):
                            e.append(ev)
                        else:
                            for a in agents:
                                print(a.action,condition,condition_detail)
                                if (condition in a.action.lower() and condition_detail in a.action.lower()):
                                    e.append(ev)
                                    break


        for e_ in e:
            self.events.remove(e_)
        return e

    def range_detect(self,env,e):
        agents = []
        objs = []
        range_ = set()
        if (str(type(e.pos)) == "<class 'tuple'>"):
            range_ = e.range_detail
        elif (str(type(e.pos)) == "<class 'str'>"):
            jdg = False
            for i in env.mm.description["area"].keys():
                if (re.findall(r"Area Name: (.*?)\n", env.mm.description["area"][i])[0].lower().replace(" ",
                                                                                                         "") == e.pos.lower().replace(
                        " ", "")):
                    x, y = np.where(env.mm.map_list[-1] == i)
                    for j in range(len(x)):
                        range_.add((x[j], y[j]))
                    jdg = True
                    break
            if (not jdg):
                return agents,objs

        for obj in e.target:
            if (obj == "agent"):
                for a in env.agents.agent_list:
                    if (tuple(a.pos) in range_):
                        agents.append(a)
            elif (obj in ["furniture", "item"]):
                for i in env.mm.description["object"].keys():
                    for j in list(env.mm.description["object"][i]["area"]):
                        if (j in range_):
                            desc = env.mm.description["object"][i]["description"]
                            range0 = env.mm.description["object"][i]["area"]
                            n = re.findall(r"Name: (.*?)\n", desc)[0]
                            objs.append({"name": n, "range": range0, "type": "object", "desc": desc, "index": i})
                            break
        return agents,objs

# ec=EventController()
# ec.add_event("add","aaaaa",5,(10,10),3,["agent"])
# print(ec.event_jdg(5))