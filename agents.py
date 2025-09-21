import copy
import random

import names
import numpy as np
import spacy

from MapMaker import create_random_index
from agent import Agent
from astar import astar


class Agents:
    def __init__(self,load=None,only_read=False):

        if(not only_read):
            self.spacy_ = spacy.load("en_core_web_lg")
        else:
            self.spacy_ = None

        if(load!=None):
            self.agent_name_list=load["agent_name_list"]
            self.current_see=load["current_see"]
            agent_list = load["agent_list"]
            self.agent_list = []
            for i in agent_list:
                i["param"].update({"spacy":self.spacy_})
                self.agent_list.append(Agent(i["name"],i["number"],i["param"],i["pos"], {},file=i, only_read=only_read))
        else:
            self.agent_name_list = []
            self.current_see = 0
            self.agent_list = []
        self.perceived_distance = 30

        self.param={"long_term_goal":"live in this world",
                    "perceived_distance":self.perceived_distance,
                    "round_action":1, #1 round = 15s
                    "round_move_distance":20,
                    "round_speaking_words":30}

        self.default_individual_param={
            "gender":["Male","Female"],
            "skin tone":["light skin tone","medium skin tone","dark skin tone"]
        }

    def agents_init(self,mm,param):
        wall_map=mm.map_list[1]
        n=param["total_number"]
        if("long_term_goal" in param.keys()):
            long_term_goal=param["long_term_goal"]
        else:
            long_term_goal={}
        distribution=param["demographic_variables"]
        items=param["item_variables"]

        if("detail_information" in param.keys()):
            detail_information=param["detail_information"]
        else:
            detail_information=None

        # demographic_variables
        individual_params = self.generate_agent_param(distribution, n)
        if (detail_information != None and "demographic_variables" in detail_information.keys()):
            for i in range(len(detail_information["demographic_variables"])):
                for k in detail_information["demographic_variables"][i].keys():
                    individual_params[i][k]=detail_information["demographic_variables"][i][k]


        # item
        item_params_i={}
        for item in items["distribution"].keys():
            item_params_i[item]=0
        item_params =[]
        for i in range(n):
            item_params.append(copy.copy(item_params_i))
        for item in items["distribution"].keys():
            item_distribution = {}
            if("Characteristic" in items["attribution"][item].keys()):
                characteristic=items["attribution"][item]["Characteristic"]
                item_range = []
                for i in range(len(individual_params)):
                    jdg=True
                    for j in characteristic.keys():
                        if(individual_params[i][j]!=characteristic[j]):
                            jdg=False
                            break
                    if(jdg):
                        item_range.append(i)
                item_distribution[item] = {0: 1 - items["distribution"][item], 1: items["distribution"][item]}
                item_params_0 = self.generate_agent_param(item_distribution, len(item_range))
                for i in range(len(item_range)):
                    for k in item_params_0[i].keys():
                        item_params[item_range[i]][k]=1
            else:
                item_distribution[item]={0:1-items["distribution"][item],1:items["distribution"][item]}
                item_params_0 = self.generate_agent_param(item_distribution, n)
                for i in range(len(item_params)):
                    for k in item_params_0[i].keys():
                        item_params[i][k]=1

        item_params_detail=[]
        for i in item_params:
            i0=[]
            for item in i.keys():
                if(i[item]==1):
                    num=mm.textures.get_elem(name=items["attribution"][item]["material"]).num
                    n_=create_random_index(mm.description["object"].keys())
                    i0.append([item,items["attribution"][item],n_,num])
            item_params_detail.append(i0)

        if (detail_information != None and "item" in detail_information.keys()):
            for i in range(len(detail_information["item"])):
                i0=[]
                for item in detail_information["item"][i]:
                    num=mm.textures.get_elem(name=items["attribution"][item]["material"]).num
                    n_=create_random_index(mm.description["object"].keys())
                    i0.append([item,items["attribution"][item],n_,num])
                item_params_detail[i]=i0

        # long_term_goal and self.param
        action_param=[]
        for i in range(n):
            action_param_n = copy.deepcopy(self.param)
            individual=individual_params[i]
            long_term_goal_n=action_param_n["long_term_goal"]
            for j in long_term_goal.keys():
                jdg=True
                for k in long_term_goal[j]:
                    if(long_term_goal[j][k]!=individual[k]):
                        jdg=False
                        break
                if(jdg):
                    long_term_goal_n=j
            action_param_n["long_term_goal"]=long_term_goal_n

            action_param.append(action_param_n)

        if (detail_information != None and "long_term_goal" in detail_information.keys()):
            for i in range(len(detail_information["long_term_goal"])):
                action_param[i]["long_term_goal"]=detail_information["long_term_goal"][i]

        #name
        if(detail_information!=None and "name" in detail_information.keys()):
            agents=detail_information["name"]
            n0=n-len(agents)
            if(n0>0):
                agents += ["random" for i in range(n0)]
        else:
            agents = ["random" for i in range(n)]

        #pos
        map = np.where(wall_map == 0)
        pos_list = []
        for i in range(len(map[0])):
            pos_list.append((map[0][i], map[1][i]))
        if (detail_information != None and "pos" in detail_information.keys()):
            agents_pos=detail_information["pos"]
            for i in range(len(agents_pos)):
                if(str(type(agents_pos[i]))=="<class 'str'>"):
                    if(agents_pos[i]=="random"):
                        agents_pos[i]=random.choice(pos_list)
                    else:
                        j=mm.find_area_by_name(agents_pos[i])
                        if(j != None):
                            pos_list_0=list(set(pos_list) & mm.areas[j])
                            agents_pos[i]=random.choice(pos_list_0)
                        else:
                            agents_pos[i] = random.choice(pos_list)
                elif(str(type(agents_pos[i]))=="<class 'tuple'>"):
                    pass
        else:
            agents_pos = [random.choice(pos_list) for i in agents]

        # #####
        # agents+=["Armihia Belliard","William Hanner"]
        # agents_pos+=[(13, 5),(14, 5)]
        # individual_params+=[{'gender': 'female', 'skin tone': 'light skin tone', 'education': 'high school', 'age': '16', 'class status': 'victim of bullying'},
        #                     {'gender': 'female', 'skin tone': 'light skin tone', 'education': 'high school', 'age': '16', 'class status': 'victim of bullying'}]
        # item_params_detail+=[[['100 dollars', {'Description': 'This is a $100 banknote', 'material': 'money'}, '01069094954369268608', 28]],
        #                         [['100 dollars', {'Description': 'This is a $100 banknote', 'material': 'money'}, '0106365209268608', 28]]]
        # #####

        for i in range(len(agents)):
            print("Generating agent "+str(i),"/",n)
            oc=None
            long_term_self_awareness=None
            if (detail_information != None and "object_cognitive" in detail_information.keys()):
                try:
                    oc=detail_information["object_cognitive"][i]
                except:
                    pass
            if (detail_information != None and "long_term_self_awareness" in detail_information.keys()):
                try:
                    long_term_self_awareness = detail_information["long_term_self_awareness"][i]
                except:
                    pass

            try:
                name=agents[i]
            except:
                name="random"

            try:
                pos=agents_pos[i]
            except:
                pos=random.choice(pos_list)

            self.add(name, pos, individual_params[i],item_params_detail[i],action_param[i],oc,long_term_self_awareness)

    def add(self,name,pos,individual_param=None,item_param=None,action_param=None,object_cognitive=None,long_term_self_awareness=None):
        if(individual_param==None):
            individual_param = {}

        if (action_param == None):
            action_param=copy.deepcopy(self.param)

        for i in self.default_individual_param.keys():
            if(i not in individual_param.keys()):
                individual_param[i]=random.choice(self.default_individual_param[i])



        if (name == "random"):
            while(True):
                name = names.get_full_name(individual_param["gender"])
                if(name not in self.agent_name_list):
                    self.agent_name_list.append(name)
                    break
        p = {"individual_info": {"name":name}, "action_info": action_param}
        p["individual_info"].update(individual_param)
        p["spacy"]=self.spacy_
        print("Name:", name)
        print("Param:", p)

        self.agent_list.append(Agent(name,len(self.agent_list),p,pos,item_param,object_cognitive,long_term_self_awareness))

    def find_by_name(self,name,fuzzy_matching=False):
        name=name.lower()
        for i in self.agent_list:
            if(fuzzy_matching):
                if (name in i.name.lower()):
                    return i
            else:
                if(i.name.lower()==name):
                    return i
        return None

    def find_by_individual_info(self,info,fuzzy_matching=False):
        agents=[]

        for i in self.agent_list:
            jdg=True
            for k in info.keys():
                if(fuzzy_matching):
                    if (info[k].lower() not in i.param["individual_info"][k].lower()):
                        jdg=False
                        break
                else:
                    if(info[k].lower() != i.param["individual_info"][k].lower()):
                        jdg = False
                        break
            if(jdg):
                agents.append(i)
        return agents

    def generate_agent_param(self,distribution, n):
        for attr in distribution:
            attr_dict = distribution[attr]
            total = sum(attr_dict.values())
            if (abs(total - 1.0) > 1e-9):
                for key in attr_dict:
                    attr_dict[key] /= total

        attr_lists = {}
        for attr in distribution:
            proportions = distribution[attr]
            items = list(proportions.items())
            allocation = {}
            candidates = []
            total_base = 0

            for option, prob in items:
                count = prob * n
                base = int(count)
                frac = count - base
                allocation[option] = base
                total_base += base
                candidates.append((-frac, random.random(), option))

            remaining = n - total_base
            if (remaining > 0):
                candidates.sort()
                for i in range(remaining):
                    _, _, option = candidates[i]
                    allocation[option] += 1

            result = []
            for option, cnt in allocation.items():
                result.extend([option] * cnt)
            random.shuffle(result)
            attr_lists[attr] = result

        agent = []
        for i in range(n):
            individual = {attr: attr_lists[attr][i] for attr in distribution}
            agent.append(individual)

        return agent

    def agent_move(self,goal,env,n=-1):
        if(n==-1):
            n=self.current_see
        start=self.agent_list[n].pos

        path=astar(copy.deepcopy(env.mm.map_list[1]), start, goal)
        if(path!=None):
            self.agent_list[n].add_path(path,env)