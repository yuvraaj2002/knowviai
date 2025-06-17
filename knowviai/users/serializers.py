from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

# Serializers
class UserSerializer(serializers.ModelSerializer):
    refresh = serializers.SerializerMethodField()
    access = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'refresh', 'access', 'last_login', 'is_superuser', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined']

    def get_refresh(self, user):
        return str(RefreshToken.for_user(user))

    def get_access(self, user):
        return str(RefreshToken.for_user(user).access_token)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Remove the UUID from username when returning data
        if '_' in data['username']:
            data['username'] = data['username'].split('_')[0]
        return data


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        email = data['email'].strip().lower()
        
        # Check if email is already registered
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("This email is already registered. Kindly Sign In.")

        return data
    
    def validate_username(self, value):
        """Ensure username does not contain `_` before storing it in the database."""
        if "_" in value:
            raise serializers.ValidationError("Username cannot contain the '_' character.")
        return value
    
    def create(self, validated_data):
        """Append a UUID to the username before storing it in the database."""
        username = validated_data.get('username')
        username_with_uuid = f"{username}_{uuid.uuid4()}"  
        validated_data['username'] = username_with_uuid
        user = User.objects.create_user(**validated_data)
        return user

class SigninSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    