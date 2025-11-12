"""
Formularios específicos para cada tipo de evento.
"""
from django import forms
from django.core.exceptions import ValidationError
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
from .event_models import EVENT_TYPE_MODEL_MAP


class BaseEventForm(forms.ModelForm):
    """Formulario base con campos comunes a todos los eventos."""
    
    class Meta:
        model = Event
        fields = ['event_type', 'field', 'campaign', 'timestamp', 'observations']
        widgets = {
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'field': forms.Select(attrs={'class': 'form-select'}),
            'campaign': forms.Select(attrs={'class': 'form-select'}),
            'timestamp': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'observations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }


class IrrigationEventForm(BaseEventForm):
    """Formulario para eventos de riego."""
    
    class Meta(BaseEventForm.Meta):
        model = IrrigationEvent
        fields = BaseEventForm.Meta.fields + [
            'metodo', 'duracion_minutos', 'fuente_agua',
            'volumen_m3', 'presion_bar', 'ce_uScm', 'ph'
        ]
        widgets = {
            **BaseEventForm.Meta.widgets,
            'metodo': forms.Select(attrs={'class': 'form-select'}),
            'duracion_minutos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'fuente_agua': forms.Select(attrs={'class': 'form-select'}),
            'volumen_m3': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'presion_bar': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'max': 10
            }),
            'ce_uScm': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'ph': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'max': 14
            }),
        }


class FertilizationEventForm(BaseEventForm):
    """Formulario para eventos de fertilización."""
    
    class Meta(BaseEventForm.Meta):
        model = FertilizationEvent
        fields = BaseEventForm.Meta.fields + [
            'producto', 'metodo_aplicacion', 'dosis', 'unidad_dosis',
            'n_porcentaje', 'p_porcentaje', 'k_porcentaje', 'volumen_caldo_l'
        ]
        widgets = {
            **BaseEventForm.Meta.widgets,
            'producto': forms.TextInput(attrs={'class': 'form-control'}),
            'metodo_aplicacion': forms.Select(attrs={'class': 'form-select'}),
            'dosis': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'unidad_dosis': forms.TextInput(attrs={'class': 'form-control'}),
            'n_porcentaje': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'max': 100
            }),
            'p_porcentaje': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'max': 100
            }),
            'k_porcentaje': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'max': 100
            }),
            'volumen_caldo_l': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
        }


class PhytosanitaryEventForm(BaseEventForm):
    """Formulario para eventos fitosanitarios."""
    
    class Meta(BaseEventForm.Meta):
        model = PhytosanitaryEvent
        fields = BaseEventForm.Meta.fields + [
            'producto', 'ingrediente_activo', 'tipo_producto', 'objetivo',
            'metodo_aplicacion', 'dosis', 'unidad_dosis', 'lote_producto',
            'volumen_caldo_l', 'presion_bar', 'intervalo_seguridad_dias',
            'responsable_aplicacion', 'eficacia_observada', 'fitotoxicidad'
        ]
        widgets = {
            **BaseEventForm.Meta.widgets,
            'producto': forms.TextInput(attrs={'class': 'form-control'}),
            'ingrediente_activo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_producto': forms.Select(attrs={'class': 'form-select'}),
            'objetivo': forms.TextInput(attrs={'class': 'form-control'}),
            'metodo_aplicacion': forms.Select(attrs={'class': 'form-select'}),
            'dosis': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'unidad_dosis': forms.TextInput(attrs={'class': 'form-control'}),
            'lote_producto': forms.TextInput(attrs={'class': 'form-control'}),
            'volumen_caldo_l': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'presion_bar': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'intervalo_seguridad_dias': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'responsable_aplicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'eficacia_observada': forms.Select(attrs={'class': 'form-select'}),
            'fitotoxicidad': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MaintenanceEventForm(BaseEventForm):
    """Formulario para eventos de labores de cultivo."""
    
    class Meta(BaseEventForm.Meta):
        model = MaintenanceEvent
        fields = BaseEventForm.Meta.fields + [
            'actividad', 'herramienta_equipo', 'numero_jornales',
            'horas_hombre', 'objetivo', 'porcentaje_completado',
            'herramientas_desinfectadas'
        ]
        widgets = {
            **BaseEventForm.Meta.widgets,
            'actividad': forms.Select(attrs={'class': 'form-select'}),
            'herramienta_equipo': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_jornales': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'horas_hombre': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'objetivo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
            'porcentaje_completado': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'max': 100
            }),
            'herramientas_desinfectadas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MonitoringEventForm(BaseEventForm):
    """Formulario para eventos de monitoreo."""
    
    class Meta(BaseEventForm.Meta):
        model = MonitoringEvent
        fields = BaseEventForm.Meta.fields + [
            'plaga_enfermedad', 'metodo_muestreo', 'incidencia', 'severidad',
            'ubicacion_campo', 'numero_muestras', 'accion_recomendada'
        ]
        widgets = {
            **BaseEventForm.Meta.widgets,
            'plaga_enfermedad': forms.TextInput(attrs={'class': 'form-control'}),
            'metodo_muestreo': forms.Select(attrs={'class': 'form-select'}),
            'incidencia': forms.Select(attrs={'class': 'form-select'}),
            'severidad': forms.Select(attrs={'class': 'form-select'}),
            'ubicacion_campo': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_muestras': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'accion_recomendada': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
        }


