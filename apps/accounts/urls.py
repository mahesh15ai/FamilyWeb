from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ChangePasswordAPIView,
    ForgotPasswordAPIView,
    LoginAPIView,
    LogoutAPIView,
    ProfileAPIView,
    RegisterAPIView,
    ResetPasswordAPIView,
)

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", ProfileAPIView.as_view(), name="profile"),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change_password"),
    path("forgot-password/", ForgotPasswordAPIView.as_view(), name="forgot_password"),
    path("reset-password/", ResetPasswordAPIView.as_view(), name="reset_password"),
]