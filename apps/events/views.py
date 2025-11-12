from rest_framework import generics, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
import pytz
from django.http import JsonResponse
from .models import Event, EventType, Attachment
from apps.catalogs.models import Field, Campaign
from .forms import get_event_form, EVENT_FORM_MAP
from .event_models import get_event_model, EVENT_TYPE_MODEL_MAP
from .serializers import (
    EventSerializer, 
    EventListSerializer, 
    EventTypeSerializer,
    EventCreateSerializer,
    get_event_serializer,
)


# ========== API Views ==========


@extend_schema(
    summary="Listar Eventos",
    description="""
    Obtiene una lista de todos los eventos de trazabilidad registrados en el sistema.
    
    Los eventos representan actividades que ocurren durante el ciclo de cultivo como:
    - Aplicaciones fitosanitarias
    - Riegos y fertilizaciones
    - Cosechas
    - Podas y labores culturales
    - Monitoreo de plagas y enfermedades
    
    **Casos de uso:**
    - Consultar historial de actividades por campo o campaña
    - Auditar trazabilidad de productos
    - Generar reportes de actividades
    - Análisis de prácticas agrícolas
    """,
    tags=['Eventos de Trazabilidad'],
    parameters=[
        OpenApiParameter(
            name='event_type',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.QUERY,
            description='Filtrar por tipo de evento (UUID)',
            required=False,
        ),
        OpenApiParameter(
            name='date_from',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description='Fecha inicial para filtrar eventos (formato: YYYY-MM-DD)',
            required=False,
        ),
        OpenApiParameter(
            name='date_to',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description='Fecha final para filtrar eventos (formato: YYYY-MM-DD)',
            required=False,
        ),
    ],
    responses={
        200: EventListSerializer(many=True),
    },
    examples=[
        OpenApiExample(
            'Eventos registrados',
            summary='Lista de eventos',
            description='Ejemplo de respuesta con eventos de trazabilidad',
            value=[
                {
                    'id': '550e8400-e29b-41d4-a716-446655440010',
                    'event_type': '550e8400-e29b-41d4-a716-446655440020',
                    'event_type_name': 'Riego',
                    'field': '550e8400-e29b-41d4-a716-446655440000',
                    'field_name': 'Parcela Norte',
                    'timestamp': '2024-10-27T10:30:00Z',
                    'observations': 'Riego por goteo - 2 horas'
                }
            ],
            response_only=True,
        ),
    ],
)
class EventListView(generics.ListAPIView):
    """
    API endpoint para listar eventos de trazabilidad.
    
    Permite filtrar por tipo de evento y rango de fechas mediante query parameters.
    """
    serializer_class = EventListSerializer
    
    def get_queryset(self):
        queryset = Event.objects.all().select_related('event_type').order_by('-timestamp')
        
        # Filtrar por tipo de evento
        event_type = self.request.query_params.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type_id=event_type)
        
        # Filtrar por rango de fechas
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        
        return queryset


@extend_schema(
    summary="Listar Tipos de Eventos",
    description="""
    Obtiene una lista de todos los tipos de eventos disponibles en el sistema.
    
    Los tipos de eventos definen las categorías de actividades que pueden registrarse:
    - Riego
    - Fertilización
    - Aplicación fitosanitaria
    - Cosecha
    - Poda
    - Monitoreo
    - Otros
    
    **Casos de uso:**
    - Consultar tipos disponibles para crear nuevos eventos
    - Validar esquemas JSON de datos de eventos
    - Obtener categorías para filtros en reportes
    """,
    tags=['Eventos de Trazabilidad'],
    parameters=[
        OpenApiParameter(
            name='category',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filtrar por categoría de evento',
            required=False,
        ),
        OpenApiParameter(
            name='is_active',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description='Filtrar por estado: true (activos) o false (inactivos)',
            required=False,
        ),
    ],
    responses={
        200: EventTypeSerializer(many=True),
    },
)
class EventTypeListView(generics.ListAPIView):
    """
    API endpoint para listar tipos de eventos.
    
    Permite filtrar por categoría y estado mediante query parameters.
    """
    serializer_class = EventTypeSerializer
    
    def get_queryset(self):
        queryset = EventType.objects.all().order_by('name')
        
        category = self.request.query_params.get('category')
        is_active = self.request.query_params.get('is_active')
        
        if category:
            queryset = queryset.filter(category__icontains=category)
        
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        return queryset


