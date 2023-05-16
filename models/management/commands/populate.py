# Populate database
# This file has to be placed within the
# catalog/management/commands directory in your project.
# If that directory doesn't exist, create it.
# The name of the script is the name of the custom command,
# that is, populate.py.
#
# execute python manage.py  populate
#
# use module Faker generator to generate data
# (https://zetcode.com/python/faker/)
import os
import random

from django.core.management.base import BaseCommand
from models.models import User as User
from models.models import Questionnaire as Questionnaire
from models.models import Question as Question
from models.models import Answer as Answer
from models.models import Game as Game
from models.models import Participant as Participant
from models.models import Guess as Guess
import models.constants as constants

from faker import Faker

# The name of this class is not optional must be Command
# otherwise manage.py will not process it properly


class Command(BaseCommand):
    # helps and arguments shown when command python manage.py help populate
    # is executed.
    help = """populate kahootclone database
           """
    # if you want to pass an argument to the function
    # uncomment this line
    # def add_arguments(self, parser):
    #    parser.add_argument('publicId',
    #        type=int,
    #        help='game the participants will join to')
    #    parser.add_argument('sleep',
    #        type=float,
    #        default=2.,
    #        help='wait this seconds until inserting next participant')

    def __init__(self, sneaky=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # "if 'RENDER'" allows you to deal with different
        # behaviour in render.com and locally
        # That is, we check a variable ('RENDER')
        # that is only defined in render.com
        if 'RENDER' in os.environ:
            pass
        else:
            pass

        self.NUMBERUSERS = 4
        self.NUMBERQESTIONARIES = 30
        self.NUMBERQUESTIONS = 100
        self.NUMBERPARTICIPANTS = 20
        self.NUMBERANSWERPERQUESTION = 4
        self.NUMBERGAMES = 4

    # handle is another compulsory name, do not change it"
    # handle function will be executed by 'manage populate'
    def handle(self, *args, **kwargs):
        "this function will be executed by default"

        self.cleanDataBase()   # clean database
        # The faker.Faker() creates and initializes a faker generator,
        self.faker = Faker()
        self.user()  # create users
        self.questionnaire()  # create questionaries
        self.question()  # create questions
        self.answer()  # create answers
        self.game()  # create games

    def cleanDataBase(self):
        # delete all models stored (clean table)
        # in database
        # order in which data is deleted is important
        Guess.objects.all().delete()
        Answer.objects.all().delete()
        Question.objects.all().delete()
        Questionnaire.objects.all().delete()
        Participant.objects.all().delete()
        Game.objects.all().delete()
        User.objects.all().delete()
        print("clean Database")

    def user(self):
        " Insert users"
        print("Users")
        # create user
        for _ in range(self.NUMBERUSERS):
            username = self.faker.user_name()
            email = self.faker.email()
            password = self.faker.password()
            user = User.objects.create_user(
                username=username, email=email, password=password)
            user.save()

    def questionnaire(self):
        "insert questionnaires"
        print("Questionnaire")
        # assign users randomly to the questionnaires
        for _ in range(self.NUMBERQESTIONARIES):
            title = self.faker.sentence(nb_words=3, variable_nb_words=True)
            owner = User.objects.order_by("?").first()
            questionnaire = Questionnaire(
                title=title, user=owner)
            questionnaire.save()

    def question(self):
        " insert questions, assign randomly to questionnaires"
        print("Question")
        # assign questions randomly to the questionnaires
        for _ in range(self.NUMBERQUESTIONS):
            question = self.faker.text()
            questionnaire = Questionnaire.objects.order_by("?").first()
            answerTime = random.randint(5, 10)
            question = Question(
                question=question, questionnaire=questionnaire,
                answerTime=answerTime)
            question.save()

    def answer(self):
        "insert answers, one of them must be the correct one"
        print("Answer")
        # assign answer randomly to the questions
        # maximum number of answers per question is four
        for question in Question.objects.all():
            correct_answer = self.faker.word()
            answer_choices = [correct_answer]
            for _ in range(self.NUMBERANSWERPERQUESTION - 1):
                answer_choices.append(self.faker.word())

            random.shuffle(answer_choices)

            for answer_text in answer_choices:
                is_correct = answer_text == correct_answer
                answer = Answer(answer=answer_text,
                                correct=is_correct, question=question)
                answer.save()

    def game(self):
        "insert some games"
        print("Game")
        # choose at random the questionnaries
        for _ in range(self.NUMBERGAMES):
            questionnaire = Questionnaire.objects.order_by("?").first()
            state = random.choice([constants.WAITING, constants.QUESTION,
                                   constants.LEADERBOARD, constants.ANSWER])
            countDown = random.randint(5, 10)
            game = Game(questionnaire=questionnaire, state=state,
                        countdownTime=countDown, questionNo=4)
            game.save()
