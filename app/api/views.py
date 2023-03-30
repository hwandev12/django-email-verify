from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics, status, views
from .serializers import RegisterSerializer, VerifyEmailSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
import jwt
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from ..models import User
from django.urls import reverse

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username

        return token

class MyTokenObtainPariView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(["GET"])
def getRoutes(request):
    routes = [
        "/api/token",
        "/api/token/refresh"
    ]
    return Response(routes)

class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    
    def post(self, request):
        user = request.data
        serializers = self.serializer_class(data=user)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        
        user_data = serializers.data
        user = User.objects.get(email=user_data['email'])
        
        token = RefreshToken.for_user(user).access_token
        
        current_site = get_current_site(request).domain
        relativeLink = reverse("verify_email")
        absoluteurl = "http://" + current_site + relativeLink + "?token=" + str(token)
        email_body = "Hi " + user.username + ". Use link below to verify your email\n" + absoluteurl
        data = {"email_body": email_body, "to_email": user.email, "email_subject": "Verify Email"}
        
        Util.send_email(data)
        
        return Response(user_data, status=status.HTTP_201_CREATED)

class VerifyEmail(views.APIView):
    serializer_class = VerifyEmailSerializer
    token_params_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description='email verify', type=openapi.TYPE_STRING)

    
    @swagger_auto_schema(manual_parameters=[token_params_config])
    def get(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
            user = User.objects.get(id=payload["user_id"])
            if user.is_active and not user.is_verified:
                user.is_verified = True
                user.save()
            
            return Response({"email": "Your email is successfully activated"}, status=status.HTTP_200_OK)
            
        except jwt.ExpiredSignatureError as identifier:
            return Response({"error": "Your activation link is expired"}, status=status.HTTP_400_BAD_REQUEST)
        
        except jwt.DecodeError as identifier:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
