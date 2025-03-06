import os

from django.http import HttpResponse
from django.views import View
from .serializers import (UserSerializer, TodoListSerializer, 
                          UserRegistrationSerializer, LoginSerializer,
                          PasswordResetSerializer, PasswordResetConfirmSerializer)
from .models import TodoList
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import permissions, viewsets, status
import happsay_backend.settings as settings           



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

        to filter by is_done, /todolist/?is_done=true
        to filter by is_archived, /todolist/?is_archived=true
        """
        
        user = self.request.user
        is_done = self.request.query_params.get('is_done')
        is_archived = self.request.query_params.get('is_archived')

        queryset = TodoList.objects.filter(user=user)

        if is_done is not None:
            queryset = queryset.filter(is_done=is_done.title())
        if is_archived is not None:
            queryset = queryset.filter(is_archived=is_archived.title())

        return queryset


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
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)

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
    

class PasswordResetView(APIView):
    """
    API endpoint that allows users to reset their password.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        token = RefreshToken.for_user(user)

        # temporary solution to get the reset link
        #reset_link = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'token': str(token)}))
        reset_link = f"https://happsay-frontend.vercel.app/reset-password/{str(token)}"

        send_mail(
            'Password Reset Request',
            f'Hello {user.username}, you have requested for a password reset. Please click the link to reset your password: {reset_link}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return Response({"message": f"Password reset link sent has been sent to {email}."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    Password Reset confirmation after the user clicks the link sent to their email.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, token):
        try:
            # Decode the token to get the user
            UntypedToken(token)
            user_id = RefreshToken(token).payload['user_id']
            user = User.objects.get(id=user_id)

        except (InvalidToken, TokenError, User.DoesNotExist):
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user)

        # Blacklist the token
        try:
            refresh_token = RefreshToken(token)
            refresh_token.blacklist()
        except Exception as e:
            return Response({"error": f"Failed to blacklist token. {e}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Password has been reset."}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            logout(request)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({
                "message": "Successfully logged out.",
                "redirect_url": "/"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Failed to blacklist token. {e}"}, status=status.HTTP_400_BAD_REQUEST)
        


class ZeroSSLValidationTextView(View):
    def get(self, request, filename, *args, **kwargs):
        if not (file_path := os.path.join(settings.BASE_DIR, "happsay_backend", "static_files", filename)):
            return HttpResponse("File not found", status=
                                status.HTTP_404_NOT_FOUND)
        with open(file_path, 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type="text/plain")
    

class ValidateTokenView(APIView):
    def post(self, request):
        token = request.data.get('token')

        if not token:
            return Response({'valid': False, 'message': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            UntypedToken(token)
            return Response({'valid': True}, status=status.HTTP_200_OK)
        except (InvalidToken, TokenError):
            return Response({'valid': False, 'message': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)