from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer, RegisterSerializer, SigninSerializer
from django.contrib.auth.backends import ModelBackend
from django.utils.timezone import now
from django.db.models import Q
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

# Views
class SignupView(APIView):
    """
    Register a new user.
    
    Endpoint: /signup/
    Method: POST
    
    Request Body (application/json):
        {
            "username": "string",
            "email": "string",
            "password": "string"
        }
    
    Response (201):
        User data with JWT tokens on success.
    """
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer  # For schema generation

    def post(self, request):    
        """
        Handle user registration. Expects username, email, and password in the request body.
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=201)
        return Response(serializer.errors, status=400)

class SigninView(APIView):
    """
    Authenticate a user with email and password.
    
    Endpoint: /signin/
    Method: POST
    
    Request Body (application/json):
        {
            "email": "string",
            "password": "string"
        }
    
    Response (200):
        User data with JWT tokens on success.
    """
    permission_classes = [AllowAny]
    serializer_class = SigninSerializer  # For schema generation

    def post(self, request):
        """
        Handle user authentication. Expects email and password in the request body.
        """
        serializer = SigninSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
        username = user.username
        authenticated_user = authenticate(username=username, password=password)
        if authenticated_user:
            authenticated_user.last_login = now()
            authenticated_user.save(update_fields=['last_login'])  
            return Response(UserSerializer(authenticated_user).data, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
    

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f"https://your-frontend.com/reset-password?uid={uid}&token={token}"
            # send_mail(
            #     subject="Reset your password",
            #     message=f"Click the link to reset: {reset_url}",
            #     from_email="support@yourapp.com",
            #     recipient_list=[email],
            # )
        return Response({"message": "If that email exists, we sent a reset link."})
    
class ResetPasswordView(APIView):
    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        try:
            uid = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Invalid token"}, status=400)

        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password reset successful."})
        else:
            return Response({"error": "Invalid or expired token"}, status=400)
        

class RefreshTokenView(TokenRefreshView):
    """
    Refresh JWT tokens.
    
    Endpoint: /token/refresh/
    Method: POST
    
    Request Body (application/json):
        {
            "refresh": "string"
        }
    
    Response (200):
        New access and refresh tokens.
    """
    permission_classes = [AllowAny]

class UserProfileEditView(APIView):
    """
    Edit the authenticated user's profile.
    
    Endpoint: /profile/edit/
    Method: PUT
    
    Request Body (application/json):
        Partial or full user fields (e.g., first_name, last_name, email)
    
    Response (200):
        Updated user data.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        """
        Handle profile update for the authenticated user.
        """
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)