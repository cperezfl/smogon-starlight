import streamlit as st
from utils.ui import (
    mostrar_logo_inferior_derecho,
    mostrar_video_fondo,
    aplicar_estilos_transparentes_selectbox,
    sidebar,  # ya importado de ui.py
)
from PIL import Image
import os
import base64

# --- Obtén idioma desde sidebar (importado desde ui.py) ---
idioma = sidebar()
if "idioma_selector" not in st.session_state:
    st.session_state["idioma_selector"] = "Español"

# --- Textos por idioma ---
textos = {
    "Español": {
        "title": "Narval Carnaval 🐳",
        "intro": """
        ¡Hola comunidad de Splatoon! 🐳

        Narval Carnaval es una organización orientada a Torneos Latinoamericanos e Internacionales.  
        Nuestro objetivo principal es mantener a la escena competitiva LATAM e Internacional activa con torneos mensuales innovadores y de calidad.

        Narval Carnaval fue evolucionando y migró a Splatoon 3 en 2022, organizando varios torneos, siendo el más reconocido **SMOGON Starlight**, que reunió hasta 78 equipos en un solo torneo.  
        A través de las distintas temporadas de Splatoon 3 generó gran expectación, destacando armas con menor uso en la escena competitiva, fomentando la creatividad y el uso de armas menos convencionales.
        """,
        "historia": """
        ---
        ### Historia

        El primer torneo de Narval Carnaval fue **Festaluna** en 2021, un torneo de Splatoon 2 con 17 equipos latinoamericanos, organizado por Bowen y Kloud, dos organizadores chilenos.  
        Este evento logró reunir a la gran mayoría de equipos existentes en Latinoamérica en ese momento.
        """,
        "banner_warning": "No se encontró el banner de Narval Carnaval."
    },
    "English": {
        "title": "Narval Carnaval 🐳",
        "intro": """
        Hello Splatoon community! 🐳

        Narval Carnaval is an organization focused on Latin American and Global Tourneys.  
        Our main goal is to keep the competitive LATAM and Global scene active with innovative and quality monthly tourneys.

        Narval Carnaval evolved and migrated to Splatoon 3 in 2022, organizing several tournaments, being the most recognized **SMOGON Starlight**, which gathered up to 78 teams in a single tournament.  
        Throughout the different Splatoon 3 seasons, it generated great excitement, highlighting less-used weapons competitively and encouraging creativity and unconventional weapon use.
        """,
        "historia": """
        ---
        ### History

        The first Narval Carnaval tournament was **Festaluna** in 2021, a Splatoon 2 tournament with 17 Latin American teams, organized by Bowen and Kloud, two Chilean organizers.  
        This event managed to gather most of the existing teams in Latin America at that time.
        """,
        "banner_warning": "Narval Carnaval banner not found."
    }
}

# --- Configuración página ---
st.set_page_config(
    page_title="Smogon Starlight - Sobre Nosotros",
    layout="wide",
    page_icon="images/narval_logo.png",
)
mostrar_video_fondo("videos/fondo.mp4")
mostrar_logo_inferior_derecho("images/smogon_logo.png")
aplicar_estilos_transparentes_selectbox()

# --- Mostrar banner AL INICIO y CENTRADO ---
banner_path = os.path.join("images", "narval_banner.png")
if os.path.exists(banner_path):
    with open(banner_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    banner_html = f"""
    <div style="display:flex; justify-content:center; margin-bottom:30px;">
        <a href="https://x.com/NarvalCarnaval" target="_blank" rel="noopener noreferrer">
            <img src="data:image/png;base64,{data}" alt="Banner Narval Carnaval" 
                 style="max-width:900px; width:100%; cursor:pointer;" />
        </a>
    </div>
    """
    st.markdown(banner_html, unsafe_allow_html=True)
else:
    st.warning(textos[idioma]["banner_warning"])

# --- CSS para centrar texto y tamaño ---
st.markdown(
    """
    <style>
    /* Contenedor texto centrado con ancho máximo */
    .content-container {
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
        text-align: center;
        font-size: 20px;
        line-height: 1.8;
    }
    /* Título grande y centrado */
    .custom-title {
        font-size: 48px;
        font-weight: 700;
        margin-bottom: 30px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Contenido principal ---
with st.container():
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    st.markdown(f'<h1 class="custom-title">{textos[idioma]["title"]}</h1>', unsafe_allow_html=True)
    st.markdown(textos[idioma]["intro"])
    st.markdown(textos[idioma]["historia"])
    st.markdown("</div>", unsafe_allow_html=True)
