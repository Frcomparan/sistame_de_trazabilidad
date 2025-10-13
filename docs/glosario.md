# Glosario de Términos

[← Volver al índice](../README.md) | [← Plan de Pruebas](./10_pruebas.md) | [Referencias →](./referencias.md)

## A

**Adjunto (Attachment)**  
Archivo digital (foto, PDF, CSV) asociado a un evento de trazabilidad como evidencia o documentación complementaria.

**API (Application Programming Interface)**  
Interfaz de programación que permite la comunicación entre diferentes sistemas o componentes de software. En este proyecto, REST API para acceso programático a datos.

**API REST**  
Arquitectura de API que utiliza métodos HTTP estándar (GET, POST, PUT, DELETE) para operaciones CRUD sobre recursos.

**Auditoría**  
Registro cronológico de todas las acciones realizadas en el sistema (quién, qué, cuándo) para trazabilidad de cambios y cumplimiento normativo.

## B

**Backend**  
Parte del sistema que se ejecuta en el servidor y gestiona la lógica de negocio, acceso a datos y procesamiento. En este proyecto: Django + PostgreSQL.

**Backup**  
Copia de seguridad de la base de datos y archivos del sistema para recuperación ante desastres.

**BCRYPT**  
Algoritmo de hash criptográfico para almacenar contraseñas de forma segura.

## C

**Campaña (Campaign)**  
Período de producción agrícola definido por fechas de inicio y fin, variedad cultivada y temporada. Ejemplo: "2025 - Temporada Alta".

**CE (Conductividad Eléctrica)**  
Medida de la concentración de sales disueltas en agua o suelo, expresada en µS/cm (microsiemens por centímetro).

**CORS (Cross-Origin Resource Sharing)**  
Mecanismo que permite o restringe el acceso a la API desde dominios web diferentes al del servidor.

**CRUD**  
Acrónimo de Create (Crear), Read (Leer), Update (Actualizar), Delete (Eliminar). Operaciones básicas sobre datos.

**CSRF (Cross-Site Request Forgery)**  
Ataque web que Django previene mediante tokens únicos en formularios.

## D

**Dashboard**  
Panel de control que muestra información resumida, KPIs y visualizaciones del sistema.

**Django**  
Framework web de Python de alto nivel que facilita el desarrollo rápido y limpio de aplicaciones.

**Django REST Framework (DRF)**  
Librería de Django para construir APIs REST de forma eficiente.

**Dosis**  
Cantidad de producto aplicado por unidad de área, típicamente expresada en kg/ha (kilogramos por hectárea) o L/ha (litros por hectárea).

## E

**Evento (Event)**  
Registro de una actividad o acción realizada en el cultivo (riego, fertilización, cosecha, etc.) con fecha, lugar y datos específicos.

**EventType (Tipo de Evento)**  
Definición de una categoría de evento con su esquema de campos. Ejemplo: "Riego" con campos método, duración, volumen.

**Evento Dinámico**  
Capacidad del sistema de crear nuevos tipos de eventos y sus campos sin modificar código fuente, usando JSON Schema.

## F

**Fertilización**  
Aplicación de nutrientes al suelo o planta para mejorar crecimiento y producción.

**Field (Lote/Parcela)**  
Unidad física de terreno agrícola donde se cultiva. Identificada por nombre, código y superficie.

**Fitosanitario**  
Producto químico o biológico usado para control de plagas, enfermedades y malezas (fungicida, insecticida, herbicida).

**Frontend**  
Parte del sistema con la que interactúa el usuario (interfaz web). En este proyecto: HTML, CSS, JavaScript (HTMX/Alpine.js).

## G

**GeoJSON**  
Formato estándar para representar geometrías geográficas en JSON. Usado para polígonos de lotes.

**Georreferenciación**  
Proceso de asignar coordenadas geográficas (latitud/longitud) a un objeto o ubicación.

**GIN (Generalized Inverted Index)**  
Tipo de índice de PostgreSQL optimizado para búsquedas en campos JSONB y arrays.

**Gunicorn**  
Servidor WSGI para ejecutar aplicaciones Django en producción.

## H

**Hash**  
Función criptográfica que convierte texto (ej. contraseña) en cadena de caracteres fija e irreversible.

**HTMX**  
Librería JavaScript que permite interacciones dinámicas en HTML sin escribir JavaScript explícito.

**Humedad Relativa (HR)**  
Porcentaje de vapor de agua en el aire respecto al máximo que puede contener a esa temperatura.

## I

**Índice (Database Index)**  
Estructura de datos que mejora la velocidad de consultas en una tabla, similar a un índice de libro.

**IoT (Internet of Things)**  
Dispositivos conectados a internet que recopilan y transmiten datos automáticamente (sensores de clima, suelo).

## J

**JSON (JavaScript Object Notation)**  
Formato de texto ligero para intercambio de datos, fácil de leer para humanos y máquinas.

**JSONB**  
Tipo de dato de PostgreSQL para almacenar JSON de forma binaria eficiente, con soporte para consultas e índices.

**JSON Schema**  
Estándar para describir y validar la estructura de datos JSON. Define tipos, rangos, valores permitidos.

**JWT (JSON Web Token)**  
Token de autenticación compacto y auto-contenido para transmitir información de forma segura entre cliente y servidor.

## K

**KPI (Key Performance Indicator)**  
Indicador clave de rendimiento que mide el éxito de una actividad. Ejemplo: rendimiento kg/ha, eficiencia de riego.

