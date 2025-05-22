import tkinter as tk
from tkinter import ttk, filedialog
from PIL import ImageTk, Image, ImageDraw
import os
import subprocess

# === Inicializacion ===
historial_botones = []
videos_gafas = []
seconds = 0
running = False
imagenes_miniaturas = []


def registrar_boton(nombre):
    historial_botones.append(nombre)

def cargar_imagen():
    archivo = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
    if archivo:
        img = Image.open(archivo)
        img = img.resize((250, 150))
        imagen = ImageTk.PhotoImage(img)
        imagen_label.config(image=imagen)
        imagen_label.image = imagen

def abrir_video(ruta):
    try:
        subprocess.Popen([ruta], shell=True)
    except Exception as e:
        print(f"Error al abrir el video: {e}")

def cargar_video():
    archivo = filedialog.askopenfilename(filetypes=[("Videos", "*.mp4;*.avi;*.mov;*.mkv")])
    if archivo:
        video_label.config(text=f"Video cargado:\n{archivo.split('/')[-1]}")
        videos_gafas.append(archivo)
        nombre = os.path.basename(archivo)
        btn = tk.Button(frame_videos_gafas, text=nombre, anchor="w", relief="groove",
                        command=lambda path=archivo: abrir_video(path))
        btn.pack(fill="x", pady=2, padx=2)

def mostrar_informe():
    ventana = tk.Toplevel(root)
    ventana.title("Informe de Sesión")
    ventana.geometry("400x400")

    tk.Label(ventana, text="Historial de botones pulsados:", font=("Segoe UI", 12, "bold")).pack(pady=10)

    frame_texto = tk.Frame(ventana)
    frame_texto.pack(fill="both",  padx=10, pady=5)

    scrollbar = tk.Scrollbar(frame_texto)
    scrollbar.pack(side="right", fill="y")

    texto = tk.Text(frame_texto, wrap="word", yscrollcommand=scrollbar.set)
    texto.pack(fill="both")

    scrollbar.config(command=texto.yview)

    if historial_botones:
        for linea in historial_botones:
            texto.insert("end", f"• {linea}\n")
    else:
        texto.insert("end", "No se ha pulsado ningún botón aún.")

    texto.config(state="disabled")

def reset_timer():
    global running, seconds
    running = False
    seconds = 0
    timer_var.set("00:00")

def actualizar_timer():
    global seconds
    if running:
        minutos = seconds // 60
        segundos = seconds % 60
        timer_var.set(f"{minutos:02}:{segundos:02}")
        seconds += 1
    root.after(1000, actualizar_timer)

def empezar_aplicacion():
    global running, seconds
    seconds = 0
    running = True

def parar_aplicacion():
    global running
    running = False

def crear_botones_imagenes_desde_carpeta():
    carpeta = filedialog.askdirectory()
    if carpeta:
        extensiones_validas = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
        archivos = [
            f for f in os.listdir(carpeta)
            if os.path.isfile(os.path.join(carpeta, f)) and f.lower().endswith(extensiones_validas)
        ]

        for widget in frame_imagenes_dinamicas.winfo_children():
            if isinstance(widget, tk.Button) and widget != btn_cargar_imagenes:
                widget.destroy()

        for archivo in archivos:
            ruta_completa = os.path.join(carpeta, archivo)
            btn = tk.Button(frame_imagenes_dinamicas, text=archivo, anchor="w",
                            command=lambda path=ruta_completa: mostrar_imagen_en_panel(path))
            btn.pack(fill="x", padx=5, pady=2)


def crear_botones_desde_carpeta():
    carpeta = filedialog.askdirectory()
    if carpeta:
        archivos = [f for f in os.listdir(carpeta) if os.path.isfile(os.path.join(carpeta, f))]

        for widget in frame_archivos.winfo_children():
            widget.destroy()

        for archivo in archivos:
            btn = tk.Button(frame_archivos, text=archivo, anchor="w")
            btn.pack(fill="x", padx=5, pady=2)

def crear_botones_videos_desde_carpeta():
    carpeta = filedialog.askdirectory()
    if carpeta:
        extensiones_validas = ('.mp4', '.avi', '.mov', '.mkv')
        archivos = [
            f for f in os.listdir(carpeta)
            if os.path.isfile(os.path.join(carpeta, f)) and f.lower().endswith(extensiones_validas)
        ]

        for widget in frame_videos_dinamicos.winfo_children():
            widget.destroy()

        for archivo in archivos:
            ruta_completa = os.path.join(carpeta, archivo)
            btn = tk.Button(frame_videos_dinamicos, text=archivo, anchor="w",
                            command=lambda path=ruta_completa: abrir_video(path))
            btn.pack(fill="x", padx=5, pady=2)

