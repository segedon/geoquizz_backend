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