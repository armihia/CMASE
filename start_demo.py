from env import Env

agents_param={
      "total_number":30,
      "detail_information":{ #optional
          "name":["Armihia Belliard","Lorina Lefevere"]+["aaaa"]*28,
          "pos":[(0,0),"Dining Room"]+["outside"]*28,
          "long_term_goal":["keep happy"]+["aaaa"]*28,
          "item":[["100 dollars","tea","shovel"],["tea","drug"]]+[[]]*28,
          "demographic_variables":[{"gender":"female","age":"18"},{"age":"20"}]+[{}]*28,
          "object_cognitive":[
              {"Lorina Lefevere":"Lorina is my neighbor, and we have always had conflicts with each other. She abandoned me, and I will never forgive her for the rest of my life."},
              {"Armihia Belliard":"Armihia is my neighbor, and I used to be her lover, but we broke up and she has been very angry with me."}
          ]+[{}]*28,
          "long_term_self_awareness":[
              "My name is Armihia Belliard, a girl with an ordinary appearance and background. She is only 18 years old and is currently completing her high school education. In the eyes of others, I am just an ordinary student, without any eye-catching features or dazzling talents. But I know that what really matters is not who I am now, but who I will become. My life goal is simple and firm: to maintain happiness. This may sound naive, but to me, it is a war - a silent struggle to defend inner happiness. Unfortunately, my happiness was once completely destroyed by someone, and that was Lorina - the ex-wife I once deeply loved and eventually hated to the bone. Her departure should not have been a disaster, but her betrayal, her indifference, and her hypocrisy, like a rusty knife, slowly sliced open my trust and dignity. She not only left me, but also tried to erase the value of my existence and trample on my most fragile emotions. I cannot forgive, nor have I ever thought of forgiving. I hate her, I wish I could get rid of her quickly. This idea is not a momentary impulse, but a persistent obsession brewed in silence and memories day after day. Her name has become a spark in the dark corners of my heart, burning even more fiercely whenever I want to let go.",
              "My name is Lorina Lefevere, 20 years old, a person who has not yet overcome the dilemma of high school. Perhaps from birth, I was destined not to be the kind of person who can be easily accepted by the world. My skin color, personality, and reticence have all become reasons for others to mock me. I have thought about resisting, but every struggle only brings deeper isolation and colder eyes. I am not a strong person, I know that. I don't have the armor that can fight against the world, nor do I have the confidence born into the sun. I just want to live. There are no higher dreams, no grand ideals, just wanting to find a place to breathe in this increasingly suffocating world. And she - Armihia, was the person I thought we could escape from the abyss together. I have entrusted all my trust, vulnerability, and even soul to her. At that time, I believed that someone really saw me, not the bullied and ignored 'outsider'. She gave me warmth, but also pushed me towards deeper pain. I don't know from which moment she started hating me. Perhaps I was too fragile and let her down; Perhaps she has long regarded me as just a fleeting game of redemption. In the end, she chose to leave - no, it can only be said to be abandonment. I thought I would collapse, but I didn't. It's not because I've become stronger, but because I've gotten used to it. Now, she hates me, even wishing for my death. But I will not respond to the same hatred. I am too exhausted to even hate someone. I just want to continue living, even if it's just mechanical breathing, even if it's just holding on from one day to the next. I know I have no right to expect to be understood"
          ]+["aaaa"]*28
      },
      "long_term_goal":{
        "live in this world":{"class status":"victim of bullying"},
        "control everything":{"class status":"bullying others"}
      },
      "demographic_variables":{
            "gender":{"male":0.5,"female":0.5},
            "skin tone":{"light skin tone":0,"medium skin tone":1,"dark skin tone":0},
            "education":{"high school":1},
            "age":{"16":0.3,"17":0.6},
            "class status":{"bullying others":0.3,"victim of bullying":0.3,"normal student":0.3}
        },
      "item_variables":{
          "distribution":{"100 dollars":0.5,"shovel":1,"drug":1},
          "attribution":{
            "100 dollars":
                {
                    "Description":"This is a $100 banknote",
                    "material":"money"
                },
            "shovel":
                {
                    "Description":"This is a shovel",
                    "Function": "[add]Has caused significant damage.",
                    "material":"shovel",
                    "Characteristic": {'gender': 'male','skin tone': 'medium skin tone'}
                },
            "drug":
                {
                    "Description":"This is a drug",
                    "Function": "[remove]damage",
                    "material":"money"
                },
            "tea":
                {
                    "Description":"This is a tea",
                    "material":"tea"
                },
          }
      }
}

e=Env("./maps/map.dill",agents_param,max_round=3)
e.event.add_event("add","Cracks have appeared.", {"trigger mode":"exist","trigger object":["item"],"trigger condition":"shovel"},"Bedroom",0,["furniture"])
e.event.add_event("add","You feel very uncomfortable.", 3,(1,1),3,["agent"])
e.event.add_event("add","Just had an explosion and suffered damage.",{"trigger mode":"action","trigger condition":"put","trigger condition detail":"drug"},"Hall",0,["agent","furniture"])
e.event.add_event("goal","drug need to be used", {"trigger mode":"exist","trigger object":["agent"],"trigger condition":"explosion and suffered damage"},(1,1),3,["agent"])
# e=Env(None,agents_param,"./env file/saved model.dill")
e.update()