@extend_schema(
    summary="Crear Evento",
    description="""
    Crea un nuevo evento de trazabilidad.
    
    **IMPORTANTE:** El tipo de evento determina qué campos específicos se requieren.
    
    ## Tipos de Eventos Disponibles:
    
    ### 1. Aplicación de Riego
    **Campos básicos:** event_type, field, campaign (opcional), timestamp, observations
    
    **Campos específicos:**
    - `metodo` (string): Método de riego (goteo, aspersión, gravedad, etc.)
    - `duracion_minutos` (integer): Duración en minutos
    - `fuente_agua` (string): Fuente del agua (pozo, río, canal, etc.)
    - `volumen_m3` (decimal): Volumen aplicado en m³
    - `presion_bar` (decimal): Presión del sistema en bar
    - `ce_uScm` (integer): Conductividad eléctrica en µS/cm
    - `ph` (decimal): pH del agua
    
    ### 2. Aplicación de Fertilizante
    **Campos específicos:**
    - `producto` (string): Nombre del fertilizante
    - `metodo_aplicacion` (string): Método (fertirriego, foliar, suelo, etc.)
    - `dosis` (decimal): Cantidad aplicada
    - `unidad_dosis` (string): Unidad de medida (kg/ha, L/ha, etc.)
    - `n_porcentaje` (decimal): % de Nitrógeno
    - `p_porcentaje` (decimal): % de Fósforo
    - `k_porcentaje` (decimal): % de Potasio
    - `volumen_caldo_l` (decimal): Volumen de caldo en litros
    
    ### 3. Aplicación Fitosanitaria
    **Campos específicos:**
    - `producto` (string): Nombre del producto fitosanitario
    - `ingrediente_activo` (string): Ingrediente activo
    - `tipo_producto` (string): Tipo (fungicida, insecticida, herbicida, etc.)
    - `objetivo` (string): Plaga/enfermedad objetivo
    - `metodo_aplicacion` (string): Método (aspersión, espolvoreo, etc.)
    - `dosis` (decimal): Dosis aplicada
    - `unidad_dosis` (string): Unidad de medida
    - `lote_producto` (string): Número de lote
    - `volumen_caldo_l` (decimal): Volumen de caldo
    - `presion_bar` (decimal): Presión de aplicación
    - `intervalo_seguridad_dias` (integer): Días de intervalo de seguridad
    - `responsable_aplicacion` (string): Nombre del responsable
    - `eficacia_observada` (string): Nivel de eficacia
    - `fitotoxicidad` (boolean): ¿Se observó fitotoxicidad?
    
    ### 4. Labores de Cultivo
    **Campos específicos:**
    - `actividad` (string): Tipo de labor (poda, deshierbe, etc.)
    - `herramienta_equipo` (string): Herramientas utilizadas
    - `numero_jornales` (integer): Número de jornales
    - `horas_hombre` (decimal): Horas hombre trabajadas
    - `objetivo` (string): Objetivo de la labor
    - `porcentaje_completado` (integer): % completado (0-100)
    - `herramientas_desinfectadas` (boolean): ¿Se desinfectaron?
    
    ### 5. Cosecha
    **Campos específicos:**
    - `variedad` (string): Variedad cosechada
    - `volumen_kg` (decimal): Volumen cosechado en kg
    - `rendimiento_kg_ha` (decimal): Rendimiento en kg/ha
    - `calidad` (string): Calidad del producto
    - `numero_trabajadores` (integer): Número de trabajadores
    - `horas_trabajo` (decimal): Horas de trabajo
    - `fecha_inicio` (datetime): Fecha de inicio
    - `fecha_fin` (datetime): Fecha de finalización
    
    **Otros tipos disponibles:** Monitoreo de Plagas, Brote de Plaga/Enfermedad, Condiciones Climáticas, Almacenamiento Poscosecha, Mano de Obra y Costos.
    
    ## Pasos para crear un evento:
    1. Consultar tipos de eventos disponibles: `GET /api/v1/events/types/`
    2. Identificar el `event_type` (UUID) que deseas usar
    3. Preparar el JSON con los campos básicos + específicos del tipo
    4. Enviar POST a `/api/v1/events/create/`
    
    **Validación:**
    - El tipo de evento debe estar activo (is_active=true)
    - El campo debe existir y estar activo
    - Los campos requeridos dependen del tipo de evento seleccionado
    """,
    tags=['Eventos de Trazabilidad'],
    request=EventCreateSerializer,
    responses={
        201: EventSerializer,
        400: OpenApiResponse(description="Datos inválidos o campos requeridos faltantes"),
    },
    examples=[
        OpenApiExample(
            'Ejemplo 1: Riego por goteo',
            summary='Crear evento de riego',
            description='Ejemplo de creación de un evento de riego por goteo con todos los detalles',
            value={
                'event_type': '550e8400-e29b-41d4-a716-446655440001',
                'field': '550e8400-e29b-41d4-a716-446655440000',
                'campaign': '550e8400-e29b-41d4-a716-446655440005',
                'timestamp': '2024-11-12T08:30:00Z',
                'observations': 'Riego matutino, condiciones óptimas',
                'metodo': 'Goteo',
                'duracion_minutos': 120,
                'fuente_agua': 'Pozo profundo',
                'volumen_m3': 50.5,
                'presion_bar': 2.5,
                'ce_uScm': 850,
                'ph': 7.2
            },
            request_only=True,
        ),
        OpenApiExample(
            'Ejemplo 2: Fertilización foliar',
            summary='Crear evento de fertilización',
            description='Ejemplo de aplicación de fertilizante foliar NPK',
            value={
                'event_type': '550e8400-e29b-41d4-a716-446655440002',
                'field': '550e8400-e29b-41d4-a716-446655440000',
                'timestamp': '2024-11-12T10:00:00Z',
                'observations': 'Fertilización foliar preventiva',
                'producto': 'NPK 20-20-20',
                'metodo_aplicacion': 'Foliar',
                'dosis': 2.5,
                'unidad_dosis': 'kg/ha',
                'n_porcentaje': 20.0,
                'p_porcentaje': 20.0,
                'k_porcentaje': 20.0,
                'volumen_caldo_l': 500
            },
            request_only=True,
        ),
        OpenApiExample(
            'Ejemplo 3: Aplicación fitosanitaria',
            summary='Crear evento fitosanitario',
            description='Ejemplo de aplicación de fungicida contra antracnosis',
            value={
                'event_type': '550e8400-e29b-41d4-a716-446655440003',
                'field': '550e8400-e29b-41d4-a716-446655440000',
                'campaign': '550e8400-e29b-41d4-a716-446655440005',
                'timestamp': '2024-11-12T15:00:00Z',
                'observations': 'Aplicación preventiva contra antracnosis',
                'producto': 'Azoxystrobin 50%',
                'ingrediente_activo': 'Azoxystrobin',
                'tipo_producto': 'Fungicida',
                'objetivo': 'Antracnosis (Colletotrichum)',
                'metodo_aplicacion': 'Aspersión',
                'dosis': 0.8,
                'unidad_dosis': 'L/ha',
                'lote_producto': 'LOT-2024-089',
                'volumen_caldo_l': 600,
                'presion_bar': 3.0,
                'intervalo_seguridad_dias': 7,
                'responsable_aplicacion': 'Juan Pérez',
                'eficacia_observada': 'Pendiente',
                'fitotoxicidad': False
            },
            request_only=True,
        ),
        OpenApiExample(
            'Ejemplo 4: Cosecha',
            summary='Crear evento de cosecha',
            description='Ejemplo de registro de cosecha de limón persa',
            value={
                'event_type': '550e8400-e29b-41d4-a716-446655440008',
                'field': '550e8400-e29b-41d4-a716-446655440000',
                'campaign': '550e8400-e29b-41d4-a716-446655440005',
                'timestamp': '2024-11-12T07:00:00Z',
                'observations': 'Cosecha de calidad premium',
                'variedad': 'Limón Persa',
                'volumen_kg': 2500.0,
                'rendimiento_kg_ha': 1000.0,
                'calidad': 'Premium',
                'numero_trabajadores': 8,
                'horas_trabajo': 6.5,
                'fecha_inicio': '2024-11-12T07:00:00Z',
                'fecha_fin': '2024-11-12T13:30:00Z'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Respuesta exitosa',
            summary='Evento creado exitosamente',
            description='Ejemplo de respuesta cuando el evento se crea correctamente',
            value={
                'id': '550e8400-e29b-41d4-a716-446655440010',
                'event_type': '550e8400-e29b-41d4-a716-446655440001',
                'event_type_name': 'Aplicación de Riego',
                'event_type_detail': {
                    'id': '550e8400-e29b-41d4-a716-446655440001',
                    'name': 'Aplicación de Riego',
                    'category': 'Manejo de Agua',
                    'is_active': True
                },
                'field': '550e8400-e29b-41d4-a716-446655440000',
                'field_name': 'Parcela Norte',
                'campaign': '550e8400-e29b-41d4-a716-446655440005',
                'campaign_name': 'Primavera 2024',
                'timestamp': '2024-11-12T08:30:00Z',
                'observations': 'Riego matutino, condiciones óptimas',
                'created_at': '2024-11-12T08:35:00Z',
                'updated_at': '2024-11-12T08:35:00Z'
            },
            response_only=True,
        ),
    ],
)
class EventCreateView(generics.CreateAPIView):
    """
    API endpoint para crear eventos de trazabilidad.
    
    Crea un evento usando el modelo específico según el tipo de evento.
    """
    serializer_class = EventCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Obtener el tipo de evento y determinar el modelo específico
        event_type = serializer.validated_data['event_type']
        model_class = get_event_model(event_type.name)
        serializer_class = get_event_serializer(event_type.name)
        
        # Si hay un serializer específico, usarlo
        if serializer_class != EventSerializer:
            specific_serializer = serializer_class(data=request.data)
            specific_serializer.is_valid(raise_exception=True)
            event = specific_serializer.save(
                event_type=event_type,
                created_by=request.user if request.user.is_authenticated else None
            )
            response_serializer = serializer_class(event)
        else:
            # Fallback al serializer base
            event = serializer.save(created_by=request.user if request.user.is_authenticated else None)
            response_serializer = EventSerializer(event)
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Obtener Detalle de Evento",
    description="""
    Obtiene los detalles completos de un evento específico por su ID.
    
    La respuesta incluye:
    - Información básica del evento
    - Detalles del tipo de evento
    - Información del campo y campaña
    - Campos específicos según el tipo de evento
    - Datos de auditoría (creado por, fechas)
    
    **Casos de uso:**
    - Consultar información completa de un evento
    - Verificar detalles de una aplicación específica
    - Auditoría de trazabilidad
    """,
    tags=['Eventos de Trazabilidad'],
    responses={
        200: EventSerializer,
        404: OpenApiResponse(description="Evento no encontrado"),
    },
    examples=[
        OpenApiExample(
            'Detalle de evento de riego',
            summary='Respuesta con detalles completos',
            value={
                'id': '550e8400-e29b-41d4-a716-446655440010',
                'event_type': '550e8400-e29b-41d4-a716-446655440001',
                'event_type_name': 'Aplicación de Riego',
                'event_type_detail': {
                    'id': '550e8400-e29b-41d4-a716-446655440001',
                    'name': 'Aplicación de Riego',
                    'category': 'Manejo de Agua',
                    'is_active': True
                },
                'field': '550e8400-e29b-41d4-a716-446655440000',
                'field_name': 'Parcela Norte',
                'campaign': '550e8400-e29b-41d4-a716-446655440005',
                'campaign_name': 'Primavera 2024',
                'timestamp': '2024-11-12T08:30:00Z',
                'observations': 'Riego matutino',
                'created_at': '2024-11-12T08:35:00Z',
                'updated_at': '2024-11-12T08:35:00Z'
            },
            response_only=True,
        ),
    ],
)
class EventDetailView(generics.RetrieveAPIView):
    """
    API endpoint para obtener el detalle de un evento específico.
    """
    queryset = Event.objects.all().select_related('event_type', 'field', 'campaign', 'created_by')
    serializer_class = EventSerializer
    
    def get_serializer_class(self):
        """Usar el serializer específico del tipo de evento si existe."""
        event = self.get_object()
        if event.event_type:
            specific_serializer = get_event_serializer(event.event_type.name)
            if specific_serializer:
                return specific_serializer
        return EventSerializer