def crear_botones_imagenes_desde_carpeta():
    carpeta = filedialog.askdirectory()
    if carpeta:
        extensiones_validas = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
        archivos = [
            f for f in os.listdir(carpeta)
            if os.path.isfile(os.path.join(carpeta, f)) and f.lower().endswith(extensiones_validas)
        ]

        for widget in frame_imagenes_dinamicas.winfo_children():
            if isinstance(widget, tk.Button) and widget != btn_cargar_imagenes:
                widget.destroy()

        imagenes_miniaturas.clear()

        for archivo in archivos:
            ruta_completa = os.path.join(carpeta, archivo)
            try:
                img = Image.open(ruta_completa)
                img.thumbnail((60, 60))
                img_tk = ImageTk.PhotoImage(img)
                imagenes_miniaturas.append(img_tk)  # evitar que se borre de memoria

                btn = tk.Button(frame_imagenes_dinamicas, image=img_tk,
                                command=lambda path=ruta_completa: mostrar_imagen_en_panel(path))
                btn.pack(side="left", padx=3, pady=3)
            except Exception as e:
                print(f"Error cargando {archivo}: {e}")

def mostrar_imagen_en_panel(path):
    try:
        img = Image.open(path)
        img.thumbnail((400, 300))
        img_tk = ImageTk.PhotoImage(img)
        imagen_preview_label.config(image=img_tk)
        imagen_preview_label.image = img_tk
    except Exception as e:
        print(f"No se pudo mostrar la imagen: {e}")


def reorganizar_botones(event=None):
    ancho = root.winfo_width()
    if ancho < 800:
        for i, b in enumerate(botones):
            b.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
        frame_botones.columnconfigure(0, weight=1)
    else:
        for i, b in enumerate(botones):
            b.grid(row=0, column=i, sticky="ew", padx=5, pady=2)
        for i in range(len(botones)):
            frame_botones.columnconfigure(i, weight=1)

# === Root window ===
root = tk.Tk()
root.title("Interfaz adaptable")
root.attributes("-fullscreen", True)
root.geometry("1200x700")

# === Barra herramientas ===
toolbar = tk.Frame(root, bd=1, relief="raised", bg="#f0f0f0")
toolbar.pack(side="top", fill="x")

btn_abrir_img = tk.Button(toolbar, text="Abrir Imagen", command=cargar_imagen)
btn_abrir_img.pack(side="left", padx=2, pady=2)

btn_abrir_video = tk.Button(toolbar, text="Abrir Video", command=cargar_video)
btn_abrir_video.pack(side="left", padx=2, pady=2)

btn_guardar = tk.Button(toolbar, text="Guardar Sesión")
btn_guardar.pack(side="left", padx=2, pady=2)

btn_salir = tk.Button(toolbar, text="Salir", command=root.quit)
btn_salir.pack(side="right", padx=2, pady=2)

btn_ventana = tk.Button(toolbar, text="Modo ventana", command=lambda: root.attributes("-fullscreen", False))
btn_ventana.pack(side="left", padx=2, pady=2)

# === Contenido principal ===
frame_contenido = tk.Frame(root)
frame_contenido.pack(fill="both", expand=True)
frame_contenido.columnconfigure(0, weight=3)
frame_contenido.columnconfigure(1, weight=2)



# Para quitar el scroll==
# === scrol izquierda ===
frame_scroll = tk.Frame(frame_contenido)
frame_scroll.grid(row=0, column=0, sticky="nsew")

canvas_izquierda = tk.Canvas(frame_scroll)
scrollbar_izquierda = tk.Scrollbar(frame_scroll, orient="vertical", command=canvas_izquierda.yview)
canvas_izquierda.configure(yscrollcommand=scrollbar_izquierda.set)

scrollbar_izquierda.pack(side="right", fill="y")
canvas_izquierda.pack(side="left", fill="both", expand=True)

# Marco real donde van los widgets
frame_izquierda = tk.Frame(canvas_izquierda)
canvas_izquierda.create_window((0, 0), window=frame_izquierda, anchor="nw")

