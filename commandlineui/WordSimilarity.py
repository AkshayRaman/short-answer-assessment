from nltk.corpus import wordnet as wn

def getMaxSim(w1, w2):
    maxSim = None
    synsets1 = wn.synsets(w1, "n")
    synsets2 = wn.synsets(w2, "n")

    for s1 in synsets1:
        for s2 in synsets2:
            sim = s1.wup_similarity(s2)
            if maxSim == None or maxSim <sim:
                maxSim = sim
    return maxSim


s1 = raw_input("Enter string 1: ")
s2 = raw_input("Enter string 2: ")

print getMaxSim(s1, s2)
