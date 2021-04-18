from rest_framework import serializers
from rest_framework_gis.serializers import (GeometrySerializerMethodField,
                                            GeometryField)
from .models import Category, Game, Round


class CategorySerializer(serializers.ModelSerializer):
    points_count = serializers.ReadOnlyField()
    image = serializers.SerializerMethodField()

    def get_image(self, instance):
        return instance.image.url if instance.image else None

    class Meta:
        model = Category
        fields = '__all__'


class GameStartRequestBodySerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(queryset=Category.objects.all(),
                                            slug_field='codename')

    def create(self, validated_data):
        validated_data['user'] = self.context['user']
        return super(GameStartRequestBodySerializer, self).create(validated_data)

    class Meta:
        model = Game
        fields = ['category']


class GameStartResponseSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    def get_category(self, obj):
        return CategorySerializer(obj.game.category).data

    class Meta:
        model = Round
        fields = '__all__'



class GameReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'


class RoundSetPointSerializer(serializers.ModelSerializer):
    user_point = GeometryField()

    class Meta:
        model = Round
        fields = ['user_point']


class RoundReadSerializer(serializers.ModelSerializer):
    random_point = GeometrySerializerMethodField()

    def get_random_point(self, obj):
        return obj.random_point.point

    class Meta:
        model = Round
        fields = '__all__'