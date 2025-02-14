from .models import TodoList
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password 
from django.contrib.auth.models import User
from rest_framework import serializers

class UserValidationMixin:
    def validate(self, attrs):
        # Trim username and password fields
        attrs['username'] = attrs['username'].strip()
        attrs['password'] = attrs['password'].strip()
        attrs['password2'] = attrs['password2'].strip()

        # Ensure password and password2 match
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    

class TodoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoList
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer, UserValidationMixin):
    username = serializers.CharField(max_length=150, allow_blank=True)
    password = serializers.CharField(write_only=True, allow_blank=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, allow_blank=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password2']

    def validate(self, attrs):
        # Call the validate method from UserValidationMixin
        attrs = UserValidationMixin.validate(self, attrs)
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])  # Hash password
        validated_data.pop('password2', None)  # Remove password2 field

        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'username' in validated_data:
            if validated_data['username'] == '':
                validated_data.pop('username')
            instance.username = validated_data.get('username', instance.username)
        
        if 'password' in validated_data:
            if validated_data['password'] == '':
                validated_data.pop('password')
                validated_data.pop('password2', None)  # Remove password2 field
            else:
                validated_data['password'] = make_password(validated_data['password'])  # Hash on update
                validated_data.pop('password2', None)  # Remove password2 field

        return super().update(instance, validated_data)


class UserRegistrationSerializer(serializers.ModelSerializer, UserValidationMixin):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        # Call the validate method from UserValidationMixin
        attrs = UserValidationMixin.validate(self, attrs)
        return super().validate(attrs)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
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
            raise serializers.ValidationError("Invalid credentials")
        
        attrs['user'] = user

        return attrs

