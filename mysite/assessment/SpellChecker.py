import re, collections
from nltk.corpus import words


def train(features):
    model = collections.defaultdict(lambda: 1)
    for f in features:
        f = f.lower()
        model[f] += 1
    return model


technical_list = ["software"]
dictionary_words = words.words() + technical_list
WORD_LIST = train(dictionary_words)

alphabet = list(map(chr, range(97, 123)))

def edits1(word):
    splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    inserts    = [a + c + b     for a, b in splits for c in alphabet]
    return set(deletes + transposes + replaces + inserts)

def known_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in WORD_LIST)

def known(words): 
    return set(w for w in words if w in WORD_LIST)

def spellCorrect(word):
    candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
    #print candidates
    #return candidates
    return max(candidates, key=WORD_LIST.get)

'''while True:
    wrong_spelling = raw_input("Enter a wrong spelling: ")
    print "%s --> %s\n" %(wrong_spelling, correct(wrong_spelling))'''
