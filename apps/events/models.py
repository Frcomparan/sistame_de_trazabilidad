from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
import uuid


class EventType(models.Model):
    """Modelo para definir tipos de eventos predefinidos."""
    CATEGORIES = [
        ('irrigation', 'Riego'),
        ('fertilization', 'Fertilización'),
        ('phytosanitary', 'Fitosanitarios'),
        ('maintenance', 'Labores de Cultivo'),
        ('monitoring', 'Monitoreo'),
        ('harvest', 'Cosecha'),
        ('postharvest', 'Poscosecha'),
        ('other', 'Otro'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    category = models.CharField(max_length=50, choices=CATEGORIES, verbose_name="Categoría")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
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
    """Modelo base para eventos de trazabilidad."""
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


# ========== MODELOS ESPECÍFICOS POR TIPO DE EVENTO ==========

class IrrigationEvent(Event):
    """Evento de aplicación de riego."""
    METHOD_CHOICES = [
        ('Aspersión', 'Aspersión'),
        ('Goteo', 'Goteo'),
        ('Surco', 'Surco'),
        ('Pivote', 'Pivote'),
        ('Manual', 'Manual'),
        ('Microaspersión', 'Microaspersión'),
    ]
    
    WATER_SOURCE_CHOICES = [
        ('Pozo', 'Pozo'),
        ('Río', 'Río'),
        ('Presa', 'Presa'),
        ('Red municipal', 'Red municipal'),
        ('Otro', 'Otro'),
    ]

    metodo = models.CharField(max_length=50, choices=METHOD_CHOICES, verbose_name="Método de Riego")
    duracion_minutos = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Duración (minutos)"
    )
    fuente_agua = models.CharField(max_length=50, choices=WATER_SOURCE_CHOICES, verbose_name="Fuente de Agua")
    volumen_m3 = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Volumen (m³)"
    )
    presion_bar = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="Presión (bar)"
    )
    ce_uScm = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="CE (µS/cm)"
    )
    ph = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(14)],
        verbose_name="pH"
    )

    class Meta:
        db_table = 'irrigation_events'
        verbose_name = "Evento de Riego"
        verbose_name_plural = "Eventos de Riego"


class FertilizationEvent(Event):
    """Evento de aplicación de fertilizante."""
    APPLICATION_METHOD_CHOICES = [
        ('Foliar', 'Foliar'),
        ('Fertirriego', 'Fertirriego'),
        ('Edáfica', 'Edáfica'),
        ('Inyección', 'Inyección'),
    ]

    producto = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    metodo_aplicacion = models.CharField(
        max_length=50, 
        choices=APPLICATION_METHOD_CHOICES,
        verbose_name="Método de Aplicación"
    )
    dosis = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Dosis"
    )
    unidad_dosis = models.CharField(
        max_length=20,
        default='kg/ha',
        verbose_name="Unidad de Dosis"
    )
    n_porcentaje = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Nitrógeno (%)"
    )
    p_porcentaje = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Fósforo (%)"
    )
    k_porcentaje = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Potasio (%)"
    )
    volumen_caldo_l = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Volumen de Caldo (L)"
    )

    class Meta:
        db_table = 'fertilization_events'
        verbose_name = "Evento de Fertilización"
        verbose_name_plural = "Eventos de Fertilización"


