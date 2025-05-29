import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import scrcpy
from adbutils import adb
import threading
import cv2
import time
import os

root = tk.Tk()
root.title("Mirror Gafas")

label_video = tk.Label(root)
label_video.pack()

def list_devices_tcpip():
    devices = adb.device_list()
    items = [i.serial for i in devices if ":" in i.serial]  # solo TCP/IP
    return items[0] if items else None


def crop_non_black_area(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    coords = cv2.findNonZero(thresh)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        cropped = image[y:y+h, x:x+w]
        return cropped
    else:
        return image

def crop_left_white_border(image, threshold=230):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Mean brightness along each column
    column_brightness = np.mean(gray, axis=0)

    # Find the first column from the left that is not "white"
    non_white_index = 0
    for i, val in enumerate(column_brightness):
        if val < threshold:
            non_white_index = i
            break

    # Crop from that point
    return image[:, non_white_index:]

def on_frame2(frame):
    if frame is not None:
        useful = crop_non_black_area(frame)
        useful = crop_left_white_border(useful)

        eye_frame_rgb = cv2.cvtColor(useful, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(eye_frame_rgb)

        # Resize larger (1280px wide)
        target_width = 1280
        w_percent = target_width / float(img.width)
        target_height = int(float(img.height) * w_percent)
        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

        imgtk = ImageTk.PhotoImage(img)
        label_video.imgtk = imgtk
        label_video.configure(image=imgtk)
        root.update()

def run_scrcpy():
    device_serial = list_devices_tcpip()
    if device_serial:
        print(f"Dispositivo detectado: {device_serial}")
        device = adb.device(serial=device_serial)
        client = scrcpy.Client(device=device, bitrate=1000000000, max_fps=5)
        client.add_listener(scrcpy.EVENT_FRAME, on_frame2)
        print("Iniciando cliente scrcpy...")
        client.start()
    else:
        print("No devices found")

# Iniciar scrcpy en hilo separado
threading.Thread(target=run_scrcpy, daemon=True).start()
root.mainloop()



