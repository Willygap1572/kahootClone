from django.shortcuts import render
from django.views import generic
from models.models import Questionnaire, Question
from models.models import Answer, Game, Participant, Guess
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from models import constants
import os


class HomeView(generic.ListView):
    template_name = 'home.html'
    model = Questionnaire
    context_object_name = 'latest_questionnaire_list'

    # Mostrar los cuestionarios del usuario logado
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Questionnaire.objects.filter(
                user=self.request.user).order_by('-updated_at')[:5]
        else:
            return None


class QuestionnaireView(LoginRequiredMixin, generic.DetailView):
    template_name = 'questionnaire-detail.html'
    model = Questionnaire
    # check if the user is the owner of the questionnaire

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('login')
        obj = self.get_object()
        if obj.user != self.request.user:
            return render(request, 'error.html')
        return super().dispatch(request, *args, **kwargs)


class QuestionnaireListView(LoginRequiredMixin, generic.ListView):
    template_name = 'questionnaire-list.html'
    model = Questionnaire

    # Mostrar los cuestionarios del usuario logado
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Questionnaire.objects.filter(
                user=self.request.user).order_by('-updated_at')


class QuestionnaireRemoveView(LoginRequiredMixin, generic.DeleteView):
    model = Questionnaire
    template_name = 'questionnaire-remove.html'
    success_url = reverse_lazy('questionnaire-list')

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('login')
        obj = self.get_object()
        if obj.user != self.request.user:
            return render(request, 'error.html')
        return super().dispatch(request, *args, **kwargs)


class QuestionnaireUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Questionnaire
    fields = ['title']
    template_name = 'questionnaire-form.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('login')
        obj = self.get_object()
        if obj.user != self.request.user:
            return render(request, 'error.html')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('questionnaire-detail', args=[self.object.id])


class QuestionnaireCreateView(LoginRequiredMixin, generic.CreateView):
    model = Questionnaire
    fields = ['title']
    template_name = 'questionnaire-form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(QuestionnaireCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('questionnaire-detail', args=[self.object.id])


class QuestionView(LoginRequiredMixin, generic.DetailView):
    template_name = 'question-detail.html'
    model = Question

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('login')
        obj = self.get_object()
        if obj.questionnaire.user != self.request.user:
            return render(request, 'error.html')
        return super().dispatch(request, *args, **kwargs)


class QuestionRemoveView(LoginRequiredMixin, generic.DeleteView):
    model = Question
    template_name = 'question-remove.html'

    def get_success_url(self):
        return reverse('questionnaire-detail',
                       args=[self.object.questionnaire.id])

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('login')
        obj = self.get_object()
        if obj.questionnaire.user != self.request.user:
            return render(request, 'error.html')
        return super().dispatch(request, *args, **kwargs)


class QuestionUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Question
    fields = ['question', 'questionnaire']
    template_name = 'question-form.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('login')
        obj = self.get_object()
        if obj.questionnaire.user != self.request.user:
            return render(request, 'error.html')
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['questionnaire'].disabled = True
        return form

    def get_success_url(self):
        return reverse('question-detail', args=[self.object.id])


