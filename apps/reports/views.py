from rest_framework import views, response, status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    summary="Health Check",
    description="""
    Endpoint de verificación de estado del servicio (health check).
    
    Este endpoint permite verificar que el servicio API está funcionando correctamente
    y puede responder a peticiones.
    
    **Casos de uso:**
    - Monitoreo de disponibilidad del servicio
    - Validación en sistemas de balanceo de carga
    - Pruebas de conectividad
    - Verificación de despliegues
    
    **Respuesta:**
    - Status 200: El servicio está operativo
    - Incluye información básica del estado del sistema
    """,
    tags=['Sistema - Reportes'],
    responses={
        200: OpenApiResponse(
            description="Servicio operativo",
            response={
                'type': 'object',
                'properties': {
                    'status': {
                        'type': 'string',
                        'example': 'ok',
                        'description': 'Estado del servicio'
                    },
                    'service': {
                        'type': 'string',
                        'example': 'Sistema de Trazabilidad Agrícola',
                        'description': 'Nombre del servicio'
                    },
                    'version': {
                        'type': 'string',
                        'example': '1.0.0',
                        'description': 'Versión de la API'
                    }
                }
            }
        ),
    },
)
class HealthCheckView(views.APIView):
    """
    API endpoint para verificación de estado del servicio.
    
    Retorna un JSON simple indicando que el servicio está operativo.
    """
    
    def get(self, request):
        """
        Verifica el estado del servicio.
        
        Returns:
            Response: JSON con el estado del servicio
        """
        return response.Response({
            'status': 'ok',
            'service': 'Sistema de Trazabilidad Agrícola',
            'version': '1.0.0',
        }, status=status.HTTP_200_OK)

