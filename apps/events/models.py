from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
import uuid


class EventType(models.Model):
    """Modelo para definir tipos de eventos con esquemas dinámicos."""
    CATEGORIES = [
        ('irrigation', 'Riego'),
        ('fertilization', 'Fertilización'),
        ('phytosanitary', 'Fitosanitarios'),
        ('maintenance', 'Labores de Cultivo'),
        ('monitoring', 'Monitoreo'),
        ('harvest', 'Cosecha'),
        ('postharvest', 'Poscosecha'),
        ('analysis', 'Análisis'),
        ('pruning', 'Poda'),
        ('other', 'Otro'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    category = models.CharField(max_length=50, choices=CATEGORIES, verbose_name="Categoría")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    schema = models.JSONField(default=dict, verbose_name="Esquema JSON", help_text="JSON Schema para validación")
    version = models.IntegerField(default=1, verbose_name="Versión")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="Icono CSS")
    color = models.CharField(max_length=7, blank=True, null=True, verbose_name="Color Hex")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'event_types'
        ordering = ['category', 'name']
        verbose_name = "Tipo de Evento"
        verbose_name_plural = "Tipos de Eventos"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Event(models.Model):
    """Modelo para instancias de eventos registrados."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.ForeignKey(
        EventType, 
        on_delete=models.PROTECT, 
        related_name='events',
        verbose_name="Tipo de Evento"
    )
    field = models.ForeignKey(
        'catalogs.Field', 
        on_delete=models.CASCADE, 
        related_name='events',
        verbose_name="Campo"
    )
    campaign = models.ForeignKey(
        'catalogs.Campaign', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='events',
        verbose_name="Campaña"
    )
    timestamp = models.DateTimeField(verbose_name="Fecha y Hora")
    payload = models.JSONField(default=dict, verbose_name="Datos", help_text="Datos capturados según el esquema")
    observations = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='events_created',
        verbose_name="Creado Por"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        ordering = ['-timestamp']
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        indexes = [
            models.Index(fields=['field', '-timestamp']),
            models.Index(fields=['event_type']),
            models.Index(fields=['campaign']),
            models.Index(fields=['-timestamp']),
            models.Index(fields=['created_by']),
        ]

    def clean(self):
        """Validación personalizada del modelo."""
        super().clean()
        # Validar que el timestamp no esté más de 1 hora en el futuro
        max_timestamp = timezone.now() + timedelta(hours=1)
        if self.timestamp and self.timestamp > max_timestamp:
            from django.core.exceptions import ValidationError
            raise ValidationError({
                'timestamp': f'El timestamp no puede estar más de 1 hora en el futuro. Máximo permitido: {max_timestamp}'
            })

    def __str__(self):
        return f"{self.event_type.name} - {self.field.name} @ {self.timestamp}"


class Attachment(models.Model):
    """Modelo para archivos adjuntos a eventos."""
    id = models.BigAutoField(primary_key=True)
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        related_name='attachments',
        verbose_name="Evento"
    )
    file = models.FileField(upload_to='event_attachments/%Y/%m/', verbose_name="Archivo")
    file_name = models.CharField(max_length=255, verbose_name="Nombre del Archivo")
    file_size = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10485760)],  # Max 10MB
        verbose_name="Tamaño (bytes)"
    )
    mime_type = models.CharField(max_length=100, verbose_name="Tipo MIME")
    metadata = models.JSONField(blank=True, null=True, verbose_name="Metadatos")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='attachments_uploaded',
        verbose_name="Subido Por"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attachments'
        ordering = ['-uploaded_at']
        verbose_name = "Adjunto"
        verbose_name_plural = "Adjuntos"
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['-uploaded_at']),
        ]

    def __str__(self):
        return f"{self.file_name} - {self.event}"


class Variable(models.Model):
    """Modelo para variables ambientales/IoT."""
    VARIABLE_TYPES = [
        ('soil_moisture', 'Humedad del Suelo (%)'),
        ('soil_temp', 'Temperatura del Suelo (°C)'),
        ('soil_ec', 'CE del Suelo (µS/cm)'),
        ('soil_ph', 'pH del Suelo'),
        ('air_temp', 'Temperatura del Aire (°C)'),
        ('humidity', 'Humedad Relativa (%)'),
        ('precipitation', 'Precipitación (mm)'),
        ('wind_speed', 'Velocidad del Viento (m/s)'),
        ('solar_radiation', 'Radiación Solar (W/m²)'),
        ('ndvi', 'NDVI'),
        ('ndre', 'NDRE'),
    ]

    SOURCES = [
        ('manual', 'Manual'),
        ('automatic', 'Automático'),
    ]

    id = models.BigAutoField(primary_key=True)
    station = models.ForeignKey(
        'catalogs.Station', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='variables',
        verbose_name="Estación"
    )
    field = models.ForeignKey(
        'catalogs.Field', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='variables',
        verbose_name="Campo"
    )
    timestamp = models.DateTimeField(verbose_name="Fecha y Hora")
    variable_type = models.CharField(max_length=50, choices=VARIABLE_TYPES, verbose_name="Tipo de Variable")
    value = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="Valor")
    unit = models.CharField(max_length=20, verbose_name="Unidad")
    source = models.CharField(max_length=20, choices=SOURCES, default='manual', verbose_name="Fuente")
    metadata = models.JSONField(blank=True, null=True, verbose_name="Metadatos")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'variables'
        ordering = ['-timestamp']
        verbose_name = "Variable"
        verbose_name_plural = "Variables"
        indexes = [
            models.Index(fields=['station', '-timestamp']),
            models.Index(fields=['field', '-timestamp']),
            models.Index(fields=['variable_type', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(station__isnull=False) | models.Q(field__isnull=False),
                name='check_variable_location'
            )
        ]

    def __str__(self):
        location = self.station.name if self.station else self.field.name
        return f"{self.get_variable_type_display()} = {self.value} {self.unit} @ {location}" 
