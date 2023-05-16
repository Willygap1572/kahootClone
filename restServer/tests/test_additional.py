from rest_framework.test import APITestCase, APIClient
from models.models import Participant, Game, Guess
from models.models import Questionnaire, Question, Answer, User
from django.urls import reverse
import uuid


class RestServerTest(APITestCase):
    """Test module for restServer views"""
    def setUp(self):
        self.client = APIClient()
        # create user
        self.userDict = {"username": 'a',
                         "password": 'a',
                         "first_name": 'a',
                         "last_name": 'a',
                         "email": 'a@aa.es'
                         }
        user, created = User.objects.get_or_create(**self.userDict)
        # save password encripted
        if created:
            user.set_password(self.userDict['password'])
            user.save()
        self.user = user

        # create questionnaire
        self.questionnaireDict = {"title": 'questionnaire_title',
                                  "user": self.user
                                  }
        self.questionnaire = Questionnaire.objects.get_or_create(
            **self.questionnaireDict)[0]

        # create a few questions
        # question 1
        self.questionDict = {"question": 'this is a question',
                             "questionnaire": self.questionnaire,
                             }
        self.question = Question.objects.get_or_create(**self.questionDict)[0]

        # question2
        self.questionDict2 = {"question": 'this is a question2',
                              "questionnaire": self.questionnaire,
                              }
        self.question2 = Question.objects.get_or_create(
            **self.questionDict2)[0]

        # create a few answers
        # answer1
        self.answerDict = {"answer": 'this is an answer',
                           "question": self.question,
                           "correct": True
                           }
        self.answer = Answer.objects.get_or_create(**self.answerDict)[0]

        # answer2
        self.answerDict2 = {"answer": 'this is an answer2',
                            "question": self.question,
                            "correct": False
                            }
        self.answer2 = Answer.objects.get_or_create(**self.answerDict2)[0]

        # answer3
        self.answerDict3 = {"answer": 'this is an answer3',
                            "question": self.question2,
                            "correct": True
                            }
        self.answer3 = Answer.objects.get_or_create(**self.answerDict3)[0]

        # create a game
        self.gameDict = {
            'questionnaire': self.questionnaire,
            'publicId': 123456,
            'questionNo': 2,
        }
        self.game = Game.objects.get_or_create(**self.gameDict)[0]

        # create a participant
        self.participantDict = {
            'game': self.game,
            'alias': "pepe"}
        self.participant = Participant.objects.get_or_create(
            **self.participantDict)[0]

        # create a guess
        self.guessDict = {
            'participant': self.participant,
            'game': self.game,
            'question': self.question,
            'answer': self.answer,
            }
        self.guess = Guess.objects.get_or_create(**self.guessDict)[0]

    @classmethod
    def decode(cls, txt):
        """convert the html return by the client in something that may 
           by printed on the screen"""
        return txt.decode("utf-8")

    def test_create_participant_game_does_not_exist(self):
        data = {
            'game': 123123,
            'alias': 'new_participant'
        }
        response = self.client.post(reverse('participant-list'), data)
        self.assertEqual(response.status_code, 403)
        expected_error = {'detail': 'Game does not exist.'}
        self.assertEqual(response.data, expected_error)

    def test_create_participant_alias_taken(self):
        data = {
            'game': self.game.publicId,
            'alias': self.participant.alias
        }
        response = self.client.post(reverse('participant-list'), data)
        self.assertEqual(response.status_code, 403)
        expected_error = {
            'detail': 'Participant already exists in the game.'
        }
        self.assertEqual(response.data, expected_error)

    def test_create_participant_game_not_waiting(self):
        data = {
            'game': self.game.publicId,
            'alias': self.participant.alias
        }
        game = Game.objects.get(publicId=self.game.publicId)
        game.state=4
        game.save()
        response = self.client.post(reverse('participant-list'), data)
        self.assertEqual(response.status_code, 403)
        expected_error = {
            'detail': 'Alias is already taken or \
game is not in WAITING state.'
        }
        self.assertEqual(response.data, expected_error)


    def test_create_guess_game_does_not_exist(self):
        data = {
            'game': 121,
            'uuidp': uuid.uuid4(),
        }
        response = self.client.post(reverse('guess-list'), data)
        self.assertEqual(response.status_code, 403)
        expected_error = {'detail': 'Game does not exist.'}
        self.assertEqual(response.data, expected_error)

    def test_create_guess_participant_does_not_exist(self):
        data = {
            'game': 123456,
            'uuidp': uuid.uuid4(),
        }
        response = self.client.post(reverse('guess-list'), data)
        self.assertEqual(response.status_code, 403)
        expected_error = {'detail': 'Participant does not exist.'}
        self.assertEqual(response.data, expected_error)

    def test_create_guess_answer_not_valid(self):
        data = {
            'game': self.game.publicId,
            'uuidp': self.participant.uuidP,
            'answer': 2,
        }
        response = self.client.post(reverse('guess-list'), data)
        self.assertEqual(response.status_code, 403)
        expected_error = {'detail': 'Invalid answer.'}
        self.assertEqual(response.data, expected_error)

    def test_create_guess_correct(self):
        data = {
            'game': self.game.publicId,
            'uuidp': self.participant.uuidP,
            'answer': 1,
        }
        response = self.client.post(reverse('guess-list'), data)
        self.assertEqual(response.status_code, 201)