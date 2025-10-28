from rest_framework import generics
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import Event, EventType
from .serializers import EventSerializer, EventListSerializer, EventTypeSerializer


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