# Ajustar scroll al tamaño del contenido
def ajustar_scroll(event):
    canvas_izquierda.configure(scrollregion=canvas_izquierda.bbox("all"))

frame_izquierda.bind("<Configure>", ajustar_scroll)

frame_izquierda.columnconfigure(0, weight=1)

# === Frame superior: Datos paciente ===
frame_superior = tk.Frame(frame_izquierda)
frame_superior.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
for i in range(4):
    frame_superior.columnconfigure(i, weight=1)

tk.Label(frame_superior, text="ID del paciente").grid(row=0, column=0, sticky="w")
tk.Entry(frame_superior).grid(row=0, column=1, sticky="ew", padx=5)
tk.Label(frame_superior, text="Nº sesión").grid(row=0, column=2, sticky="w")
tk.Entry(frame_superior).grid(row=0, column=3, sticky="ew", padx=5)

# === Botones principales + Timer ===
frame_botones = tk.Frame(frame_izquierda)
frame_botones.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

botones = [
    tk.Button(frame_botones, text="EMPEZAR APLICACIÓN", bg="lightgreen"),
    tk.Button(frame_botones, text="PARAR APLICACIÓN", bg="red", fg="white")
]
for b in botones:
    b.grid()

frame_timer = tk.LabelFrame(frame_botones, text="Timer")
frame_timer.grid(row=0, column=3, rowspan=2, padx=10)

timer_var = tk.StringVar()
timer_var.set("00:00")
timer_label = tk.Label(frame_timer, textvariable=timer_var, font=("Courier", 16))
timer_label.pack(padx=5, pady=(5, 2))
btn_restart = tk.Button(frame_timer, text="Restart", command=reset_timer)
btn_restart.pack(pady=(0, 5))

botones[0].config(command=lambda: [registrar_boton("EMPEZAR APLICACIÓN"), empezar_aplicacion()])
botones[1].config(command=lambda: [registrar_boton("PARAR APLICACIÓN"), parar_aplicacion()])


# === Frame tareas ===
frame_tareas = tk.Frame(frame_izquierda)
frame_tareas.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
frame_tareas.columnconfigure(1, weight=1)

tk.Label(frame_tareas, text="TAREA 1").grid(row=0, column=0, sticky="w", pady=5)
ttk.Combobox(frame_tareas, values=["Nivel 1", "Nivel 2", "Nivel 3"]).grid(row=0, column=1, sticky="ew", pady=5)

tk.Label(frame_tareas, text="TAREA 2").grid(row=1, column=0, sticky="w", pady=5)
ttk.Combobox(frame_tareas, values=["Nivel 1", "Nivel 2", "Nivel 3"]).grid(row=1, column=1, sticky="ew", pady=5)

# === Archivos Gafas ===
frame_videos_gafas = tk.LabelFrame(frame_izquierda, text="Archivos de las Gafas", padx=5, pady=5)
frame_videos_gafas.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 10))
frame_videos_gafas.columnconfigure(0, weight=1)

# === Dispositivo ===
frame_dispositivo = tk.LabelFrame(frame_izquierda, text="Dispositivo", padx=5, pady=5)
frame_dispositivo.grid(row=5, column=0, sticky="ew", padx=10, pady=(0, 10))
frame_dispositivo.columnconfigure(1, weight=1)

tk.Label(frame_dispositivo, text="IP:").grid(row=0, column=0, sticky="e")
ip_combo = ttk.Combobox(frame_dispositivo, values=["192.168.1.77", "192.168.1.88", "10.0.0.50"])
ip_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
ip_combo.current(0)

tk.Label(frame_dispositivo, text="Batería:").grid(row=1, column=0, sticky="e")
battery_entry = tk.Entry(frame_dispositivo, state="readonly", justify="center")
battery_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
battery_entry.insert(0, "42%")

# === Volumen ===
frame_volumen = tk.LabelFrame(frame_izquierda, text="Volumen", padx=10, pady=5)
frame_volumen.grid(row=6, column=0, sticky="ew", padx=10, pady=(0, 10))
frame_volumen.columnconfigure(0, weight=1)

volumen_slider = tk.Scale(frame_volumen, from_=0, to=100, orient="horizontal", label="Nivel de Volumen")
volumen_slider.set(50)
volumen_slider.grid(row=0, column=0, sticky="ew")

