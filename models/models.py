from random import randint
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from .constants import WAITING, QUESTION, ANSWER, LEADERBOARD


# Create your models here.
class User(AbstractUser):
    '''Default user class, just in case we want
    to add something extra in the future '''
    pass


class Questionnaire(models.Model):
    '''Questionnaire model'''
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta():
        ordering = ['title']


class Question(models.Model):
    '''Question model'''
    question = models.CharField(max_length=255)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    answerTime = models.IntegerField(default=10)

    class Meta():
        ordering = ['question']

    def __str__(self):
        return self.question


class Answer(models.Model):
    '''Answer model'''
    answer = models.CharField(max_length=255)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return self.answer


class Game(models.Model):
    '''Game model'''

    CHOICES = {
        (WAITING, 'Waiting'),
        (QUESTION, 'Question'),
        (ANSWER, 'Answer'),
        (LEADERBOARD, 'Leaderboard'),
    }

    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    state = models.PositiveIntegerField(default=1, choices=CHOICES)
    publicId = models.IntegerField(unique=True)
    countdownTime = models.IntegerField(default=10)
    questionNo = models.IntegerField(default=0)

    def __str__(self):
        return str(self.publicId) + " " + str(self.state)

    def save(self, *args, **kwargs):
        if self.publicId is None:
            self.publicId = randint(1, 10**6)
        super(Game, self).save(*args, **kwargs)


class Participant(models.Model):
    '''Participant model'''
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    alias = models.CharField(max_length=25)
    points = models.IntegerField(default=0)
    uuidP = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.alias + " " + str(self.uuidP)


class Guess(models.Model):
    '''Guess model'''
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    # El juego deberia estar en modo QUESTION??
    # def __str__(self):
    #     return self.answer
    def __str__(self):
        return str(self.participant) + " " + str(self.answer)

    def save(self, *args, **kwargs):
        if self.answer.correct:
            self.participant.points += 1
            self.participant.save()
        super(Guess, self).save(*args, **kwargs)
