from django.utils import timezone
from rest_framework import viewsets
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .serializers import (CategorySerializer, GameReadSerializer, GameStartSerializer,
                          RoundReadSerializer, RoundSetPointSerializer)
from .models import Category, Game, Round


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameReadSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    @swagger_auto_schema(method='POST', request_body=GameStartSerializer(),
                        responses={
                            '201': RoundReadSerializer()
                        })
    @action(methods=['POST'], detail=False, url_name='start_game')
    def start_game(self, request):
        """
        Начало игры
        """
        serializer = GameStartSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        game = serializer.save()
        first_round = Round.objects.create(game=game, num=1)
        first_round.set_random_point()
        return Response(RoundReadSerializer(first_round).data,
                        status=status.HTTP_201_CREATED)

    @swagger_auto_schema(method='POST', request_body=None,
                         responses={
                             '201': RoundReadSerializer()
                         })
    @action(methods=['POST'], detail=True, url_name='next_round')
    def next_round(self, request, pk):
        """
        Начать следующий раунд
        """
        game = self.get_object()
        next_round = Round.objects.create(game=game)
        next_round.set_round_num()
        next_round.set_random_point()
        return Response(RoundReadSerializer(next_round).data,
                        status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, url_name='end_game')
    def end_game(self, request, pk):
        """
        Завершить игру
        """
        game = self.get_object()
        game.is_over = True
        game.save()
        return Response(GameReadSerializer(game).data)


class RoundViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundReadSerializer

    @swagger_auto_schema(method='PATCH', request_body=RoundSetPointSerializer())
    @action(methods=['PATCH'], detail=True, url_name='set_user_point')
    def set_user_point(self, request, pk):
        """
        Указание пользователем точки
        """
        round = self.get_object()
        serializer = RoundSetPointSerializer(round, data=request.data)
        serializer.is_valid(raise_exception=True)
        round = serializer.save()
        round.date_end = timezone.now()
        round.save()
        return Response()
