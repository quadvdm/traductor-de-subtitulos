"""
Traductor de subtítulos SRT
Traduce archivos de subtítulos del inglés al español (u otros idiomas)
"""

import re
from deep_translator import GoogleTranslator
import sys
import os


class TraductorSRT:
    def __init__(self, idioma_origen='auto', idioma_destino='es'):
        """
        Inicializa el traductor
        
        Args:
            idioma_origen: Código del idioma origen (default: 'auto' para detección automática)
            idioma_destino: Código del idioma destino (default: 'es' para español)
        """
        self.idioma_origen = idioma_origen
        self.idioma_destino = idioma_destino
        self.traductor = GoogleTranslator(source=idioma_origen, target=idioma_destino)
    
    def parsear_srt(self, contenido):
        """
        Parsea el contenido de un archivo SRT
        
        Returns:
            Lista de diccionarios con la información de cada subtítulo
        """
        # Patrón para dividir los subtítulos
        patron_subtitulo = re.compile(
            r'(\d+)\s*\n'  # Número de secuencia
            r'([\d:,]+ --> [\d:,]+)\s*\n'  # Marcas de tiempo
            r'((?:.*\n)*?)'  # Texto (puede ser multilínea)
            r'(?=\n\d+\s*\n|$)',  # Hasta el siguiente subtítulo o fin de archivo
            re.MULTILINE
        )
        
        subtitulos = []
        for match in patron_subtitulo.finditer(contenido):
            numero = match.group(1)
            tiempo = match.group(2)
            texto = match.group(3).strip()
            
            subtitulos.append({
                'numero': numero,
                'tiempo': tiempo,
                'texto': texto
            })
        
        return subtitulos
    
    def traducir_texto(self, texto):
        """
        Traduce un texto manteniendo etiquetas HTML y líneas vacías
        """
        if not texto.strip():
            return texto
        
        try:
            # Dividir en líneas para traducir cada una
            lineas = texto.split('\n')
            lineas_traducidas = []
            
            for linea in lineas:
                if linea.strip():
                    # Traducir la línea
                    traduccion = self.traductor.translate(linea)
                    lineas_traducidas.append(traduccion)
                else:
                    lineas_traducidas.append('')
            
            return '\n'.join(lineas_traducidas)
        except Exception as e:
            print(f"Error al traducir: {e}")
            return texto
    
    def traducir_archivo(self, archivo_entrada, archivo_salida=None):
        """
        Traduce un archivo SRT completo
        
        Args:
            archivo_entrada: Ruta al archivo SRT original
            archivo_salida: Ruta para guardar el archivo traducido (opcional)
        """
        # Si no se especifica archivo de salida, crear uno con sufijo '_traducido'
        if archivo_salida is None:
            nombre_base = os.path.splitext(archivo_entrada)[0]
            archivo_salida = f"{nombre_base}_traducido.srt"
        
        # Leer el archivo original
        try:
            with open(archivo_entrada, 'r', encoding='utf-8') as f:
                contenido = f.read()
        except UnicodeDecodeError:
            # Intentar con otra codificación común
            with open(archivo_entrada, 'r', encoding='latin-1') as f:
                contenido = f.read()
        
        # Parsear los subtítulos
        print(f"Parseando archivo: {archivo_entrada}")
        subtitulos = self.parsear_srt(contenido)
        print(f"Se encontraron {len(subtitulos)} subtítulos")
        
        # Traducir cada subtítulo
        print(f"Traduciendo de {self.idioma_origen} a {self.idioma_destino}...")
        subtitulos_traducidos = []
        
        for i, sub in enumerate(subtitulos, 1):
            print(f"Traduciendo subtítulo {i}/{len(subtitulos)}", end='\r')
            texto_traducido = self.traducir_texto(sub['texto'])
            subtitulos_traducidos.append({
                'numero': sub['numero'],
                'tiempo': sub['tiempo'],
                'texto': texto_traducido
            })
        
        print(f"\nTraducción completada                    ")
        
        # Escribir el archivo traducido
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            for sub in subtitulos_traducidos:
                f.write(f"{sub['numero']}\n")
                f.write(f"{sub['tiempo']}\n")
                f.write(f"{sub['texto']}\n")
                f.write("\n")
        
        print(f"Archivo guardado en: {archivo_salida}")
        return archivo_salida


def main():
    """
    Función principal para usar desde línea de comandos
    """
    if len(sys.argv) < 2:
        print("Uso: python traductor_srt.py <archivo.srt> [idioma_origen] [idioma_destino]")
        print("Ejemplo: python traductor_srt.py subtitulos.srt en es")
        print("Ejemplo con detección automática: python traductor_srt.py subtitulos.srt auto es")
        print("\nCódigos de idioma comunes:")
        print("  en = inglés, es = español, fr = francés, de = alemán")
        print("  it = italiano, pt = portugués, ja = japonés, ko = coreano")
        print("  auto = detección automática")
        sys.exit(1)
    
    archivo_entrada = sys.argv[1]
    idioma_origen = sys.argv[2] if len(sys.argv) > 2 else 'auto'
    idioma_destino = sys.argv[3] if len(sys.argv) > 3 else 'es'
    
    if not os.path.exists(archivo_entrada):
        print(f"Error: El archivo '{archivo_entrada}' no existe")
        sys.exit(1)
    
    # Crear el traductor y procesar el archivo
    traductor = TraductorSRT(idioma_origen, idioma_destino)
    traductor.traducir_archivo(archivo_entrada)


if __name__ == "__main__":
    main()
