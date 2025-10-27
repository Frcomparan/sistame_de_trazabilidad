import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    """Custom user model using UUID as primary key."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        db_table = 'auth_user'
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"


class UserProfile(models.Model):
    """Extensión del perfil de usuario con roles."""
    ROLES = [
        ('ADMIN', 'Administrador'),
        ('SUPERVISOR', 'Supervisor'),
        ('FIELD_TECH', 'Técnico de Campo'),
        ('CONSULTANT', 'Consultor'),
        ('INTEGRATION', 'Integración'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='profile',
        verbose_name="Usuario"
    )
    role = models.CharField(max_length=20, choices=ROLES, verbose_name="Rol")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    notes = models.TextField(blank=True, null=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class AuditLog(models.Model):
    """Modelo para registro de auditoría de operaciones."""
    ACTIONS = [
        ('CREATE_EVENT', 'Crear Evento'),
        ('UPDATE_EVENT', 'Actualizar Evento'),
        ('DELETE_EVENT', 'Eliminar Evento'),
        ('CREATE_FIELD', 'Crear Campo'),
        ('UPDATE_FIELD', 'Actualizar Campo'),
        ('DELETE_FIELD', 'Eliminar Campo'),
        ('CREATE_CAMPAIGN', 'Crear Campaña'),
        ('UPDATE_CAMPAIGN', 'Actualizar Campaña'),
        ('CREATE_EVENT_TYPE', 'Crear Tipo de Evento'),
        ('UPDATE_EVENT_TYPE', 'Actualizar Tipo de Evento'),
        ('API_READ', 'Lectura API'),
        ('API_WRITE', 'Escritura API'),
        ('LOGIN', 'Inicio de Sesión'),
        ('LOGOUT', 'Cierre de Sesión'),
        ('LOGIN_FAILED', 'Intento de Login Fallido'),
        ('EXPORT_REPORT', 'Exportar Reporte'),
    ]

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='audit_logs',
        verbose_name="Usuario"
    )
    action = models.CharField(max_length=50, choices=ACTIONS, verbose_name="Acción")
    entity = models.CharField(max_length=50, verbose_name="Entidad")
    entity_id = models.CharField(max_length=100, verbose_name="ID de Entidad")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="Dirección IP")
    user_agent = models.CharField(max_length=255, blank=True, null=True, verbose_name="User Agent")
    diff = models.JSONField(blank=True, null=True, verbose_name="Diferencias", 
                           help_text="Cambios antes/después")

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['entity', 'entity_id']),
            models.Index(fields=['-timestamp']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else "Anónimo"
        return f"{user_str} - {self.get_action_display()} - {self.entity} #{self.entity_id}"