# === Botones dinámicos por archivo === Creacioón de botón de archvios por carpeta
# frame_archivos = tk.LabelFrame(frame_izquierda, text="Archivos de Carpeta", padx=10, pady=5)
# frame_archivos.grid(row=8, column=0, sticky="ew", padx=10, pady=(0, 10))

#btn_cargar_carpeta = tk.Button(frame_archivos, text="Seleccionar carpeta", command=crear_botones_desde_carpeta)
#btn_cargar_carpeta.pack(fill="x", padx=5, pady=5)

# === Botones de videos encontrados en carpeta ===
frame_videos_dinamicos = tk.LabelFrame(frame_izquierda, text="Videos de Carpeta", padx=10, pady=5)
frame_videos_dinamicos.grid(row=9, column=0, sticky="ew", padx=10, pady=(0, 10))

btn_cargar_videos = tk.Button(frame_videos_dinamicos, text="Seleccionar carpeta de videos", command=crear_botones_videos_desde_carpeta)
btn_cargar_videos.pack(fill="x", padx=5, pady=5)

# === Botones de imágenes encontradas en carpeta ===
frame_imagenes_dinamicas = tk.LabelFrame(frame_izquierda, text="Imágenes de Carpeta", padx=10, pady=5)
frame_imagenes_dinamicas.grid(row=10, column=0, sticky="ew", padx=10, pady=(0, 10))

btn_cargar_imagenes = tk.Button(frame_imagenes_dinamicas, text="Seleccionar carpeta de imágenes", command=crear_botones_imagenes_desde_carpeta)
btn_cargar_imagenes.pack(fill="x", padx=5, pady=5)

imagen_preview_label = tk.Label(frame_imagenes_dinamicas, bg="white", relief="sunken")
imagen_preview_label.pack(fill="both",  padx=5, pady=5)

# === Votacion ===
frame_votacion = tk.Frame(frame_izquierda)
frame_votacion.grid(row=8, column=0, sticky="ew", padx=10, pady=(0, 10))
frame_votacion.columnconfigure((0, 1, 2), weight=1)

tk.Button(frame_votacion, text="Lanzar votación", command=lambda: registrar_boton("Lanzar votación")).grid(row=0, column=0, padx=5, pady=2, sticky="ew")
tk.Button(frame_votacion, text="Parar Votación", command=lambda: registrar_boton("Parar votación")).grid(row=0, column=1, padx=5, pady=2, sticky="ew")
tk.Button(frame_votacion, text="Votación errónea", command=lambda: registrar_boton("Votación errónea")).grid(row=0, column=2, padx=5, pady=2, sticky="ew")



# === Gafas (parte derecha) ===
frame_gafas = tk.LabelFrame(frame_contenido, text="Vista de Gafas", bg="white", padx=5, pady=5)
frame_gafas.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
frame_gafas.columnconfigure(0, weight=1)

try:
    imagen_gafas_original = Image.open("gafas.png")
except FileNotFoundError:
    imagen_gafas_original = Image.new("RGB", (400, 300), "gray")
    d = ImageDraw.Draw(imagen_gafas_original)
    d.text((100, 130), "Sin imagen", fill="white")

label_gafas = tk.Label(frame_gafas, bg="white", relief="solid", bd=1)
label_gafas.grid(row=0, column=0, sticky="nsew")

def redimensionar_gafas(event):
    max_alto = 400
    ancho = frame_gafas.winfo_width()
    alto_original = imagen_gafas_original.height
    ancho_original = imagen_gafas_original.width
    escala = min(ancho / ancho_original, max_alto / alto_original)
    nuevo_ancho = int(ancho_original * escala)
    nuevo_alto = int(alto_original * escala)
    imagen_redimensionada = imagen_gafas_original.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
    imagen_tk = ImageTk.PhotoImage(imagen_redimensionada)
    label_gafas.config(image=imagen_tk)
    label_gafas.image = imagen_tk

# === Generar Informe ===
btn_generar_informe = tk.Button(frame_izquierda, text="Generar informe", bg="#4da6ff", fg="white", font=("Segoe UI", 10, "bold"), command=mostrar_informe)
btn_generar_informe.grid(row=11, column=0, sticky="ew", padx=10, pady=(0, 10))

frame_gafas.bind("<Configure>", redimensionar_gafas)
root.bind("<Configure>", reorganizar_botones)
actualizar_timer()
root.mainloop()
