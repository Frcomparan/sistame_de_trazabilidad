"""
Serializers para la API de Autenticación.
Incluye serialización para tokens JWT.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para obtener tokens JWT.
    Incluye información adicional del usuario en la respuesta.
    """
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Agregar claims personalizados al token
        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Agregar información adicional del usuario en la respuesta
        data['user'] = {
            'id': str(self.user.id),
            'username': self.user.username,
            'email': self.user.email,
            'full_name': self.user.get_full_name() or self.user.username,
            'is_staff': self.user.is_staff,
            'is_superuser': self.user.is_superuser,
        }
        
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo User.
    Incluye información básica del usuario autenticado.
    """
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'is_staff',
            'is_superuser',
            'is_active',
            'date_joined',
            'last_login',
        ]
        read_only_fields = fields
    
    def get_full_name(self, obj):
        """Retorna el nombre completo del usuario."""
        return obj.get_full_name() or obj.username
