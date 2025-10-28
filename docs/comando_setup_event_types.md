# Comando: setup_event_types

## Descripción

Comando de Django para crear o actualizar los 10 tipos de eventos base del sistema de trazabilidad agrícola. Este comando garantiza que todos los tipos de eventos necesarios estén disponibles en la base de datos.

## Tipos de Eventos Creados

1. **Aplicación de Riego** - Registro de aplicaciones de riego con diferentes métodos
2. **Aplicación de Fertilizante** - Fertilización al suelo o foliar
3. **Aplicación Fitosanitaria** - Aplicación de fungicidas, insecticidas, herbicidas
4. **Labores de Cultivo** - Actividades de mantenimiento (poda, deshierbe, etc.)
5. **Monitoreo de Plagas** - Inspección y monitoreo preventivo
6. **Brote de Plaga/Enfermedad** - Registro de brotes severos
7. **Condiciones Climáticas** - Registro de variables meteorológicas
8. **Cosecha** - Actividades de recolección y clasificación
9. **Almacenamiento Poscosecha** - Control de almacenamiento del producto
10. **Mano de Obra y Costos** - Registro de recursos humanos y costos

## Uso

### Crear tipos de eventos (primera vez)

```bash
# En desarrollo con Docker
docker-compose exec web python manage.py setup_event_types

# Sin Docker (con virtualenv activado)
python manage.py setup_event_types
```

### Actualizar tipos de eventos existentes

Si ya existen los tipos de eventos y quieres actualizarlos con nuevos datos:

```bash
docker-compose exec web python manage.py setup_event_types --update
```

## Comportamiento

### Sin la opción `--update`

- **Crea** tipos de eventos que no existen
- **Omite** tipos de eventos que ya existen (no los modifica)
- Muestra un resumen al final con los tipos creados, actualizados y omitidos

### Con la opción `--update`

- **Crea** tipos de eventos que no existen
- **Actualiza** tipos de eventos existentes con los nuevos datos del comando
- **Preserva** el ID de los tipos existentes
- Útil para actualizar esquemas JSON o corregir descripciones

## Salida del Comando

```
✓ Creado: Aplicación de Riego
✓ Creado: Aplicación de Fertilizante
✓ Creado: Aplicación Fitosanitaria
...

============================================================
RESUMEN DE LA OPERACIÓN
============================================================
Tipos de eventos creados:      10
Tipos de eventos actualizados: 0
Tipos de eventos omitidos:     0
============================================================

✓ Sistema configurado correctamente con 10 tipos de eventos.
```

## Verificación

Para verificar que los tipos de eventos se crearon correctamente:

```bash
# Contar tipos de eventos
docker-compose exec web python manage.py shell -c "from apps.events.models import EventType; print(EventType.objects.count())"

# Listar todos los tipos de eventos
docker-compose exec web python manage.py shell -c "from apps.events.models import EventType; [print(f'{et.name} ({et.category})') for et in EventType.objects.all()]"

# Ver un tipo específico con su schema
docker-compose exec web python manage.py shell -c "from apps.events.models import EventType; import json; et = EventType.objects.get(name='Aplicación de Riego'); print(json.dumps(et.schema, indent=2))"
```

## Estructura de cada Tipo de Evento

Cada tipo de evento incluye:

- **name**: Nombre descriptivo
- **description**: Descripción detallada del evento
- **category**: Categoría (irrigation, fertilization, phytosanitary, etc.)
- **icon**: Icono de Bootstrap Icons (sin prefijo "bi-")
- **color**: Color hexadecimal para la UI
- **is_active**: Siempre `True` al crearse
- **schema**: JSON Schema completo con:
  - Campos requeridos (`required`)
  - Propiedades con tipos de datos
  - Validaciones (min, max, enum, etc.)
  - Títulos y descripciones
  - Ejemplos de valores

## Ejemplo de Schema

```json
{
  "type": "object",
  "title": "Datos de Aplicación de Riego",
  "required": ["metodo", "duracion_minutos", "fuente_agua"],
  "properties": {
    "metodo": {
      "type": "string",
      "title": "Método de Riego",
      "enum": ["Aspersión", "Goteo", "Surco", "Pivote", "Manual"],
      "example": "Goteo"
    },
    "duracion_minutos": {
      "type": "integer",
      "title": "Duración (minutos)",
      "minimum": 1,
      "example": 120
    }
  }
}
```

## Cuándo Usar Este Comando

- **Instalación inicial** del sistema
- **Después de un reset de base de datos**
- **Actualización de esquemas** (con `--update`)
- **Recuperación de datos** si se eliminaron tipos de eventos
- **Desarrollo/Testing** para tener datos consistentes

## Seguridad

- El comando usa **transacciones atómicas** para garantizar la integridad de los datos
- Si ocurre un error, todos los cambios se revierten automáticamente
- No elimina tipos de eventos existentes
- Preserva eventos ya registrados en el sistema

## Relación con Otros Componentes

Este comando es **independiente** de:
- Migraciones de Django (no requiere migración)
- Datos de usuarios
- Eventos ya registrados
- Campos y campañas existentes

## Notas Importantes

1. **No es una migración**: Este comando se ejecuta manualmente cuando sea necesario
2. **Idempotente con --update**: Puedes ejecutarlo múltiples veces sin problemas
3. **Preserva eventos**: Los eventos ya creados mantienen su relación con los tipos
4. **Personalizable**: Puedes modificar los schemas directamente en el admin después
5. **Basado en especificación**: Los eventos siguen la especificación del documento "Sistema IoT Monitoreo de Variables"

## Personalización Post-Creación

Después de crear los tipos base, puedes:

1. Ir al admin: `/admin/events/eventtype/`
2. Modificar cualquier tipo de evento:
   - Cambiar iconos o colores
   - Ajustar schemas JSON
   - Agregar o quitar campos
   - Desactivar tipos no utilizados
3. Crear nuevos tipos de eventos personalizados

## Solución de Problemas

### Error: "No module named 'django'"

**Causa**: El entorno virtual no está activado o Django no está instalado.

**Solución**: 
```bash
# Con Docker
docker-compose exec web python manage.py setup_event_types

# Sin Docker
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
python manage.py setup_event_types
```

### Error: "Table 'events_eventtype' doesn't exist"

**Causa**: Las migraciones no se han ejecutado.

**Solución**:
```bash
docker-compose exec web python manage.py migrate
```

### Tipos de eventos no aparecen en el formulario

**Causa**: El campo `is_active` está en `False`.

**Solución**: Verificar en el admin que `is_active=True`.

## Mantenimiento

Para mantener los tipos de eventos actualizados:

1. **Documentar cambios**: Si modificas schemas, documenta los cambios
2. **Versionado**: Considera llevar un control de versiones de los schemas
3. **Backup**: Antes de actualizar masivamente con `--update`, haz backup
4. **Testing**: Prueba los nuevos schemas antes de aplicarlos en producción

## Código Fuente

El comando está ubicado en:
```
apps/events/management/commands/setup_event_types.py
```

Puedes modificarlo para:
- Agregar nuevos tipos de eventos
- Cambiar schemas existentes
- Ajustar categorías o colores
- Personalizar para tu caso de uso específico
