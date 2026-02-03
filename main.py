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


class TraductorSRT:
    def __init__(self, idioma_origen='auto', idioma_destino='es', callback_progreso=None):
        self.idioma_origen = idioma_origen
        self.idioma_destino = idioma_destino
        self.traductor = GoogleTranslator(source=idioma_origen, target=idioma_destino)
        self.callback_progreso = callback_progreso
    
    def parsear_srt(self, contenido):
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
        
        return subtitulos
    
    def traducir_texto(self, texto):
        if not texto.strip():
            return texto
        
        try:
            lineas = texto.split('\n')
            lineas_traducidas = []
            
            for linea in lineas:
                if linea.strip():
                    traduccion = self.traductor.translate(linea)
                    lineas_traducidas.append(traduccion)
                else:
                    lineas_traducidas.append('')
            
            return '\n'.join(lineas_traducidas)
        except Exception as e:
            return texto
    
    def traducir_archivo(self, archivo_entrada, archivo_salida=None):
        if archivo_salida is None:
            nombre_base = os.path.splitext(archivo_entrada)[0]
            archivo_salida = f"{nombre_base}_traducido.srt"
        
        try:
            with open(archivo_entrada, 'r', encoding='utf-8') as f:
                contenido = f.read()
        except UnicodeDecodeError:
            with open(archivo_entrada, 'r', encoding='latin-1') as f:
                contenido = f.read()
        
        subtitulos = self.parsear_srt(contenido)
        total = len(subtitulos)
        
        if self.callback_progreso:
            self.callback_progreso(0, total, "Iniciando...")
        
        subtitulos_traducidos = []
        
        for i, sub in enumerate(subtitulos, 1):
            texto_traducido = self.traducir_texto(sub['texto'])
            subtitulos_traducidos.append({
                'numero': sub['numero'],
                'tiempo': sub['tiempo'],
                'texto': texto_traducido
            })
            
            if self.callback_progreso:
                self.callback_progreso(i, total, f"Traduciendo {i}/{total}")
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            for sub in subtitulos_traducidos:
                f.write(f"{sub['numero']}\n")
                f.write(f"{sub['tiempo']}\n")
                f.write(f"{sub['texto']}\n")
                f.write("\n")
        
        return archivo_salida


class AplicacionTraductor:
    def __init__(self, root):
        self.root = root
        self.root.title("Traductor de Subtítulos SRT")
        self.root.geometry("700x550")
        self.root.resizable(False, False)
        
        # Configurar estilo moderno
        self.configurar_estilo()
        
        # Variables
        self.archivo_seleccionado = tk.StringVar()
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
                       padding=12,
                       font=('Segoe UI', 10, 'bold'))
        
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
        
        # Selección de archivo
        archivo_label = tk.Label(contenido,
                                text="Archivo SRT",
                                font=('Segoe UI', 11, 'bold'),
                                bg=self.card_color,
                                fg=self.text_color)
        archivo_label.pack(anchor='w', pady=(0, 8))
        
        archivo_frame = tk.Frame(contenido, bg=self.card_color)
        archivo_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.archivo_entry = tk.Entry(archivo_frame,
                                      textvariable=self.archivo_seleccionado,
                                      font=('Segoe UI', 10),
                                      relief=tk.FLAT,
                                      bg="#f8f9fa",
                                      fg=self.text_color,
                                      state='readonly')
        self.archivo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, ipadx=10)
        
        btn_examinar = ttk.Button(archivo_frame,
                                 text="Examinar",
                                 command=self.seleccionar_archivo,
                                 style="Primary.TButton")
        btn_examinar.pack(side=tk.RIGHT, padx=(10, 0))
        
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
        
        # Progreso
        self.progreso_frame = tk.Frame(contenido, bg=self.card_color)
        self.progreso_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.progreso_label = tk.Label(self.progreso_frame,
                                       text="",
                                       font=('Segoe UI', 9),
                                       bg=self.card_color,
                                       fg=self.text_light)
        self.progreso_label.pack(anchor='w', pady=(0, 8))
        
        self.barra_progreso = ttk.Progressbar(self.progreso_frame,
                                             mode='determinate',
                                             length=300)
        self.barra_progreso.pack(fill=tk.X)
        
        self.progreso_frame.pack_forget()  # Ocultar inicialmente
        
        # Botón traducir
        self.btn_traducir = ttk.Button(contenido,
                                      text="Traducir Subtítulos",
                                      command=self.iniciar_traduccion,
                                      style="Primary.TButton")
        self.btn_traducir.pack(pady=(10, 0))
    
    def centrar_ventana(self):
        self.root.update_idletasks()
        ancho = self.root.winfo_width()
        alto = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto // 2)
        self.root.geometry(f'{ancho}x{alto}+{x}+{y}')
    
    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo SRT",
            filetypes=[("Archivos SRT", "*.srt"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            self.archivo_seleccionado.set(archivo)
    
    def obtener_codigo_idioma(self, nombre):
        return self.mapa_idiomas.get(nombre, nombre)
    
    def actualizar_progreso(self, actual, total, mensaje):
        porcentaje = (actual / total) * 100 if total > 0 else 0
        self.barra_progreso['value'] = porcentaje
        self.progreso_label.config(text=mensaje)
        self.root.update_idletasks()
    
    def iniciar_traduccion(self):
        if not self.archivo_seleccionado.get():
            messagebox.showwarning("Advertencia", "Por favor selecciona un archivo SRT")
            return
        
        if not os.path.exists(self.archivo_seleccionado.get()):
            messagebox.showerror("Error", "El archivo seleccionado no existe")
            return
        
        if self.traduciendo:
            return
        
        self.traduciendo = True
        self.btn_traducir.config(state='disabled', text="Traduciendo...")
        self.progreso_frame.pack(fill=tk.X, pady=(0, 20))
        self.barra_progreso['value'] = 0
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=self.traducir)
        thread.daemon = True
        thread.start()
    
    def traducir(self):
        try:
            idioma_orig = self.obtener_codigo_idioma(self.combo_origen.get())
            idioma_dest = self.obtener_codigo_idioma(self.combo_destino.get())
            
            traductor = TraductorSRT(
                idioma_origen=idioma_orig,
                idioma_destino=idioma_dest,
                callback_progreso=self.actualizar_progreso
            )
            
            archivo_salida = traductor.traducir_archivo(self.archivo_seleccionado.get())
            
            self.root.after(0, lambda: self.traduccion_completada(archivo_salida))
        except Exception as e:
            self.root.after(0, lambda: self.traduccion_error(str(e)))
    
    def traduccion_completada(self, archivo_salida):
        self.traduciendo = False
        self.btn_traducir.config(state='normal', text="Traducir Subtítulos")
        self.barra_progreso['value'] = 100
        self.progreso_label.config(text="¡Traducción completada!")
        
        messagebox.showinfo(
            "Éxito",
            f"Traducción completada correctamente.\n\nArchivo guardado en:\n{archivo_salida}"
        )
    
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