class PhytosanitaryEvent(Event):
    """Evento de aplicación fitosanitaria."""
    PRODUCT_TYPE_CHOICES = [
        ('Insecticida', 'Insecticida'),
        ('Fungicida', 'Fungicida'),
        ('Herbicida', 'Herbicida'),
        ('Acaricida', 'Acaricida'),
        ('Nematicida', 'Nematicida'),
        ('Bactericida', 'Bactericida'),
        ('Coadyuvante', 'Coadyuvante'),
    ]
    
    APPLICATION_METHOD_CHOICES = [
        ('Mochila manual', 'Mochila manual'),
        ('Mochila motorizada', 'Mochila motorizada'),
        ('Tractor', 'Tractor'),
        ('Dron', 'Dron'),
        ('Avión', 'Avión'),
        ('Fertirrigación', 'Fertirrigación'),
        ('Inyección al tronco', 'Inyección al tronco'),
    ]

    producto = models.CharField(max_length=200, verbose_name="Nombre Comercial")
    ingrediente_activo = models.CharField(
        max_length=200, 
        null=True, 
        blank=True,
        verbose_name="Ingrediente Activo"
    )
    tipo_producto = models.CharField(
        max_length=50, 
        choices=PRODUCT_TYPE_CHOICES,
        verbose_name="Tipo de Producto"
    )
    objetivo = models.CharField(max_length=200, verbose_name="Plaga/Enfermedad/Maleza Objetivo")
    metodo_aplicacion = models.CharField(
        max_length=50, 
        choices=APPLICATION_METHOD_CHOICES,
        verbose_name="Método de Aplicación"
    )
    dosis = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Dosis"
    )
    unidad_dosis = models.CharField(
        max_length=20,
        default='L/ha',
        verbose_name="Unidad de Dosis"
    )
    lote_producto = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Lote del Producto"
    )
    volumen_caldo_l = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Volumen de Caldo (L)"
    )
    presion_bar = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Presión de Aplicación (bar)"
    )
    intervalo_seguridad_dias = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Intervalo de Seguridad (días)"
    )
    responsable_aplicacion = models.CharField(
        max_length=200, 
        null=True, 
        blank=True,
        verbose_name="Responsable de la Aplicación"
    )
    eficacia_observada = models.CharField(
        max_length=20,
        choices=[
            ('No evaluada', 'No evaluada'),
            ('Muy baja', 'Muy baja'),
            ('Baja', 'Baja'),
            ('Media', 'Media'),
            ('Alta', 'Alta'),
            ('Muy alta', 'Muy alta'),
        ],
        null=True,
        blank=True,
        verbose_name="Eficacia Observada"
    )
    fitotoxicidad = models.BooleanField(
        default=False,
        verbose_name="¿Fitotoxicidad Observada?"
    )

    class Meta:
        db_table = 'phytosanitary_events'
        verbose_name = "Evento Fitosanitario"
        verbose_name_plural = "Eventos Fitosanitarios"


class MaintenanceEvent(Event):
    """Evento de labores de cultivo."""
    ACTIVITY_CHOICES = [
        ('Poda', 'Poda'),
        ('Deshierbe', 'Deshierbe'),
        ('Entutorado', 'Entutorado'),
        ('Aclareo de frutos', 'Aclareo de frutos'),
        ('Despunte', 'Despunte'),
        ('Cobertura vegetal', 'Cobertura vegetal'),
        ('Desbrote', 'Desbrote'),
        ('Raleo', 'Raleo'),
        ('Limpieza de canales', 'Limpieza de canales'),
        ('Reparación de sistema de riego', 'Reparación de sistema de riego'),
    ]

    actividad = models.CharField(max_length=100, choices=ACTIVITY_CHOICES, verbose_name="Tipo de Actividad")
    horas_hombre = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Total Horas-Hombre"
    )
    herramienta_equipo = models.CharField(
        max_length=200, 
        null=True, 
        blank=True,
        verbose_name="Herramienta/Equipo Usado"
    )
    numero_jornales = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name="Número de Jornales"
    )
    objetivo = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Objetivo de la Labor"
    )
    porcentaje_completado = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Porcentaje Completado (%)"
    )
    herramientas_desinfectadas = models.BooleanField(
        null=True, 
        blank=True,
        verbose_name="¿Herramientas Desinfectadas?"
    )

    class Meta:
        db_table = 'maintenance_events'
        verbose_name = "Evento de Labores"
        verbose_name_plural = "Eventos de Labores"