## L

**Lote**  
Ver **Field**.

**Logs**  
Registros cronológicos de eventos del sistema para debugging, auditoría y monitoreo.

## M

**Metadata**  
Datos sobre datos. Información adicional que describe características de un recurso (ej. fecha subida, tamaño archivo).

**Migración (Database Migration)**  
Archivo que define cambios en el esquema de base de datos de forma versionada y reversible. Django las gestiona automáticamente.

**Middleware**  
Componente de software que intercepta requests/responses para aplicar lógica transversal (auditoría, autenticación).

## N

**NDRE (Normalized Difference Red Edge)**  
Índice de vegetación sensible a contenido de clorofila y nitrógeno, calculado desde imágenes satelitales/dron.

**NDVI (Normalized Difference Vegetation Index)**  
Índice que mide vigor y salud vegetal basado en reflectancia infrarroja y roja. Rango -1 a 1.

**Nginx**  
Servidor web de alto rendimiento usado como proxy inverso y para servir archivos estáticos.

## O

**ORM (Object-Relational Mapping)**  
Técnica que permite interactuar con base de datos usando objetos en lugar de SQL directo. Django tiene su propio ORM.

**OWASP**  
Organización de seguridad web que publica el "Top 10" de vulnerabilidades más críticas.

## P

**Paginación**  
Técnica de dividir grandes conjuntos de resultados en páginas más pequeñas para mejorar rendimiento y UX.

**Parcela**  
Ver **Field**.

**Payload**  
Datos contenidos en un evento, almacenados en formato JSON según el esquema del EventType.

**pH**  
Medida de acidez o alcalinidad de una solución. Escala 0-14, donde 7 es neutro.

**Poscosecha**  
Operaciones realizadas después de la cosecha: almacenamiento, selección, empaque, transporte.

**PostgreSQL**  
Sistema de gestión de base de datos relacional open-source, robusto y con características avanzadas (JSONB, PostGIS).

**PostGIS**  
Extensión de PostgreSQL para almacenar y consultar datos geoespaciales.

## R

**Rate Limiting**  
Técnica para limitar el número de peticiones que un usuario/sistema puede hacer en un período (ej. 100 req/min).

**RBAC (Role-Based Access Control)**  
Control de acceso basado en roles. Usuarios tienen roles (Admin, Técnico) que determinan permisos.

**Riego**  
Aplicación de agua al cultivo mediante diversos métodos (goteo, microaspersión, gravedad).

**Rendimiento**  
Cantidad de producto cosechado por unidad de área, típicamente kg/ha (kilogramos por hectárea).

## S

**Schema**  
1. Estructura de la base de datos (tablas, relaciones).  
2. JSON Schema: definición de estructura y validación de datos JSON.

**Serializer (DRF)**  
Componente de Django REST Framework que convierte objetos Django a/desde JSON.

**Severidad (de plaga/enfermedad)**  
Grado de daño causado por una plaga o enfermedad, típicamente en escala porcentual o categórica.

**Soft Delete**  
Eliminación lógica (marcar como inactivo) en lugar de eliminación física de registros en BD.

**SQL Injection**  
Vulnerabilidad donde un atacante inyecta código SQL malicioso. Django ORM protege contra esto.

**Station (Estación de Monitoreo)**  
Punto físico donde se instalan sensores para medir variables ambientales (clima, suelo).

## T

**Template**  
Archivo HTML con sintaxis especial de Django para renderizar contenido dinámico.

**Timestamp**  
Fecha y hora precisa de un evento, almacenada con zona horaria (ej. 2025-10-13T08:30:00-06:00).

**Token**  
Cadena de caracteres que identifica y autentica a un usuario/sistema (ej. JWT).

**Trazabilidad**  
Capacidad de rastrear el historial completo de un producto desde origen hasta destino. En este proyecto: todas las actividades realizadas en un lote.

## U

**UUID (Universally Unique Identifier)**  
Identificador único de 128 bits usado para eventos (ej. `a1b2c3d4-e5f6-7890-abcd-ef1234567890`).

**UX (User Experience)**  
Experiencia del usuario al interactuar con el sistema. Incluye usabilidad, diseño, flujos.

## V

**Validación**  
Verificación de que los datos cumplen reglas definidas (tipos, rangos, formato).

**Variable Ambiental**  
Medición de condiciones del entorno que afectan el cultivo (temperatura, humedad, precipitación).

**Variedad**  
Tipo específico de cultivo con características genéticas distintivas. Ejemplo: Limón Persa, Limón Real.

**Versionado**  
Sistema para gestionar cambios en código o esquemas, manteniendo historial. Git para código, versión en EventType para esquemas.

**Vista (View)**  
Componente de Django que procesa una petición HTTP y retorna una respuesta.

## W

**WSGI (Web Server Gateway Interface)**  
Estándar de Python para comunicación entre servidor web y aplicación (ej. Nginx → Gunicorn → Django).

## X

**XSS (Cross-Site Scripting)**  
Vulnerabilidad donde un atacante inyecta JavaScript malicioso. Django templates auto-escapan por defecto.

## Z

**Zona Horaria (Timezone)**  
Región que observa un horario estándar. En este proyecto: America/Mexico_City (UTC-6).

---

**Siguiente**: [Referencias →](./referencias.md)

[← Volver al índice](../README.md)
