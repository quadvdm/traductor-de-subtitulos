"""
Traductor de subtítulos SRT con interfaz gráfica
Traduce archivos de subtítulos del inglés al español (u otros idiomas)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import re
from deep_translator import GoogleTranslator
import os
import time


class TraductorSRT:
    def __init__(self, idioma_origen='auto', idioma_destino='es', callback_progreso=None):
        self.idioma_origen = idioma_origen
        self.idioma_destino = idioma_destino
        self.traductor = GoogleTranslator(source=idioma_origen, target=idioma_destino)
        self.callback_progreso = callback_progreso
    
    def parsear_srt(self, contenido):
        print(f"Parseando SRT, tamaño del contenido: {len(contenido)} caracteres")  # Debug
        patron_subtitulo = re.compile(
            r'(\d+)\s*\n'
            r'([\d:,]+ --> [\d:,]+)\s*\n'
            r'((?:.*\n)*?)'
            r'(?=\n\d+\s*\n|$)',
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
        
        print(f"Subtítulos parseados: {len(subtitulos)}")  # Debug
        return subtitulos
    
    def traducir_texto(self, texto):
        if not texto.strip():
            return texto
        
        try:
            print(f"Traduciendo texto: {texto[:50]}...")  # Debug
            
            # Traducir todo el texto de una vez es mucho más rápido
            # que traducir línea por línea
            try:
                traduccion = self.traductor.translate(texto)
                print(f"Traducción completada")  # Debug
                time.sleep(0.05)  # Delay reducido para evitar rate limiting
                return traduccion
            except Exception as e:
                print(f"Error en traducción completa, intentando línea por línea: {e}")
                # Fallback: traducir línea por línea si falla
                lineas = texto.split('\n')
                lineas_traducidas = []
                
                for i, linea in enumerate(lineas, 1):
                    if linea.strip():
                        try:
                            print(f"Traduciendo línea {i}: {linea[:30]}...")  # Debug
                            traduccion = self.traductor.translate(linea)
                            lineas_traducidas.append(traduccion)
                            time.sleep(0.05)  # Delay reducido
                        except Exception as e:
                            print(f"Error traduciendo línea: {e}")
                            lineas_traducidas.append(linea)  # Mantener original si falla
                    else:
                        lineas_traducidas.append('')
                
                resultado = '\n'.join(lineas_traducidas)
                return resultado
        except Exception as e:
            print(f"Error en traducir_texto: {e}")
            import traceback
            traceback.print_exc()
            return texto
    
    def traducir_archivo(self, archivo_entrada, archivo_salida=None):
        print(f"traducir_archivo: inicio - {archivo_entrada}")  # Debug
        if archivo_salida is None:
            nombre_base = os.path.splitext(archivo_entrada)[0]
            archivo_salida = f"{nombre_base}_traducido.srt"
        
        print(f"Archivo de salida: {archivo_salida}")  # Debug
        
        try:
            with open(archivo_entrada, 'r', encoding='utf-8') as f:
                contenido = f.read()
            print("Archivo leído con UTF-8")  # Debug
        except UnicodeDecodeError:
            print("Error UTF-8, intentando latin-1")  # Debug
            with open(archivo_entrada, 'r', encoding='latin-1') as f:
                contenido = f.read()
        
        print("Parseando subtítulos...")  # Debug
        subtitulos = self.parsear_srt(contenido)
        total = len(subtitulos)
        print(f"Total de subtítulos a traducir: {total}")  # Debug
        
        if self.callback_progreso:
            print("Llamando callback_progreso inicial")  # Debug
            self.callback_progreso(0, total, "Iniciando...")
        
        subtitulos_traducidos = []
        batch_size = 3  # Procesar 3 subtítulos antes de actualizar progreso
        
        for i, sub in enumerate(subtitulos, 1):
            print(f"\n--- Subtítulo {i}/{total} ---")  # Debug
            print(f"Texto original: {sub['texto']}")  # Debug
            texto_traducido = self.traducir_texto(sub['texto'])
            subtitulos_traducidos.append({
                'numero': sub['numero'],
                'tiempo': sub['tiempo'],
                'texto': texto_traducido
            })
            
            # Actualizar progreso cada batch_size subtítulos o al final
            if self.callback_progreso and (i % batch_size == 0 or i == total):
                print(f"Llamando callback_progreso: {i}/{total}")  # Debug
                self.callback_progreso(i, total, f"Traduciendo {i}/{total}")
        
        print(f"Escribiendo archivo de salida: {archivo_salida}")  # Debug
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            for sub in subtitulos_traducidos:
                f.write(f"{sub['numero']}\n")
                f.write(f"{sub['tiempo']}\n")
                f.write(f"{sub['texto']}\n")
                f.write("\n")
        
        print(f"Archivo traducido guardado exitosamente")  # Debug
        return archivo_salida


class AplicacionTraductor:
    def __init__(self, root):
        self.root = root
        self.root.title("Traductor de Subtítulos SRT")
        self.root.geometry("700x650")
        self.root.resizable(False, False)
        
        # Configurar estilo moderno
        self.configurar_estilo()
        
        # Variables
        self.archivos_seleccionados = []  # Lista de archivos
        self.idioma_origen = tk.StringVar(value="auto")
        self.idioma_destino = tk.StringVar(value="es")
        self.traduciendo = False
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Centrar ventana
        self.centrar_ventana()
    
    def configurar_estilo(self):
        # Colores modernos
        self.bg_color = "#f5f6fa"
        self.card_color = "#ffffff"
        self.primary_color = "#4834df"
        self.secondary_color = "#686de0"
        self.success_color = "#26de81"
        self.text_color = "#2f3542"
        self.text_light = "#747d8c"
        
        self.root.configure(bg=self.bg_color)
        
        # Estilo para widgets
        style = ttk.Style()
        style.theme_use('clam')
        
        # Botones
        style.configure("Primary.TButton",
                       background=self.primary_color,
                       foreground="white",
                       borderwidth=0,
                       focuscolor='none',
                       padding=10,
                       font=('Segoe UI', 9, 'bold'))
        
        style.map("Primary.TButton",
                 background=[('active', self.secondary_color)])
        
        # Combobox
        style.configure("TCombobox",
                       fieldbackground="white",
                       background="white",
                       padding=8)
        
        # Progressbar
        style.configure("TProgressbar",
                       background=self.primary_color,
                       troughcolor="#e1e8ed",
                       borderwidth=0,
                       thickness=8)
    
    def crear_interfaz(self):
        # Título
        titulo_frame = tk.Frame(self.root, bg=self.bg_color)
        titulo_frame.pack(pady=(30, 10))
        
        titulo = tk.Label(titulo_frame,
                         text="🎬 Traductor de Subtítulos",
                         font=('Segoe UI', 24, 'bold'),
                         bg=self.bg_color,
                         fg=self.text_color)
        titulo.pack()
        
        subtitulo = tk.Label(titulo_frame,
                            text="Traduce archivos SRT de forma rápida y sencilla",
                            font=('Segoe UI', 10),
                            bg=self.bg_color,
                            fg=self.text_light)
        subtitulo.pack()
        
        # Card principal
        card = tk.Frame(self.root, bg=self.card_color, relief=tk.FLAT)
        card.pack(padx=30, pady=20, fill=tk.BOTH, expand=True)
        
        # Sombra simulada
        card.configure(highlightbackground="#d2dae2", highlightthickness=1)
        
        # Contenido del card
        contenido = tk.Frame(card, bg=self.card_color)
        contenido.pack(padx=30, pady=30, fill=tk.BOTH, expand=True)
        
        # Selección de archivos
        archivo_label = tk.Label(contenido,
                                text="Archivos SRT",
                                font=('Segoe UI', 11, 'bold'),
                                bg=self.card_color,
                                fg=self.text_color)
        archivo_label.pack(anchor='w', pady=(0, 8))
        
        archivo_frame = tk.Frame(contenido, bg=self.card_color)
        archivo_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Frame para lista de archivos con scroll
        lista_frame = tk.Frame(archivo_frame, bg="#f8f9fa", relief=tk.FLAT)
        lista_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(lista_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.lista_archivos = tk.Listbox(lista_frame,
                                         font=('Segoe UI', 9),
                                         relief=tk.FLAT,
                                         bg="#f8f9fa",
                                         fg=self.text_color,
                                         height=4,
                                         yscrollcommand=scrollbar.set)
        self.lista_archivos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.lista_archivos.yview)
        
        # Frame de botones
        botones_frame = tk.Frame(archivo_frame, bg=self.card_color)
        botones_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        btn_agregar = ttk.Button(botones_frame,
                                text="Agregar",
                                command=self.seleccionar_archivos,
                                style="Primary.TButton")
        btn_agregar.pack(pady=(0, 5))
        
        btn_limpiar = ttk.Button(botones_frame,
                                text="Limpiar",
                                command=self.limpiar_archivos,
                                style="Primary.TButton")
        btn_limpiar.pack()
        
        # Idiomas
        idiomas_frame = tk.Frame(contenido, bg=self.card_color)
        idiomas_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Idioma origen
        origen_frame = tk.Frame(idiomas_frame, bg=self.card_color)
        origen_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        origen_label = tk.Label(origen_frame,
                               text="Idioma Origen",
                               font=('Segoe UI', 11, 'bold'),
                               bg=self.card_color,
                               fg=self.text_color)
        origen_label.pack(anchor='w', pady=(0, 8))
        
        idiomas_origen = [
            ("Detección automática", "auto"),
            ("Inglés", "en"),
            ("Español", "es"),
            ("Francés", "fr"),
            ("Alemán", "de"),
            ("Italiano", "it"),
            ("Portugués", "pt"),
            ("Japonés", "ja"),
            ("Coreano", "ko")
        ]
        
        self.combo_origen = ttk.Combobox(origen_frame,
                                        textvariable=self.idioma_origen,
                                        values=[nombre for nombre, _ in idiomas_origen],
                                        state='readonly',
                                        font=('Segoe UI', 10))
        self.combo_origen.pack(fill=tk.X, ipady=8)
        self.combo_origen.set("Detección automática")
        
        # Idioma destino
        destino_frame = tk.Frame(idiomas_frame, bg=self.card_color)
        destino_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        destino_label = tk.Label(destino_frame,
                                text="Idioma Destino",
                                font=('Segoe UI', 11, 'bold'),
                                bg=self.card_color,
                                fg=self.text_color)
        destino_label.pack(anchor='w', pady=(0, 8))
        
        idiomas_destino = [
            ("Español", "es"),
            ("Inglés", "en"),
            ("Francés", "fr"),
            ("Alemán", "de"),
            ("Italiano", "it"),
            ("Portugués", "pt"),
            ("Japonés", "ja"),
            ("Coreano", "ko")
        ]
        
        self.combo_destino = ttk.Combobox(destino_frame,
                                         textvariable=self.idioma_destino,
                                         values=[nombre for nombre, _ in idiomas_destino],
                                         state='readonly',
                                         font=('Segoe UI', 10))
        self.combo_destino.pack(fill=tk.X, ipady=8)
        self.combo_destino.set("Español")
        
        # Mapa de idiomas
        self.mapa_idiomas = dict(idiomas_origen + idiomas_destino)
        
        # Progreso - Sección mejorada con altura más grande
        self.progreso_frame = tk.Frame(contenido, bg=self.card_color, height=100)
        self.progreso_frame.pack(fill=tk.X, pady=(10, 10))
        self.progreso_frame.pack_propagate(False)  # Mantener altura fija
        
        # Etiqueta de estado del archivo actual
        self.progreso_archivo_label = tk.Label(self.progreso_frame,
                                              text="Esperando...",
                                              font=('Segoe UI', 10, 'bold'),
                                              bg=self.card_color,
                                              fg=self.text_color,
                                              anchor='w')
        self.progreso_archivo_label.pack(fill=tk.X, pady=(8, 5))
        
        # Etiqueta de progreso detallado
        self.progreso_label = tk.Label(self.progreso_frame,
                                       text="Listo para traducir",
                                       font=('Segoe UI', 9),
                                       bg=self.card_color,
                                       fg=self.text_light,
                                       anchor='w')
        self.progreso_label.pack(fill=tk.X, pady=(0, 8))
        
        # Barra de progreso más grande y visible
        self.barra_progreso = ttk.Progressbar(self.progreso_frame,
                                             mode='determinate',
                                             length=400)
        self.barra_progreso.pack(fill=tk.X, pady=(0, 8), ipady=8)
        
        # Etiqueta de porcentaje
        self.porcentaje_label = tk.Label(self.progreso_frame,
                                         text="0%",
                                         font=('Segoe UI', 11, 'bold'),
                                         bg=self.card_color,
                                         fg=self.primary_color,
                                         anchor='center')
        self.porcentaje_label.pack()
        
        # Mostrar siempre el frame de progreso
        # self.progreso_frame.pack_forget()  # No ocultar
        
        # Botón traducir - con más espacio
        self.btn_traducir = ttk.Button(contenido,
                                      text="⬇ Traducir Subtítulos ⬇",
                                      command=self.iniciar_traduccion,
                                      style="Primary.TButton")
        self.btn_traducir.pack(pady=(15, 10))
    
    def centrar_ventana(self):
        self.root.update_idletasks()
        ancho = self.root.winfo_width()
        alto = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto // 2)
        self.root.geometry(f'{ancho}x{alto}+{x}+{y}')
    
    def seleccionar_archivos(self):
        archivos = filedialog.askopenfilenames(
            title="Seleccionar archivos SRT",
            filetypes=[("Archivos SRT", "*.srt"), ("Todos los archivos", "*.*")]
        )
        for archivo in archivos:
            if archivo not in self.archivos_seleccionados:
                self.archivos_seleccionados.append(archivo)
                # Mostrar solo el nombre del archivo en la lista
                nombre_archivo = os.path.basename(archivo)
                self.lista_archivos.insert(tk.END, nombre_archivo)
    
    def limpiar_archivos(self):
        self.archivos_seleccionados.clear()
        self.lista_archivos.delete(0, tk.END)
    
    def obtener_codigo_idioma(self, nombre):
        return self.mapa_idiomas.get(nombre, nombre)
    
    def actualizar_progreso(self, actual, total, mensaje):
        porcentaje = (actual / total) * 100 if total > 0 else 0
        self.barra_progreso['value'] = porcentaje
        self.progreso_label.config(text=mensaje)
        self.root.update_idletasks()
    
    def iniciar_traduccion(self):
        if not self.archivos_seleccionados:
            messagebox.showwarning("Advertencia", "Por favor selecciona al menos un archivo SRT")
            return
        
        # Verificar que todos los archivos existan
        for archivo in self.archivos_seleccionados:
            if not os.path.exists(archivo):
                messagebox.showerror("Error", f"El archivo no existe: {os.path.basename(archivo)}")
                return
        
        if self.traduciendo:
            return
        
        print("Iniciando traducción...")  # Debug
        self.traduciendo = True
        self.btn_traducir.config(state='disabled', text="Traduciendo...")
        self.barra_progreso['value'] = 0
        self.porcentaje_label.config(text="0%")
        self.progreso_archivo_label.config(text="Iniciando traducción...")
        self.progreso_label.config(text="Preparando archivos...")
        self.root.update()  # Forzar actualización inmediata
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=self.traducir)
        thread.daemon = True
        thread.start()
    
    def traducir(self):
        try:
            print("Thread de traducción iniciado")  # Debug
            idioma_orig = self.obtener_codigo_idioma(self.combo_origen.get())
            idioma_dest = self.obtener_codigo_idioma(self.combo_destino.get())
            print(f"Idiomas: {idioma_orig} -> {idioma_dest}")  # Debug
            
            total_archivos = len(self.archivos_seleccionados)
            archivos_traducidos = []
            
            for idx, archivo_entrada in enumerate(self.archivos_seleccionados, 1):
                try:
                    print(f"Procesando archivo {idx}/{total_archivos}: {os.path.basename(archivo_entrada)}")  # Debug
                    
                    # Crear nombre de salida: nombre.esp.srt
                    directorio = os.path.dirname(archivo_entrada)
                    nombre_base = os.path.splitext(os.path.basename(archivo_entrada))[0]
                    extension = os.path.splitext(archivo_entrada)[1]
                    archivo_salida = os.path.join(directorio, f"{nombre_base}.esp{extension}")
                    
                    # Variables para cerrar sobre el valor actual de idx
                    archivo_actual = idx
                    nombre_archivo = os.path.basename(archivo_entrada)
                    
                    # Callback para progreso de cada archivo - usar after() para thread-safety
                    def callback_progreso(actual, total, mensaje):
                        try:
                            progreso_archivo = (actual / total) * 100 if total > 0 else 0
                            progreso_total = ((archivo_actual - 1) / total_archivos * 100) + (progreso_archivo / total_archivos)
                            
                            # Usar after() para actualizar GUI desde thread secundario de forma segura
                            def actualizar_gui():
                                try:
                                    self.barra_progreso['value'] = progreso_total
                                    self.porcentaje_label.config(text=f"{int(progreso_total)}%")
                                    self.progreso_archivo_label.config(text=f"Archivo {archivo_actual}/{total_archivos}: {nombre_archivo}")
                                    self.progreso_label.config(text=mensaje)
                                except Exception as e:
                                    print(f"Error actualizando GUI: {e}")
                            
                            self.root.after(0, actualizar_gui)
                        except Exception as e:
                            print(f"Error en callback_progreso: {e}")
                    
                    traductor = TraductorSRT(
                        idioma_origen=idioma_orig,
                        idioma_destino=idioma_dest,
                        callback_progreso=callback_progreso
                    )
                    
                    print(f"Iniciando traducción de {nombre_archivo}...")  # Debug
                    traductor.traducir_archivo(archivo_entrada, archivo_salida)
                    archivos_traducidos.append(archivo_salida)
                    print(f"Archivo {nombre_archivo} traducido exitosamente")  # Debug
                except Exception as e:
                    error_msg = f"Error en archivo {os.path.basename(archivo_entrada)}: {str(e)}"
                    print(error_msg)
                    import traceback
                    traceback.print_exc()
                    self.root.after(0, lambda msg=error_msg: messagebox.showwarning("Error en archivo", msg))
            
            print("Traducción completada, actualizando GUI...")  # Debug
            self.root.after(0, lambda: self.traduccion_completada(archivos_traducidos))
        except Exception as e:
            print(f"Error general: {str(e)}")
            import traceback
            traceback.print_exc()
            self.root.after(0, lambda: self.traduccion_error(str(e)))
    
    def traduccion_completada(self, archivos_salida):
        print("traduccion_completada llamado")  # Debug
        self.traduciendo = False
        self.btn_traducir.config(state='normal', text="Traducir Subtítulos")
        self.barra_progreso['value'] = 100
        self.porcentaje_label.config(text="100%")
        self.progreso_archivo_label.config(text="¡Traducción completada!")
        self.progreso_label.config(text=f"{len(archivos_salida)} archivo(s) traducido(s) exitosamente")
        self.root.update()  # Forzar actualización
        
        total = len(archivos_salida)
        mensaje = f"Traducción completada correctamente.\n\n{total} archivo(s) traducido(s):\n\n"
        
        # Mostrar solo nombres de archivos
        for archivo in archivos_salida[:5]:  # Mostrar máximo 5
            mensaje += f"• {os.path.basename(archivo)}\n"
        
        if total > 5:
            mensaje += f"\n... y {total - 5} más"
        
        messagebox.showinfo("Éxito", mensaje)
    
    def traduccion_error(self, error):
        self.traduciendo = False
        self.btn_traducir.config(state='normal', text="Traducir Subtítulos")
        self.progreso_frame.pack_forget()
        
        messagebox.showerror("Error", f"Error al traducir:\n{error}")


def main():
    root = tk.Tk()
    app = AplicacionTraductor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
