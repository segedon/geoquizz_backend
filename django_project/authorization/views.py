from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import permissions
from drf_yasg.utils import swagger_auto_schema
from game.serializers import CategorySerializer
from .serializers import (UserRegistrationSerializer, UserLoginSerializer,
                          UserReadSerializer, UserChangePasswordSerializer)


@swagger_auto_schema(method='POST', request_body=UserRegistrationSerializer(),
                     responses={
                         '201': UserReadSerializer()
                     },
                     tags=['Авторизация'])
@api_view(['POST'])
def user_registration(request):
    """
    Регистрация пользователя
    """
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    login(request, user)
    user_data = UserReadSerializer(user).data
    return Response(user_data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(method='POST', request_body=UserLoginSerializer(),
                     responses={
                         '200': UserReadSerializer()
                     },
                     tags=['Авторизация'])
@api_view(['POST'])
def user_login(request):
    """
    Аутентификация пользователя
    """
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = authenticate(username=serializer.validated_data['login'],
                        password=serializer.validated_data['password'])
    if user is None:
        raise AuthenticationFailed('Неверный логин или пароль')
    login(request, user)
    user_data = UserReadSerializer(user).data
    return Response(user_data)


@swagger_auto_schema(method='GET', tags=['Авторизация'])
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, ])
def user_logout(request):
    """
    Выход
    """
    logout(request)
    return Response({'status': 'success'})


@swagger_auto_schema(method='GET',
                     responses={
                         '200': UserReadSerializer()
                     },
                     tags=['Авторизация'])
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, ])
def user_info(request):
    """
    Получение информации о пользователе
    """
    user_data = UserReadSerializer(request.user).data
    return Response(user_data)


@swagger_auto_schema(method='POST', tags=['Авторизация'])
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, ])
def change_password(request):
    """
    Смена пароля
    """
    serializer = UserChangePasswordSerializer(request.user,
                                              data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({'status': 'success'})


@swagger_auto_schema(method='GET', responses={'200': CategorySerializer(many=True)})
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, ])
def liked_category(request):
    """
    Понравившиеся категории
    """
    return Response(CategorySerializer(request.user.liked_category, many=True).data)




