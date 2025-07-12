import streamlit as st
import base64
import os

def mostrar_logo_inferior_derecho(image_path, width=130):
    """Muestra el logo fijo en la esquina inferior derecha con animación al pasar el mouse."""
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <style>
                .logo-fixed {{
                    position: fixed;
                    bottom: 1rem;
                    right: 1rem;
                    z-index: 1000;
                    transition: transform 0.3s ease;
                }}
                .logo-fixed:hover {{
                    transform: scale(1.1);
                }}
            </style>
            <div class="logo-fixed">
                <img src="data:image/png;base64,{img_base64}" width="{width}">
            </div>
        """, unsafe_allow_html=True)

def mostrar_video_fondo(path: str):

    with open(path, "rb") as f:
        video_bytes = f.read()
    encoded = base64.b64encode(video_bytes).decode()

    fondo_html = f"""
    <style>
    /* Que el video cubra toda la app, incluido sidebar */
    .stApp {{
        background: transparent;
        overflow: hidden;
    }}

    /* Sidebar transparente para que deje ver el fondo */
    [data-testid="stSidebar"] {{
        background: transparent !important;
        box-shadow: none !important;
    }}

    /* Video atrás de todo */
    #video-background {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        z-index: -1;
    }}
    </style>

    <video autoplay muted loop id="video-background">
        <source src="data:video/mp4;base64,{encoded}" type="video/mp4">
    </video>
    """
    st.markdown(fondo_html, unsafe_allow_html=True)

def aplicar_estilos_transparentes_selectbox():
    st.markdown(
        """
        <style>
        /* Contenedor padre del input del selectbox */
        div[role="combobox"] {
            background-color: rgba(0, 0, 0, 0.2) !important;
            border-radius: 8px !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
        }

        /* Input dentro del selectbox */
        div[role="combobox"] input {
            background-color: rgba(0, 0, 0, 0.0) !important;
            color: white !important;
        }

        /* Flecha desplegable */
        div[role="combobox"] svg {
            fill: white !important;
        }

        /* Estilo del menú desplegable */
        ul[role="listbox"] {
            background-color: rgba(0, 0, 0, 0.8) !important;
            color: white !important;
        }

        /* Opciones del menú */
        li[role="option"] {
            background-color: transparent !important;
            color: white !important;
        }

        li[role="option"]:hover {
            background-color: rgba(255, 255, 255, 0.1) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

import streamlit as st
import os
import base64

def sidebar():
    st.sidebar.markdown("### Ir al torneo")

    banner_path = os.path.join("images", "battlefy_logo.png")
    torneo_url = "https://battlefy.com/narval-carnaval/smogon-starlight-fresh-season/647027826bda2d6c91059775/info?infoTab=details"

    if os.path.exists(banner_path):
        with open(banner_path, "rb") as img_file:
            encoded_banner = base64.b64encode(img_file.read()).decode()
        html_link = f'''
        <a href="{torneo_url}" target="_blank">
            <img src="data:image/png;base64,{encoded_banner}" style="width:100%; cursor:pointer;" alt="Banner Torneo" />
        </a>
        '''
        st.sidebar.markdown(html_link, unsafe_allow_html=True)
    else:
        st.sidebar.warning("No se encontró el banner del torneo.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Torneo desarrollado por:")
    logo_path = os.path.join("images", "narval_banner.png")
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_container_width=True)
    else:
        st.sidebar.warning("No se encontró el logo de la organizadora.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Síguenos o escríbenos:")

    # Paths de los iconos
    x_path = os.path.join("images", "x_logo.png")
    discord_path = os.path.join("images", "discord_logo.png")
    twitch_path = os.path.join("images", "twitch_logo.png")
    gmail_path = os.path.join("images", "gmail_logo.png")

    # URLs
    x_url = "https://x.com/NarvalCarnaval"
    discord_url = "https://discord.gg/jK33KnWZRv"
    twitch_url = "https://www.twitch.tv/narvalcarnaval"
    gmail_url = "https://mail.google.com/mail/?view=cm&fs=1&to=narvalcarnaval@gmail.com"

    # Función para cargar y codificar imágenes
    def img_to_base64(path):
        if os.path.exists(path):
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        return None

    x_encoded = img_to_base64(x_path)
    discord_encoded = img_to_base64(discord_path)
    gmail_encoded = img_to_base64(gmail_path)
    twitch_encoded = img_to_base64(twitch_path)

    # HTML centrado con íconos clickeables
    html_contact = '<div style="display: flex; justify-content: center; gap: 10px;">'

    if x_encoded:
        html_contact += f'''
        <a href="{x_url}" target="_blank">
            <img src="data:image/png;base64,{x_encoded}" style="width:32px; height:32px; cursor:pointer;" alt="X/Twitter" />
        </a>'''
    if discord_encoded:
        html_contact += f'''
        <a href="{discord_url}" target="_blank">
            <img src="data:image/png;base64,{discord_encoded}" style="width:32px; height:32px; cursor:pointer;" alt="Discord" />
        </a>'''
    if twitch_encoded:
        html_contact += f'''
        <a href="{twitch_url}" target="_blank">
            <img src="data:image/png;base64,{twitch_encoded}" style="width:32px; height:32px; cursor:pointer;" alt="Twitch" />
        </a>'''
    if gmail_encoded:
        html_contact += f'''
        <a href="{gmail_url}" target="_blank">
            <img src="data:image/png;base64,{gmail_encoded}" style="width:32px; height:32px; cursor:pointer;" alt="Gmail" />
        </a>'''

    html_contact += '</div>'
    st.sidebar.markdown(html_contact, unsafe_allow_html=True)

    # Idioma al final del sidebar (sin fixed)
    st.sidebar.markdown("---")
    selected_idioma = st.sidebar.selectbox(
        "Selecciona idioma / Select Language",
        ["Español", "English"],
        key="idioma_selector"
    )

    # Footer legal
    st.sidebar.markdown(
        """
        <div style='text-align: center; font-size: 12px; margin-top: 15px;'>
            Splatoon is trademark &copy; of Nintendo 2014–2025.<br>
            Narval Carnaval is not affiliated with Nintendo.<br><br>
            Página creada por Chris
        </div>
        """,
        unsafe_allow_html=True
    )

    return selected_idioma