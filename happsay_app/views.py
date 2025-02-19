from django.http import HttpResponseRedirect
from .serializers import UserSerializer, TodoListSerializer, UserRegistrationSerializer, LoginSerializer
from .models import TodoList
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, render
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions, viewsets, status           



# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        """
        Handle PUT requests for user update.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({"message": "Update successful"}, status=status.HTTP_200_OK)

class TodoListViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows todo lists to be viewed or edited.
    """
    serializer_class = TodoListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        This view should return a list of all the todo lists
        for the currently authenticated user.
        """
        user = self.request.user
        return TodoList.objects.filter(user=user)


class RegisterAPIView(APIView):
    """
    API endpoint that allows users to register.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Handle POST requests for user registration.
        """
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginAPIView(APIView):
    """
    API endpoint that allows users to log in.
    """
    http_method_names = ['post']
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Handle POST requests for user login.
        """
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        login(request, user)
        refresh = RefreshToken.for_user(user)

        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "redirect_url": "/todolist/"
        }, status=status.HTTP_200_OK)