@extend_schema(
    summary="Actualizar Evento",
    description="""
    Actualiza un evento existente.
    
    Permite modificar cualquier campo del evento, incluyendo:
    - Fecha y hora del evento
    - Observaciones
    - Campos específicos del tipo de evento
    - Campo y campaña asociados
    
    **NOTA:** No se puede cambiar el tipo de evento una vez creado.
    
    **Validaciones:**
    - El evento debe existir
    - Los campos requeridos según el tipo de evento deben estar presentes
    - Las fechas deben ser válidas
    """,
    tags=['Eventos de Trazabilidad'],
    request=EventSerializer,
    responses={
        200: EventSerializer,
        400: OpenApiResponse(description="Datos inválidos"),
        404: OpenApiResponse(description="Evento no encontrado"),
    },
    examples=[
        OpenApiExample(
            'Actualizar observaciones',
            summary='Actualizar observaciones de un evento',
            value={
                'observations': 'Riego matutino - Actualizado: presión ajustada a 2.8 bar',
                'presion_bar': 2.8
            },
            request_only=True,
        ),
    ],
)
class EventUpdateView(generics.UpdateAPIView):
    """
    API endpoint para actualizar eventos.
    Soporta PUT (actualización completa) y PATCH (actualización parcial).
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    
    def get_serializer_class(self):
        """Usar el serializer específico del tipo de evento si existe."""
        event = self.get_object()
        if event.event_type:
            specific_serializer = get_event_serializer(event.event_type.name)
            if specific_serializer:
                return specific_serializer
        return EventSerializer


@extend_schema(
    summary="Eliminar Evento",
    description="""
    Elimina un evento del sistema.
    
    **ADVERTENCIA:** Esta acción es permanente y no se puede deshacer.
    
    **Consideraciones:**
    - Se eliminará toda la información del evento
    - Los reportes que incluían este evento se verán afectados
    - Se recomienda hacer respaldos antes de eliminaciones masivas
    
    **Casos de uso:**
    - Eliminar eventos creados por error
    - Limpiar datos de prueba
    - Corregir duplicados
    """,
    tags=['Eventos de Trazabilidad'],
    responses={
        204: OpenApiResponse(description="Evento eliminado exitosamente"),
        404: OpenApiResponse(description="Evento no encontrado"),
    },
)
class EventDeleteView(generics.DestroyAPIView):
    """
    API endpoint para eliminar eventos.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer


