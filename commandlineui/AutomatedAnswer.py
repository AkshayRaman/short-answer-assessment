import logging
import numpy
from SpellChecker import *
#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import json
import hashlib
import re

from gensim import corpora, models, similarities
from nltk.stem.porter import *
from nltk.corpus import stopwords

import matplotlib.pyplot as plt

SCALE_FACTOR = 2.0 #total marks

def conv(x):
    if x>=0.8:
        return 1.0*SCALE_FACTOR
    if x>=0.5:
        return 0.75*SCALE_FACTOR
    if x>=0.3:
        return 0.5*SCALE_FACTOR
    if x>=0.1:
        return 0.25*SCALE_FACTOR
    return 0.0

stoplist = stopwords.words('english')

#create a stemmer
stemmer = PorterStemmer()

fp = open("data.json")
data = json.load(fp)['data']

answer_files = ["testplanmarks.txt", "transitionmarks.txt", "usabilitymarks.txt"]
q_number = 0

teacher_marks_vector = []
comp_marks_vector = []
adjusted_marks_vector = []

comment_re = re.compile('^#')

for question_data in data:

    enabled = question_data['enabled']
    if not enabled:
        continue
    
    answer_file = 'data/%s' %(answer_files[q_number]) # get answer file for current question
    q_number += 1

    question = question_data['question']
    keywords = question_data['keywords']
    keywords = [stemmer.stem(i) for i in keywords]

    save_file = hashlib.md5(question).hexdigest()

    dictionary = corpora.Dictionary.load('/tmp/%s.dict' %save_file)
    corpus = corpora.MmCorpus('/tmp/%s.mm' %save_file)
    #print(corpus)

    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=100)

    for d in open(answer_file):
        if comment_re.match(d):
            continue

        reg_number, user_answer, marks = [i.strip() for i in d.split('\t')]
        marks = float(marks)

        answer_words = user_answer.lower().split()
        answer_words = [correct(i) for i in answer_words if i not in stoplist]

        try:
            vec_bow = dictionary.doc2bow(answer_words)
            vec_lsi = []
            if vec_bow:
                vec_lsi = lsi[vec_bow] # convert the query to LSI space
            #print(vec_lsi)

            index = similarities.MatrixSimilarity(lsi[corpus]) # transform corpus to LSI space and index it
            #index.save('/tmp/%s.index' %save_file)
            #index = similarities.MatrixSimilarity.load('/tmp/%s.index' %save_file)

            sims = index[vec_lsi] # perform a similarity query against the corpus
            #print(list(enumerate(sims))) # print (document_number, document_similarity) 2-tuples

            sims = sorted(enumerate(sims), key=lambda item: -item[1])
            #print(sims) # print sorted (document number, similarity score) 2-tuples

            all_marks = [i[1] for i in sims]
            avg = sum(all_marks)/len(all_marks)

            print reg_number, marks, avg*SCALE_FACTOR
            teacher_marks_vector.append(marks)
            comp_marks_vector.append(avg*SCALE_FACTOR)

            #adjusted_marks_vector.append(conv(avg))

        except:
            pass

        '''
        stemmed_answer_words = stemmer.stem(user_answer) #[stemmer.stem(i) for i in answer_words]

        keyword_count = 0
        for keyword in keywords:
            if keyword in answer_words:
                keyword_count+=1

        print "Keywords reached: %s/%s" %(keyword_count, len(keywords))
        '''

    print "Cumulative Correlation is %s" %numpy.corrcoef(teacher_marks_vector, comp_marks_vector)
    print "-"*50

    plt.title("Comparison between human assessment and automated assessment")
    plt.plot(teacher_marks_vector)
    plt.plot(comp_marks_vector)
    plt.legend(('Teacher', 'Computer'))

    #print numpy.corrcoef(teacher_marks_vector, adjusted_marks_vector)
    #plt.plot(adjusted_marks_vector)

    plt.show()
    #raw_input("Press enter to continue..")
