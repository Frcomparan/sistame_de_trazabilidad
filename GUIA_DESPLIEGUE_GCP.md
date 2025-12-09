# Guía de Despliegue en Google Cloud Platform (GCP)

Esta guía detalla el proceso completo para desplegar el Sistema de Trazabilidad en una máquina virtual de Google Cloud Platform.

---

## 1. Creación y Configuración de la Máquina Virtual en GCP

### 1.1 Acceso al Proyecto

Si no tiene un proyecto creado en GCP:

- Acceda a la consola de Google Cloud Platform
- Cree un nuevo proyecto desde el menú superior
- Asigne un nombre descriptivo al proyecto

### 1.2 Navegación a Compute Engine

Existen dos formas de acceder a la creación de instancias:

**Opción A: Mediante el menú lateral**

- Navegue al apartado "Compute Engine"
- Seleccione la sección "Instancias de VM"

**Opción B: Mediante el buscador**

- Utilice el buscador superior
- Busque "Máquina Virtual" o "Virtual Machine"

### 1.3 Creación de la Instancia

Haga clic en el botón "Crear Instancia" y configure los siguientes parámetros:

**Configuración Básica:**

- **Nombre**: Asigne un nombre identificable a la instancia (ejemplo: `trazabilidad-prod`)
- **Región**: Seleccione la región que mejor se adapte a sus necesidades
  - Recomendado: `us-central1` (Iowa)
- **Zona**: Seleccione "Cualquiera" para permitir asignación automática

**Configuración de Hardware:**

- **Tipo de máquina**: Series E2
- **Modelo**: e2-medium
  - 2 CPU virtuales
  - 1 núcleo
  - 4 GB de memoria
- **Modelo de aprovisionamiento**: Estándar

**Configuración de Disco de Arranque:**

- Sistema operativo recomendado: Ubuntu 20.04 LTS o superior
- Tipo de disco: Disco persistente estándar
- Tamaño: Mínimo 10 GB (recomendado 20 GB)

**Configuración de Firewall:**

- Marque las casillas:
  - Permitir tráfico HTTP
  - Permitir tráfico HTTPS

Haga clic en "Crear" y espere a que la máquina virtual se aprovisione. Este proceso puede tomar de 1 a 3 minutos.

### 1.4 Acceso a la Máquina Virtual

Una vez que la instancia esté en estado "En ejecución":

1. Localice el botón "SSH" en la columna "Conectar" de la lista de instancias
2. Haga clic en "SSH" para abrir una terminal en el navegador
3. Alternativamente, puede usar el comando desde su terminal local:
   ```bash
   gcloud compute ssh NOMBRE_INSTANCIA --zone=ZONA
   ```

---

## 2. Instalación de Dependencias

### 2.1 Actualizar el Sistema

Una vez conectado a la VM mediante SSH, ejecute:

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 2.2 Instalar Git

Git es necesario para clonar el repositorio del proyecto:

```bash
sudo apt install git -y
```

Verifique la instalación:

```bash
git --version
```

### 2.3 Instalar Docker

Docker es el motor de contenedores que ejecutará la aplicación:

```bash
sudo apt-get install -y docker.io docker-compose
```

Inicie y habilite el servicio de Docker:

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

Agregue su usuario al grupo docker para ejecutar comandos sin sudo:

```bash
sudo usermod -aG docker $USER
```

**Importante**: Cierre la sesión SSH y vuelva a conectarse para que los cambios de grupo surtan efecto.

### 2.4 Verificar Instalación de Docker

```bash
docker --version
docker-compose --version
```

Debería ver las versiones instaladas de ambas herramientas.

---

## 3. Clonar el Repositorio

Clone el repositorio del proyecto en la máquina virtual:

```bash
cd ~
git clone https://github.com/Frcomparan/sistame_de_trazabilidad.git
cd sistame_de_trazabilidad
```

---

## 4. Configuración de Variables de Entorno

### 4.1 Crear el Archivo de Configuración

Copie el archivo de ejemplo y edítelo:

```bash
cp .env.gcp.example .env
nano .env
```

### 4.2 Configurar Variables Críticas

Modifique las siguientes variables en el archivo `.env`:

**DEBUG**: Debe estar en False para producción

```
DEBUG=False
```

**SECRET_KEY**: Genere una clave secreta única

```bash
# En otra terminal, genere una clave:
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copie el resultado y péguelo en la variable SECRET_KEY.

**ALLOWED_HOSTS**: Configure los hosts permitidos

```
ALLOWED_HOSTS=localhost,127.0.0.1,EXTERNAL_IP
```

Reemplace `EXTERNAL_IP` con la dirección IP externa de su VM (visible en la consola de GCP).

**Database Configuration**: Puede mantener los valores por defecto o personalizarlos

```
POSTGRES_DB=trazabilidad_db
POSTGRES_USER=trazabilidad_user
POSTGRES_PASSWORD=cambie_esta_contraseña_por_una_segura
```

**ThingSpeak Configuration**: Mantenga las credenciales existentes

```
THINGSPEAK_CHANNEL_ID=3142831
THINGSPEAK_API_KEY=FQR4GTLHXXO0I3K2
```

Guarde el archivo (Ctrl + O, Enter, Ctrl + X en nano).

---

## 5. Configuración de Firewall en GCP

Para que la aplicación sea accesible desde Internet, debe configurar las reglas de firewall:

### 5.1 Mediante la Consola de GCP

1. Navegue a "VPC network" > "Firewall"
2. Haga clic en "Crear regla de firewall"
3. Configure:
   - **Nombre**: allow-http-trazabilidad
   - **Dirección del tráfico**: Entrada
   - **Acción en caso de coincidencia**: Permitir
   - **Destinos**: Todas las instancias de la red
   - **Filtro de origen**: Rangos de IPv4
   - **Rangos de IPv4 de origen**: 0.0.0.0/0
   - **Protocolos y puertos**: tcp:80
4. Haga clic en "Crear"

### 5.2 Mediante gcloud CLI (alternativa)

```bash
gcloud compute firewall-rules create allow-http-trazabilidad \
    --allow tcp:80 \
    --source-ranges 0.0.0.0/0 \
    --description="Allow HTTP traffic to port 80"