@extend_schema(
    summary="Obtener Detalle de Tipo de Evento",
    description="""
    Obtiene los detalles completos de un tipo de evento específico.
    
    La respuesta incluye:
    - Nombre y categoría del tipo de evento
    - Descripción y campos requeridos
    - Estado (activo/inactivo)
    - Configuración visual (icono, color)
    - Esquema JSON de campos específicos
    
    **Casos de uso:**
    - Consultar configuración de un tipo de evento
    - Obtener lista de campos requeridos antes de crear evento
    - Validar disponibilidad de un tipo de evento
    """,
    tags=['Tipos de Eventos'],
    responses={
        200: EventTypeSerializer,
        404: OpenApiResponse(description="Tipo de evento no encontrado"),
    },
    examples=[
        OpenApiExample(
            'Detalle de tipo de evento',
            summary='Información completa del tipo de evento',
            value={
                'id': '550e8400-e29b-41d4-a716-446655440001',
                'name': 'Aplicación de Riego',
                'category': 'Manejo de Agua',
                'description': 'Registro de aplicaciones de riego en los campos',
                'is_active': True,
                'icon': 'bi-droplet',
                'color': '#0dcaf0',
                'created_at': '2024-01-15T10:00:00Z',
                'updated_at': '2024-01-15T10:00:00Z'
            },
            response_only=True,
        ),
    ],
)
class EventTypeDetailView(generics.RetrieveAPIView):
    """
    API endpoint para obtener el detalle de un tipo de evento específico.
    """
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer


