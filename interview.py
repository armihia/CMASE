import random

from env import Env

def find_agent(agents,name=None,individual_info=None):
    if(name!=None):
        return agents.find_by_name(name,fuzzy_matching=True)
    elif(individual_info!=None):
        return agents.find_by_individual_info(individual_info,fuzzy_matching=True)
    return None

e=Env(None, None, "env file/auto_save_50.dill")

with open("prompt example/interview-example.txt","r",encoding="utf-8") as f:
    interview_example=[i.split("——") for i in f.read().split("\n+++++\n")]

name="Yeon-seo Choi"
# individual_info={'gender': 'Male', 'skin tone': 'dark skin tone', 'education': 'high school', 'age': '17', 'class status': 'normal student'}
agent=find_agent(e.agents,name=name)
#agents=find_agent(e.agents,individual_info=individual_info)
# agent=random.choice(agents)

while(True):
    q=input("qst:")

    _action="[passive action] chatted up by interviewer: '"+q+"'"
    agent.cg_action(_action,True)

    t=agent.get_self_desc(False)

    t += "\nNow you need to respond to the reviewer's questions. You are required to include in your response a description of your awareness of your own short-term situation, a new short-term goal, and a cognitive description of the interviewer. Your reply format should be as follows:\n"
    t += "short-term situational cognition: 'Your description of your own short-term situation'\n"
    t += "short-term goal: 'The new short-term goal you have formulated'\n"
    t += "interviewer cognitive description: 'Your new cognitive description of the interviewer'\n"
    t += "chat content: 'What you want to say to interviewer.'"

    with open("test.txt", "w") as f:
        f.write(t)

    while(True):
        asw_raw = agent.llm.chat(t, his=interview_example, model="gpt", version="gpt-4o")

        asw = agent.asw_analysis(asw_raw)
        if("chat content" in asw.keys()):
            break
        else:
            print("error",asw_raw)
    # for i in asw.keys():
    #     print(i,": ",asw[i],"\n\n")
    action_raw="chat with interviewer: "+asw["chat content"]

    if ("short-term goal" in asw.keys()):
        agent.short_term_goal = asw["short-term goal"]
    else:
        agent.short_term_goal = "none"
    if ("short-term situational cognition" in asw.keys()):
        agent.short_term_situational_cognition = asw["short-term situational cognition"]
    if(len(agent.condition)!=0):
        agent.short_term_situational_cognition += "\n"+"\n".join(agent.condition)

    vad,vec=agent.vad_model.analyze_vad(agent.short_term_situational_cognition)
    agent.vad=agent.vad_model.desc(vad)

    agent.memory.add(agent.short_term_situational_cognition,agent.vad,vec,action_raw)

    if ("interactive object cognitive description" in asw.keys()):
        agent.object_cognitive["interviewer"] = asw["interactive object cognitive description"]
    content = asw["chat content"]

    agent.cg_action(action_raw,l=1000)

    print("asw: ",content)