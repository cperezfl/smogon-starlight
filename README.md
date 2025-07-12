# Smogon Starlight - Dashboard de Torneo

![Smogon Starlight](https://github.com/user/repo/blob/main/images/smogon_banner.png?raw=true)

Este es un dashboard interactivo creado con Streamlit para analizar el metajuego y los resultados del torneo de Splatoon 3 "Smogon Starlight", organizado por **Narval Carnaval**.

La aplicación permite a jugadores y organizadores explorar en detalle:
*   Uso general de armas y clases.
*   Estadísticas detalladas por arma, sub-arma y especial.
*   Información sobre los equipos participantes, su origen y su progreso en el torneo.
*   Resultados de la fase suiza y los brackets finales.

## 🚀 Requisitos Previos

Asegúrate de tener instalado **Python 3.8** o una versión superior.

- [Python](https://www.python.org/downloads/)
- `pip` (generalmente se instala con Python)

## ⚙️ Instalación

Sigue estos pasos para configurar el entorno y ejecutar la aplicación localmente.

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/tu-usuario/tu-repositorio.git
    cd tu-repositorio
    ```

2.  **Crea y activa un entorno virtual** (recomendado):

    *   **En Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   **En macOS / Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Instala las dependencias:**
    Usa el archivo `requirements.txt` para instalar todas las librerías necesarias.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Prepara los datos y los assets:**
    Este repositorio no incluye los archivos de datos, imágenes o videos para mantenerlo ligero. Deberás crearlos y poblarlos manualmente.

    Crea las siguientes carpetas en la raíz del proyecto:
    *   `data/`
    *   `images/`
    *   `videos/`

    Coloca los archivos necesarios dentro de estas carpetas. Por ejemplo:
    *   `data/datos.xlsx`
    *   `data/participants.xlsx`
    *   `data/weapons.xlsx`
    *   `images/smogon_banner.png`
    *   `images/narval_logo.png`
    *   `videos/fondo.mp4`
    *   ... y todas las demás imágenes de armas, mapas, etc.

## ▶️ Cómo Ejecutar la Aplicación

Una vez que hayas instalado las dependencias y preparado los datos, ejecuta el siguiente comando desde la carpeta raíz del proyecto:

```bash
streamlit run 0_Bienvenida.py
```

Se abrirá una nueva pestaña en tu navegador con la aplicación funcionando.

## 📂 Estructura del Proyecto

```
.
├── 0_Bienvenida.py         # Página principal de bienvenida
├── 1_Tourney.py            # Página: Torneo General
├── 2_Weapon_Stats.py       # Página: Estadísticas de Armas
├── 3_Team_Stats.py         # Página: Estadísticas de Equipos
├── 4_About_Us.py           # Página: Sobre Nosotros
├── utils/                  # Módulos de utilidad
│   ├── __init__.py
│   ├── data_loader.py      # Lógica para cargar datos
│   ├── ui.py               # Componentes de UI reutilizables
│   └── viz.py              # Lógica para crear visualizaciones
├── data/                   # (Carpeta para tus archivos .xlsx)
├── images/                 # (Carpeta para tus imágenes .png, .jpg)
├── videos/                 # (Carpeta para tus videos .mp4)
├── requirements.txt        # Dependencias de Python
├── .gitignore              # Archivos a ignorar por Git
└── README.md               # Este archivo
```