```

---

## 6. Construcción y Despliegue de Contenedores

### 6.1 Construir las Imágenes

Desde el directorio del proyecto, ejecute:

```bash
docker-compose build
```

Este proceso puede tomar varios minutos la primera vez, ya que descarga las imágenes base y construye la aplicación.

### 6.2 Iniciar los Contenedores

```bash
docker-compose up -d
```

El flag `-d` ejecuta los contenedores en segundo plano (modo detached).

### 6.3 Verificar el Estado de los Contenedores

```bash
docker-compose ps
```

Debería ver dos contenedores en estado "Up":

- `trazabilidad_db` (PostgreSQL)
- `trazabilidad_web` (Django)

---

## 7. Verificación del Despliegue

### 7.1 Revisar los Logs

Monitoree los logs para asegurarse de que no haya errores:

```bash
docker-compose logs -f
```

Presione Ctrl + C para salir del modo de seguimiento.

### 7.2 Verificar desde la VM

Dentro de la VM, verifique que el servidor responde:

```bash
curl http://localhost
```

Debería recibir una respuesta HTML.

### 7.3 Acceso desde el Navegador

Obtenga la dirección IP externa de su VM desde la consola de GCP o ejecutando:

```bash
curl ifconfig.me
```

Abra un navegador y acceda a:

```
http://EXTERNAL_IP/
```

Debería ver la página de inicio de sesión del Sistema de Trazabilidad.

### 7.4 Crear Superusuario

Para acceder al sistema por primera vez, debe crear un usuario administrador:

```bash
docker-compose exec web python manage.py createsuperuser
```

El sistema le solicitará la siguiente información:

1. **Nombre de usuario**: Ingrese el nombre de usuario deseado (por ejemplo: admin)
2. **Email**: Ingrese una dirección de correo electrónico (opcional, puede presionar Enter para omitir)
3. **Contraseña**: Ingrese una contraseña segura
4. **Confirmación de contraseña**: Vuelva a ingresar la contraseña

Una vez creado el superusuario, podrá acceder a:

- Panel de administración: `http://EXTERNAL_IP/admin`
- Sistema de trazabilidad: `http://EXTERNAL_IP/`

---

## 8. Comandos Útiles de Mantenimiento

### Ver logs en tiempo real

```bash
docker-compose logs -f
```

### Ver logs de un servicio específico

```bash
docker-compose logs -f web
docker-compose logs -f db
```

### Reiniciar los servicios

```bash
docker-compose restart
```

### Detener los servicios

```bash
docker-compose down
```

### Detener y eliminar volúmenes (PRECAUCIÓN: elimina datos)

```bash
docker-compose down -v
```

### Crear superusuario (primera vez)

```bash
docker-compose exec web python manage.py createsuperuser
```

Siga las instrucciones en pantalla para ingresar:

- Nombre de usuario
- Email (opcional)
- Contraseña

### Ejecutar comandos Django dentro del contenedor

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```

### Acceder a la shell de Django

```bash
docker-compose exec web python manage.py shell
```

### Acceder a la base de datos PostgreSQL

```bash
docker-compose exec db psql -U trazabilidad_user -d trazabilidad_db
```

---

## 9. Solución de Problemas

### El sitio no es accesible desde el navegador

- Verifique que las reglas de firewall estén configuradas correctamente
- Confirme que los contenedores están en ejecución: `docker-compose ps`
- Revise los logs: `docker-compose logs`
- Verifique que ALLOWED_HOSTS en `.env` incluya la IP externa

### Error "Bad Request (400)"

- Revise la configuración de ALLOWED_HOSTS en el archivo `.env`
- Asegúrese de incluir la IP externa de la VM
- Reinicie los contenedores después de cambiar `.env`: `docker-compose restart`

### La base de datos no se conecta

- Verifique que el contenedor de PostgreSQL esté en ejecución
- Revise los logs del contenedor db: `docker-compose logs db`
- Confirme que las credenciales en `.env` coincidan con la configuración de docker-compose.yml

### Errores de migración de base de datos

```bash
docker-compose exec web python manage.py migrate
```

### Falta el usuario administrador

```bash
docker-compose exec web python manage.py createsuperuser
```

---

## 10. Consideraciones de Seguridad

### Recomendaciones para Producción

1. **HTTPS**: Configure un certificado SSL usando Let's Encrypt
2. **Contraseñas**: Use contraseñas robustas para la base de datos
3. **Backups**: Configure respaldos automáticos de la base de datos
4. **Actualizaciones**: Mantenga el sistema y Docker actualizados
5. **Monitoreo**: Implemente monitoreo de recursos y logs
6. **Firewall**: Restrinja el acceso SSH solo a IPs conocidas


**Última actualización**: Diciembre 2025
