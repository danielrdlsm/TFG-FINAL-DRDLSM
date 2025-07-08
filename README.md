# Aplicación para el control de sesiones inmersivas

Aplicación desarrollada en Python con Tkinter destinada a facilitar el
desarrollo de sesiones inmersivas. A través de esta aplicación se podra controlar todo lo necesario para realizar 
una sesión con el uso de dispositivos XR.

## Funcionalidades

- **Gestión de participantes**: Registro, búsqueda y almacenamiento de los usuarios.
- **Control de sesiones**: Creación y seguimiento de sesiones terapéuticas personalizadas.
- **Conexión con dispositivos**: Comunicación directa con dispositivos Android mediante ADB y HTTP Screen Steam.
- **Gestión de escenas**: Selección y reproducción de contenido multimedia (Escenas mostradas en las gafas).
- **Generación de informes**: Exportación de datos y resultados en formatos accesibles (PDF o Word).


## ⚙️ Requisitos

- Python 3.8
- Módulos:
  - `tkinter`
  - `Pillow`
  - `pandas`
  - `adbutils`
  - `opencv-python`

##  Ejecución

1. Clona el repositorio:
   ```bash
   git clone https://github.com/danielrdlsm/TFG-FINAL-DRDLSM.git

2. Accede a la carpeta del proyecto:
      ```bash
   cd TFG-FINAL-DRDLSM/Interfaz

3. Instala las dependencias necesarias:
    ```bash
    pip install pillow pandas adbutils opencv-python
    ```
4.  Ejecuta la aplicación:
    ```bash
    python interfaz.py

