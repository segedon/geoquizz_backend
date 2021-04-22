from django.db.models import Max, Avg
from rest_framework import serializers
from game.models import Round
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = User.objects.create_user(login=validated_data['login'],
                                        password=validated_data['password'])
        return user

    class Meta:
        model = User
        fields = ['login', 'password', ]


class UserLoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField()


class UserReadSerializer(serializers.ModelSerializer):
    games_count = serializers.SerializerMethodField()
    best_game_score = serializers.SerializerMethodField()
    avg_game_score = serializers.SerializerMethodField()
    best_round_score = serializers.SerializerMethodField()
    avg_round_score = serializers.SerializerMethodField()

    def get_best_round_score(self, obj):
        result = Round.objects.filter(game__user=obj, game__is_over=True).\
            aggregate(best_score=Max('score'))
        return result['best_score']

    def get_avg_round_score(self, obj):
        query = Round.objects.filter(game__user=obj, game__is_over=True). \
            aggregate(avg_score=Avg('score', distinct=True))
        avg_round_score = query['avg_score']
        return round(avg_round_score) if avg_round_score is not None else avg_round_score

    def get_avg_game_score(self, obj):
        query = obj.games.finished().aggregate(avg_score=Avg('score'))
        avg_game_score = query['avg_score']
        return round(avg_game_score) if avg_game_score is not None else None

    def get_best_game_score(self, obj):
        result = obj.games.finished().aggregate(best_score=Max('score'))
        return result['best_score']

    def get_games_count(self, obj):
        return obj.games.finished().count()


    class Meta:
        model = User
        fields = ['login', 'id', 'games_count', 'best_game_score', 'avg_game_score',
                  'best_round_score', 'avg_round_score']


class UserChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_old_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError('Введен неправильный пароль')
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ['old_password', 'new_password', ]