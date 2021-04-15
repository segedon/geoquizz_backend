from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    points_count = serializers.ReadOnlyField()
    image = serializers.SerializerMethodField()

    def get_image(self, instance):
        return instance.image.url

    class Meta:
        model = Category
        fields = '__all__'