from django.db import models
from assessment.models import *
from django.contrib.auth.models import User

class Response(models.Model):
    student_id = models.ForeignKey(User)
    question_id = models.ForeignKey(Question)
    student_answer = models.TextField(max_length=1500)

    class Meta:
        unique_together = ('student_id', 'question_id',)

    def __unicode__(self):
        return self.student_answer

class Submission(models.Model):
    student_id = models.ForeignKey(User)

    def __unicode__(self):
        return str(self.student_id.username)

