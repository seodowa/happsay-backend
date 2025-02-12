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


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=make_password(validated_data['password'])
        )
        return user