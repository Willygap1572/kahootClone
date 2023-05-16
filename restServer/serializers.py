from models.models import Participant, Game, Guess
from rest_framework import serializers


class ParticipantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Participant
        fields = '__all__'


class GameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = '__all__'


class GuessSerializer(serializers.ModelSerializer):

    class Meta:
        model = Guess
        # all fields
        fields = '__all__'
