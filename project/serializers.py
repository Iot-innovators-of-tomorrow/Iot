from rest_framework import serializers

class ImageUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    camera_index = serializers.IntegerField()
    text = serializers.CharField()