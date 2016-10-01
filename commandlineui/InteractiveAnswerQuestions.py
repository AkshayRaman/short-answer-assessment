import logging
#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import json
import hashlib

from gensim import corpora, models, similarities
from nltk.stem.porter import *

#create a stemmer
stemmer = PorterStemmer()

fp = open("data.json")
data = json.load(fp)['data']

q_number = 0

for question_data in data:

    enabled = question_data['enabled']

    if not enabled:
        continue

    q_number += 1
    question = question_data['question']
    keywords = question_data['keywords']
    keywords = [stemmer.stem(i) for i in keywords]

    save_file = hashlib.md5(question).hexdigest()

    dictionary = corpora.Dictionary.load('/tmp/%s.dict' %save_file)
    corpus = corpora.MmCorpus('/tmp/%s.mm' %save_file)
    #print(corpus)

    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=200)

    user_answer = raw_input("\nQuestion %s: %s\n" %(q_number, question))
    answer_words = user_answer.lower().split()

    vec_lsi = []
    vec_bow = dictionary.doc2bow(answer_words)
    if vec_bow:
        vec_lsi = lsi[vec_bow] # convert the query to LSI space
    #print(vec_lsi)

    index = similarities.MatrixSimilarity(lsi[corpus]) # transform corpus to LSI space and index it

    #index.save('/tmp/%s.index' %save_file)
    #index = similarities.MatrixSimilarity.load('/tmp/%s.index' %save_file)

    sims = index[vec_lsi] # perform a similarity query against the corpus
    #print(list(enumerate(sims))) # print (document_number, document_similarity) 2-tuples

    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    print(sims) # print sorted (document number, similarity score) 2-tuples
    avg = sum(i[1] for i in sims)/len(sims)
    print avg

    stemmed_answer_words = stemmer.stem(user_answer) #[stemmer.stem(i) for i in answer_words]

    keyword_count = 0
    for keyword in keywords:
        if keyword in stemmed_answer_words:
            keyword_count+=1

    print "Keywords reached: %s/%s" %(keyword_count, len(keywords))
