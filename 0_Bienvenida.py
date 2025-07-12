import streamlit as st
from utils.ui import (
    mostrar_logo_inferior_derecho,
    mostrar_video_fondo,
    aplicar_estilos_transparentes_selectbox,
    sidebar
)
import base64
import os

# --- Obtener idioma desde sidebar ---
idioma = sidebar()

# --- Diccionario de textos (usando puro Markdown) ---
textos = {
    "Español": {
        "page_title": "Smogon Starlight - Bienvenida",
        "banner_warning": "No se encontró el banner del torneo.",
        "titulo": "¿Qué es Smogon Starlight?",
        "contenido": """
SMOGON Starlight, parte de la serie *Narval Carnaval*, fue un torneo único de Splatoon 3 centrado en un innovador sistema de armas por **tiers**.

---

🧠 **Esto no es anti-meta... ¡es un meta completamente nuevo!**

Inspirado en los tiers competitivos de Pokémon, Smogon Starlight introdujo un formato en el que las armas **OverUsed (OU)** estaban **baneadas**, permitiendo solo el uso de armas **UnderUsed (UU)** y **NeverUsed (NU)**.  
Esto fomentó un metajuego mucho más **creativo**, **diverso** y lleno de **estrategias inusuales**.

---

⚔️ **Sistema de Tiers**

- **OU** (OverUsed) → 🔒 Baneadas  
- **UU & NU** (Under/NeverUsed) → ✅ Permitidas

---

📊 **¿Qué puedes encontrar en este dashboard?**

Este dashboard fue creado tanto para **jugadores** como para **organizadores**, con el fin de explorar el comportamiento del metajuego bajo estas reglas únicas.

Aquí encontrarás:

- **Welcome (Bienvenida)**: Esta página introductoria que explica el contexto general del torneo.  
- **General Tournament (Torneo General)**: Un resumen del uso de armas permitidas y su desempeño durante el torneo, enfocado en las distintas **clases de armas**.  
- **Weapon Stats (Info de Armas)**: Un análisis detallado de cada arma, incluyendo su uso por **modo de juego**, así como su **arma secundaria y especial**.  
- **Team Stats (Info de Participantes)**: Estadísticas y procedencia de los equipos participantes, junto con su **desempeño** en el torneo.  
- **About Us (Sobre Nosotros)**: Conoce a **Narval Carnaval**, el equipo organizador detrás de este evento.

¡Esperamos que lo disfrutes tanto como nosotros disfrutamos organizándolo! 🎉
"""
    },
    "English": {
        "page_title": "Smogon Starlight - Welcome",
        "banner_warning": "Tournament banner not found.",
        "titulo": "What is Smogon Starlight?",
        "contenido": """
SMOGON Starlight, part of the *Narval Carnaval* series, was a one-of-a-kind Splatoon 3 tournament based on an innovative **tier-based weapon system**.

---

🧠 **This isn't anti-meta... it's an entirely new meta!**

Inspired by Pokémon’s competitive tiers, Smogon Starlight introduced a format where **OverUsed (OU)** weapons were **banned**, allowing only **UnderUsed (UU)** and **NeverUsed (NU)**.  
This encouraged a much more **creative**, **diverse**, and **unexpected** metagame.

---

⚔️ **Tier System**

- **OU** (OverUsed) → 🔒 Banned  
- **UU & NU** (Under/NeverUsed) → ✅ Allowed

---

📊 **What will you find in this dashboard?**

This dashboard was created for both **players** and **organizers** to explore how the metagame evolved under this unique format.

Here's what each page offers:

- **Welcome**: This introductory page explaining the overall context of the tournament.  
- **General Tournament**: An overview of the allowed weapons and their usage throughout the tournament, focusing on **weapon classes**.  
- **Weapon Stats**: A deeper analysis of each weapon's usage by **game mode**, including their **sub** and **special weapons**.  
- **Team Stats**: Information about participating teams, their **countries of origin**, and their **tournament performance**.  
- **About Us**: Meet **Narval Carnaval**, the organizing team behind the event.

We hope you enjoy it as much as we enjoyed organizing it! 🎉
"""
    }
}

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title=textos[idioma]["page_title"], layout="wide", page_icon="images/narval_logo.png")
mostrar_video_fondo("videos/fondo.mp4")
mostrar_logo_inferior_derecho("images/smogon_logo.png")
aplicar_estilos_transparentes_selectbox()

# --- Mostrar banner si existe ---
banner_path = os.path.join("images", "smogon_banner.png")
if os.path.exists(banner_path):
    with open(banner_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center;">
            <img src="data:image/png;base64,{encoded}" style="width: 80%; max-width: 1000px;" />
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning(textos[idioma]["banner_warning"])

# --- Título principal (centrado con Markdown) ---
st.markdown(f"## {textos[idioma]['titulo']}", help=None)

# --- Mostrar el contenido como bloque Markdown puro ---
st.markdown(textos[idioma]["contenido"])
