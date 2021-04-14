from rest_framework import serializers
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
    class Meta:
        model = User
        fields = ['login', ]