@extend_schema(
    summary="Actualizar Tipo de Evento",
    description="""
    Actualiza un tipo de evento existente.
    
    **Campos actualizables:**
    - `is_active`: Activar/desactivar el tipo de evento
    - `description`: Actualizar la descripción
    - `icon`: Cambiar el icono de Bootstrap
    - `color`: Modificar el color en formato hexadecimal
    
    **IMPORTANTE:**
    - No se puede cambiar el `name` ni la `category` una vez creado
    - Desactivar un tipo de evento (`is_active: false`) impide crear nuevos eventos de ese tipo
    - Los eventos existentes no se ven afectados al desactivar un tipo
    
    **Casos de uso:**
    - Desactivar temporalmente un tipo de evento
    - Actualizar la descripción para mayor claridad
    - Personalizar la apariencia visual
    """,
    tags=['Tipos de Eventos'],
    request=EventTypeSerializer,
    responses={
        200: EventTypeSerializer,
        400: OpenApiResponse(description="Datos inválidos"),
        404: OpenApiResponse(description="Tipo de evento no encontrado"),
    },
    examples=[
        OpenApiExample(
            'Desactivar tipo de evento',
            summary='Desactivar un tipo de evento',
            value={
                'is_active': False
            },
            request_only=True,
        ),
        OpenApiExample(
            'Actualizar descripción y color',
            summary='Actualizar información visual',
            value={
                'description': 'Registro detallado de aplicaciones de riego - Incluye mediciones de presión y volumen',
                'color': '#0099ff'
            },
            request_only=True,
        ),
    ],
)
class EventTypeUpdateView(generics.UpdateAPIView):
    """
    API endpoint para actualizar tipos de eventos.
    Soporta PATCH para actualizaciones parciales (ej: solo cambiar is_active).
    """
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer


