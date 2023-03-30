from rest_framework import serializers
from ..models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=60, min_length=6, write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        
    def validate(self, attrs):
        email = attrs.get("email", "")
        username = attrs.get("username", "")
        
        if not username.isalnum():
            raise serializers.ValidationError("Username must only have word alphanumerics")
        return attrs
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
class VerifyEmailSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=344)
    
    class Meta:
        model = User
        fields = ["token"]