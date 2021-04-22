from django.utils import timezone
from django.db.models import F
from rest_framework import viewsets
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from authorization.models import User
from .serializers import (CategorySerializer, GameReadSerializer, GameStartRequestBodySerializer,
                          RoundReadSerializer, RoundSetPointRequestBodySerializer, GameStartResponseSerializer,
                          RoundSetPointResponseSerializer, TopPlayersResponseSerializer)
from .models import Category, Game, Round
from .permissions import PlayInCategoryPermission


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @swagger_auto_schema(method='POST',
                         responses={
                             '200': CategorySerializer()
                         }
                         )
    @action(methods=['POST'], detail=True, url_name='set_like',
            permission_classes=[PlayInCategoryPermission, ])
    def set_like(self, request, pk):
        category = self.get_object()
        category.likes.add(request.user)
        return Response(CategorySerializer(category).data)

    def get_serializer_context(self):
        context = super(CategoryViewSet, self).get_serializer_context()
        context['user'] = self.request.user
        return context


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameReadSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    @swagger_auto_schema(method='POST', request_body=GameStartRequestBodySerializer(),
                        responses={
                            '201': GameStartResponseSerializer()
                        })
    @action(methods=['POST'], detail=False, url_name='start_game')
    def start_game(self, request):
        """
        Начало игры
        """
        serializer = GameStartRequestBodySerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        game = serializer.save()
        first_round = Round.objects.create(game=game, num=1)
        first_round.set_random_point()
        first_round.save()
        return Response(GameStartResponseSerializer(first_round).data,
                        status=status.HTTP_201_CREATED)

    @swagger_auto_schema(method='POST',
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
        next_round.save()
        return Response(RoundReadSerializer(next_round).data,
                        status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, url_name='end_game')
    def end_game(self, request, pk):
        """
        Завершить игру
        """
        game = self.get_object()
        game.is_over = True
        game.set_score()
        game.save()
        return Response(GameReadSerializer(game).data)

    def get_queryset(self):
        if self.action in ['next_round', 'end_game']:
            return self.queryset.active()
        return super().get_queryset()


class RoundViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundReadSerializer

    @swagger_auto_schema(method='PATCH', request_body=RoundSetPointRequestBodySerializer(),
                         responses={
                             '200': RoundSetPointResponseSerializer()
                         })
    @action(methods=['PATCH'], detail=True, url_name='set_user_point')
    def set_user_point(self, request, pk):
        """
        Указание пользователем точки
        """
        round = self.get_object()
        serializer = RoundSetPointRequestBodySerializer(round, data=request.data)
        serializer.is_valid(raise_exception=True)
        round = serializer.save()
        round.date_end = timezone.now()
        round.set_score()
        round.save()
        return Response(RoundSetPointResponseSerializer(round).data)


@swagger_auto_schema(method='GET', responses={'200': TopPlayersResponseSerializer(many=True)})
@api_view(['GET'])
def top_players(request):
    limit = int(request.GET.get('limit', 10))
    query = 'SELECT u.id as id, u.login as login, avg((gg.score::float / gc.max_score::float) * 100) as avg_score, ' \
            'sum(gg.score) as sum_score FROM users u INNER JOIN game_game gg on u.id = gg.user_id ' \
            'INNER JOIN game_category gc on gg.category_id = gc.id ' \
            'GROUP BY u.id, u.login ORDER BY avg_score DESC'
    result = User.objects.raw(query)[:limit]
    return Response(TopPlayersResponseSerializer(result, many=True).data)

