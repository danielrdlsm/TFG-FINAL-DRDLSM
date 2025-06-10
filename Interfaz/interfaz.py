import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import ImageTk, Image, ImageDraw
import os
import subprocess
from adbutils import adb
import cv2
import re
import time
import threading

import pandas as pd

EXCEL_PATH = "participantes.xlsx"

def inicializar_excel():
    if not os.path.exists(EXCEL_PATH):
        df = pd.DataFrame(columns=["nombre", "sesion", "escena"])
        df.to_excel(EXCEL_PATH, index=False)
    else:
        df = pd.read_excel(EXCEL_PATH)
        for col in ["nombre", "sesion", "escena"]:
            if col not in df.columns:
                df[col] = ""
        df.to_excel(EXCEL_PATH, index=False)

def actualizar_ultima_escena(nombre, escena):
    df = pd.read_excel(EXCEL_PATH)
    idx = df[df["nombre"] == nombre].index
    if not idx.empty:
        df.at[idx[0], "escena"] = escena
        df.to_excel(EXCEL_PATH, index=False)



def agregar_participante_excel(nombre):
    df = pd.read_excel(EXCEL_PATH)
    if nombre not in df["nombre"].values:
        nuevo = pd.DataFrame([[nombre, 0]], columns=["nombre", "sesion"])
        df = pd.concat([df, nuevo], ignore_index=True)
        df.to_excel(EXCEL_PATH, index=False)

def obtener_sesion(nombre):
    df = pd.read_excel(EXCEL_PATH)
    fila = df[df["nombre"] == nombre]
    if not fila.empty:
        return int(fila["sesion"].values[0])
    return 0

def incrementar_sesion(nombre):
    df = pd.read_excel(EXCEL_PATH)
    idx = df[df["nombre"] == nombre].index
    if not idx.empty:
        df.at[idx[0], "sesion"] += 1
        df.to_excel(EXCEL_PATH, index=False)
        return df.at[idx[0], "sesion"]
    return None


# Carpeta para guardar pacientes
PARTICIPANTES_DIR = "participantes"

if not os.path.exists(PARTICIPANTES_DIR):
    os.makedirs(PARTICIPANTES_DIR)

# === Inicializacion ===
historial_botones = []
participantes = {}  # {nombre: sesión_actual}
participante_actual = None

videos_gafas = []
seconds = 0
running = False
imagenes_miniaturas = []
video_actual = None
video_inicio_segundos = None


def registrar_boton(nombre):
    tiempo = timer_var.get()
    historial_botones.append(f"[{tiempo}] {nombre}")


def cargar_imagen():
    archivo = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
    if archivo:
        img = Image.open(archivo)
        img = img.resize((250, 150))
        imagen = ImageTk.PhotoImage(img)
        imagen_label.config(image=imagen)
        imagen_label.image = imagen

def generar_thumbnail(ruta_video):
    try:
        cap = cv2.VideoCapture(ruta_video)
        ret, frame = cap.read()
        cap.release()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(frame_rgb).resize((160, 90))
            return ImageTk.PhotoImage(img_pil)
    except Exception as e:
        print(f"Error generando thumbnail para {ruta_video}: {e}")
    return None


def abrir_video(ruta):
    global video_actual, video_inicio_segundos

    try:
        nombre_video = os.path.basename(ruta)

        # cerrar anterior
        if video_actual:
            duracion = seconds - video_inicio_segundos
            minutos = duracion // 60
            segundos_restantes = duracion % 60
            registrar_boton(f"Fin de video: {video_actual} (duración: {minutos:02}:{segundos_restantes:02})")

        # abrir nuevo
        subprocess.Popen([ruta], shell=True)
        registrar_boton(f"Inicio de video: {nombre_video}")

        video_actual = nombre_video
        video_inicio_segundos = seconds

        # actualizar excel
        if participante_actual:
            actualizar_ultima_escena(participante_actual, nombre_video)

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
    frame_texto.pack(fill="both", expand=True, padx=10, pady=(0, 5))

    scrollbar = tk.Scrollbar(frame_texto)
    scrollbar.pack(side="right", fill="y")

    texto = tk.Text(frame_texto, wrap="word", yscrollcommand=scrollbar.set, height=15)
    texto.pack(side="left", fill="both", expand=True)

    scrollbar.config(command=texto.yview)

    if historial_botones:
        for linea in historial_botones:
            texto.insert("end", f"• {linea}\n")
    else:
        texto.insert("end", "No se ha pulsado ningún botón aún.")

    texto.config(state="disabled")

    frame_boton = tk.Frame(ventana)
    frame_boton.pack(fill="x", pady=(0, 10))

    btn_exportar_pdf = tk.Button(frame_boton, text="Exportar a PDF", command=exportar_informe_pdf)
    btn_exportar_pdf.pack(side="left", padx=10)

    btn_exportar_word = tk.Button(frame_boton, text="Exportar a Word", command=exportar_informe_word)
    btn_exportar_word.pack(side="left", padx=10)



