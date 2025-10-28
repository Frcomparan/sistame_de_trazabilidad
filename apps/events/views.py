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
from django.http import JsonResponse
import json
from jsonschema import validate as json_validate, ValidationError as JSONSchemaValidationError
from .models import Event, EventType, Attachment
from apps.catalogs.models import Field, Campaign
from .serializers import (
    EventSerializer, 
    EventListSerializer, 
    EventTypeSerializer,
    EventCreateSerializer
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
    Crea un nuevo evento de trazabilidad con validación dinámica del payload.
    
    El payload debe cumplir con el JSON Schema definido en el EventType.
    
    **Casos de uso:**
    - Registrar aplicación fitosanitaria
    - Registrar riego o fertilización
    - Registrar cosecha
    - Registrar cualquier actividad definida en los tipos de eventos
    
    **Validación:**
    - El tipo de evento debe estar activo
    - El campo debe existir y estar activo
    - El payload debe cumplir con el JSON Schema
    - La campaña (opcional) debe pertenecer al campo
    """,
    tags=['Eventos de Trazabilidad'],
    request=EventCreateSerializer,
    responses={
        201: EventSerializer,
        400: OpenApiResponse(description="Datos inválidos o payload que no cumple schema"),
    },
)
class EventCreateView(generics.CreateAPIView):
    """
    API endpoint para crear eventos de trazabilidad.
    
    Valida el payload contra el JSON Schema del tipo de evento.
    """
    serializer_class = EventCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validar payload contra el schema del tipo de evento
        event_type = serializer.validated_data['event_type']
        payload = serializer.validated_data.get('payload', {})
        
        if event_type.schema:
            try:
                json_validate(instance=payload, schema=event_type.schema)
            except JSONSchemaValidationError as e:
                return Response(
                    {'payload': f'El payload no cumple con el schema: {e.message}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Crear el evento
        event = serializer.save(created_by=request.user if request.user.is_authenticated else None)
        
        # Serializar respuesta completa
        response_serializer = EventSerializer(event)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


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
    campaigns = Campaign.objects.filter(is_active=True).order_by('-start_date')
    
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
        'total_count': Event.objects.count(),
    }
    return render(request, 'events/event_list.html', context)


@login_required
def event_create_view(request):
    """Vista para crear un nuevo evento dinámico."""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Obtener datos del formulario
                event_type = get_object_or_404(EventType, pk=request.POST.get('event_type'))
                field = get_object_or_404(Field, pk=request.POST.get('field'))
                campaign_id = request.POST.get('campaign')
                campaign = get_object_or_404(Campaign, pk=campaign_id) if campaign_id else None
                
                # Construir payload dinámico desde el formulario
                payload = {}
                for key, value in request.POST.items():
                    if key.startswith('payload_'):
                        field_name = key.replace('payload_', '')
                        # Intentar parsear como JSON si parece ser un objeto/array
                        if value.startswith('{') or value.startswith('['):
                            try:
                                payload[field_name] = json.loads(value)
                            except json.JSONDecodeError:
                                payload[field_name] = value
                        elif value.lower() in ('true', 'false'):
                            payload[field_name] = value.lower() == 'true'
                        elif value.replace('.', '', 1).isdigit():
                            payload[field_name] = float(value) if '.' in value else int(value)
                        else:
                            payload[field_name] = value
                
                # Validar payload contra schema
                if event_type.schema:
                    try:
                        json_validate(instance=payload, schema=event_type.schema)
                    except JSONSchemaValidationError as e:
                        messages.error(request, f'Error en los datos: {e.message}')
                        raise
                
                # Crear evento
                event = Event.objects.create(
                    event_type=event_type,
                    field=field,
                    campaign=campaign,
                    timestamp=request.POST.get('timestamp'),
                    payload=payload,
                    observations=request.POST.get('observations', ''),
                    created_by=request.user
                )
                
                messages.success(request, f'Evento "{event_type.name}" registrado exitosamente.')
                return redirect('event_list')
                
        except Exception as e:
            messages.error(request, f'Error al crear evento: {str(e)}')
    
    # GET request - mostrar formulario
    event_types = EventType.objects.filter(is_active=True).order_by('category', 'name')
    fields = Field.objects.filter(is_active=True).order_by('name')
    campaigns = Campaign.objects.filter(is_active=True).order_by('-start_date')
    
    # Serializar schemas a JSON para el template
    for et in event_types:
        if et.schema:
            et.schema_json = json.dumps(et.schema)
        else:
            et.schema_json = '{}'
    
    context = {
        'event_types': event_types,
        'fields': fields,
        'campaigns': campaigns,
        'action': 'Crear'
    }
    return render(request, 'events/event_form.html', context)


@login_required
def event_detail_view(request, pk):
    """Vista de detalle de un evento."""
    event = get_object_or_404(
        Event.objects.select_related('event_type', 'field', 'campaign', 'created_by'),
        pk=pk
    )
    
    # Formatear payload para visualización
    payload_formatted = json.dumps(event.payload, indent=2, ensure_ascii=False)
    
    context = {
        'event': event,
        'payload_formatted': payload_formatted,
    }
    return render(request, 'events/event_detail.html', context)


@login_required
def get_event_type_schema(request, pk):
    """API auxiliar para obtener el schema de un tipo de evento."""
    event_type = get_object_or_404(EventType, pk=pk)
    
    return JsonResponse({
        'id': event_type.id,
        'name': event_type.name,
        'category': event_type.category,
        'description': event_type.description,
        'schema': event_type.schema,
        'icon': event_type.icon,
        'color': event_type.color,
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
    """Vista para crear un nuevo tipo de evento."""
    if request.method == 'POST':
        try:
            # Parsear schema JSON
            schema_text = request.POST.get('schema', '{}')
            try:
                schema = json.loads(schema_text)
            except json.JSONDecodeError:
                messages.error(request, 'El esquema JSON no es válido')
                raise
            
            # Crear tipo de evento
            event_type = EventType.objects.create(
                name=request.POST.get('name'),
                category=request.POST.get('category'),
                description=request.POST.get('description', ''),
                schema=schema,
                icon=request.POST.get('icon', 'calendar-event'),
                color=request.POST.get('color', '#6c757d'),
                is_active=request.POST.get('is_active') == 'on'
            )
            
            messages.success(request, f'Tipo de evento "{event_type.name}" creado exitosamente.')
            return redirect('event_type_list')
            
        except Exception as e:
            messages.error(request, f'Error al crear tipo de evento: {str(e)}')
    
    # Ejemplo de schema para ayudar al usuario
    example_schema = {
        "type": "object",
        "title": "Datos del Evento",
        "required": ["campo_obligatorio"],
        "properties": {
            "campo_obligatorio": {
                "type": "string",
                "title": "Campo Obligatorio",
                "description": "Descripción del campo",
                "maxLength": 200,
                "example": "Valor de ejemplo"
            },
            "campo_numero": {
                "type": "number",
                "title": "Campo Numérico",
                "minimum": 0,
                "maximum": 100,
                "example": 50
            },
            "campo_seleccion": {
                "type": "string",
                "title": "Campo de Selección",
                "enum": ["Opción 1", "Opción 2", "Opción 3"],
                "example": "Opción 1"
            }
        }
    }
    
    context = {
        'action': 'Crear',
        'categories': EventType.CATEGORIES,
        'example_schema': json.dumps(example_schema, indent=2, ensure_ascii=False),
    }
    return render(request, 'events/event_type_form.html', context)


@login_required
def event_type_edit_view(request, pk):
    """Vista para editar un tipo de evento existente."""
    event_type = get_object_or_404(EventType, pk=pk)
    
    if request.method == 'POST':
        try:
            # Parsear schema JSON
            schema_text = request.POST.get('schema', '{}')
            try:
                schema = json.loads(schema_text)
            except json.JSONDecodeError:
                messages.error(request, 'El esquema JSON no es válido')
                raise
            
            # Actualizar tipo de evento
            event_type.name = request.POST.get('name')
            event_type.category = request.POST.get('category')
            event_type.description = request.POST.get('description', '')
            event_type.schema = schema
            event_type.icon = request.POST.get('icon', 'calendar-event')
            event_type.color = request.POST.get('color', '#6c757d')
            event_type.is_active = request.POST.get('is_active') == 'on'
            event_type.save()
            
            messages.success(request, f'Tipo de evento "{event_type.name}" actualizado exitosamente.')
            return redirect('event_type_list')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar tipo de evento: {str(e)}')
    
    # Schema de ejemplo para referencia
    example_schema = {
        "type": "object",
        "title": "Ejemplo de Evento",
        "required": ["campo1"],
        "properties": {
            "campo1": {
                "type": "string",
                "title": "Campo de Texto",
                "description": "Descripción del campo",
                "example": "Valor de ejemplo",
                "maxLength": 100
            },
            "campo2": {
                "type": "number",
                "title": "Campo Numérico",
                "example": 10.5,
                "minimum": 0,
                "maximum": 100
            },
            "campo3": {
                "type": "string",
                "title": "Selección",
                "enum": ["Opción 1", "Opción 2", "Opción 3"],
                "example": "Opción 1"
            }
        }
    }
    
    context = {
        'action': 'Editar',
        'event_type': event_type,
        'categories': EventType.CATEGORIES,
        'schema_json': json.dumps(event_type.schema, indent=2, ensure_ascii=False) if event_type.schema else '{}',
        'example_schema': json.dumps(example_schema, indent=2, ensure_ascii=False),
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


