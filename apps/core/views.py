from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import CustomTokenObtainPairSerializer


class CustomLoginView(LoginView):
    """
    Vista personalizada de login que redirige al dashboard si el usuario ya está autenticado.
    """
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirigir al dashboard después del login exitoso."""
        return reverse_lazy('dashboard')


@login_required
def dashboard_view(request):
    """Vista del dashboard principal después del login."""
    return render(request, 'dashboard.html')


# ========== API Views ==========

@extend_schema(
    summary="Obtener Token JWT",
    description="""
    Autentica al usuario y obtiene un par de tokens JWT (access y refresh).
    
    El token de acceso (access token) debe incluirse en el header Authorization 
    de todas las peticiones protegidas: `Authorization: Bearer {access_token}`
    
    **Flujo de autenticación:**
    1. Enviar credenciales (username y password)
    2. Recibir access_token y refresh_token
    3. Usar access_token en peticiones subsecuentes
    4. Cuando expire, usar refresh_token para obtener nuevo access_token
    
    **Duración de tokens:**
    - Access Token: 60 minutos (configurable)
    - Refresh Token: 24 horas (configurable)
    
    **Información incluida:**
    - Tokens JWT firmados
    - Información básica del usuario autenticado
    """,
    tags=['Autenticación'],
    examples=[
        OpenApiExample(
            'Login exitoso',
            summary='Respuesta de autenticación exitosa',
            description='Ejemplo de respuesta cuando las credenciales son válidas',
            value={
                'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'user': {
                    'id': '550e8400-e29b-41d4-a716-446655440000',
                    'username': 'admin',
                    'email': 'admin@example.com',
                    'full_name': 'Administrador',
                    'is_staff': True,
                    'is_superuser': True
                }
            },
            response_only=True,
        ),
    ],
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista personalizada para obtener tokens JWT.
    Incluye información adicional del usuario en la respuesta.
    """
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
    summary="Refrescar Token JWT",
    description="""
    Obtiene un nuevo token de acceso (access token) usando un refresh token válido.
    
    Cuando el access token expira, puedes usar el refresh token para obtener 
    uno nuevo sin necesidad de volver a enviar las credenciales del usuario.
    
    **Flujo:**
    1. El access token expira después de 60 minutos
    2. Enviar el refresh token a este endpoint
    3. Recibir un nuevo access token
    4. Actualizar el token en tu aplicación cliente
    
    **Notas importantes:**
    - El refresh token también expira (24 horas por defecto)
    - Cada vez que se usa, se genera un nuevo refresh token (rotación)
    - El refresh token antiguo se invalida automáticamente
    
    **Seguridad:**
    - Los tokens expirados no pueden ser refrescados
    - Los tokens invalidados (blacklist) son rechazados
    - La rotación de tokens previene reutilización
    """,
    tags=['Autenticación'],
    examples=[
        OpenApiExample(
            'Token refrescado',
            summary='Respuesta de refresh exitoso',
            description='Ejemplo de respuesta cuando el refresh es válido',
            value={
                'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
            },
            response_only=True,
        ),
    ],
)
class CustomTokenRefreshView(TokenRefreshView):
    """
    Vista para refrescar tokens JWT.
    Permite obtener un nuevo access token sin reautenticarse.
    """
    pass