# ========== Template Views ==========

@login_required
def event_list_view(request):
    """Vista de lista de eventos."""
    events_list = Event.objects.all().select_related(
        'event_type', 'field', 'campaign', 'created_by'
    ).order_by('-timestamp')
    
    # Filtros
    event_type_id = request.GET.get('event_type')
    field_id = request.GET.get('field')
    campaign_id = request.GET.get('campaign')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if event_type_id:
        events_list = events_list.filter(event_type_id=event_type_id)
    if field_id:
        events_list = events_list.filter(field_id=field_id)
    if campaign_id:
        events_list = events_list.filter(campaign_id=campaign_id)
    if date_from:
        events_list = events_list.filter(timestamp__gte=date_from)
    if date_to:
        events_list = events_list.filter(timestamp__lte=date_to)
    
    # Paginación
    paginator = Paginator(events_list, 20)
    page_number = request.GET.get('page')
    events = paginator.get_page(page_number)
    
    # Datos para filtros
    event_types = EventType.objects.filter(is_active=True).order_by('category', 'name')
    fields = Field.objects.filter(is_active=True).order_by('name')
    # Mostrar todas las campañas (activas e inactivas) para permitir filtrar eventos históricos
    campaigns = Campaign.objects.all().order_by('-start_date')
    
    context = {
        'events': events,
        'event_types': event_types,
        'fields': fields,
        'campaigns': campaigns,
        'selected_event_type': event_type_id,
        'selected_field': field_id,
        'selected_campaign': campaign_id,
        'date_from': date_from,
        'date_to': date_to,
        # Contar eventos con filtros aplicados (no todos los eventos)
        'total_count': events_list.count(),
    }
    return render(request, 'events/event_list.html', context)