class OutbreakEventForm(BaseEventForm):
    """Formulario para eventos de brote."""
    
    class Meta(BaseEventForm.Meta):
        model = OutbreakEvent
        fields = BaseEventForm.Meta.fields + [
            'tipo_problema', 'severidad', 'metodo_deteccion',
            'area_afectada_ha', 'porcentaje_afectacion',
            'accion_inmediata', 'requiere_tratamiento'
        ]
        widgets = {
            **BaseEventForm.Meta.widgets,
            'tipo_problema': forms.TextInput(attrs={'class': 'form-control'}),
            'severidad': forms.Select(attrs={'class': 'form-select'}),
            'metodo_deteccion': forms.Select(attrs={'class': 'form-select'}),
            'area_afectada_ha': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0001',
                'min': 0
            }),
            'porcentaje_afectacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'max': 100
            }),
            'accion_inmediata': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'requiere_tratamiento': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ClimateEventForm(BaseEventForm):
    """Formulario para eventos climáticos."""
    
    class Meta(BaseEventForm.Meta):
        model = ClimateEvent
        fields = BaseEventForm.Meta.fields + [
            'temperatura_max', 'temperatura_min', 'humedad_relativa',
            'precipitacion_mm', 'velocidad_viento_ms', 'viento',
            'radiacion_solar_wm2'
        ]
        widgets = {
            **BaseEventForm.Meta.widgets,
            'temperatura_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': -20,
                'max': 50
            }),
            'temperatura_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': -20,
                'max': 50
            }),
            'humedad_relativa': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'max': 100
            }),
            'precipitacion_mm': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'velocidad_viento_ms': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'viento': forms.Select(attrs={'class': 'form-select'}),
            'radiacion_solar_wm2': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
        }
    
    def clean(self):
        """Valida que temperatura_max >= temperatura_min."""
        cleaned_data = super().clean()
        temp_max = cleaned_data.get('temperatura_max')
        temp_min = cleaned_data.get('temperatura_min')
        
        if temp_max is not None and temp_min is not None:
            if temp_max < temp_min:
                raise ValidationError({
                    'temperatura_max': 'La temperatura máxima debe ser mayor o igual a la mínima.'
                })
        
        return cleaned_data