from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

def exportar_informe_pdf():
    if not historial_botones:
        messagebox.showinfo("Sin datos", "No hay historial para exportar.")
        return

    nombre_archivo = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        title="Guardar informe como PDF"
    )
    if not nombre_archivo:
        return

    try:
        c = canvas.Canvas(nombre_archivo, pagesize=A4)
        width, height = A4
        margen = 50
        y = height - margen
        nombre = entry_id.get()
        sesion = entry_sesion.get()
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margen, y, "Informe de sesión")
        y -= 30

        c.setFont("Helvetica", 12)
        c.drawString(margen, y, f"Paciente: {nombre}")
        y -= 20
        c.drawString(margen, y, f"Sesión Nº: {sesion}")
        y -= 30

        c.setFont("Helvetica", 12)

        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        nombre = entry_id.get()
        sesion = entry_sesion.get()

        c.drawString(margen, y, f"Fecha: {fecha_actual}")
        y -= 20
        c.drawString(margen, y, f"Paciente: {nombre}")
        y -= 20
        c.drawString(margen, y, f"Sesión Nº: {sesion}")
        y -= 30
        c.drawString(margen, y, f"Fecha: {fecha_actual}")
        y -= 30

        c.setFont("Helvetica", 11)
        for linea in historial_botones:
            if y < margen + 30:
                c.showPage()
                y = height - margen
                c.setFont("Helvetica", 11)
            c.drawString(margen, y, f"- {linea}")
            y -= 20

        c.save()
        messagebox.showinfo("Informe exportado", "El informe se ha guardado correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el PDF:\n{e}")

from docx import Document
from docx.shared import Inches
from datetime import datetime

def exportar_informe_word():
    if not historial_botones:
        messagebox.showinfo("Sin datos", "No hay historial para exportar.")
        return

    nombre_archivo = filedialog.asksaveasfilename(
        defaultextension=".docx",
        filetypes=[("Word files", "*.docx")],
        title="Guardar informe como Word"
    )
    if not nombre_archivo:
        return

    try:
        doc = Document()
        doc.add_heading('Informe de sesión', 0)

        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        nombre = entry_id.get()
        sesion = entry_sesion.get()

        doc.add_paragraph(f"Fecha: {fecha_actual}")

        doc.add_heading('Historial de botones pulsados', level=1)
        for linea in historial_botones:
            doc.add_paragraph(f"- {linea}", style='List Bullet')

        doc.save(nombre_archivo)
        messagebox.showinfo("Informe exportado", "El informe se ha guardado correctamente en Word.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el Word:\n{e}")


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

    if participante_actual:
        nueva_sesion = incrementar_sesion(participante_actual)
        if nueva_sesion is not None:
            entry_sesion.configure(state="normal")
            entry_sesion.delete(0, tk.END)
            entry_sesion.insert(0, str(nueva_sesion))
            entry_sesion.configure(state="readonly")

    seconds = 0
    running = True


def parar_aplicacion():
    global running, video_actual, video_inicio_segundos
    running = False

    if video_actual:
        duracion = seconds - video_inicio_segundos
        minutos = duracion // 60
        segundos_restantes = duracion % 60
        registrar_boton(f"Fin de video: {video_actual} (duración: {minutos:02}:{segundos_restantes:02})")
        video_actual = None
        video_inicio_segundos = None


