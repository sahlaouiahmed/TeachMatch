from django.urls import path
from .views import (
    RegisterView, LoginView, MeView,
    ChangePasswordView,
    PasswordResetRequestView, PasswordResetConfirmView,
    EmailVerificationRequestView, VerifyEmailView
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("me/", MeView.as_view()),
    path("change-password/", ChangePasswordView.as_view()),

    path("reset-password/request/", PasswordResetRequestView.as_view()),
    path("reset-password/confirm/", PasswordResetConfirmView.as_view()),

    path("verify-email/request/", EmailVerificationRequestView.as_view()),
    path("verify-email/", VerifyEmailView.as_view()),
]
