from .models import TodoList
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password 
from django.contrib.auth.models import User
from rest_framework import serializers
import re

class UserValidationMixin:
    def validate(self, attrs):
        # Trim username and password fields
        attrs['username'] = attrs['username'].strip()
        attrs['email'] = attrs['email'].strip()
        attrs['password'] = attrs['password'].strip()
        attrs['confirm_password'] = attrs['confirm_password'].strip()

        email_regex = re.compile(
        r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        )

        # email validation
        if not email_regex.match(attrs['email']):
            raise serializers.ValidationError("Please enter a valid email address.")

        # Ensure password and confirm_password match
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    

class TodoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoList
        fields = ['id', 'title', 'content', 'is_done', 'is_archived', 'deadline']

    def create(self, validated_data):
        user = self.context['request'].user
        return TodoList.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if value == '':
                continue
            setattr(instance, attr, value)
        instance.save()
        return instance

class UserSerializer(serializers.ModelSerializer, UserValidationMixin):
    username = serializers.CharField(max_length=150, allow_blank=True)
    email = serializers.EmailField(allow_blank=True)
    password = serializers.CharField(write_only=True, allow_blank=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, allow_blank=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'confirm_password']

    def validate(self, attrs):
        # Call the validate method from UserValidationMixin
        attrs = UserValidationMixin.validate(self, attrs)
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])  # Hash password
        validated_data.pop('confirm_password', None)  # Remove confirm_password field
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'username' in validated_data:
            if validated_data['username'] == '':
                validated_data.pop('username')
            else:
                instance.username = validated_data.get('username', instance.username)
        
        if 'email' in validated_data:
            if validated_data['email'] == '':
                validated_data.pop('email')
            else:
                instance.email = validated_data.get('email', instance.email)
        
        if 'password' in validated_data:
            if validated_data['password'] == '':
                validated_data.pop('password')
                validated_data.pop('confirm_password', None)  # Remove confirm_password field
            else:
                instance.password = make_password(validated_data['password'])  # Hash on update
                validated_data.pop('confirm_password', None)  # Remove confirm_password field

        instance.save()
        return instance

class UserRegistrationSerializer(serializers.ModelSerializer, UserValidationMixin):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        # Call the validate method from UserValidationMixin
        attrs = UserValidationMixin.validate(self, attrs)

        # Check if username already exists
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError()
        
        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("A user with this email address already exists.")
        
        return super().validate(attrs)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get('request'),
            username=attrs.get('username'),
            password=attrs.get('password')
        )

        if not user:
            raise serializers.ValidationError({"error": "Invalid credentials"})
        
        attrs['user'] = user

        return attrs


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user is associated with this email address.")
        return value
    

class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Password fields didn't match.")
        return attrs
    
    def save(self, user):
        user.password = make_password(self.validated_data['password'])
        user.save()