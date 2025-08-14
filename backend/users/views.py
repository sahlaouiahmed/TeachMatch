from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from rest_framework import status, permissions, views
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserSerializer, RegisterSerializer, UserUpdateSerializer,
    PasswordChangeSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, EmailVerificationRequestSerializer
)

User = get_user_model()

def _jwt_for(user: User):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}

class RegisterView(views.APIView):
    def post(self, request):
        s = RegisterSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=400)
        user = s.save()
        tokens = _jwt_for(user)
        return Response({"user": UserSerializer(user).data, **tokens}, status=201)

class LoginView(views.APIView):
    def post(self, request):
        email = (request.data.get("email") or "").lower()
        password = request.data.get("password") or ""
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"detail": "Invalid credentials"}, status=401)

        if not user.check_password(password):
            return Response({"detail": "Invalid credentials"}, status=401)

        tokens = _jwt_for(user)
        return Response({"user": UserSerializer(user).data, **tokens}, status=200)

class MeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    parser_classes = [MultiPartParser, FormParser]  # allow avatar upload

    def patch(self, request):
        s = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if s.is_valid():
            user = s.save()
            return Response(UserSerializer(user).data)
        return Response(s.errors, status=400)

class ChangePasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        s = PasswordChangeSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=400)
        if not request.user.check_password(s.validated_data["old_password"]):
            return Response({"old_password": ["Incorrect password"]}, status=400)
        request.user.set_password(s.validated_data["new_password"])
        request.user.save()
        return Response({"detail": "Password changed successfully"})

class PasswordResetRequestView(views.APIView):
    def post(self, request):
        s = PasswordResetRequestSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=400)

        email = s.validated_data["email"].lower()
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Don't leak which emails exist
            return Response({"detail": "If the email exists, a reset link was sent."})

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        api_link = f"{request.build_absolute_uri('/').rstrip('/')}/api/users/reset-password/confirm/?uid={uid}&token={token}"
        # Optional: point to frontend page if you have it
        fe_link = f"{settings.SITE_URL}/reset-password?uid={uid}&token={token}"

        send_mail(
            subject="TeachMatch: Password reset",
            message=f"Reset your password:\n\nAPI: {api_link}\nFrontend: {fe_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )
        return Response({"detail": "If the email exists, a reset link was sent."})

class PasswordResetConfirmView(views.APIView):
    def post(self, request):
        s = PasswordResetConfirmSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=400)

        try:
            uid = force_str(urlsafe_base64_decode(s.validated_data["uid"]))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"detail": "Invalid link"}, status=400)

        token = s.validated_data["token"]
        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired token"}, status=400)

        user.set_password(s.validated_data["new_password"])
        user.save()
        return Response({"detail": "Password has been reset"})

class EmailVerificationRequestView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.is_verified:
            return Response({"detail": "Already verified"})
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        api_link = f"{request.build_absolute_uri('/').rstrip('/')}/api/users/verify-email/?uid={uid}&token={token}"
        fe_link = f"{settings.SITE_URL}/verify-email?uid={uid}&token={token}"
        send_mail(
            subject="TeachMatch: Verify your email",
            message=f"Verify your email:\n\nAPI: {api_link}\nFrontend: {fe_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
        return Response({"detail": "Verification email sent"})

class VerifyEmailView(views.APIView):
    def get(self, request):
        uid = request.query_params.get("uid")
        token = request.query_params.get("token")
        if not uid or not token:
            return Response({"detail": "Missing uid or token"}, status=400)
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except Exception:
            return Response({"detail": "Invalid link"}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired token"}, status=400)

        user.is_verified = True
        user.save()
        return Response({"detail": "Email verified"})
