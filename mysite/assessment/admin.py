from django.contrib import admin
from assessment.models import Question, ReferenceAnswer

admin.site.site_header = "Adminstrator Portal"

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

class RefAnswerInLine(admin.TabularInline):
    model = ReferenceAnswer
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [ (None, {'fields': ['question_text']}), ]
    inlines = [RefAnswerInLine]
    search_fields = ['question_text']

    #def has_add_permission(self, request):
    #    return False

admin.site.register(Question, QuestionAdmin)