def parar_aplicacion():
    global running, video_actual, video_inicio_segundos
    running = False

    registrar_boton("PARAR APLICACIÓN")

    # Marca final del video #
    if video_actual:
        duracion = seconds - video_inicio_segundos
        minutos = duracion // 60
        segundos_restantes = duracion % 60
        registrar_boton(f"Fin de video: {video_actual} (duración: {minutos:02}:{segundos_restantes:02})")
        video_actual = None
        video_inicio_segundos = None

    # Registrar duración total de la sesión
    minutos = seconds // 60
    segundos_restantes = seconds % 60
    historial_botones.append(f"Duración total de la sesión: {minutos:02}:{segundos_restantes:02}")

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

        for widget in frame_galeria_videos.winfo_children():
            widget.destroy()

        imagenes_miniaturas.clear()
        columnas = 4
        fila = 0
        columna = 0

        for archivo in archivos:
            ruta_completa = os.path.join(carpeta, archivo)
            thumbnail = generar_thumbnail(ruta_completa)
            if thumbnail:
                btn = tk.Button(frame_galeria_videos, image=thumbnail,
                                command=lambda path=ruta_completa: abrir_video(path))
                btn.image = thumbnail
                btn.grid(row=fila, column=columna, padx=5, pady=5)
                columna += 1
                if columna >= columnas:
                    columna = 0
                    fila += 1

global frame_galeria_videos



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


##NUEVO MARTA##
def get_device_ip(device):
    try:
        device = adb.device(device)
        output = device.shell("ip route")
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)$", output)
        return match.group(1) if match else None
    except Exception as e:
        # print(f"Error getting IP: {e}")
        return None

def connect_devices_adb():
    devices = adb.device_list()
    items = [i.serial for i in devices if ":" in i.serial]  # Filtrar solo dispositivos TCP/IP
    try:
        device = adb.device(items)
        output = device.shell("ip route")
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)$", output)
        device.tcpip(5555)
        time.sleep(2)
        for _ in range(1):
            subprocess.call(f"adb connect {match.group(1)}")
            return True
    except Exception as e:
        print(f"Error getting IP: {e}")
        return None

def conectar_y_actualizar():
    conectado = connect_devices_adb()
    if conectado:
        # Actualiza lista de dispositivos en el ComboBox
        nuevos_dispositivos = list_devices_tcpip()
        ip_combo['values'] = nuevos_dispositivos
        if nuevos_dispositivos:
            ip_combo.set(nuevos_dispositivos[0])
            start_battery_monitoring(nuevos_dispositivos[0], battery_entry, root)
        else:
            ip_combo.set("No devices found")
            battery_entry.configure(state="normal")
            battery_entry.delete(0, tk.END)
            battery_entry.insert(0, "No device found")
            battery_entry.configure(state="readonly")

def list_devices_tcpip():
    devices = adb.device_list()
    items = [i.serial for i in devices if ":" in i.serial]  # solo dispositivos TCP/IP
    return items

def start_scrcpy(serial, extra_args=None):
    try:
        scrcpy_path = r"C:\Users\danie\OneDrive\Escritorio\TFG-Final\scrcpy-win64-v3.2\scrcpy.exe"
        print("Starting scrcpy with device:", serial)
        command = [
            scrcpy_path,
            '-s', serial,
            '--crop', '1832:1920:0:0'
        ]
        if extra_args:
            command += extra_args
        print("Executing command:", command)

        def run_scrcpy():
            subprocess.run(command)

        scrcpy_thread = threading.Thread(target=run_scrcpy)
        scrcpy_thread.start()

    except Exception as e:
        print("Exception:", e)
        messagebox.showerror("Error", str(e))

def mirror_hmd_view():
    selected_indices = list_devices_tcpip()
    if selected_indices:
        start_scrcpy(selected_indices[0])
    else:
        print("No devices found")

def actualizar_bateria(device, battery_entry):
    device = adb.device(serial=device)
    if device:
        try:
            output = device.shell("dumpsys battery | grep level")
            battery_level = int(output.strip().split(":")[1])

            # Update Entry
            battery_entry.configure(state="normal")
            battery_entry.delete(0, tk.END)
            battery_entry.insert(0, f"{battery_level}%")

            # Update color based on battery level
            color = "red" if battery_level < 20 else "black"
            battery_entry.configure(fg=color)
            battery_entry.configure(state="readonly")

        except Exception as e:
            print(f"Error reading battery level: {e}")

def start_battery_monitoring(device, battery_entry, root, interval_ms=60000):
    def update():
        actualizar_bateria(device, battery_entry)
        root.after(interval_ms, update)
    update()

def cargar_videos_gafas():
    #print("hola")
    devices = [ip for ip in list_devices_tcpip() if ip.strip() != ""]
    device = adb.device(devices[0])
    output = device.shell('ls /sdcard/Movies/EscenariosNeutros')
    videos = []
    for f in output.split('\n'):
        f = f.strip()
        if f.endswith('.mp4'):
            videos.append(f)
    #print("MP4 videos found:", videos)
    return videos

