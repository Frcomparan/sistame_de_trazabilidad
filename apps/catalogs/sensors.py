"""
Servicio para integración con ThingSpeak IoT Platform.
Permite consultar datos de sensores en tiempo real.
"""
import requests
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ThingSpeakService:
    """Servicio para consultar datos de sensores desde ThingSpeak."""
    
    BASE_URL = "https://api.thingspeak.com"
    
    def __init__(self, channel_id: str, api_key: str):
        """
        Inicializa el servicio de ThingSpeak.
        
        Args:
            channel_id: ID del canal de ThingSpeak
            api_key: API key de lectura del canal
        """
        self.channel_id = channel_id
        self.api_key = api_key
    
    def get_latest_feeds(self, results: int = 10, start_date: str = None, end_date: str = None) -> Optional[Dict]:
        """
        Obtiene los últimos registros del canal.
        
        Args:
            results: Número de registros a obtener (por defecto 10, máximo 8000)
            start_date: Fecha de inicio en formato ISO (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)
            end_date: Fecha de fin en formato ISO (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)
            
        Returns:
            Diccionario con información del canal y feeds, o None si hay error
        """
        try:
            url = f"{self.BASE_URL}/channels/{self.channel_id}/feeds.json"
            params = {
                'api_key': self.api_key,
                'results': min(results, 8000)  # ThingSpeak limita a 8000
            }
            
            # Agregar filtros de fecha si se proporcionan
            if start_date:
                params['start'] = start_date
            if end_date:
                params['end'] = end_date
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al consultar ThingSpeak: {e}")
            return None
    
    def get_field_data(self, field_number: int, results: int = 10) -> Optional[Dict]:
        """
        Obtiene datos de un campo específico del canal.
        
        Args:
            field_number: Número del campo (1-8)
            results: Número de registros a obtener
            
        Returns:
            Diccionario con datos del campo, o None si hay error
        """
        try:
            url = f"{self.BASE_URL}/channels/{self.channel_id}/fields/{field_number}.json"
            params = {
                'api_key': self.api_key,
                'results': results
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al consultar campo {field_number}: {e}")
            return None
    
    def get_last_entry(self) -> Optional[Dict]:
        """
        Obtiene la última entrada del canal.
        
        Returns:
            Diccionario con la última entrada, o None si hay error
        """
        data = self.get_latest_feeds(results=1)
        if data and data.get('feeds'):
            return data['feeds'][0]
        return None
    
    def parse_sensor_data(self, data: Dict) -> List[Dict]:
        """
        Parsea los datos del sensor en un formato más amigable.
        
        Args:
            data: Datos crudos de ThingSpeak
            
        Returns:
            Lista de lecturas parseadas con timestamp y valores
        """
        if not data or 'feeds' not in data:
            return []
        
        channel_info = data.get('channel', {})
        feeds = data.get('feeds', [])
        
        parsed_readings = []
        for feed in feeds:
            reading = {
                'timestamp': feed.get('created_at'),
                'entry_id': feed.get('entry_id'),
                'values': {}
            }
            
            # Extraer valores de los campos
            for i in range(1, 9):  # ThingSpeak soporta hasta 8 campos
                field_key = f'field{i}'
                field_name_key = f'field{i}'
                
                if field_key in feed and feed[field_key] is not None:
                    field_name = channel_info.get(field_name_key, f'Campo {i}')
                    reading['values'][field_name] = {
                        'value': float(feed[field_key]),
                        'field_number': i
                    }
            
            parsed_readings.append(reading)
        
        return parsed_readings
    
    def get_formatted_current_data(self) -> Optional[Dict]:
        """
        Obtiene y formatea los datos actuales del sensor.
        
        Returns:
            Diccionario con datos formateados o None si hay error
        """
        data = self.get_latest_feeds(results=1)
        if not data:
            return None
        
        channel = data.get('channel', {})
        feeds = data.get('feeds', [])
        
        if not feeds:
            return None
        
        current_feed = feeds[0]
        
        result = {
            'channel_id': channel.get('id'),
            'channel_name': channel.get('name'),
            'description': channel.get('description'),
            'timestamp': current_feed.get('created_at'),
            'entry_id': current_feed.get('entry_id'),
            'sensors': []
        }
        
        # Mapeo de campos a nombres de sensores
        field_mappings = {
            'field1': {'name': channel.get('field1', 'Temperatura'), 'unit': '°C', 'icon': 'bi-thermometer-half'},
            'field2': {'name': channel.get('field2', 'Humedad'), 'unit': '%', 'icon': 'bi-droplet-fill'},
            'field3': {'name': channel.get('field3', 'Campo 3'), 'unit': '', 'icon': 'bi-speedometer2'},
            'field4': {'name': channel.get('field4', 'Campo 4'), 'unit': '', 'icon': 'bi-speedometer2'},
            'field5': {'name': channel.get('field5', 'Campo 5'), 'unit': '', 'icon': 'bi-speedometer2'},
            'field6': {'name': channel.get('field6', 'Campo 6'), 'unit': '', 'icon': 'bi-speedometer2'},
            'field7': {'name': channel.get('field7', 'Campo 7'), 'unit': '', 'icon': 'bi-speedometer2'},
            'field8': {'name': channel.get('field8', 'Campo 8'), 'unit': '', 'icon': 'bi-speedometer2'},
        }
        
        for field_key, field_info in field_mappings.items():
            value = current_feed.get(field_key)
            if value is not None:
                result['sensors'].append({
                    'name': field_info['name'],
                    'value': float(value),
                    'unit': field_info['unit'],
                    'icon': field_info['icon']
                })
        
        return result
    
    def get_formatted_historical_data(self, results: int = 20, start_date: str = None, end_date: str = None) -> Optional[Dict]:
        """
        Obtiene y formatea datos históricos de sensores.
        
        Args:
            results: Número de registros históricos a obtener (por defecto 20, máximo 8000)
            start_date: Fecha de inicio en formato ISO (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)
            end_date: Fecha de fin en formato ISO (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)
            
        Returns:
            Diccionario con datos históricos formateados o None si hay error
        """
        data = self.get_latest_feeds(results=results, start_date=start_date, end_date=end_date)
        if not data:
            return None
        
        channel = data.get('channel', {})
        feeds = data.get('feeds', [])
        
        if not feeds:
            return None
        
        # Información del canal
        result = {
            'channel_id': channel.get('id'),
            'channel_name': channel.get('name'),
            'description': channel.get('description'),
            'field_names': {
                'field1': channel.get('field1', 'Temperatura'),
                'field2': channel.get('field2', 'Humedad'),
            },
            'feeds': []
        }
        
        # Procesar cada feed
        for feed in feeds:
            feed_data = {
                'timestamp': feed.get('created_at'),
                'entry_id': feed.get('entry_id'),
                'temperature': float(feed.get('field1')) if feed.get('field1') else None,
                'humidity': float(feed.get('field2')) if feed.get('field2') else None,
            }
            result['feeds'].append(feed_data)
        
        return result


def get_thingspeak_service() -> ThingSpeakService:
    """
    Crea una instancia del servicio ThingSpeak con la configuración del proyecto.
    
    Returns:
        Instancia de ThingSpeakService
    """
    # Configuración del canal de ThingSpeak
    CHANNEL_ID = "3142831"
    API_KEY = "FQR4GTLHXXO0I3K2"
    
    return ThingSpeakService(CHANNEL_ID, API_KEY)
