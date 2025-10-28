"""
Comando de Django para crear o actualizar los tipos de eventos base del sistema.

Uso:
    python manage.py setup_event_types
    python manage.py setup_event_types --update  # Actualiza tipos existentes
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.events.models import EventType


class Command(BaseCommand):
    help = 'Crea los tipos de eventos base del sistema de trazabilidad agrícola'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Actualiza los tipos de eventos existentes con nuevos datos',
        )

    def handle(self, *args, **options):
        update_existing = options['update']
        
        event_types_data = [
            # 1) Aplicación de riego
            {
                'name': 'Aplicación de Riego',
                'description': 'Registro de aplicación de riego en cultivos de limón',
                'category': 'irrigation',
                'icon': 'droplet-fill',
                'color': '#0dcaf0',
                'schema': {
                    "type": "object",
                    "title": "Datos de Aplicación de Riego",
                    "required": ["metodo", "duracion_minutos", "fuente_agua"],
                    "properties": {
                        "metodo": {
                            "type": "string",
                            "title": "Método de Riego",
                            "enum": ["Aspersión", "Goteo", "Surco", "Pivote", "Manual", "Microaspersión"],
                            "description": "Método utilizado para el riego",
                            "example": "Goteo"
                        },
                        "duracion_minutos": {
                            "type": "integer",
                            "title": "Duración (minutos)",
                            "description": "Duración total del riego en minutos",
                            "minimum": 1,
                            "example": 120
                        },
                        "volumen_m3": {
                            "type": "number",
                            "title": "Volumen Aplicado (m³)",
                            "description": "Volumen de agua aplicado en metros cúbicos",
                            "minimum": 0,
                            "example": 50.5
                        },
                        "volumen_mm_ha": {
                            "type": "number",
                            "title": "Lámina de Riego (mm/ha)",
                            "description": "Lámina de agua aplicada en milímetros por hectárea",
                            "minimum": 0,
                            "example": 25.0
                        },
                        "presion_bar": {
                            "type": "number",
                            "title": "Presión del Sistema (bar)",
                            "description": "Presión de operación del sistema de riego",
                            "minimum": 0,
                            "example": 1.5
                        },
                        "temperatura_agua": {
                            "type": "number",
                            "title": "Temperatura del Agua (°C)",
                            "minimum": 0,
                            "maximum": 50,
                            "example": 18.5
                        },
                        "ce_agua": {
                            "type": "number",
                            "title": "Conductividad Eléctrica (dS/m)",
                            "description": "CE del agua de riego",
                            "minimum": 0,
                            "example": 0.8
                        },
                        "ph_agua": {
                            "type": "number",
                            "title": "pH del Agua",
                            "minimum": 0,
                            "maximum": 14,
                            "example": 7.2
                        },
                        "fuente_agua": {
                            "type": "string",
                            "title": "Fuente de Agua",
                            "enum": ["Pozo", "Río", "Tanque", "Represa", "Red municipal", "Laguna"],
                            "example": "Pozo"
                        },
                        "uniformidad": {
                            "type": "string",
                            "title": "Uniformidad del Riego",
                            "enum": ["Excelente", "Buena", "Regular", "Deficiente"],
                            "example": "Buena"
                        },
                        "fugas_detectadas": {
                            "type": "boolean",
                            "title": "¿Fugas Detectadas?",
                            "example": False
                        }
                    }
                }
            },
            
            # 2) Aplicación de fertilizante
            {
                'name': 'Aplicación de Fertilizante',
                'description': 'Registro de fertilización al suelo o foliar',
                'category': 'fertilization',
                'icon': 'moisture',
                'color': '#198754',
                'schema': {
                    "type": "object",
                    "title": "Datos de Fertilización",
                    "required": ["producto", "metodo_aplicacion", "dosis"],
                    "properties": {
                        "producto": {
                            "type": "string",
                            "title": "Nombre del Producto",
                            "description": "Nombre comercial del fertilizante",
                            "maxLength": 200,
                            "example": "Nitrofoska 15-15-15"
                        },
                        "ingrediente_activo": {
                            "type": "string",
                            "title": "Ingrediente Activo / Fórmula",
                            "maxLength": 200,
                            "example": "NPK 15-15-15"
                        },
                        "lote_producto": {
                            "type": "string",
                            "title": "Lote del Producto",
                            "description": "Número de lote para trazabilidad",
                            "maxLength": 100,
                            "example": "LOTE-2024-0815"
                        },
                        "metodo_aplicacion": {
                            "type": "string",
                            "title": "Método de Aplicación",
                            "enum": ["Goteo", "Manual", "Aspersión", "Mecanizada", "Foliar", "Fertirrigación", "Incorporado"],
                            "example": "Foliar"
                        },
                        "dosis": {
                            "type": "number",
                            "title": "Dosis Aplicada",
                            "description": "Cantidad aplicada por unidad",
                            "minimum": 0,
                            "example": 3.5
                        },
                        "unidad_dosis": {
                            "type": "string",
                            "title": "Unidad de Dosis",
                            "enum": ["kg/ha", "L/ha", "g/planta", "mL/planta", "kg/m2"],
                            "example": "kg/ha"
                        },
                        "numero_aplicaciones": {
                            "type": "integer",
                            "title": "Aplicación Número",
                            "description": "Número de aplicación del programa",
                            "minimum": 1,
                            "example": 2
                        },
                        "objetivo": {
                            "type": "string",
                            "title": "Objetivo de la Aplicación",
                            "enum": ["Crecimiento vegetativo", "Floración", "Cuajado", "Desarrollo radicular", "Engorde de fruto", "Corrección de deficiencia", "Mantenimiento"],
                            "example": "Floración"
                        },
                        "mezclas": {
                            "type": "string",
                            "title": "Mezclas Realizadas",
                            "description": "Productos con los que se mezcló",
                            "maxLength": 300,
                            "example": "Mezclado con ácido húmico"
                        },
                        "temperatura_aplicacion": {
                            "type": "number",
                            "title": "Temperatura (°C)",
                            "minimum": -10,
                            "maximum": 50,
                            "example": 22.0
                        },
                        "humedad_relativa": {
                            "type": "number",
                            "title": "Humedad Relativa (%)",
                            "minimum": 0,
                            "maximum": 100,
                            "example": 65
                        },
                        "viento": {
                            "type": "string",
                            "title": "Condición de Viento",
                            "enum": ["Sin viento", "Viento leve", "Viento moderado", "Viento fuerte"],
                            "example": "Viento leve"
                        }
                    }
                }
            },
            
            # 3) Aplicación fitosanitaria (fungicida/insecticida/herbicida)
            {
                'name': 'Aplicación Fitosanitaria',
                'description': 'Aplicación de fungicidas, insecticidas, herbicidas o acaricidas',
                'category': 'phytosanitary',
                'icon': 'bug-fill',
                'color': '#dc3545',
                'schema': {
                    "type": "object",
                    "title": "Datos de Aplicación Fitosanitaria",
                    "required": ["producto", "tipo_producto", "objetivo", "metodo_aplicacion", "dosis"],
                    "properties": {
                        "producto": {
                            "type": "string",
                            "title": "Nombre Comercial",
                            "maxLength": 200,
                            "example": "Confidor 200 SL"
                        },
                        "ingrediente_activo": {
                            "type": "string",
                            "title": "Ingrediente Activo",
                            "maxLength": 200,
                            "example": "Imidacloprid 20%"
                        },
                        "tipo_producto": {
                            "type": "string",
                            "title": "Tipo de Producto",
                            "enum": ["Insecticida", "Fungicida", "Herbicida", "Acaricida", "Nematicida", "Bactericida", "Coadyuvante"],
                            "example": "Insecticida"
                        },
                        "objetivo": {
                            "type": "string",
                            "title": "Plaga/Enfermedad/Maleza Objetivo",
                            "maxLength": 200,
                            "example": "Minador de la hoja (Phyllocnistis citrella)"
                        },
                        "lote_producto": {
                            "type": "string",
                            "title": "Lote del Producto",
                            "maxLength": 100,
                            "example": "LOTE-FIT-2024-0520"
                        },
                        "metodo_aplicacion": {
                            "type": "string",
                            "title": "Método de Aplicación",
                            "enum": ["Mochila manual", "Mochila motorizada", "Tractor", "Dron", "Avión", "Fertirrigación", "Inyección al tronco"],
                            "example": "Mochila motorizada"
                        },
                        "dosis": {
                            "type": "number",
                            "title": "Dosis",
                            "minimum": 0,
                            "example": 0.5
                        },
                        "unidad_dosis": {
                            "type": "string",
                            "title": "Unidad de Dosis",
                            "enum": ["L/ha", "mL/L", "g/L", "kg/ha", "cc/árbol"],
                            "example": "L/ha"
                        },
                        "volumen_caldo_l": {
                            "type": "number",
                            "title": "Volumen de Caldo (L)",
                            "minimum": 0,
                            "example": 400
                        },
                        "presion_bar": {
                            "type": "number",
                            "title": "Presión de Aplicación (bar)",
                            "minimum": 0,
                            "example": 3.0
                        },
                        "tipo_boquilla": {
                            "type": "string",
                            "title": "Tipo de Boquilla",
                            "maxLength": 100,
                            "example": "Cono hueco"
                        },
                        "intervalo_seguridad_dias": {
                            "type": "integer",
                            "title": "Intervalo de Seguridad (días)",
                            "description": "Días antes de cosecha permitidos",
                            "minimum": 0,
                            "example": 21
                        },
                        "temperatura_aplicacion": {
                            "type": "number",
                            "title": "Temperatura (°C)",
                            "example": 24.0
                        },
                        "humedad_relativa": {
                            "type": "number",
                            "title": "Humedad Relativa (%)",
                            "minimum": 0,
                            "maximum": 100,
                            "example": 70
                        },
                        "viento": {
                            "type": "string",
                            "title": "Condición de Viento",
                            "enum": ["Sin viento", "Viento leve", "Viento moderado", "Viento fuerte"],
                            "example": "Viento leve"
                        },
                        "responsable_aplicacion": {
                            "type": "string",
                            "title": "Responsable de la Aplicación",
                            "maxLength": 200,
                            "example": "Juan Pérez"
                        },
                        "eficacia_observada": {
                            "type": "string",
                            "title": "Eficacia Observada",
                            "enum": ["No evaluada", "Muy baja", "Baja", "Media", "Alta", "Muy alta"],
                            "example": "Alta"
                        },
                        "fitotoxicidad": {
                            "type": "boolean",
                            "title": "¿Fitotoxicidad Observada?",
                            "example": False
                        }
                    }
                }
            },
            
            # 4) Labores de cultivo (mantenimiento)
            {
                'name': 'Labores de Cultivo',
                'description': 'Actividades de mantenimiento y cuidado del cultivo',
                'category': 'maintenance',
                'icon': 'tools',
                'color': '#6f42c1',
                'schema': {
                    "type": "object",
                    "title": "Datos de Labores de Cultivo",
                    "required": ["actividad", "horas_hombre"],
                    "properties": {
                        "actividad": {
                            "type": "string",
                            "title": "Tipo de Actividad",
                            "enum": ["Poda", "Deshierbe", "Entutorado", "Aclareo de frutos", "Despunte", "Cobertura vegetal", "Desbrote", "Raleo", "Limpieza de canales", "Reparación de sistema de riego"],
                            "example": "Poda"
                        },
                        "herramienta_equipo": {
                            "type": "string",
                            "title": "Herramienta/Equipo Usado",
                            "maxLength": 200,
                            "example": "Tijera de podar, motosierra"
                        },
                        "numero_jornales": {
                            "type": "integer",
                            "title": "Número de Jornales",
                            "description": "Cantidad de trabajadores",
                            "minimum": 1,
                            "example": 3
                        },
                        "horas_hombre": {
                            "type": "number",
                            "title": "Total Horas-Hombre",
                            "minimum": 0,
                            "example": 24.0
                        },
                        "objetivo": {
                            "type": "string",
                            "title": "Objetivo de la Labor",
                            "maxLength": 300,
                            "example": "Mejorar aireación y penetración de luz"
                        },
                        "porcentaje_completado": {
                            "type": "number",
                            "title": "Porcentaje Completado (%)",
                            "minimum": 0,
                            "maximum": 100,
                            "example": 100
                        },
                        "herramientas_desinfectadas": {
                            "type": "boolean",
                            "title": "¿Herramientas Desinfectadas?",
                            "example": True
                        }
                    }
                }
            },
            
            # 5) Monitoreo de plagas y enfermedades
            {
                'name': 'Monitoreo de Plagas',
                'description': 'Registro de monitoreo y detección temprana de plagas y enfermedades',
                'category': 'monitoring',
                'icon': 'eye-fill',
                'color': '#fd7e14',
                'schema': {
                    "type": "object",
                    "title": "Datos de Monitoreo",
                    "required": ["plaga_enfermedad", "metodo_muestreo", "incidencia"],
                    "properties": {
                        "plaga_enfermedad": {
                            "type": "string",
                            "title": "Plaga/Enfermedad Observada",
                            "maxLength": 200,
                            "example": "Araña roja (Tetranychus urticae)"
                        },
                        "metodo_muestreo": {
                            "type": "string",
                            "title": "Método de Muestreo",
                            "enum": ["Trampas cromáticas", "Trampas de feromonas", "Conteo visual", "Muestreo de hojas", "Muestreo de frutos", "Golpeo de rama", "Transecto"],
                            "example": "Conteo visual"
                        },
                        "numero_individuos": {
                            "type": "integer",
                            "title": "Número de Individuos",
                            "description": "Cantidad de individuos contados",
                            "minimum": 0,
                            "example": 12
                        },
                        "incidencia": {
                            "type": "number",
                            "title": "Incidencia (%)",
                            "description": "Porcentaje de plantas/frutos afectados",
                            "minimum": 0,
                            "maximum": 100,
                            "example": 8.5
                        },
                        "severidad": {
                            "type": "string",
                            "title": "Nivel de Severidad",
                            "enum": ["Ausente", "Bajo", "Medio", "Alto", "Muy alto"],
                            "example": "Bajo"
                        },
                        "umbral_economico": {
                            "type": "boolean",
                            "title": "¿Umbral Económico Alcanzado?",
                            "description": "Indica si se requiere intervención",
                            "example": False
                        },
                        "estado_fenologico": {
                            "type": "string",
                            "title": "Estado Fenológico",
                            "enum": ["Brotación", "Vegetativo", "Floración", "Cuajado", "Desarrollo de fruto", "Maduración", "Cosecha"],
                            "example": "Floración"
                        },
                        "plantas_muestreadas": {
                            "type": "integer",
                            "title": "Número de Plantas Muestreadas",
                            "minimum": 1,
                            "example": 50
                        },
                        "plantas_afectadas": {
                            "type": "integer",
                            "title": "Plantas Afectadas",
                            "minimum": 0,
                            "example": 4
                        },
                        "requiere_tratamiento": {
                            "type": "boolean",
                            "title": "¿Requiere Tratamiento Inmediato?",
                            "example": False
                        }
                    }
                }
            },
            
            # 6) Brotes de plagas o enfermedades
            {
                'name': 'Brote de Plaga/Enfermedad',
                'description': 'Registro de brotes severos que requieren atención inmediata',
                'category': 'monitoring',
                'icon': 'exclamation-triangle-fill',
                'color': '#dc3545',
                'schema': {
                    "type": "object",
                    "title": "Datos del Brote",
                    "required": ["tipo_problema", "severidad", "metodo_deteccion"],
                    "properties": {
                        "tipo_problema": {
                            "type": "string",
                            "title": "Tipo de Plaga/Enfermedad",
                            "maxLength": 200,
                            "example": "Gomosis (Phytophthora spp.)"
                        },
                        "nombre_cientifico": {
                            "type": "string",
                            "title": "Nombre Científico",
                            "maxLength": 200,
                            "example": "Phytophthora citrophthora"
                        },
                        "severidad": {
                            "type": "string",
                            "title": "Nivel de Severidad",
                            "enum": ["Leve", "Moderado", "Severo", "Muy severo", "Crítico"],
                            "example": "Severo"
                        },
                        "incidencia_pct": {
                            "type": "number",
                            "title": "Incidencia (%)",
                            "description": "Porcentaje de plantas afectadas",
                            "minimum": 0,
                            "maximum": 100,
                            "example": 35.0
                        },
                        "area_afectada_ha": {
                            "type": "number",
                            "title": "Área Afectada (ha)",
                            "minimum": 0,
                            "example": 2.5
                        },
                        "metodo_deteccion": {
                            "type": "string",
                            "title": "Método de Detección",
                            "enum": ["Visual en campo", "Trampa", "Muestreo sistemático", "Imagen satelital", "Sensor IoT", "Reporte de trabajador"],
                            "example": "Visual en campo"
                        },
                        "estado_fenologico": {
                            "type": "string",
                            "title": "Estado Fenológico del Cultivo",
                            "enum": ["Plántula", "Vegetativo", "Floración", "Fructificación", "Madurez"],
                            "example": "Fructificación"
                        },
                        "plantas_afectadas": {
                            "type": "integer",
                            "title": "Número de Plantas Afectadas",
                            "minimum": 0,
                            "example": 150
                        },
                        "responsable_deteccion": {
                            "type": "string",
                            "title": "Responsable de la Detección",
                            "maxLength": 200,
                            "example": "María González - Ingeniera Agrónoma"
                        },
                        "accion_inmediata": {
                            "type": "string",
                            "title": "Acción Inmediata Tomada",
                            "maxLength": 500,
                            "example": "Aislamiento del área afectada y notificación a gerencia"
                        },
                        "requiere_cuarentena": {
                            "type": "boolean",
                            "title": "¿Requiere Cuarentena?",
                            "example": False
                        }
                    }
                }
            },
            
            # 7) Registro de condiciones climáticas
            {
                'name': 'Condiciones Climáticas',
                'description': 'Registro de variables climáticas observadas o medidas',
                'category': 'monitoring',
                'icon': 'cloud-sun-fill',
                'color': '#20c997',
                'schema': {
                    "type": "object",
                    "title": "Datos Climáticos",
                    "required": ["temperatura_max", "temperatura_min"],
                    "properties": {
                        "temperatura_min": {
                            "type": "number",
                            "title": "Temperatura Mínima (°C)",
                            "minimum": -20,
                            "maximum": 50,
                            "example": 12.5
                        },
                        "temperatura_max": {
                            "type": "number",
                            "title": "Temperatura Máxima (°C)",
                            "minimum": -20,
                            "maximum": 60,
                            "example": 28.3
                        },
                        "temperatura_media": {
                            "type": "number",
                            "title": "Temperatura Media (°C)",
                            "minimum": -20,
                            "maximum": 50,
                            "example": 20.4
                        },
                        "humedad_relativa": {
                            "type": "number",
                            "title": "Humedad Relativa (%)",
                            "minimum": 0,
                            "maximum": 100,
                            "example": 65
                        },
                        "precipitacion_mm": {
                            "type": "number",
                            "title": "Precipitación (mm)",
                            "minimum": 0,
                            "example": 5.2
                        },
                        "velocidad_viento_kmh": {
                            "type": "number",
                            "title": "Velocidad del Viento (km/h)",
                            "minimum": 0,
                            "example": 15.0
                        },
                        "direccion_viento": {
                            "type": "string",
                            "title": "Dirección del Viento",
                            "enum": ["N", "NE", "E", "SE", "S", "SO", "O", "NO"],
                            "example": "SO"
                        },
                        "radiacion_solar": {
                            "type": "number",
                            "title": "Radiación Solar (W/m²)",
                            "minimum": 0,
                            "example": 850.0
                        },
                        "nubosidad": {
                            "type": "string",
                            "title": "Nubosidad",
                            "enum": ["Despejado", "Parcialmente nublado", "Nublado", "Muy nublado"],
                            "example": "Parcialmente nublado"
                        },
                        "evento_extremo": {
                            "type": "string",
                            "title": "Evento Climático Extremo",
                            "enum": ["Ninguno", "Helada", "Granizo", "Tormenta eléctrica", "Viento fuerte", "Ola de calor", "Sequía"],
                            "example": "Ninguno"
                        },
                        "fuente_datos": {
                            "type": "string",
                            "title": "Fuente de Datos",
                            "enum": ["Estación meteorológica en campo", "Estación IoT", "Observación visual", "Servicio meteorológico nacional", "Sensor manual"],
                            "example": "Estación meteorológica en campo"
                        }
                    }
                }
            },
            
            # 8) Cosecha
            {
                'name': 'Cosecha',
                'description': 'Registro de actividades de cosecha de limones',
                'category': 'harvest',
                'icon': 'basket-fill',
                'color': '#ffc107',
                'schema': {
                    "type": "object",
                    "title": "Datos de Cosecha",
                    "required": ["volumen_kg", "rendimiento_kg_ha"],
                    "properties": {
                        "variedad": {
                            "type": "string",
                            "title": "Variedad de Limón",
                            "maxLength": 100,
                            "example": "Limón Persa (Tahití)"
                        },
                        "etapa_madurez": {
                            "type": "string",
                            "title": "Etapa de Madurez",
                            "enum": ["Verde", "3/4 maduro", "Maduro", "Sobremaduro"],
                            "example": "3/4 maduro"
                        },
                        "criterio_cosecha": {
                            "type": "string",
                            "title": "Criterio de Cosecha",
                            "maxLength": 200,
                            "example": "Tamaño mínimo 5cm, color verde intenso"
                        },
                        "volumen_kg": {
                            "type": "number",
                            "title": "Volumen Cosechado (kg)",
                            "minimum": 0,
                            "example": 2500.5
                        },
                        "numero_cajas": {
                            "type": "integer",
                            "title": "Número de Cajas",
                            "minimum": 0,
                            "example": 100
                        },
                        "peso_promedio_caja": {
                            "type": "number",
                            "title": "Peso Promedio por Caja (kg)",
                            "minimum": 0,
                            "example": 25.0
                        },
                        "rendimiento_kg_ha": {
                            "type": "number",
                            "title": "Rendimiento (kg/ha)",
                            "minimum": 0,
                            "example": 15000.0
                        },
                        "calibre": {
                            "type": "string",
                            "title": "Calibre Predominante",
                            "enum": ["Extra grande", "Grande", "Mediano", "Pequeño", "Mixto"],
                            "example": "Grande"
                        },
                        "calidad_a_pct": {
                            "type": "number",
                            "title": "Calidad A (%)",
                            "minimum": 0,
                            "maximum": 100,
                            "example": 70.0
                        },
                        "calidad_b_pct": {
                            "type": "number",
                            "title": "Calidad B (%)",
                            "minimum": 0,
                            "maximum": 100,
                            "example": 25.0
                        },
                        "descarte_pct": {
                            "type": "number",
                            "title": "Descarte (%)",
                            "minimum": 0,
                            "maximum": 100,
                            "example": 5.0
                        },
                        "destino": {
                            "type": "string",
                            "title": "Destino de la Cosecha",
                            "enum": ["Exportación", "Mercado local", "Industria", "Autoconsumo", "Almacenamiento"],
                            "example": "Exportación"
                        },
                        "transporte": {
                            "type": "string",
                            "title": "Tipo de Transporte",
                            "enum": ["Camión refrigerado", "Camión convencional", "Furgoneta", "Otro"],
                            "example": "Camión refrigerado"
                        },
                        "numero_recolectores": {
                            "type": "integer",
                            "title": "Número de Recolectores",
                            "minimum": 1,
                            "example": 15
                        },
                        "horas_trabajo": {
                            "type": "number",
                            "title": "Horas de Trabajo Total",
                            "minimum": 0,
                            "example": 60.0
                        }
                    }
                }
            },
            
            # 9) Almacenamiento / Poscosecha
            {
                'name': 'Almacenamiento Poscosecha',
                'description': 'Control de almacenamiento y conservación del producto',
                'category': 'postharvest',
                'icon': 'box-seam-fill',
                'color': '#795548',
                'schema': {
                    "type": "object",
                    "title": "Datos de Almacenamiento",
                    "required": ["producto", "cantidad_kg", "temperatura", "humedad"],
                    "properties": {
                        "producto": {
                            "type": "string",
                            "title": "Producto Almacenado",
                            "maxLength": 200,
                            "example": "Limón Persa - Calidad A"
                        },
                        "variedad": {
                            "type": "string",
                            "title": "Variedad",
                            "maxLength": 100,
                            "example": "Tahití"
                        },
                        "cantidad_kg": {
                            "type": "number",
                            "title": "Cantidad Almacenada (kg)",
                            "minimum": 0,
                            "example": 5000.0
                        },
                        "numero_lote": {
                            "type": "string",
                            "title": "Número de Lote",
                            "maxLength": 100,
                            "example": "COSECHA-2024-10-15"
                        },
                        "fecha_entrada": {
                            "type": "string",
                            "title": "Fecha de Entrada",
                            "example": "2024-10-15"
                        },
                        "temperatura": {
                            "type": "number",
                            "title": "Temperatura de Almacenamiento (°C)",
                            "minimum": -5,
                            "maximum": 30,
                            "example": 10.0
                        },
                        "humedad": {
                            "type": "number",
                            "title": "Humedad Relativa (%)",
                            "minimum": 0,
                            "maximum": 100,
                            "example": 85.0
                        },
                        "atmosfera_controlada": {
                            "type": "boolean",
                            "title": "¿Atmósfera Controlada?",
                            "example": False
                        },
                        "co2_pct": {
                            "type": "number",
                            "title": "CO₂ (%)",
                            "minimum": 0,
                            "maximum": 100,
                            "example": 5.0
                        },
                        "o2_pct": {
                            "type": "number",
                            "title": "O₂ (%)",
                            "minimum": 0,
                            "maximum": 100,
                            "example": 3.0
                        },
                        "perdidas_kg": {
                            "type": "number",
                            "title": "Pérdidas (kg)",
                            "minimum": 0,
                            "example": 50.0
                        },
                        "causa_perdidas": {
                            "type": "string",
                            "title": "Causa de Pérdidas",
                            "enum": ["Ninguna", "Podredumbre", "Deshidratación", "Daño mecánico", "Plagas", "Otro"],
                            "example": "Ninguna"
                        },
                        "tratamiento_aplicado": {
                            "type": "string",
                            "title": "Tratamiento Aplicado",
                            "maxLength": 300,
                            "example": "Encerado y fungicida poscosecha"
                        }
                    }
                }
            },
            
            # 10) Mano de obra y costos
            {
                'name': 'Mano de Obra y Costos',
                'description': 'Registro de recursos humanos y costos asociados a actividades',
                'category': 'other',
                'icon': 'people-fill',
                'color': '#6c757d',
                'schema': {
                    "type": "object",
                    "title": "Datos de Mano de Obra y Costos",
                    "required": ["actividad", "numero_trabajadores", "costo_total"],
                    "properties": {
                        "actividad": {
                            "type": "string",
                            "title": "Actividad Realizada",
                            "enum": ["Riego", "Fertilización", "Aplicación fitosanitaria", "Poda", "Deshierbe", "Cosecha", "Mantenimiento", "Transporte", "Otra"],
                            "example": "Cosecha"
                        },
                        "descripcion_actividad": {
                            "type": "string",
                            "title": "Descripción Detallada",
                            "maxLength": 300,
                            "example": "Cosecha manual de limón para exportación"
                        },
                        "numero_trabajadores": {
                            "type": "integer",
                            "title": "Número de Trabajadores",
                            "minimum": 1,
                            "example": 15
                        },
                        "horas_trabajadas": {
                            "type": "number",
                            "title": "Horas Trabajadas (total)",
                            "minimum": 0,
                            "example": 120.0
                        },
                        "jornales": {
                            "type": "number",
                            "title": "Jornales (días-hombre)",
                            "minimum": 0,
                            "example": 15.0
                        },
                        "costo_jornal": {
                            "type": "number",
                            "title": "Costo por Jornal",
                            "minimum": 0,
                            "example": 150.00
                        },
                        "costo_hora": {
                            "type": "number",
                            "title": "Costo por Hora",
                            "minimum": 0,
                            "example": 18.75
                        },
                        "costo_total": {
                            "type": "number",
                            "title": "Costo Total (mano de obra)",
                            "minimum": 0,
                            "example": 2250.00
                        },
                        "moneda": {
                            "type": "string",
                            "title": "Moneda",
                            "enum": ["MXN", "USD", "EUR", "Otra"],
                            "example": "MXN"
                        },
                        "costos_adicionales": {
                            "type": "number",
                            "title": "Costos Adicionales (insumos, equipo)",
                            "minimum": 0,
                            "example": 500.00
                        },
                        "costo_total_actividad": {
                            "type": "number",
                            "title": "Costo Total de la Actividad",
                            "description": "Incluye mano de obra + costos adicionales",
                            "minimum": 0,
                            "example": 2750.00
                        },
                        "tipo_contrato": {
                            "type": "string",
                            "title": "Tipo de Contrato",
                            "enum": ["Eventual", "Permanente", "Por tarea", "Por destajo"],
                            "example": "Eventual"
                        },
                        "supervisor": {
                            "type": "string",
                            "title": "Supervisor/Responsable",
                            "maxLength": 200,
                            "example": "Ing. Carlos Ramírez"
                        }
                    }
                }
            },
        ]
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        with transaction.atomic():
            for event_data in event_types_data:
                name = event_data['name']
                
                # Verificar si ya existe
                existing = EventType.objects.filter(name=name).first()
                
                if existing:
                    if update_existing:
                        # Actualizar el tipo de evento existente
                        for key, value in event_data.items():
                            setattr(existing, key, value)
                        existing.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'✓ Actualizado: {name}')
                        )
                    else:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.NOTICE(f'○ Ya existe: {name} (usa --update para actualizar)')
                        )
                else:
                    # Crear nuevo tipo de evento
                    EventType.objects.create(**event_data)
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Creado: {name}')
                    )
        
        # Resumen
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('RESUMEN DE LA OPERACIÓN'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'Tipos de eventos creados:      {created_count}')
        self.stdout.write(f'Tipos de eventos actualizados: {updated_count}')
        self.stdout.write(f'Tipos de eventos omitidos:     {skipped_count}')
        self.stdout.write(self.style.SUCCESS('='*60))
        
        if created_count > 0 or updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Sistema configurado correctamente con {created_count + updated_count + skipped_count} tipos de eventos.'
                )
            )
        else:
            self.stdout.write(
                self.style.NOTICE(
                    '\n○ No se realizaron cambios. Todos los tipos de eventos ya existen.'
                )
            )