class MonitoringEvent(Event):
    """Evento de monitoreo de plagas."""
    SAMPLING_METHOD_CHOICES = [
        ('Visual directa', 'Visual directa'),
        ('Trampa adhesiva', 'Trampa adhesiva'),
        ('Trampa de luz', 'Trampa de luz'),
        ('Muestreo de suelo', 'Muestreo de suelo'),
        ('Muestreo foliar', 'Muestreo foliar'),
        ('Otro', 'Otro'),
    ]

    plaga_enfermedad = models.CharField(max_length=200, verbose_name="Plaga/Enfermedad Observada")
    metodo_muestreo = models.CharField(
        max_length=50, 
        choices=SAMPLING_METHOD_CHOICES,
        verbose_name="Método de Muestreo"
    )
    incidencia = models.CharField(
        max_length=20,
        choices=[
            ('Muy baja', 'Muy baja'),
            ('Baja', 'Baja'),
            ('Media', 'Media'),
            ('Alta', 'Alta'),
            ('Muy alta', 'Muy alta'),
        ],
        verbose_name="Incidencia"
    )
    severidad = models.CharField(
        max_length=20,
        choices=[
            ('Muy baja', 'Muy baja'),
            ('Baja', 'Baja'),
            ('Media', 'Media'),
            ('Alta', 'Alta'),
            ('Muy alta', 'Muy alta'),
        ],
        null=True,
        blank=True,
        verbose_name="Severidad"
    )
    ubicacion_campo = models.CharField(
        max_length=200, 
        null=True, 
        blank=True,
        verbose_name="Ubicación en el Campo"
    )
    numero_muestras = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name="Número de Muestras"
    )
    accion_recomendada = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Acción Recomendada"
    )

    class Meta:
        db_table = 'monitoring_events'
        verbose_name = "Evento de Monitoreo"
        verbose_name_plural = "Eventos de Monitoreo"


class OutbreakEvent(Event):
    """Evento de brote de plaga/enfermedad."""
    DETECTION_METHOD_CHOICES = [
        ('Monitoreo rutinario', 'Monitoreo rutinario'),
        ('Inspección visual', 'Inspección visual'),
        ('Síntomas observados', 'Síntomas observados'),
        ('Reporte de trabajador', 'Reporte de trabajador'),
        ('Análisis de laboratorio', 'Análisis de laboratorio'),
        ('Otro', 'Otro'),
    ]

    tipo_problema = models.CharField(max_length=200, verbose_name="Tipo de Plaga/Enfermedad")
    severidad = models.CharField(
        max_length=20,
        choices=[
            ('Baja', 'Baja'),
            ('Media', 'Media'),
            ('Alta', 'Alta'),
            ('Crítica', 'Crítica'),
        ],
        verbose_name="Severidad"
    )
    metodo_deteccion = models.CharField(
        max_length=50, 
        choices=DETECTION_METHOD_CHOICES,
        verbose_name="Método de Detección"
    )
    area_afectada_ha = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Área Afectada (ha)"
    )
    porcentaje_afectacion = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Porcentaje de Afectación (%)"
    )
    accion_inmediata = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Acción Inmediata Tomada"
    )
    requiere_tratamiento = models.BooleanField(
        default=True,
        verbose_name="¿Requiere Tratamiento?"
    )

    class Meta:
        db_table = 'outbreak_events'
        verbose_name = "Evento de Brote"
        verbose_name_plural = "Eventos de Brote"


class ClimateEvent(Event):
    """Evento de condiciones climáticas."""
    WIND_CONDITION_CHOICES = [
        ('Sin viento', 'Sin viento'),
        ('Viento leve', 'Viento leve'),
        ('Viento moderado', 'Viento moderado'),
        ('Viento fuerte', 'Viento fuerte'),
    ]

    temperatura_max = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(-20), MaxValueValidator(50)],
        verbose_name="Temperatura Máxima (°C)"
    )
    temperatura_min = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(-20), MaxValueValidator(50)],
        verbose_name="Temperatura Mínima (°C)"
    )
    humedad_relativa = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Humedad Relativa (%)"
    )
    precipitacion_mm = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Precipitación (mm)"
    )
    velocidad_viento_ms = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Velocidad del Viento (m/s)"
    )
    viento = models.CharField(
        max_length=20,
        choices=WIND_CONDITION_CHOICES,
        null=True,
        blank=True,
        verbose_name="Condición de Viento"
    )
    radiacion_solar_wm2 = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Radiación Solar (W/m²)"
    )

    class Meta:
        db_table = 'climate_events'
        verbose_name = "Evento Climático"
        verbose_name_plural = "Eventos Climáticos"


