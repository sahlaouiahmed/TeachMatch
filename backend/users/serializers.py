from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "phone_number", "country", "location", "date_of_birth",
            "gender", "bio", "profile_picture", "role", "is_verified",
            "last_seen", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "role", "is_verified", "last_seen", "created_at", "updated_at", "username"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "country"]

    def create(self, validated_data):
        email = validated_data["email"].lower()
        # Ensure username exists even though we log in by email
        username = email
        user = User(
            username=username,
            email=email,
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            country=validated_data.get("country", ""),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "phone_number", "country", "location",
            "date_of_birth", "gender", "bio", "profile_picture",
        ]
        extra_kwargs = {"profile_picture": {"required": False}}

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])

class EmailVerificationRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