@login_required
def event_create_view(request):
    """Vista para crear un nuevo evento."""
    event_type_id = request.GET.get('event_type') or request.POST.get('event_type')
    event_type = None
    form = None
    
    if event_type_id:
        event_type = get_object_or_404(EventType, pk=event_type_id, is_active=True)
        FormClass = get_event_form(event_type.name)
        
        if not FormClass:
            messages.error(request, f'No se encontró formulario para el tipo de evento: {event_type.name}')
            return redirect('event_list')
        
        if request.method == 'POST':
            form = FormClass(request.POST, request.FILES)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        event = form.save(commit=False)
                        event.event_type = event_type
                        event.created_by = request.user
                        event.full_clean()  # Ejecutar validaciones del modelo
                        event.save()
                        
                        # Procesar archivos adjuntos
                        files = request.FILES.getlist('attachments')
                        for file in files:
                            Attachment.objects.create(
                                event=event,
                                file=file,
                                file_name=file.name,
                                file_size=file.size,
                                mime_type=file.content_type,
                                uploaded_by=request.user
                            )
                        
                        if files:
                            messages.success(request, f'Evento "{event_type.name}" registrado exitosamente con {len(files)} archivo(s) adjunto(s).')
                        else:
                            messages.success(request, f'Evento "{event_type.name}" registrado exitosamente.')
                        return redirect('event_list')
                except Exception as e:
                    messages.error(request, f'Error al crear evento: {str(e)}')
        else:
            form = FormClass(initial={'event_type': event_type})
    else:
        # Si no hay event_type seleccionado, mostrar selector
        if request.method == 'POST':
            messages.error(request, 'Debe seleccionar un tipo de evento.')
    
    # GET request o error - mostrar formulario o selector
    event_types = EventType.objects.filter(is_active=True).order_by('category', 'name')
    fields = Field.objects.filter(is_active=True).order_by('name')
    campaigns = Campaign.objects.filter(is_active=True).order_by('-start_date')
    
    context = {
        'event_types': event_types,
        'fields': fields,
        'campaigns': campaigns,
        'event_type': event_type,
        'form': form,
        'action': 'Crear'
    }
    return render(request, 'events/event_form.html', context)


@login_required
def event_detail_view(request, pk):
    """Vista de detalle de un evento."""
    # Intentar obtener el evento específico primero
    event = None
    for model_class in EVENT_TYPE_MODEL_MAP.values():
        try:
            event = model_class.objects.select_related('event_type', 'field', 'campaign', 'created_by').get(pk=pk)
            break
        except model_class.DoesNotExist:
            continue
    
    # Si no se encontró en modelos específicos, buscar en Event base
    if event is None:
        event = get_object_or_404(
            Event.objects.select_related('event_type', 'field', 'campaign', 'created_by'),
            pk=pk
        )
    
    # Obtener adjuntos del evento
    attachments = Attachment.objects.filter(event_id=pk).order_by('-uploaded_at')
    
    context = {
        'event': event,
        'attachments': attachments,
    }
    return render(request, 'events/event_detail.html', context)