def cargar_escenas_gafas():
    devices = [ip for ip in list_devices_tcpip() if ip.strip() != ""]
    device = adb.device(devices[0])
    output = device.shell('ls -1 /sdcard/Movies/AssetBundleScenes')
    assetbundles = []
    for f in output.split('\n'):
        f = f.strip()
        if f and not (f.endswith('.meta') or f.endswith('.manifest')):
            assetbundles.append(f)
    #print("Escenas:", assetbundles)
    return assetbundles

##TERMINA NUEVO MARTA##

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



'''
# === Setup device ===

devices = list_devices_tcpip()
if len(devices) > 0:
    ip = get_device_ip(devices)
    device = adb.device(serial=devices)
    alive = True
    client = scrcpy.Client(device=device, bitrate=1000000, max_fps=5)
    #client.add_listener(scrcpy.EVENT_INIT, self.on_init)
    #client.add_listener(scrcpy.EVENT_FRAME, self.on_frame)
    client.add_listener(scrcpy.EVENT_FRAME, on_frame2)

    #self.start_scrcpy_thread()  # Llamar al hilo de Scrcpy
else:
    print("No ADB devices found. Running interface without device.")
    device = None
    alive = True
'''
inicializar_excel()

# === Root window ===
root = tk.Tk()
root.title("Interfaz adaptable")
root.attributes("-fullscreen", True)
root.geometry("1200x700")



# === Barra herramientas ===
toolbar = tk.Frame(root, bd=1, relief="raised", bg="#f0f0f0")
toolbar.pack(side="top", fill="x")
tk.Label(toolbar, text="Participante:").pack(side="left", padx=(10, 2))

combo_participantes = ttk.Combobox(toolbar, state="readonly")
combo_participantes.pack(side="left", padx=2)

def seleccionar_participante(event):
    seleccionado = combo_participantes.get()
    cargar_datos_participante(seleccionado)

def actualizar_lista_participantes():
    if not os.path.exists(EXCEL_PATH):
        return []
    df = pd.read_excel(EXCEL_PATH)
    return df["nombre"].tolist()


combo_participantes.bind("<<ComboboxSelected>>", seleccionar_participante)



btn_nuevo_participante = tk.Button(toolbar, text="Añadir participante", command=lambda: agregar_participante())
btn_nuevo_participante.pack(side="left", padx=2)



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

frame_contenido.columnconfigure(0, weight=3, minsize=800)
frame_contenido.columnconfigure(1, weight=2, minsize=400)




frame_contenido.rowconfigure(0, weight=1)


# Para quitar el scroll==
# === scrol izquierda ===
frame_scroll = tk.Frame(frame_contenido)
frame_scroll.grid(row=0, column=0, sticky="nsew")

frame_scroll.rowconfigure(0, weight=1)
frame_scroll.columnconfigure(0, weight=1)


canvas_izquierda = tk.Canvas(frame_scroll)
scrollbar_izquierda = tk.Scrollbar(frame_scroll, orient="vertical", command=canvas_izquierda.yview)
canvas_izquierda.configure(yscrollcommand=scrollbar_izquierda.set)

scrollbar_izquierda.pack(side="right", fill="y")
canvas_izquierda.pack(side="left", fill="both", expand=True)

# Marco real donde van los widgets
frame_izquierda = tk.Frame(canvas_izquierda)
canvas_izquierda.create_window((0, 0), window=frame_izquierda, anchor="nw", tags="contenedor")

# Ajustar scroll al tamaño del contenido
def ajustar_scroll(event):
    canvas_izquierda.configure(scrollregion=canvas_izquierda.bbox("all"))
def expandir_canvas(event):
    canvas_izquierda.itemconfig("contenedor", width=event.width)



frame_izquierda.bind("<Configure>", ajustar_scroll)
canvas_izquierda.bind("<Configure>", expandir_canvas)


frame_izquierda.columnconfigure(0, weight=1)

# === Frame superior: Datos paciente ===
frame_superior = tk.Frame(frame_izquierda)
frame_superior.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
for i in range(4):
    frame_superior.columnconfigure(i, weight=1)

tk.Label(frame_superior, text="ID del paciente").grid(row=0, column=0, sticky="w")

tk.Label(frame_superior, text="Nº sesión").grid(row=0, column=2, sticky="w")

entry_id = tk.Entry(frame_superior)
entry_id.grid(row=0, column=1, sticky="ew", padx=5)

