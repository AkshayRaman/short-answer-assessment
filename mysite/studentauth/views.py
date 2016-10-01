from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from assessment.models import *
from studentauth.models import *

import re

def view_page(request):
    if not request.user.is_authenticated():
        state = "You must be logged in to view this page!"
        return render_to_response('studentauth.html',{'state':state,'title':"Login"},context_instance=RequestContext(request))
    
    if Submission.objects.filter(student_id=request.user).exists():
        print "You have already completed this test!"
        return render_to_response('test_complete.html',{'error':"You have already completed this test!",'title':"Error"})
    
    questionList = Question.objects.order_by('?')
    return render_to_response('main_page.html',{'questionList':questionList,'user':request.user,'title':"Portal"}, context_instance=RequestContext(request))

def submit(request):
    if request.POST:
        data = request.POST
        user = request.user

        if Submission.objects.filter(student_id=user).exists():
            print "You have already completed this test!"
            return render_to_response('test_complete.html',{'error':"You have already completed this test!"})

        question_re = re.compile('^question(\d+)$')
        for i in data:
            matches = question_re.match(i)
            if matches:
                #validate question id
                question = Question.objects.filter(id=int(matches.group(1)))[0]

                if question:
                    question = question
                    answer = data.get(i).strip()

                    obj,created = Response.objects.update_or_create(question_id=question, student_id=user, defaults = {"student_answer":answer} )

        s = Submission()
        s.student_id = user
        s.save()        
        return render_to_response('test_complete.html',{'data':data,'user':user})
    return redirect('/view_page/')

def logout_user(request):
    logout(request)
    state = "You have been logged out!"
    return render_to_response('studentauth.html',{'state':state,'title':"Login"},context_instance=RequestContext(request))


def login_user(request):
    state = ""
    username = password = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                if user.groups.filter(name='student').exists():
                    state = "You're successfully logged in!"
                    return redirect('/view_page/')
                else:
                    state = "This login is for students only!"
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."
    return render_to_response('studentauth.html',{'state':state, 'username': username, 'title':"Login"},context_instance=RequestContext(request))
