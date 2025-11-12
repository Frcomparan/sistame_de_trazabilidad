# Guía de Uso: Sistema de Eventos

## Introducción

El sistema de eventos permite registrar actividades de trazabilidad agrícola. El sistema incluye 10 tipos de eventos predefinidos, cada uno con campos específicos definidos mediante JSON Schema.

## Primeros Pasos

### 1. Cargar Tipos de Eventos

Para comenzar a usar el sistema, primero debes cargar los tipos de eventos predefinidos:

```powershell
python manage.py loaddata apps/events/fixtures/event_types.json
```

Esto creará los 10 tipos de eventos predefinidos:
1. Aplicación de Riego
2. Aplicación de Fertilizante
3. Aplicación Fitosanitaria
4. Labores de Cultivo
5. Monitoreo de Plagas
6. Brote de Plaga/Enfermedad
7. Condiciones Climáticas
8. Cosecha
9. Almacenamiento Poscosecha
10. Mano de Obra y Costos

### 2. Acceder al Sistema

#### Opción A: Interfaz Web

1. Inicia el servidor de desarrollo:
   ```powershell
   python manage.py runserver
   ```

2. Abre tu navegador en `http://localhost:8000`

3. Inicia sesión con tu usuario

4. En el dashboard, haz clic en "Ver Lista" en la tarjeta de **Eventos**

#### Opción B: API REST

Accede a la documentación interactiva de la API:
```
http://localhost:8000/api/docs/
```

## Crear un Evento (Web)

### Paso 1: Ir al Formulario de Creación

Navega a `/events/create/` o haz clic en el botón "Crear" desde la lista de eventos.

### Paso 2: Completar Información Básica

1. **Tipo de Evento**: Selecciona el tipo de actividad (ej: Riego por Goteo)
2. **Fecha y Hora**: Momento en que ocurrió el evento
3. **Campo**: Selecciona la parcela donde ocurrió
4. **Campaña**: (Opcional) Asocia el evento a una campaña

### Paso 3: Completar Campos del Evento

Cuando selecciones un tipo de evento, el formulario mostrará automáticamente los campos específicos definidos en el esquema del tipo:

**Ejemplo para "Riego por Goteo":**
- Duración (horas) - Campo numérico
- Caudal (L/h) - Campo numérico
- Presión (bar) - Campo numérico
- Fuente de Agua - Lista desplegable

### Paso 4: Agregar Observaciones

En el campo de observaciones puedes agregar notas adicionales:
- Condiciones climáticas
- Personal involucrado
- Resultados observados
- Cualquier otra información relevante

### Paso 5: Registrar el Evento

Haz clic en "Registrar Evento" para guardar.

## Crear un Evento (API)

### Autenticación

Primero obtén un token JWT:

```bash
curl -X POST http://localhost:8000/api/v1/core/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "tu_usuario",
    "password": "tu_contraseña"
  }'
```

Respuesta:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Consultar Tipos de Eventos

```bash
curl http://localhost:8000/api/v1/events/types/ \
  -H "Authorization: Bearer {access_token}"
```

### Crear un Evento de Riego

```bash
curl -X POST http://localhost:8000/api/v1/events/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {access_token}" \
  -d '{
    "event_type": 1,
    "field": 1,
    "campaign": 1,
    "timestamp": "2024-01-15T08:00:00Z",
    "payload": {
      "duracion_horas": 3.5,
      "caudal_l_h": 200,
      "presion_bar": 1.8,
      "fuente_agua": "Pozo"
    },
    "observations": "Riego matutino, condiciones normales"
  }'
```

### Crear un Evento de Fertilización

```bash
curl -X POST http://localhost:8000/api/v1/events/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {access_token}" \
  -d '{
    "event_type": 2,
    "field": 1,
    "timestamp": "2024-01-16T10:00:00Z",
    "payload": {
      "producto": "Nitrofoska 15-15-15",
      "dosis_l_ha": 3.5,
      "concentracion_ppm": 1500,
      "volumen_caldo_l": 500,
      "metodo_aplicacion": "Aspersión"
    },
    "observations": "Aplicación foliar post-floración"
  }'
```

### Crear un Evento de Cosecha

```bash
curl -X POST http://localhost:8000/api/v1/events/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {access_token}" \
  -d '{
    "event_type": 4,
    "field": 1,
    "campaign": 1,
    "timestamp": "2024-06-20T14:00:00Z",
    "payload": {
      "cantidad_kg": 1500.5,
      "numero_cajas": 60,
      "calidad": "Primera",
      "calibre_promedio": "Mediano",
      "destino": "Exportación",
      "equipo_cosecha": "Cuadrilla A"
    },
    "observations": "Cosecha de alta calidad, frutos de buen tamaño"
  }'
```

## Consultar Eventos

### Listar Todos los Eventos (Web)

Navega a `/events/` para ver la lista completa con:
- Filtros por tipo, campo, campaña
- Filtros por rango de fechas
- Paginación automática
- Iconos y colores según el tipo de evento

### Ver Detalle de un Evento (Web)

Haz clic en cualquier evento de la lista para ver:
- Información completa del evento
- Datos del payload formateados según el esquema
- Observaciones
- Metadatos (usuario, fechas)
- Información del campo y campaña

### Listar Eventos (API)