entry_sesion = tk.Entry(frame_superior, state="readonly")
entry_sesion.grid(row=0, column=3, sticky="ew", padx=5)


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
device_ips = [ip for ip in list_devices_tcpip() if ip.strip() != ""]
ip_combo = ttk.Combobox(frame_dispositivo, values=device_ips)
ip_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
if device_ips:
    ip_combo.current(0)
else:
    ip_combo.set("No devices found")

tk.Label(frame_dispositivo, text="Batería:").grid(row=1, column=0, sticky="e")
battery_entry = tk.Entry(frame_dispositivo, state="readonly", justify="center")
battery_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
battery_entry.insert(0, "42%")
if device_ips:
    start_battery_monitoring(device_ips[0], battery_entry, root)
else:
    battery_entry.insert(0, "No device found")

btn_devices = tk.Button(frame_dispositivo, text="Conectar dispositivo", command=conectar_y_actualizar) #connect_devices_adb()
btn_devices.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")

mirror_button = tk.Button(frame_dispositivo, text="Ver vista de las gafas", command=mirror_hmd_view)
mirror_button.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")





cargar_videos = tk.Button(frame_dispositivo, text="Acceder archivos gafas", command= cargar_escenas_gafas)
cargar_videos.grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")

# === Mirror vista gafas ===

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

btn_cargar_videos = tk.Button(
    frame_videos_dinamicos,
    text="Seleccionar carpeta de videos",
    command=crear_botones_videos_desde_carpeta
)
btn_cargar_videos.pack(fill="x", padx=5, pady=5)

frame_galeria_videos = tk.Frame(frame_videos_dinamicos)
frame_galeria_videos.pack(fill="both", expand=True)


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


def actualizar_sesion_en_formulario():
    if participante_actual:
        entry_id.delete(0, tk.END)
        entry_id.insert(0, participante_actual)

        sesion = participantes.get(participante_actual, 1)
        entry_sesion.configure(state="normal")
        entry_sesion.delete(0, tk.END)
        entry_sesion.insert(0, str(sesion))
        entry_sesion.configure(state="readonly")

# === Generar Informe ===
btn_generar_informe = tk.Button(frame_izquierda, text="Generar informe", bg="#4da6ff", fg="white", font=("Segoe UI", 10, "bold"), command=mostrar_informe)
btn_generar_informe.grid(row=11, column=0, sticky="ew", padx=10, pady=(0, 10))
frame_izquierda.rowconfigure(11, weight=1)

from tkinter import simpledialog


# Vista Tablet
def ver_vista_tablet():
    import cv2
    import numpy as np
    from tkinter import simpledialog

    ip = simpledialog.askstring("IP de la tablet", "Introduce la IP que aparece en IP Webcam (ej: 192.168.1.42):")
    if not ip:
        return

    url = f"http://{ip}:8080/video"
    cap = cv2.VideoCapture(url)

    def actualizar():
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (400, 300))  #
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = ImageTk.PhotoImage(Image.fromarray(frame))
                label_gafas.config(image=img)
                label_gafas.image = img
        root.after(30, actualizar)

    actualizar()

    def cerrar():
        cap.release()
        ventana.destroy()

    ventana.protocol("WM_DELETE_WINDOW", cerrar)




# === Agregar participante

def agregar_participante():
    global participante_actual

    nuevo = tk.simpledialog.askstring("Nuevo participante", "Nombre del nuevo participante:")
    if nuevo:
        agregar_participante_excel(nuevo)
        combo_participantes['values'] = actualizar_lista_participantes()
        combo_participantes.set(nuevo)
        participante_actual = nuevo
        cargar_datos_participante(nuevo)


def cargar_datos_participante(nombre):
    global participante_actual
    participante_actual = nombre
    sesion = obtener_sesion(nombre)

    entry_id.delete(0, tk.END)
    entry_id.insert(0, participante_actual)

    entry_sesion.configure(state="normal")
    entry_sesion.delete(0, tk.END)
    entry_sesion.insert(0, str(sesion))
    entry_sesion.configure(state="readonly")


#TABLET
btn_vista_tablet = tk.Button(frame_dispositivo, text="Ver vista de la tablet", command=ver_vista_tablet)
btn_vista_tablet.grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")

combo_participantes['values'] = actualizar_lista_participantes()



frame_gafas.bind("<Configure>", redimensionar_gafas)
root.bind("<Configure>", reorganizar_botones)
actualizar_timer()


root.mainloop()
