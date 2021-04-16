from rest_framework import serializers
from .models import Category, Game, Round


class CategorySerializer(serializers.ModelSerializer):
    points_count = serializers.ReadOnlyField()
    image = serializers.SerializerMethodField()

    def get_image(self, instance):
        return instance.image.url

    class Meta:
        model = Category
        fields = '__all__'


class GameStartSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(queryset=Category.objects.all(),
                                            slug_field='codename')

    def create(self, validated_data):
        validated_data['user'] = self.context['user']
        return super(GameStartSerializer, self).create(validated_data)

    class Meta:
        model = Game
        fields = ['category']


class GameReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'


class RoundReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = '__all__'