class HarvestEventForm(BaseEventForm):
    """Formulario para eventos de cosecha."""
    
    class Meta(BaseEventForm.Meta):
        model = HarvestEvent
        fields = BaseEventForm.Meta.fields + [
            'variedad', 'volumen_kg', 'rendimiento_kg_ha', 'calidad',
            'numero_trabajadores', 'horas_trabajo', 'fecha_inicio', 'fecha_fin'
        ]
        widgets = {
            **BaseEventForm.Meta.widgets,
            'variedad': forms.TextInput(attrs={'class': 'form-control'}),
            'volumen_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'rendimiento_kg_ha': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'calidad': forms.Select(attrs={'class': 'form-select'}),
            'numero_trabajadores': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'horas_trabajo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
    
    def clean(self):
        """Valida que fecha_fin >= fecha_inicio."""
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                raise ValidationError({
                    'fecha_fin': 'La fecha de fin debe ser posterior o igual a la fecha de inicio.'
                })
        
        return cleaned_data


class PostHarvestEventForm(BaseEventForm):
    """Formulario para eventos poscosecha."""
    
    class Meta(BaseEventForm.Meta):
        model = PostHarvestEvent
        fields = BaseEventForm.Meta.fields + [
            'producto', 'cantidad_kg', 'temperatura', 'humedad',
            'tipo_almacenamiento', 'fecha_ingreso', 'fecha_salida_prevista',
            'condiciones_observadas'
        ]
        widgets = {
            **BaseEventForm.Meta.widgets,
            'producto': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'temperatura': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': -5,
                'max': 30
            }),
            'humedad': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'max': 100
            }),
            'tipo_almacenamiento': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_ingreso': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'fecha_salida_prevista': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'condiciones_observadas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }


class LaborCostEventForm(BaseEventForm):
    """Formulario para eventos de mano de obra y costos."""
    
    class Meta(BaseEventForm.Meta):
        model = LaborCostEvent
        fields = BaseEventForm.Meta.fields + [
            'actividad', 'numero_trabajadores', 'horas_trabajo',
            'costo_hora', 'costo_total'
        ]
        widgets = {
            **BaseEventForm.Meta.widgets,
            'actividad': forms.Select(attrs={'class': 'form-select'}),
            'numero_trabajadores': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'horas_trabajo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'id': 'id_horas_trabajo'
            }),
            'costo_hora': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'id': 'id_costo_hora'
            }),
            'costo_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'id': 'id_costo_total',
                'readonly': True
            }),
        }
    
    def clean(self):
        """Calcula costo_total automáticamente si se proporcionan horas_trabajo y costo_hora."""
        cleaned_data = super().clean()
        horas_trabajo = cleaned_data.get('horas_trabajo')
        costo_hora = cleaned_data.get('costo_hora')
        costo_total = cleaned_data.get('costo_total')
        numero_trabajadores = cleaned_data.get('numero_trabajadores', 1)
        
        # Si se proporcionan horas_trabajo y costo_hora, calcular costo_total
        if horas_trabajo and costo_hora and not costo_total:
            cleaned_data['costo_total'] = horas_trabajo * costo_hora * numero_trabajadores
        
        return cleaned_data


# Mapeo de tipos de eventos a sus formularios
EVENT_FORM_MAP = {
    'Aplicación de Riego': IrrigationEventForm,
    'Aplicación de Fertilizante': FertilizationEventForm,
    'Aplicación Fitosanitaria': PhytosanitaryEventForm,
    'Labores de Cultivo': MaintenanceEventForm,
    'Monitoreo de Plagas': MonitoringEventForm,
    'Brote de Plaga/Enfermedad': OutbreakEventForm,
    'Condiciones Climáticas': ClimateEventForm,
    'Cosecha': HarvestEventForm,
    'Almacenamiento Poscosecha': PostHarvestEventForm,
    'Mano de Obra y Costos': LaborCostEventForm,
}


def get_event_form(event_type_name):
    """
    Obtiene el formulario apropiado para un tipo de evento.
    
    Args:
        event_type_name: Nombre del tipo de evento
        
    Returns:
        Clase del formulario o None si no se encuentra
    """
    return EVENT_FORM_MAP.get(event_type_name)

