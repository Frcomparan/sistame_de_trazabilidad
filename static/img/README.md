# Estructura de Imágenes del Proyecto

## 📁 Organización de Directorios

```
static/img/
├── logos/           # Logos originales del sistema
├── favicons/        # Iconos de favicon en diferentes tamaños
├── og/              # Imágenes para Open Graph (redes sociales)
└── README.md        # Este archivo
```

## 🎨 Logos Principales

### Logo Completo
**Archivo:** `logos/logo-full.png` (logo con texto "Green Flowers")
- **Uso:** Navbar, headers, documentos impresos
- **Formatos recomendados:** PNG de alta resolución, SVG vectorial

### Logo Corto (Icono)
**Archivo:** `logos/logo-icon.png` (solo el limón con hojas)
- **Uso:** Favicon, íconos pequeños, apps móviles
- **Formatos recomendados:** PNG transparente, SVG vectorial

## 🔖 Favicons

Los favicons se generan a partir del logo corto y se almacenan en `favicons/`:

### Archivos Requeridos
- `favicon.ico` - 16x16, 32x32, 48x48 (formato ICO multipágina)
- `favicon-16x16.png` - Para navegadores modernos
- `favicon-32x32.png` - Para navegadores modernos
- `apple-touch-icon.png` - 180x180 (iOS/Safari)
- `android-chrome-192x192.png` - Android/Chrome
- `android-chrome-512x512.png` - Android/Chrome alta resolución

### Método 1: Real Favicon Generator (Recomendado)

1. Ve a https://realfavicongenerator.net/
2. Sube `logos/logo-icon.png` o SVG
3. Configura las opciones según necesites
4. Descarga el paquete completo
5. Extrae los archivos en `static/img/favicons/`

### Método 2: ImageMagick (Línea de comandos)

```bash
# Instalar ImageMagick si no lo tienes
# Windows: choco install imagemagick
# Mac: brew install imagemagick
# Linux: apt-get install imagemagick

# Navegar a la carpeta de logos
cd static/img/logos

# Generar diferentes tamaños
convert logo-icon.png -resize 16x16 ../favicons/favicon-16x16.png
convert logo-icon.png -resize 32x32 ../favicons/favicon-32x32.png
convert logo-icon.png -resize 180x180 ../favicons/apple-touch-icon.png
convert logo-icon.png -resize 192x192 ../favicons/android-chrome-192x192.png
convert logo-icon.png -resize 512x512 ../favicons/android-chrome-512x512.png

# Generar favicon.ico multipágina
convert logo-icon.png -define icon:auto-resize=16,32,48 ../favicons/favicon.ico
```

### Método 3: Python + Pillow

```python
from PIL import Image

sizes = {
    'favicon-16x16.png': (16, 16),
    'favicon-32x32.png': (32, 32),
    'apple-touch-icon.png': (180, 180),
    'android-chrome-192x192.png': (192, 192),
    'android-chrome-512x512.png': (512, 512),
}

img = Image.open('static/img/logos/logo-icon.png')
for filename, size in sizes.items():
    resized = img.resize(size, Image.LANCZOS)
    resized.save(f'static/img/favicons/{filename}')
```

## 🌐 Open Graph (Redes Sociales)

Las imágenes Open Graph se almacenan en `og/` y deben usar el logo completo:

### Archivos Requeridos
- `og-image.png` - 1200x630 (Facebook, LinkedIn, WhatsApp)
- `og-image-square.png` - 512x512 (Twitter, otras plataformas)

### Especificaciones Técnicas
- **Formato:** PNG o JPG (PNG preferido)
- **Tamaño estándar:** 1200x630 px (ratio 1.91:1)
- **Tamaño cuadrado:** 512x512 px
- **Peso máximo:** < 1 MB recomendado
- **Contenido:** Logo completo centrado con fondo atractivo

### Método 1: Canva (Recomendado para no diseñadores)

