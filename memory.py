import copy

import numpy as np
from vad import VAD
import spacy

class Element:
    def __init__(self,desc,emotion,vec,action):
        self.desc=desc
        self.emotion=emotion
        self.vector=vec
        self.action=action

class Memory:
    def __init__(self,vad=None,file=None):
        if(file!=None):
            self.memory = file
        else:
            self.memory=[]
        self.memory_range = 2 #Recent n memories
        self.associate_interval = 2 #The first n most similar memories
        self.association_range = 1 #The n memories before and after each association will be retrieved together
        self.vad=vad

    def vector_matrix(self):
        return np.array([i.vector for i in self.memory[:-self.memory_range]])

    def add(self,desc,emotion,vec,action):
        self.memory.append(Element(desc,emotion,vec,action))

    def get_memory(self):
        m=[i for i in self.memory[-self.memory_range:]]
        m_desc=["Time: "+str(len(m)-i)+(" time steps ago" if len(m)-i!=1 else " time step ago (last time)")+"\n"+m[i].desc+"\nSelected action: "+m[i].action for i in range(len(m))]
        return m_desc

    def find_most_similar(self, x_vector):
        memory_vectors=self.vector_matrix()
        if(memory_vectors.shape[0]==0):
            return [],[]
        dot_products = np.dot(memory_vectors, x_vector)

        x_norm = np.linalg.norm(x_vector)
        memory_norms = np.linalg.norm(memory_vectors, axis=1)

        epsilon = 1e-8
        cosine_similarities = dot_products / (x_norm * memory_norms + epsilon)

        # best_index = np.argmax(cosine_similarities)
        best_indexs=np.argsort(cosine_similarities)[-self.associate_interval:]
        similarities=[]
        for best_index in best_indexs:
            similarities.append(cosine_similarities[best_index])
        return best_indexs, np.array(similarities)

    def association(self,v=None):
        if(v==None):
            if(len(self.memory)==0):
                return [],[]
            v=self.memory[-1].vector
        best_indexs, similarities=self.find_most_similar(v)
        return best_indexs, similarities

    def add_desc(self,desc,action):
        if(self.vad==None):
            self.vad = VAD(spacy.load("en_core_web_lg"))
        vad, vec = self.vad.analyze_vad(desc)
        vad = self.vad.desc(vad)
        self.add(desc, vad, vec, action)

    def add_desc_list(self,desc_list,action_list):
        for i in range(len(desc_list)):
            self.add_desc(desc_list[i],action_list[i])

    def get_memory_and_association(self):
        m1="\n_______\n".join(self.get_memory())
        best_indexs, similarities=self.association()
        associations=[]
        associations_index = list(best_indexs)
        for best_index in best_indexs:
            if(best_index-1  not in associations_index and best_index-1>=0):
                associations_index.append(best_index-1)
            if (best_index + 1 not in associations_index and best_index + 1 <len(self.memory)-self.memory_range):
                associations_index.append(best_index + 1)
        associations_index.sort()
        n=len(self.memory)
        for best_index in associations_index:
            t="Time: " + (str(n - best_index) + " time steps ago") + "\n" + self.memory[best_index].desc + "\nSelected action: " + self.memory[best_index].action
            associations.append(t)
        m2 = "\n_______\n".join(associations)
        if(m2!=""):
            m1=m2+"\n_______\n"+m1
        return m1

# m=Memory(VAD(spacy.load("en_core_web_lg")))
# desc_list=[
#     "I notice William standing near the desk, his posture relaxed but attentive, as soft light from the lamp casts gentle shadows across his thoughtful expression.",
#     "Facing challenges and setbacks, people often exhibit strong emotional fluctuations, but in the face of adversity, they are the true heroes.",
#     "A person's mood is like the weather in their life, constantly changing.",
#     "In the final moments of his lonely life, what will appear before his eyes will be the past and lost things.",
#     "People are always looking back at their past, searching for meaning in life, and this is the starting point of their success.",
#     "I want to join their conversation as it will make me appear less lonely.",
#     "At the low point of life, a person will always find themselves as dim and lonely as the sunset.",
#     "I feel a quiet ache in my chest when I see them talking without me. I want to be part of something.",
#     "Everyone has their own emotional world, just like every leaf corresponds to different seasons, this is the optimistic journey of life.",
#     "I'm not sure about my current situation."
#    ]
# action_list=["action"+str(i) for i in range(len(desc_list))]
# m.add_desc_list(desc_list,action_list)
# print(m.get_memory_and_association())