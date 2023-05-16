from django.contrib import admin
from .models import Participant, Questionnaire
from .models import Question, Answer, Game, User, Guess
# Register your models here.
admin.site.register(Participant)
admin.site.register(Answer)
admin.site.register(User)
admin.site.register(Guess)


class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'user')


admin.site.register(Questionnaire, QuestionnaireAdmin)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'questionnaire', 'created_at',
                    'updated_at', 'answerTime')


admin.site.register(Question, QuestionAdmin)


class GameAdmin(admin.ModelAdmin):
    list_display = ('questionnaire', 'created_at', 'state',
                    'publicId', 'countdownTime', 'questionNo')


admin.site.register(Game, GameAdmin)