1. Ve a https://www.canva.com/
2. Crea diseño personalizado 1200x630 px
3. Sube `logos/logo-full.png`
4. Agrega fondo verde (#e8f5e9) o gradiente
5. Agrega texto descriptivo: "Sistema de Trazabilidad Agrícola"
6. Descarga como PNG
7. Guarda en `static/img/og/og-image.png`

Para versión cuadrada (512x512), repite con el logo-icon.png

### Método 2: ImageMagick

```bash
# Crear imagen OG con fondo verde
convert -size 1200x630 xc:"#e8f5e9" \
  \( logos/logo-full.png -resize 800x \) \
  -gravity center -composite \
  og/og-image.png

# Versión cuadrada
convert -size 512x512 xc:"#e8f5e9" \
  \( logos/logo-icon.png -resize 400x \) \
  -gravity center -composite \
  og/og-image-square.png
```

### Método 3: Photoshop / GIMP

1. Nuevo archivo 1200x630 px
2. Fondo verde (#e8f5e9) o gradiente
3. Importar `logos/logo-full.png` centrado
4. Agregar texto si deseas
5. Exportar como PNG optimizado
6. Guardar en `og/og-image.png`

## 📋 Checklist de Configuración

### 1. Preparar archivos del logo
- [ ] Guarda los logos originales del usuario en `static/img/logos/`
  - [ ] `logo-full.png` - Logo completo con texto
  - [ ] `logo-icon.png` - Solo el icono (limón)

### 2. Generar favicons
Usa uno de los métodos anteriores para crear en `static/img/favicons/`:
- [ ] `favicon.ico`
- [ ] `favicon-16x16.png`
- [ ] `favicon-32x32.png`
- [ ] `apple-touch-icon.png`
- [ ] `android-chrome-192x192.png`
- [ ] `android-chrome-512x512.png`

### 3. Crear imágenes Open Graph
En `static/img/og/`:
- [ ] `og-image.png` (1200x630)
- [ ] `og-image-square.png` (512x512) - opcional

### 4. Actualizar archivos de configuración
- [ ] `templates/base.html` - Actualizar rutas de favicon y OG
- [ ] `static/manifest.json` - Actualizar iconos PWA

### 5. Recolectar estáticos y probar

```bash
# Con Docker
docker-compose exec web python manage.py collectstatic --noinput
docker-compose restart web

# Sin Docker
python manage.py collectstatic --noinput
```

Luego verifica en:
- Navegador: Pestaña del navegador debe mostrar favicon
- Facebook Debugger: https://developers.facebook.com/tools/debug/
- Twitter Validator: https://cards-dev.twitter.com/validator

## 🔗 Herramientas Útiles

- **Favicon Generator:** https://realfavicongenerator.net/
- **Open Graph Debugger:** https://developers.facebook.com/tools/debug/
- **Twitter Card Validator:** https://cards-dev.twitter.com/validator
- **LinkedIn Inspector:** https://www.linkedin.com/post-inspector/
- **Canva (diseño):** https://www.canva.com/
- **TinyPNG (optimización):** https://tinypng.com/

## 🎨 Paleta de Colores del Sistema

Para mantener consistencia visual:
- **Verde Principal:** `#28a745` (Bootstrap success)
- **Verde Claro:** `#e8f5e9` (fondos suaves)
- **Verde Oscuro:** `#2c5f2d` (textos/acentos)
- **Amarillo Limón:** `#d4ed31` (opcional, acentos)
- **Blanco:** `#ffffff`
- **Gris Texto:** `#6c757d`

## 📝 Notas Importantes

- **SVG vs PNG:** Usa SVG cuando sea posible (escalable), PNG para tamaños fijos
- **Transparencia:** Los logos deben tener fondo transparente
- **OG con fondo:** Las imágenes Open Graph necesitan fondo sólido/gradiente
- **Optimización:** Comprime las imágenes con TinyPNG antes de subirlas
- **Testing:** Prueba en diferentes dispositivos y redes sociales
- **Caché:** Si actualizas imágenes, limpia caché del navegador (Ctrl+Shift+R)

## 🚀 Próximos Pasos

Después de configurar las imágenes:
1. Actualiza las referencias en `templates/base.html`
2. Actualiza `static/manifest.json` para PWA
3. Ejecuta `collectstatic`
4. Valida con las herramientas de debugging de redes sociales
5. Prueba compartiendo un link del sistema en WhatsApp, Facebook, Twitter

Las imágenes Open Graph se almacenan en `og/` y deben usar el logo completo:

### Archivos Requeridos

### Favicons
- `favicon.svg` - Icono vectorial principal ✅ (ya existe)
- `favicon-16x16.png` - 16x16 píxeles
- `favicon-32x32.png` - 32x32 píxeles
- `apple-touch-icon.png` - 180x180 píxeles
- `favicon.ico` - (opcional) para navegadores antiguos

### OpenGraph / Redes Sociales
- `og-image.svg` - Imagen vectorial para OpenGraph ✅ (ya existe)
- `og-image.png` - 512x512 píxeles (recomendado para compartir en redes)

## Detalles de og-image.png

La imagen de OpenGraph (`og-image.png`) se usa cuando:
- Se comparte un enlace del sistema en WhatsApp, Slack, Teams
- Se previsualiza el enlace en redes sociales
- Se guarda el enlace en marcadores sociales

**Características:**
- Tamaño: 512x512 píxeles (proporción 1:1, ideal para Twitter summary card)
- Formato: PNG con fondo (no transparente)
- Fondo verde (#28a745) del tema
- Limón central con texto "Trazabilidad"
- Elementos decorativos

**Alternativa 1200x630 (opcional):**
Para preview más grande en Facebook/LinkedIn, puedes crear una versión 1200x630:
```bash
convert -background none og-image.svg -resize 1200x630 og-image-large.png
```

## Nota

Los archivos PNG se generan bajo demanda. Si no existen, el navegador usará el SVG como fallback.

**Para producción, se recomienda generar todos los PNG** para máxima compatibilidad.