@login_required
def get_event_type_info(request, pk):
    """API auxiliar para obtener información de un tipo de evento."""
    event_type = get_object_or_404(EventType, pk=pk)
    
    # Obtener el modelo específico asociado
    model_class = get_event_model(event_type.name)
    form_class = get_event_form(event_type.name)
    
    return JsonResponse({
        'id': event_type.id,
        'name': event_type.name,
        'category': event_type.category,
        'description': event_type.description,
        'icon': event_type.icon,
        'color': event_type.color,
        'model_name': model_class.__name__ if model_class else 'Event',
        'has_form': form_class is not None,
    })


# ========== Event Type CRUD Views ==========


@login_required
def event_type_list_view(request):
    """Vista para listar tipos de eventos."""
    event_types = EventType.objects.all().order_by('category', 'name')
    
    # Contar eventos por tipo
    for et in event_types:
        et.event_count = et.events.count()
    
    context = {
        'event_types': event_types,
        'total_count': EventType.objects.count(),
        'active_count': EventType.objects.filter(is_active=True).count(),
    }
    return render(request, 'events/event_type_list.html', context)


@login_required
def event_type_create_view(request):
    """Vista para crear un nuevo tipo de evento (deshabilitada - tipos son fijos)."""
    messages.warning(request, 'Los tipos de eventos son predefinidos y no se pueden crear nuevos.')
    return redirect('event_type_list')


@login_required
def event_type_edit_view(request, pk):
    """Vista para editar metadata de un tipo de evento (solo icon, color, description, is_active)."""
    event_type = get_object_or_404(EventType, pk=pk)
    
    if request.method == 'POST':
        try:
            # Solo permitir editar metadata, no name ni category (son fijos)
            event_type.description = request.POST.get('description', '')
            event_type.icon = request.POST.get('icon', '')
            event_type.color = request.POST.get('color', '#6c757d')
            event_type.is_active = request.POST.get('is_active') == 'on'
            event_type.save()
            
            messages.success(request, f'Metadata del tipo de evento "{event_type.name}" actualizado exitosamente.')
            return redirect('event_type_list')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar tipo de evento: {str(e)}')
    
    context = {
        'action': 'Editar',
        'event_type': event_type,
        'categories': EventType.CATEGORIES,
    }
    return render(request, 'events/event_type_form.html', context)


@login_required
def event_type_delete_view(request, pk):
    """Vista para eliminar un tipo de evento."""
    event_type = get_object_or_404(EventType, pk=pk)
    
    # Verificar si hay eventos asociados
    event_count = event_type.events.count()
    
    if request.method == 'POST':
        if event_count > 0:
            messages.error(
                request, 
                f'No se puede eliminar "{event_type.name}" porque tiene {event_count} evento(s) registrado(s).'
            )
        else:
            name = event_type.name
            event_type.delete()
            messages.success(request, f'Tipo de evento "{name}" eliminado exitosamente.')
            return redirect('event_type_list')
    
    context = {
        'event_type': event_type,
        'event_count': event_count,
    }
    return render(request, 'events/event_type_confirm_delete.html', context)


@login_required
def event_type_toggle_view(request, pk):
    """Vista para activar/desactivar un tipo de evento."""
    event_type = get_object_or_404(EventType, pk=pk)
    
    if request.method == 'POST':
        event_type.is_active = not event_type.is_active
        event_type.save()
        
        status = "activado" if event_type.is_active else "desactivado"
        messages.success(request, f'Tipo de evento "{event_type.name}" {status} exitosamente.')
        return redirect('event_type_list')
    
    return redirect('event_type_list')
