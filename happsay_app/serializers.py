from .models import TodoList
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers



class TodoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoList
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password']


    def create(self, validated_data):

        validated_data['password'] = make_password(validated_data['password'])  # Hash password

        return super().create(validated_data)


    def update(self, instance, validated_data):

        if 'password' in validated_data:

            validated_data['password'] = make_password(validated_data['password'])  # Hash on update

        return super().update(instance, validated_data)