```bash
# Todos los eventos
curl http://localhost:8000/api/v1/events/ \
  -H "Authorization: Bearer {access_token}"

# Filtrar por tipo de evento
curl "http://localhost:8000/api/v1/events/?event_type=1" \
  -H "Authorization: Bearer {access_token}"

# Filtrar por campo
curl "http://localhost:8000/api/v1/events/?field=1" \
  -H "Authorization: Bearer {access_token}"

# Filtrar por rango de fechas
curl "http://localhost:8000/api/v1/events/?date_from=2024-01-01&date_to=2024-12-31" \
  -H "Authorization: Bearer {access_token}"

# Combinar filtros
curl "http://localhost:8000/api/v1/events/?event_type=1&field=1&date_from=2024-01-01" \
  -H "Authorization: Bearer {access_token}"
```

## Crear Tipo de Evento Personalizado

### Desde el Admin

1. Ve a `/admin/events/eventtype/`
2. Haz clic en "Agregar tipo de evento"
3. Completa los campos:
   - **Nombre**: Nombre descriptivo
   - **Descripción**: Descripción detallada
   - **Categoría**: Selecciona una categoría o usa "other"
   - **Icono**: Nombre del icono de Bootstrap Icons (sin el prefijo "bi-")
   - **Color**: Color en hexadecimal (ej: #28a745)
   - **Schema**: JSON Schema que define los campos
   - **Is active**: Marcado

### Ejemplo de Schema Personalizado

Para un evento de "Control de Plagas":

```json
{
  "type": "object",
  "title": "Control de Plagas",
  "required": ["metodo_control", "plaga", "efectividad"],
  "properties": {
    "metodo_control": {
      "type": "string",
      "title": "Método de Control",
      "enum": ["Químico", "Biológico", "Cultural", "Mecánico"],
      "example": "Biológico"
    },
    "plaga": {
      "type": "string",
      "title": "Plaga Controlada",
      "maxLength": 200,
      "example": "Pulgón verde"
    },
    "producto_utilizado": {
      "type": "string",
      "title": "Producto Utilizado",
      "maxLength": 200,
      "example": "Chrysoperla carnea (depredador)"
    },
    "cantidad_aplicada": {
      "type": "number",
      "title": "Cantidad Aplicada",
      "minimum": 0,
      "example": 100
    },
    "unidad": {
      "type": "string",
      "title": "Unidad de Medida",
      "enum": ["ml", "g", "L", "kg", "unidades"],
      "example": "unidades"
    },
    "efectividad": {
      "type": "string",
      "title": "Efectividad Observada",
      "enum": ["Muy baja", "Baja", "Media", "Alta", "Muy alta"],
      "example": "Alta"
    },
    "requiere_seguimiento": {
      "type": "boolean",
      "title": "Requiere Seguimiento",
      "example": true
    }
  }
}
```

## Validación de Datos

El sistema valida automáticamente los datos en dos niveles:

### Validación en el Cliente (JavaScript)

- Campos requeridos
- Tipos de datos básicos
- Rangos numéricos (min/max)
- Longitud de texto (maxLength)

### Validación en el Servidor (Python)

- Validación completa contra JSON Schema
- Tipos de datos estrictos
- Patrones regex (si están definidos)
- Enumeraciones

Si la validación falla, se muestra un mensaje de error específico.

## Errores Comunes

### Error: "payload must be a valid object"

**Causa**: El payload no es un objeto JSON válido.

**Solución**: Asegúrate de enviar un objeto JSON:
```json
{
  "payload": {
    "campo1": "valor1",
    "campo2": 123
  }
}
```

### Error: "'campo_x' is a required property"

**Causa**: Falta un campo obligatorio definido en el schema.

**Solución**: Verifica el schema del tipo de evento y asegúrate de incluir todos los campos en `required`.

### Error: "Additional properties are not allowed"

**Causa**: Se enviaron campos que no están definidos en el schema.

**Solución**: Solo envía campos que estén en `properties` del schema.

### Error: "Invalid value for field"

**Causa**: El valor no cumple con las restricciones (enum, min/max, etc.)

**Solución**: Verifica las restricciones del campo en el schema.

## Consejos de Uso

### 1. Organización de Eventos

- Usa **campos** para organizar por ubicación física
- Usa **campañas** para organizar por ciclo productivo
- Usa **tipos de eventos** para categorizar actividades

### 2. Observaciones Efectivas

Incluye información que no se captura en los campos estructurados:
- Condiciones climáticas especiales
- Personal involucrado
- Problemas encontrados
- Resultados inesperados
- Fotos tomadas (menciona los nombres de archivo)

### 3. Consistencia en los Datos

- Usa los mismos nombres de productos
- Mantén las unidades de medida consistentes
- Registra eventos lo más pronto posible después de ocurridos

### 4. Aprovecha los Filtros

- Filtra por tipo para análisis específicos
- Usa rangos de fechas para reportes periódicos
- Combina filtros para análisis detallados

## Próximas Funcionalidades

El sistema continuará evolucionando con:
- Adjuntar fotos a los eventos
- Editar eventos existentes
- Exportar a Excel/CSV
- Gráficos y estadísticas
- Notificaciones automáticas
- Integración con dispositivos IoT

## Soporte

Para más información, consulta:
- Documentación API: `/api/docs/`
- README del módulo: `apps/events/README.md`
- Documentación general: `docs/`
