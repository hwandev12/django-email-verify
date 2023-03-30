from django.urls import path, re_path
from .views import getRoutes, MyTokenObtainPariView, RegisterView, VerifyEmail
from rest_framework_simplejwt.views import (
    TokenRefreshView
)

urlpatterns = [
    path("", getRoutes, name='routes'),

    path('token/', MyTokenObtainPariView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path("register/", RegisterView.as_view(), name='register'),
    path("verify-email/", VerifyEmail.as_view(), name='verify_email'),
    

]
