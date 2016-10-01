from django.shortcuts import render
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.db.models import Count

from assessment.models import *
from studentauth.models import *

from SpellChecker import *

import re
import logging
#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import json
import hashlib
import string

from gensim import corpora, models, similarities
from nltk.corpus import stopwords
from nltk.stem.porter import *

def createCorpus(questionList):
    #common word list
    stoplist = stopwords.words('english')

    for question in questionList:
        ref_answers = ReferenceAnswer.objects.filter(question_id=question).order_by('id')
        if ref_answers:
            answer_list = []
            for answer in ref_answers:
                answer_list.append(answer.ref_answer_text)

            #print answer_list
            save_file = hashlib.md5(str(question.id)).hexdigest()

            # remove common words, punctuation and tokenize
            texts = [[word.translate(string.punctuation).strip() for word in answer.lower().split() if word not in stoplist] for answer in answer_list]

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

def lookUpScore(questionId, user_answer):
    stoplist = stopwords.words('english')

    #create a stemmer
    stemmer = PorterStemmer()

    save_file = hashlib.md5(str(questionId)).hexdigest()

    dictionary = corpora.Dictionary.load('/tmp/%s.dict' %save_file)
    corpus = corpora.MmCorpus('/tmp/%s.mm' %save_file)

    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=100)

    answer_words = user_answer.lower().split()
    answer_words = [spellCorrect(i) for i in answer_words if i not in stoplist]

    try:
        vec_bow = dictionary.doc2bow(answer_words)
        vec_lsi = []
        if vec_bow:
            vec_lsi = lsi[vec_bow] # convert the query to LSI space
        
        index = similarities.MatrixSimilarity(lsi[corpus]) # transform corpus to LSI space and index it

        sims = index[vec_lsi] # perform a similarity query against the corpus
        #sims = sorted(enumerate(sims), key=lambda item: -item[1])
        return list(sims)
    except:
        return None

def correct_answers(request):
    questionList = Question.objects.all().order_by("id")
    createCorpus(questionList)

    questions = []
    for i in questionList:
        questions.append(i.question_text)

    consolidated_data = {}

    studentSubmittedList = Response.objects.values('student_id').distinct()
    for studentSubmitted in studentSubmittedList:
        currStudentId = studentSubmitted['student_id']
        currStudentName = User.objects.filter(id=currStudentId)[0]
        responses = Response.objects.filter(student_id=currStudentId)
        answerCount = len(responses)
        for response in responses:
            #computing score
            scores = lookUpScore(response.question_id.id, response.student_answer)

            #print currStudentName, {response.question_id.id: scores}
            if currStudentName.username not in consolidated_data:
                consolidated_data[currStudentName.username] = []
            consolidated_data[currStudentName.username].append({response.question_id.id: (response.student_answer, sum(scores)*2.0/len(scores))})

    for x in consolidated_data:
        consolidated_data[x] = sorted(consolidated_data[x])

    pass_this = {"consolidated_data":consolidated_data, "title":"Results", "answerCount":range(1,answerCount+1),"questions":questions}
    return render_to_response('result.html', pass_this, context_instance=RequestContext(request))
