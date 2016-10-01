from django.db import models

class Question(models.Model):
    question_text = models.CharField("Question", max_length=255, unique=True)

    def __unicode__(self):
        return self.question_text

    class Meta:
        ordering = ['pk']

class ReferenceAnswer(models.Model):
    question = models.ForeignKey(Question)
    ref_answer_text = models.TextField("Reference Answer", max_length=1500)

    def __unicode__(self):
        return self.ref_answer_text

    class Meta:
        ordering = ['pk']