class HarvestEvent(Event):
    """Evento de cosecha."""
    QUALITY_CHOICES = [
        ('exportacion', 'Exportación'),
        ('primera', 'Primera'),
        ('segunda', 'Segunda'),
        ('tercera', 'Tercera'),
    ]

    variedad = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Variedad de Limón"
    )
    volumen_kg = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Volumen Total (kg)"
    )
    rendimiento_kg_ha = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Rendimiento (kg/ha)"
    )
    calidad = models.CharField(
        max_length=20,
        choices=QUALITY_CHOICES,
        null=True,
        blank=True,
        verbose_name="Calidad"
    )
    numero_trabajadores = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name="Número de Trabajadores"
    )
    horas_trabajo = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Horas de Trabajo"
    )
    fecha_inicio = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Fecha Inicio"
    )
    fecha_fin = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Fecha Fin"
    )

    class Meta:
        db_table = 'harvest_events'
        verbose_name = "Evento de Cosecha"
        verbose_name_plural = "Eventos de Cosecha"


class PostHarvestEvent(Event):
    """Evento de almacenamiento poscosecha."""
    producto = models.CharField(max_length=200, verbose_name="Producto Almacenado")
    cantidad_kg = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Cantidad (kg)"
    )
    temperatura = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(-5), MaxValueValidator(30)],
        verbose_name="Temperatura (°C)"
    )
    humedad = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Humedad (%)"
    )
    tipo_almacenamiento = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Tipo de Almacenamiento"
    )
    fecha_ingreso = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Fecha de Ingreso"
    )
    fecha_salida_prevista = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Fecha de Salida Prevista"
    )
    condiciones_observadas = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Condiciones Observadas"
    )

    class Meta:
        db_table = 'postharvest_events'
        verbose_name = "Evento Poscosecha"
        verbose_name_plural = "Eventos Poscosecha"


class LaborCostEvent(Event):
    """Evento de mano de obra y costos."""
    ACTIVITY_CHOICES = [
        ('Riego', 'Riego'),
        ('Fertilización', 'Fertilización'),
        ('Aplicación fitosanitaria', 'Aplicación fitosanitaria'),
        ('Poda', 'Poda'),
        ('Deshierbe', 'Deshierbe'),
        ('Cosecha', 'Cosecha'),
        ('Mantenimiento', 'Mantenimiento'),
        ('Transporte', 'Transporte'),
        ('Otra', 'Otra'),
    ]

    actividad = models.CharField(max_length=100, choices=ACTIVITY_CHOICES, verbose_name="Actividad Realizada")
    numero_trabajadores = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Número de Trabajadores"
    )
    horas_trabajo = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Horas de Trabajo"
    )
    costo_hora = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Costo por Hora"
    )
    costo_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Costo Total"
    )
    # Campo autocalculado - se calculará automáticamente si se proporcionan horas_trabajo y costo_hora
    # Si se proporciona costo_total directamente, se usará ese valor

    def clean(self):
        """Calcula costo_total automáticamente si se proporcionan horas_trabajo y costo_hora."""
        super().clean()
        if self.horas_trabajo and self.costo_hora and not self.costo_total:
            self.costo_total = self.horas_trabajo * self.costo_hora * self.numero_trabajadores
        elif self.horas_trabajo and self.costo_total and not self.costo_hora:
            # Calcular costo_hora si se tiene costo_total y horas
            if self.horas_trabajo > 0 and self.numero_trabajadores > 0:
                self.costo_hora = self.costo_total / (self.horas_trabajo * self.numero_trabajadores)

    class Meta:
        db_table = 'labor_cost_events'
        verbose_name = "Evento de Mano de Obra"
        verbose_name_plural = "Eventos de Mano de Obra"


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
