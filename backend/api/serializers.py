from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Dataset
from datetime import datetime

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()



class DatasetSerializer(serializers.ModelSerializer):
    filename = serializers.SerializerMethodField()
    uploaded = serializers.SerializerMethodField()

    class Meta:
        model = Dataset
        fields = ["id", "filename", "uploaded", "summary"]

    def get_filename(self, obj):
        return obj.file.name.split("/")[-1]

    def get_uploaded(self, obj):
        return obj.uploaded_at.strftime("%b %d, %Y – %I:%M %p")

