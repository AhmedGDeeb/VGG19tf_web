from rest_framework import serializers
from .models import PredictionResult

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionResult
        fields = '__all__'

class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()

# prediction/serializers.py - Enhanced serializer
from rest_framework import serializers
from .models import PredictionResult
from django.urls import reverse

class PredictionHistorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = PredictionResult
        fields = ['id', 'image_url', 'result', 'confidence', 'created_at', 'time_ago']

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_time_ago(self, obj):
        from django.utils import timezone
        from django.utils.timesince import timesince
        return timesince(obj.created_at)
