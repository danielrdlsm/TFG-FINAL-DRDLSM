
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