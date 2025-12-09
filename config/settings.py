"""
Django settings para el Sistema de Trazabilidad Agrícola.
"""

import os
from pathlib import Path
from datetime import timedelta
import environ

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Inicializar django-environ
env = environ.Env(
    DEBUG=(bool, False)
)

# Leer archivo .env si existe
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-dev-key-CHANGE-IN-PRODUCTION')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', 'nwuzeo-ip-189-195-132-181.tunnelmole.net'])

# CSRF Configuration
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'http://localhost',
    'http://127.0.0.1',
    'https://*.tunnelmole.net',
])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_extensions',
    
    # Local apps
    'apps.core',
    'apps.catalogs',
    'apps.events',
    'apps.reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.middleware.AuditMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB', default='trazabilidad_db'),
        'USER': env('POSTGRES_USER', default='trazabilidad_user'),
        'PASSWORD': env('POSTGRES_PASSWORD', default='trazabilidad_pass'),
        'HOST': env('POSTGRES_HOST', default='localhost'),
        'PORT': env('POSTGRES_PORT', default='5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = env('TIME_ZONE', default='America/Mexico_City')
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'core.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env.int('JWT_ACCESS_TOKEN_LIFETIME', default=60)),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=env.int('JWT_REFRESH_TOKEN_LIFETIME', default=1440)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': env('JWT_SECRET_KEY', default=SECRET_KEY),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS Settings
CORS_ALLOW_ALL_ORIGINS = env.bool('CORS_ALLOW_ALL_ORIGINS', default=DEBUG)
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# DRF Spectacular (OpenAPI)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Sistema de Trazabilidad Agrícola - API',
    'DESCRIPTION': """
    API REST para el Sistema de Trazabilidad de Cultivo de Limón.
    
    ## Descripción General
    
    Este sistema permite gestionar la trazabilidad completa del cultivo de limón, desde la 
    definición de campos y campañas hasta el registro detallado de eventos durante el ciclo productivo.
    
    ## Módulos Principales
    
    ### 🌾 Catálogos
    - **Campos (Fields)**: Gestión de parcelas o terrenos de cultivo
    - **Campañas (Campaigns)**: Ciclos productivos y temporadas
    - **Estaciones (Stations)**: Dispositivos de monitoreo IoT
    
    ### 📋 Eventos de Trazabilidad
    - Registro de actividades agrícolas (riego, fertilización, cosecha)
    - Tipos de eventos personalizables con esquemas JSON
    - Validación automática de datos mediante JSON Schema
    
    ### 📊 Reportes y Análisis
    - Health check del sistema
    - Estadísticas de producción (próximamente)
    - Análisis de trazabilidad (próximamente)
    
    ## Autenticación
    
    La API utiliza **JWT (JSON Web Tokens)** para autenticación.
    
    1. Obtener token: `POST /api/v1/auth/token/`
    2. Usar token en headers: `Authorization: Bearer {token}`
    3. Refrescar token: `POST /api/v1/auth/token/refresh/`
    
    ## Versionado
    
    - Version actual: **v1**
    - Base URL: `/api/v1/`
    - Todas las rutas incluyen el prefijo de versión
    
    ## Contacto y Soporte
    
    - Proyecto: Sistema de Trazabilidad Agrícola
    - Versión: 1.0.0
    - Tecnología: Django REST Framework + PostgreSQL
    """,
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v1/',
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
    'SERVERS': [
        {
            'url': 'http://localhost:8000',
            'description': 'Servidor de Desarrollo'
        },
    ],
    'TAGS': [
        {
            'name': 'Autenticación',
            'description': 'Endpoints para autenticación JWT (obtener y refrescar tokens)',
        },
        {
            'name': 'Catálogos - Campos',
            'description': 'Gestión de campos/parcelas agrícolas donde se realiza el cultivo',
        },
        {
            'name': 'Catálogos - Campañas',
            'description': 'Gestión de campañas/ciclos productivos de cultivo',
        },
        {
            'name': 'Eventos de Trazabilidad',
            'description': 'Registro y consulta de eventos durante el ciclo de cultivo',
        },
        {
            'name': 'Sistema - Reportes',
            'description': 'Endpoints de sistema, monitoreo y reportes',
        },
    ],
    'EXTERNAL_DOCS': {
        'description': 'Documentación completa del proyecto',
        'url': 'https://github.com/Frcomparan/sistame_de_trazabilidad',
    },
    'CONTACT': {
        'name': 'Equipo de Desarrollo',
        'email': 'support@trazabilidad-agricola.com',
    },
    'LICENSE': {
        'name': 'MIT License',
    },
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}

# Crear directorio de logs si no existe
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Authentication Settings
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
