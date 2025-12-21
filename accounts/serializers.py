# accounts/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "phone", "bio", "profile_image", "is_staff")
        read_only_fields = ("id", "is_staff")

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2", "phone", "bio")

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop("password2", None)
        password = validated_data.pop("password")
        # Create user using create_user so password is hashed
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
      
        token["username"] = user.username
        token["email"] = user.email
        return token

    def validate(self, attrs):
      
        username_or_email = attrs.get("username")
        password = attrs.get("password")

     
        user = None
        if username_or_email is not None:
            from django.contrib.auth import get_user_model
            UserModel = get_user_model()
            try:
                # prefer exact username match
                user = UserModel.objects.get(username=username_or_email)
            except UserModel.DoesNotExist:
                # fallback to email lookup
                try:
                    user = UserModel.objects.get(email__iexact=username_or_email)
                except UserModel.DoesNotExist:
                    user = None

        # If found, check password
        if user is None or not user.check_password(password):
            raise serializers.ValidationError({"detail": "No active account found with the given credentials"}, code="authorization")

        # Create tokens using parent class (it expects self.user to be set)
        self.user = user
        data = super().validate({"username": user.username, "password": password})
        # Optionally attach serialized user profile to response
        data["user"] = UserSerializer(user).data
        return data
