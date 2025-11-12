"""
Mapeo de tipos de eventos a sus modelos específicos.
"""
from .models import (
    Event,
    IrrigationEvent,
    FertilizationEvent,
    PhytosanitaryEvent,
    MaintenanceEvent,
    MonitoringEvent,
    OutbreakEvent,
    ClimateEvent,
    HarvestEvent,
    PostHarvestEvent,
    LaborCostEvent,
)

# Mapeo de nombres de tipos de eventos a sus modelos específicos
EVENT_TYPE_MODEL_MAP = {
    'Aplicación de Riego': IrrigationEvent,
    'Aplicación de Fertilizante': FertilizationEvent,
    'Aplicación Fitosanitaria': PhytosanitaryEvent,
    'Labores de Cultivo': MaintenanceEvent,
    'Monitoreo de Plagas': MonitoringEvent,
    'Brote de Plaga/Enfermedad': OutbreakEvent,
    'Condiciones Climáticas': ClimateEvent,
    'Cosecha': HarvestEvent,
    'Almacenamiento Poscosecha': PostHarvestEvent,
    'Mano de Obra y Costos': LaborCostEvent,
}

# Mapeo inverso: modelo a nombre
MODEL_EVENT_TYPE_MAP = {v: k for k, v in EVENT_TYPE_MODEL_MAP.items()}

# Lista de todos los modelos de eventos específicos
SPECIFIC_EVENT_MODELS = list(EVENT_TYPE_MODEL_MAP.values())


def get_event_model(event_type_name):
    """
    Obtiene el modelo específico para un tipo de evento.
    
    Args:
        event_type_name: Nombre del tipo de evento
        
    Returns:
        Modelo específico o Event base si no se encuentra
    """
    return EVENT_TYPE_MODEL_MAP.get(event_type_name, Event)


def get_event_type_name(event_model):
    """
    Obtiene el nombre del tipo de evento para un modelo específico.
    
    Args:
        event_model: Clase del modelo de evento
        
    Returns:
        Nombre del tipo de evento o None
    """
    return MODEL_EVENT_TYPE_MAP.get(event_model, None)


def is_specific_event_model(model_class):
    """
    Verifica si un modelo es un modelo específico de evento (no el base).
    
    Args:
        model_class: Clase del modelo
        
    Returns:
        True si es un modelo específico, False si es Event base
    """
    return model_class in SPECIFIC_EVENT_MODELS

