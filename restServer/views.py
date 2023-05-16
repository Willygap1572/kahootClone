from models.models import Participant, Game, Guess, Answer, Question
from .serializers import ParticipantSerializer, GameSerializer, GuessSerializer
from rest_framework import viewsets
from rest_framework.response import Response


class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer

    def create(self, request):
        game = Game.objects.filter(publicId=request.data['game'])
        if game.exists() is False:
            return Response(status=403, data={
                'detail': 'Game does not exist.'})
        game = game[0]
        # check that all the identifiers are correct,
        # and the game is in WAITING state
        if request.data['alias'] is None or game.state != 1:
            return Response(status=403, data={
                'detail': 'Alias is already taken or \
game is not in WAITING state.'})
        # check that there is not already a participant
        # with the same alias in the game
        if Participant.objects.filter(alias=request.data['alias'], game=game):
            return Response(status=403, data={
                'detail': 'Participant already exists in the game.'})
        participant = Participant(alias=request.data['alias'], game=game)
        participant.save()
        # return an http response with the all the data of the participant
        serializer = ParticipantSerializer(participant)
        return Response(status=201, data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        return Response(status=400, data={
            'detail': 'Authentication credentials were not provided.'})

    def update(self, request, *args, **kwargs):
        return Response(status=405, data={
            'detail': 'Authentication credentials were not provided.'})

    def retrieve(self, request, pk=None):
        return Response(status=405, data={
            'detail': 'Authentication credentials were not provided.'})


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    lookup_field = 'publicId'

    def destroy(self, request, *args, **kwargs):
        return Response(status=405, data={
            'detail': 'Authentication credentials were not provided.'})

    def update(self, request, *args, **kwargs):
        return Response(status=405, data={
            'detail': 'Authentication credentials were not provided.'})

    def create(self, request):
        return Response(status=405, data={
            'detail': 'Authentication credentials were not provided.'})


class GuessViewSet(viewsets.ModelViewSet):
    queryset = Guess.objects.all()
    serializer_class = GuessSerializer

    def create(self, request):
        game = Game.objects.filter(publicId=request.data['game']).first()
        if not game:
            return Response(status=403, data={
                'detail': 'Game does not exist.'})
        participant = Participant.objects.filter(
            uuidP=request.data['uuidp']).first()
        if not participant:
            return Response(status=403, data={
                'detail': 'Participant does not exist.'})
        question_index = game.questionNo
        question = Question.objects.filter(
            questionnaire=game.questionnaire)[question_index-1]
        # if game.state != 2:
        #     return Response(status=403, data={
        #                   'detail': 'wait until the question is shown.'})
        try:
            answer = list(Answer.objects.filter(
                question=question))[int(request.data['answer']) - 1]
        except IndexError:
            return Response(status=403, data={
                'detail': 'Invalid answer.'})
        guess_exists = Guess.objects.filter(
            participant=participant, question=question).exists()
        if guess_exists:
            return Response(status=403, data={
                'detail': 'Guess already exists.'})
        guess = Guess(participant=participant,
                      game=game, question=question, answer=answer)
        guess.save()
        serializer = GuessSerializer(guess)
        return Response(status=201, data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        return Response(status=403, data={
            'detail': 'Authentication credentials were not provided.'})

    def update(self, request, *args, **kwargs):
        return Response(status=403, data={
            'detail': 'Authentication credentials were not provided.'})

    def retrieve(self, request, pk=None):
        return Response(status=403, data={
            'detail': 'Authentication credentials were not provided.'})
