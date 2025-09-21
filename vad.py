import numpy as np
import re
import spacy

class VAD:
    def __init__(self,spacy):
        self.vad_prototypes = {
            'anger': np.array([-0.43, 0.67, 0.34]),
            'joy': np.array([0.76, 0.48, 0.35]),
            'surprise': np.array([0.40, 0.67, -0.13]),
            'disgust': np.array([-0.60, 0.35, 0.11]),
            'fear': np.array([-0.64, 0.60, -0.43]),
            'sadness': np.array([-0.63, 0.27, -0.33])
        }

        self.vad_dict = {}
        with open("emotion dict/NRC-VAD-Lexicon-v2.1.txt", "r") as f:
            for line in f:
                word, valence, arousal, dominance = line.strip().split("\t")
                self.vad_dict[word] = {
                    'valence': float(valence),
                    'arousal': float(arousal),
                    'dominance': float(dominance)
                }
        self.phrase_dict = set()
        self.dict_max_len = 0
        for phrase in list(self.vad_dict.keys()):
            words = tuple([re.sub(r'^\W+|\W+$', '', word.lower()) for word in phrase.split()])
            self.phrase_dict.add(words)
            if len(words) > self.dict_max_len:
                self.dict_max_len = len(words)

        self.spacy = spacy

    def remove_punct_regex(self,text):
        return re.sub(r'[^\w\s]', '', text)


    def analyze_vad(self,sentence): #max=1,min=-1
        sentence=self.remove_punct_regex(sentence)
        s_nlp=self.spacy(sentence)

        vec=s_nlp.vector
        words = [token.lemma_ for token in s_nlp]
        words = [word.lower() for word in words if word]
        words = self.tokenize_sentence(words)

        v, a, d = [], [], []

        for word in words:
            if word in self.vad_dict:
                v.append(self.vad_dict[word]['valence'])
                a.append(self.vad_dict[word]['arousal'])
                d.append(self.vad_dict[word]['dominance'])
        return {
            'valence': np.mean(v) if v else 0,
            'arousal': np.mean(a) if a else 0,
            'dominance': np.mean(d) if d else 0
        },vec

    def vad_to_emotion_probs(self,vad):
        vad_input = np.array([vad['valence'],vad['arousal'],vad['dominance']])
        distances = []
        for emotion in self.vad_prototypes:
            dist = np.linalg.norm(vad_input - self.vad_prototypes[emotion])
            distances.append(1-dist/2)
        sum_=np.sum(distances)
        distances=[i/sum_ for i in distances]
        return dict(zip(self.vad_prototypes.keys(), distances))

    def desc(self,vad):
        vad_r={}
        max_=1
        min_=-1
        t1 = (max_ - min_) / 5 + min_
        t2 = (max_ - min_) / 5 * 2 + min_
        t3 = (max_ - min_) / 5 * 3 + min_
        t4 = (max_ - min_) / 5 * 4 + min_

        for i in vad.keys():
            if (vad[i] < t1):
                vad_r[i] = "low"
            elif (vad[i] > t1 and vad[i] <= t2):
                vad_r[i] = "relatively low"
            elif (vad[i] > t3 and vad[i] <= t4):
                vad_r[i] = "relatively high"
            elif (vad[i] > t4):
                vad_r[i] = "high"
            else:
                vad_r[i] = "medium"
        return vad_r

    def tokenize_sentence(self,words):
        i = 0
        result = []
        while i < len(words):
            current_max = min(self.dict_max_len, len(words) - i)
            found = False
            for j in range(current_max, 0, -1):
                candidate = tuple(words[i:i + j])
                if candidate in self.phrase_dict:
                    result.append(' '.join(candidate))
                    i += j
                    found = True
                    break
            if not found:
                i += 1
        return result

# spacy=spacy.load("en_core_web_lg")
# vad=VAD(spacy)
#
# t=[
#     "The printer in the office, is printing A4 paper.",
#    "I won the Nobel Prize and got married with my beloved in the cherry blossom rain",
#    "volcanic eruption Magma engulfs the village! Survivors flee for their lives amidst screams!",
#    "The emperor struck the ground with a scepter and ordered a 100000 strong army to launch a total attack immediately!",
#     "I notice William standing near the desk, his posture relaxed but attentive, as soft light from the lamp casts gentle shadows across his thoughtful expression.",
#     "I'm not sure about my current situation."
#    ]
#
# for sentence in t:
#     result,vec = vad.analyze_vad(sentence)
#     r=vad.desc(result)
#     print(r)
#     print(f"Valence: {result['valence']:.2f},Arousal: {result['arousal']:.2f},Dominance: {result['dominance']:.2f}",vad.vad_to_emotion_probs(result))
