from django.test import TestCase, Client
from django.urls import reverse
from models.models import Questionnaire, User, Question, Answer, Game


class QuestionnaireViewTest(TestCase):
    def setUp(self):
        # create a test user
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.user.save()

        # create a test questionnaire
        self.questionnaire = Questionnaire.objects.create(
            title='Test questionnaire',
            user=self.user)

    def test_questionnaire_view_success(self):
        # log in as the test user
        self.client.login(username='testuser', password='testpass')

        # access the questionnaire detail view
        response = self.client.get(reverse('questionnaire-detail',
                                           args=[self.questionnaire.id]))

        # verify that the response status code is 200
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.questionnaire.title)

    def test_questionnaire_view_fail(self):

        user2 = User.objects.create_user(
            username='testuser2', password='testpass')
        user2.save()

        self.client.login(username='testuser2', password='testpass')

        response = self.client.get(reverse('questionnaire-detail',
                                           args=[self.questionnaire.id]))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Error')


class QuestionnaireListViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser',
                                             password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_questionnaire_list_view_with_no_questionnaires(self):
        response = self.client.get(reverse('questionnaire-list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['object_list'], [])

    def test_questionnaire_list_view_with_questionnaires(self):
        questionnaire1 = Questionnaire.objects.create(user=self.user,
                                                      title='Questionnaire 1')
        questionnaire2 = Questionnaire.objects.create(user=self.user,
                                                      title='Questionnaire 2')

        questionnaire1 = questionnaire2
        questionnaire2 = questionnaire1

        response = self.client.get(reverse('questionnaire-list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['object_list'],
                                 ['<Questionnaire: Questionnaire 2>',
                                  '<Questionnaire: Questionnaire 1>'])

    def test_questionnaire_list_view_with_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(reverse('questionnaire-list'))
        self.assertEqual(response.status_code, 302)


class QuestionnaireRemoveViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )

        self.questionnaire = Questionnaire.objects.create(
            title='Test Questionnaire',
            user=self.user
        )

        self.url = reverse('questionnaire-remove',
                           args=[self.questionnaire.id])

    def test_remove_questionnaire_authenticated_user(self):
        self.client.login(username='testuser', password='testpass')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Are you sure you want to delete')

        response = self.client.post(self.url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Questionnaire.objects.filter(id=self.questionnaire.id).exists())

    def test_remove_questionnaire_unauthenticated_user(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_remove_questionnaire_not_owner_user(self):
        User.objects.create_user(
            username='otheruser',
            password='otherpass'
        )

        self.client.login(username='otheruser', password='otherpass')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Questionnaire.objects.filter(
            id=self.questionnaire.id).exists())


class QuestionnaireUpdateViewTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1',
                                              password='testpass123')
        self.user2 = User.objects.create_user(username='user2',
                                              password='testpass123')
        self.questionnaire = Questionnaire.objects.create(
            user=self.user1,
            title='Test questionnaire')

    def test_user_not_creator(self):
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('questionnaire-update',
                                           args=[self.questionnaire.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'error.html')

    def test_user_creator_get(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('questionnaire-update',
                                           args=[self.questionnaire.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questionnaire-form.html')

    def test_user_creator_post(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.post(reverse('questionnaire-update',
                                            args=[self.questionnaire.id]),
                                    {'title': 'Updated title'})
        self.assertRedirects(response, reverse('questionnaire-detail',
                                               args=[self.questionnaire.id]))
        updated_questionnaire = Questionnaire.objects.get(
            id=self.questionnaire.id)
        self.assertEqual(updated_questionnaire.title, 'Updated title')


class QuestionnaireCreateViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='testuser', password='testpass')
        self.create_url = reverse('questionnaire-create')

    def test_create_questionnaire_no_authenticated_user(self):
        self.client.logout()
        response = self.client.get(self.create_url)
        self.assertRedirects(
            response, '/accounts/login/?next=/services/questionnairecreate/')

    def test_create_questionnaire(self):
        form_data = {'title': 'Test Questionnaire'}
        response = self.client.post(self.create_url, form_data)
        self.assertEqual(Questionnaire.objects.count(), 1)
        questionnaire = Questionnaire.objects.first()
        self.assertEqual(questionnaire.user, self.user)
        self.assertRedirects(response, reverse('questionnaire-detail',
                                               args=[questionnaire.id]))

    def test_create_questionnaire_invalid_form(self):
        form_data = {}
        response = self.client.post(self.create_url, form_data)
        self.assertEqual(Questionnaire.objects.count(), 0)
        self.assertTemplateUsed(response, 'questionnaire-form.html')
        self.assertTrue('form' in response.context)
        self.assertTrue(response.context['form'].errors)


class QuestionViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser',
                                             password='testpass')
        args = {'title': 'Test Questionnaire', 'user': self.user}
        self.questionnaire = Questionnaire.objects.create(**args)
        args = {'questionnaire': self.questionnaire,
                'question': 'Test question'}
        self.question = Question.objects.create(**args)

    def test_user_not_owner_of_questionnaire(self):
        User.objects.create_user(username='otheruser',
                                 password='otherpass')
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.get(reverse('question-detail',
                                           args=[self.question.id]))
        self.assertTrue(response.status_code, 200)

    def test_user_owner_of_questionnaire(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('question-detail',
                                           args=[self.question.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'question-detail.html')
        self.assertEqual(response.context['object'], self.question)


class QuestionRemoveViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.questionnaire = Questionnaire.objects.create(
            user=self.user,
            title='Test questionnaire',
        )
        self.question = Question.objects.create(
            questionnaire=self.questionnaire,
            question='Test question'
        )

    def test_remove_question(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('question-remove',
                                            args=[self.question.id]))
        self.assertRedirects(response, reverse('questionnaire-detail',
                                               args=[self.questionnaire.id]))
        self.assertEqual(Question.objects.count(), 0)

    def test_user_not_questionnaire_owner(self):
        User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )
        self.client.login(username='testuser2', password='testpass123')
        response = self.client.post(reverse('question-remove',
                                            args=[self.question.id]))
        self.assertTemplateUsed(response, 'error.html')
        self.assertEqual(Question.objects.count(), 1)


class QuestionUpdateViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.questionnaire = Questionnaire.objects.create(
            title='Test Questionnaire', user=self.user)
        self.question = Question.objects.create(
            question='Test Question', questionnaire=self.questionnaire)

    def test_login_required(self):
        response = self.client.get(reverse('question-update',
                                           args=[self.question.id]))
        self.assertEqual(response.status_code, 302)

    def test_user_is_creator(self):
        User.objects.create_user(
            username='otheruser', password='testpass')
        self.client.login(username='otheruser', password='testpass')
        response = self.client.get(reverse('question-update',
                                           args=[self.question.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'error.html')

    def test_form_is_invalid(self):
        self.client.login(username='testuser', password='testpass')
        data = {'question': '', 'questionnaire': self.questionnaire.id}
        response = self.client.post(reverse(
            'question-update',
            args=[self.question.id]),
            data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'question-form.html')


class QuestionCreateViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser',
                                             password='testpass123')
        self.questionnaire = Questionnaire.objects.create(
            user=self.user,
            title='Test questionnaire')

    def test_login_required(self):
        response = self.client.get(
            reverse('question-create',
                    kwargs={'questionnaireid': self.questionnaire.id}))
        self.assertEqual(response.status_code, 302)

    def test_create_question_successful(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'question': 'Test question',
            'questionnaire': self.questionnaire.id
        }
        response = self.client.post(reverse(
            'question-create',
            kwargs={'questionnaireid': self.questionnaire.id}), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Question.objects.count(), 1)
        question = Question.objects.first()
        self.assertEqual(question.question, 'Test question')
        self.assertEqual(question.questionnaire, self.questionnaire)
        self.assertRedirects(response, reverse('question-detail',
                                               args=[question.id]))


class AnswerCreateViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser',
                                             password='testpass123')
        self.questionnaire = Questionnaire.objects.create(
            title='Test questionnaire', user=self.user)
        self.question = Question.objects.create(
            question='Test question',
            questionnaire=self.questionnaire)
        self.url = reverse(
            'answer-create', kwargs={'questionid': self.question.id})

    def test_create_answer(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'answer': 'Test answer',
            'correct': True
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.question.answer_set.count(), 1)
        answer = self.question.answer_set.first()
        self.assertEqual(answer.answer, 'Test answer')
        self.assertTrue(answer.correct)

    def test_create_correct_answer(self):
        Answer.objects.create(answer='Previous answer', question=self.question,
                              correct=True)
        self.client.login(username='testuser', password='testpass123')
        data = {
            'answer': 'Test answer',
            'correct': True
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 302)
        self.question.answer_set.first()

    def test_create_incorrect_answer(self):
        Answer.objects.create(answer='Previous answer',
                              question=self.question, correct=False)
        self.client.login(username='testuser', password='testpass123')
        data = {
            'answer': 'Test answer',
            'correct': True
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 302)
        self.question.answer_set.first()

    def test_create_duplicate_answer(self):
        Answer.objects.create(answer='Test answer', question=self.question,
                              correct=True)
        self.client.login(username='testuser', password='testpass123')
        data = {
            'answer': 'Test answer',
            'correct': False
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 302)


class AnswerRemoveViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.questionnaire = Questionnaire.objects.create(
            user=self.user,
            title='Test questionnaire',
        )
        self.question = Question.objects.create(
            questionnaire=self.questionnaire,
            question='Test question'
        )
        self.answer = Answer.objects.create(
            question=self.question,
            answer='Test answer'
        )

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('answer-remove',
                                           args=[self.answer.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('answer-remove',
                                           args=[self.answer.id]))
        self.assertTemplateUsed(response, 'answer-remove.html')

    def test_answer_removed_on_post(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('answer-remove',
                                            args=[self.answer.id]))
        self.assertEqual(response.status_code, 302)


class AnswerUpdateViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             password='12345')

        self.questionnaire = Questionnaire.objects.create(
            user=self.user,
            title='Test questionnaire',
        )

        self.question = Question.objects.create(
            question='Test question',
            questionnaire=self.questionnaire
        )

        self.answer = Answer.objects.create(
            answer='Test answer',
            question=self.question,
            correct=False
        )

    def test_update_answer_as_authenticated_owner(self):
        self.client.login(username='testuser', password='12345')

        url = reverse('answer-update', kwargs={'pk': self.answer.pk})
        data = {
            'answer': 'Test answer updated',
            'question': self.question.pk,
            'correct': True
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('question-detail',
                                               args=[self.question.pk]))

        answer_updated = Answer.objects.get(pk=self.answer.pk)
        self.assertEqual(answer_updated.answer, 'Test answer updated')
        self.assertTrue(answer_updated.correct)

    def test_update_answer_as_authenticated_non_owner(self):
        User.objects.create_user(username='testuser2',
                                 password='12345')

        self.client.login(username='testuser2', password='12345')

        url = reverse('answer-update', kwargs={'pk': self.answer.pk})
        data = {
            'answer': 'Test answer updated',
            'question': self.question.pk,
            'correct': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'error.html')

        answer_not_updated = Answer.objects.get(pk=self.answer.pk)
        self.assertEqual(answer_not_updated.answer, 'Test answer')
        self.assertFalse(answer_not_updated.correct)

    def test_update_answer_as_unauthenticated_user(self):
        url = reverse('answer-update', kwargs={'pk': self.answer.pk})
        data = {
            'answer': 'Test answer updated',
            'question': self.question.pk,
            'correct': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))

        answer_not_updated = Answer.objects.get(pk=self.answer.pk)
        self.assertEqual(answer_not_updated.answer, 'Test answer')
        self.assertFalse(answer_not_updated.correct)

    def test_form_valid(self):
        self.client.login(username='testuser', password='testpass')

        response = self.client.post(reverse('answer-update',
                                            args=[self.answer.id]), {
            'answer': 'Test answer',
            'question': self.question.id,
            'correct': True,
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Answer.objects.get(pk=self.answer.pk).correct)

        answer2 = Answer.objects.create(
            question=self.question,
            answer='Another wrong answer',
            correct=False,
        )
        response = self.client.post(reverse('answer-update',
                                            args=[answer2.id]), {
            'answer': 'Another wrong answer',
            'question': self.question.id,
            'correct': True,
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Answer.objects.get(pk=self.answer.pk).correct)


class GameCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser',
                                             password='testpass')
        self.questionnaire = Questionnaire.objects.create(
            user=self.user,
            title='Test Questionnaire')
        self.question = Question.objects.create(
            question='Test question',
            questionnaire=self.questionnaire)
        self.url = reverse('game-create', args=[self.questionnaire.id])

    def test_authenticated_user_can_create_game(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        game = Game.objects.first()
        self.assertEqual(game.questionnaire, self.questionnaire)
        self.assertEqual(game.questionNo, 1)
        self.assertEqual(response.context['game'], game)
        self.assertEqual(self.client.session['publicId'], game.publicId)
        self.assertEqual(self.client.session['game_id'], game.pk)
        self.assertEqual(self.client.session['game_state'], game.state)

    def test_creating_game_deletes_existing_game(self):
        self.client.login(username='testuser', password='testpass')
        game = Game.objects.create(questionnaire=self.questionnaire,
                                   questionNo=1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Game.objects.filter(pk=game.pk).exists())