class QuestionCreateView(LoginRequiredMixin, generic.CreateView):
    model = Question
    fields = ['question', 'questionnaire']
    template_name = 'question-form.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('login')
        questionnaire_id = self.kwargs['questionnaireid']
        questionnaire = get_object_or_404(Questionnaire, id=questionnaire_id)
        if questionnaire.user != self.request.user:
            return render(request, 'error.html')
        return super().dispatch(request, *args, **kwargs)

    # questionnaire value not editable by the user
    def get_form(self, form_class=None):
        form = super(QuestionCreateView, self).get_form(form_class)
        form.fields['questionnaire'].disabled = True
        return form

    # default questionnaire value is passed in the url
    def get_initial(self):
        initial = super(QuestionCreateView, self).get_initial()
        initial['questionnaire'] = self.kwargs['questionnaireid']
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(QuestionCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('question-detail', args=[self.object.id])


class AnswerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Answer
    fields = ['answer', 'question', 'correct']
    template_name = 'answer-form.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('login')
        questionid = self.kwargs['questionid']
        question = get_object_or_404(Question, id=questionid)
        if question.questionnaire.user != self.request.user:
            return render(request, 'error.html')
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super(AnswerCreateView, self).get_form(form_class)
        form.fields['question'].disabled = True
        return form

    def get_initial(self):
        initial = super(AnswerCreateView, self).get_initial()
        initial['question'] = self.kwargs['questionid']
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user

        # Verify if the answer is correct
        is_correct = form.cleaned_data['correct']
        if is_correct:
            # Uncheck all other answers
            question = Question.objects.get(pk=self.kwargs['questionid'])
            answers = Answer.objects.filter(question=question)
            for answer in answers:
                if answer.pk != form.instance.pk:
                    answer.correct = False
                    answer.save()

        return super(AnswerCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('question-detail', args=[self.object.question.id])


class AnswerRemoveView(LoginRequiredMixin, generic.DeleteView):
    model = Answer
    template_name = 'answer-remove.html'

    def get_success_url(self):
        return reverse('question-detail', args=[self.object.question.id])

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('login')
        answerid = self.kwargs['pk']
        answer = get_object_or_404(Answer, id=answerid)
        if answer.question.questionnaire.user != self.request.user:
            return render(request, 'error.html')
        return super().dispatch(request, *args, **kwargs)


class AnswerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Answer
    fields = ['answer', 'question', 'correct']
    template_name = 'answer-form.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('login')
        answerid = self.kwargs['pk']
        answer = get_object_or_404(Answer, id=answerid)
        if answer.question.questionnaire.user != self.request.user:
            return render(request, 'error.html')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('question-detail', args=[self.object.question.id])

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['question'].disabled = True
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user

        # Obtain the question with the form
        question = form.cleaned_data['question']

        # Verify if the answer is correct
        is_correct = form.cleaned_data['correct']
        if is_correct:
            answers = Answer.objects.filter(question=question)
            for answer in answers:
                if answer.pk != form.instance.pk:
                    answer.correct = False
                    answer.save()
        return super().form_valid(form)


class GameCreateView(generic.View):

    def get(self, request, questionnaireid):

        questionnaire = get_object_or_404(Questionnaire, id=questionnaireid)
        try:
            # If the game already exists, delete it and create a new one
            game = Game.objects.get(questionnaire=questionnaire)
            game.delete()
        except Game.DoesNotExist:
            pass
        game = Game.objects.create(
            questionnaire=questionnaire,
            questionNo=Question.objects.filter(
                questionnaire=questionnaire).count(),
        )
        request.session['publicId'] = game.publicId
        request.session['game_id'] = game.pk

        request.session['game_state'] = game.state
        url = "https://vueclient-xng7.onrender.com"
        if os.environ.get('TESTING') == '1':
            url = "http://localhost:3000"
        return render(request, 'game-create.html', {'game': game, 'url': url})

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('login')
        questionnaire_id = self.kwargs['questionnaireid']
        questionnaire = get_object_or_404(Questionnaire, id=questionnaire_id)
        if questionnaire.user != self.request.user:
            return render(request, 'error.html')
        return super().dispatch(request, *args, **kwargs)


class GameUpdateParticipantView(generic.View):

    def get(self, request):
        try:
            game = Game.objects.get(pk=request.session.get('game_id'))
        except Game.DoesNotExist:
            return render(request, 'error.html')
        participants = [
            participant.alias for participant in
            Participant.objects.filter(game=game)]
        data = {
            'publicId': request.session.get('publicId'),
            'participants': participants,
        }
        return JsonResponse(data)


class GameCountdownView(generic.TemplateView):
    template_name = "game-count-down.html"

    def get_template_names(self):
        game = Game.objects.get(pk=self.request.session.get('game_id'))
        state = game.state
        if state == constants.WAITING:
            template_name = "game-count-down.html"
            game.state = constants.QUESTION
            self.request.session['game_state'] = game.state
            game.save()
        elif state == constants.QUESTION:
            template_name = "game-question.html"
            game.state = constants.ANSWER
            self.request.session['game_state'] = game.state
            game.save()
        elif state == constants.ANSWER:
            template_name = "game-score.html"
            game.questionNo -= 1
            if game.questionNo == 0:
                game.state = constants.LEADERBOARD
            else:
                game.state = constants.QUESTION
            self.request.session['game_state'] = game.state
            game.save()
        elif state == constants.LEADERBOARD:
            template_name = "game-leaderboard.html"
        else:
            template_name = "home.html"
        return template_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = Game.objects.get(pk=self.request.session.get('game_id'))
        state = game.state
        session = self.request.session
        session['game_state'] = state
        questions = Question.objects.filter(questionnaire=game.questionnaire)
        if state == constants.WAITING:
            context["countdown"] = game.countdownTime
        elif state == constants.QUESTION:
            context["questions"] = questions
            context["answers"] = [answer for answer in Answer.objects.filter(
                question=context["questions"][game.questionNo-1])
                if answer.question.questionnaire == game.questionnaire]
            group = context["questions"][game.questionNo-1]
            context["countdown"] = group.answerTime
            context["question"] = context["questions"][game.questionNo-1]
            session['correct'] = [answer for answer in Answer.objects.filter(
                question=context["question"]) if answer.correct][0].answer
            participants = Participant.objects.filter(game=game)
            session['participants'] = [
                participant.alias for participant in participants]
        elif state == constants.ANSWER:
            context["correct"] = session.get('correct')
            context["question"] = questions[game.questionNo-1]
            context["participants"] = Participant.objects.filter(game=game)
            guesses = Guess.objects.filter(
                game=game, question=context["question"])
            total_guesses = guesses.count()
            answer = Answer.objects.get(
                question=context["question"], correct=True)
            correct_guesses = guesses.filter(answer=answer).count()
            if total_guesses != 0:
                context["correct_percentage"] = (
                    correct_guesses / total_guesses) * 100
            else:
                context["correct_percentage"] = 0
        elif state == constants.LEADERBOARD:
            try:
                context['first'] = Participant.objects.filter(
                    game=game).order_by('points')[0]
                context['second'] = Participant.objects.filter(
                    game=game).order_by('points')[1]
                context['third'] = Participant.objects.filter(
                    game=game).order_by('points')[2]
            except IndexError:
                pass
            context["questionnaire"] = game.questionnaire
        context["game"] = game
        return context
