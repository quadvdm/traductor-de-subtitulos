# Traductor de Subtítulos SRT

Traductor automático de archivos de subtítulos en formato SRT usando Google Translate con interfaz gráfica moderna.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

### Interfaz Gráfica (recomendado)
```bash
python main.py
```

Simplemente:
1. Haz clic en "Examinar" y selecciona tu archivo .srt
2. Elige el idioma origen (o deja en detección automática)
3. Elige el idioma destino
4. Haz clic en "Traducir Subtítulos"

### Línea de Comandos
```bash
python traductor_srt.py archivo.srt
```

Con idiomas específicos:
```bash
python traductor_srt.py archivo.srt en es
```

## Códigos de idioma

- `en` - Inglés
- `es` - Español
- `fr` - Francés
- `de` - Alemán
- `it` - Italiano
- `pt` - Portugués
- `ja` - Japonés
- `ko` - Coreano
- `auto` - Detección automática

## Características

- ✅ Mantiene el formato SRT original
- ✅ Preserva marcas de tiempo
- ✅ Detección automática del idioma origen
- ✅ Soporte para subtítulos multilínea
- ✅ Manejo de diferentes codificaciones (UTF-8, Latin-1)
- ✅ Progreso en tiempo real

## Ejemplo

Si tienes un archivo `movie.srt` en inglés y quieres traducirlo al español:

```bash
python traductor_srt.py movie.srt
```

Esto creará `movie_traducido.srt` con los subtítulos en español.
