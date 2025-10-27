from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Field(models.Model):
    """Modelo para parcelas/lotes de cultivo."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="Nombre")
    code = models.CharField(max_length=50, unique=True, verbose_name="Código")
    surface_ha = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Superficie (ha)"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="Notas")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fields'
        ordering = ['-created_at']
        verbose_name = "Campo/Parcela"
        verbose_name_plural = "Campos/Parcelas"
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Campaign(models.Model):
    """Modelo para campañas/temporadas de cultivo."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="Nombre")
    season = models.CharField(max_length=50, blank=True, null=True, verbose_name="Temporada")
    variety = models.CharField(max_length=100, blank=True, null=True, verbose_name="Variedad")
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(blank=True, null=True, verbose_name="Fecha de Fin")
    notes = models.TextField(blank=True, null=True, verbose_name="Notas")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaigns'
        ordering = ['-start_date']
        verbose_name = "Campaña"
        verbose_name_plural = "Campañas"
        indexes = [
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__isnull=True) | models.Q(end_date__gte=models.F('start_date')),
                name='check_campaign_dates'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.season or 'N/A'})"


class Station(models.Model):
    """Modelo para estaciones de monitoreo."""
    STATION_TYPES = [
        ('clima', 'Clima'),
        ('suelo', 'Suelo'),
        ('multivariable', 'Multivariable'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="Nombre")
    field = models.ForeignKey(
        Field, 
        on_delete=models.CASCADE, 
        related_name='stations',
        verbose_name="Campo"
    )
    station_type = models.CharField(
        max_length=50, 
        choices=STATION_TYPES, 
        default='multivariable',
        verbose_name="Tipo de Estación"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="Notas")
    is_operational = models.BooleanField(default=True, verbose_name="Operacional")
    installed_at = models.DateField(blank=True, null=True, verbose_name="Fecha de Instalación")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stations'
        ordering = ['name']
        verbose_name = "Estación de Monitoreo"
        verbose_name_plural = "Estaciones de Monitoreo"
        indexes = [
            models.Index(fields=['field']),
            models.Index(fields=['is_operational']),
        ]

    def __str__(self):
        return f"{self.name} - {self.field.name}"
