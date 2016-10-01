import logging
#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import json
import hashlib
import string

from gensim import corpora, models, similarities
from nltk.corpus import stopwords

#common word list
stoplist = stopwords.words('english') 

fp = open("data.json")
data = json.load(fp)['data']

for question_data in data:
    enabled = question_data['enabled']
    if not enabled:
        continue

    question = question_data['question']
    answer_list = question_data['answers']
    keywords = question_data['keywords']
    #print question, answer_list, keywords

    save_file = hashlib.md5(question).hexdigest()

    # remove common words, punctuation and tokenize
    texts = [[word.translate(string.punctuation).strip() for word in answer.lower().split() if word not in stoplist] for answer in answer_list]

    # remove words that appear only once
    all_tokens = sum(texts, [])
    tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
    texts = [[word for word in text if word not in tokens_once] for text in texts]
    print texts

    dictionary = corpora.Dictionary(texts)
    dictionary.save("/tmp/%s.dict" %save_file) # store the dictionary, for future reference

    print(dictionary)
    print(dictionary.token2id)

    corpus = [dictionary.doc2bow(text) for text in texts]
    corpora.MmCorpus.serialize('/tmp/%s.mm' %save_file, corpus) # store to disk, for later use
    print(corpus)
