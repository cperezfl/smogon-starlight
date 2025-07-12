import streamlit as st
from utils.data_loader import load_and_prepare_data
from utils.viz import plot_radar_arma, color_manager, plot_nolan, plot_nolan_subs
from utils.ui import (
    mostrar_logo_inferior_derecho,
    mostrar_video_fondo,
    aplicar_estilos_transparentes_selectbox,
    sidebar
)

textos_es_nolan = {
    "titulo_nolan_especiales": "Diagrama de Nolan - Uso de Especiales",
    "titulo_nolan_subs": "Diagrama de Nolan - Uso de Armas Secundarias",
    "eje_x": "{modo1} - {modo0}",
    "eje_y": "{modo2} - {modo3}",
}

textos_en_nolan = {
    "titulo_nolan_especiales": "Nolan Diagram - Special Usage",
    "titulo_nolan_subs": "Nolan Diagram - Sub Weapon Usage",
    "eje_x": "{modo1} - {modo0}",
    "eje_y": "{modo2} - {modo3}",
}

textos_modos_es_nolan  = {
    "all_modes": "Todos los modos",
    "splat_zones": "Pintazonas",
    "tower_control": "Torreón",
    "rainmaker": "Pez Dorado",
    "clam_blitz": "Asalto Ameja"
}

textos_modos_en_nolan  = {
    "all_modes": "All Modes",
    "splat_zones": "Splat Zones",
    "tower_control": "Tower Control",
    "rainmaker": "Rainmaker",
    "clam_blitz": "Clam Blitz"
}

# --- Diccionario de textos para español e inglés ---
textos = {
    "Español": {
        "page_title": "Smogon Starlight - Info de Armas",
        "titulo_principal": "🎯 Información Detallada de Armas",
        "page_description": """
Información más detallada y específica sobre las armas usadas según modo de juego, además de su arma secundaria y especial.  
En Splatoon, las armas son un kit compuesto por: arma principal + secundaria + especial.
""",
        "selecciona_armas": "Selecciona hasta 3 armas para comparar",
        "sin_seleccion": "Por favor, selecciona al menos un arma.",
        "estadisticas_arma": "**Estadísticas del arma:**",
        "titulo_radar": "📈 Comparación múltiple de Armas",
        "explicacion_radar": """
Este gráfico muestra una comparación visual en forma de radar de las estadísticas clave de cada arma seleccionada.  
Permite observar diferencias en atributos como rango, daño, velocidad de disparo y más, facilitando la comparación directa entre armas.  
Selecciona hasta 3 armas para comparar sus características principales.
""",
        "titulo_nolan_especiales": "Diagrama de Nolan para Especiales",
        "explicacion_nolan_especiales": """
El Diagrama de Nolan representa el desempeño de los diferentes especiales en los modos principales de juego.  
Cada punto o área muestra cómo se utiliza un especial en modos como Pintazones, Torreón, Pez Dorado y Asalto Ameja, ayudándote a entender su popularidad y efectividad relativa.
""",
        "titulo_nolan_subs": "Diagrama de Nolan para Subs",
        "explicacion_nolan_subs": """
Similar al diagrama para especiales, este gráfico muestra el uso y desempeño de las armas secundarias (subs) en los distintos modos de juego.  
Analiza qué subs son más frecuentes o efectivos según el modo, para ayudarte a comprender la estrategia detrás de su selección.
""",
        "seleccionar_todos_especiales": "Seleccionar todos los especiales",
        "seleccionar_todos_subs": "Seleccionar todos los subs",
        "selecciona_especiales": "Selecciona Especiales para comparar:",
        "selecciona_subs": "Selecciona Subs para comparar:",
        "info_seleccion_especiales": "Selecciona al menos un especial para mostrar.",
        "info_seleccion_subs": "Selecciona al menos un sub para mostrar.",
    },
    "English": {
        "page_title": "Smogon Starlight - Weapon Info",
        "titulo_principal": "🎯 Detailed Weapon Information",
        "page_description": """
More detailed and specific information about weapons used by game mode, including their secondary and special weapons.  
In Splatoon, weapons are a kit composed of: main weapon + sub weapon + special weapon.
""",
        "selecciona_armas": "Select up to 3 weapons to compare",
        "sin_seleccion": "Please select at least one weapon.",
        "estadisticas_arma": "**Weapon statistics:**",
        "titulo_radar": "📈 Multiple Weapon Comparison",
        "explicacion_radar": """
This radar chart visually compares key stats of each selected weapon.  
It helps highlight differences in range, damage, fire rate, and other attributes, making it easy to compare weapon features side by side.  
Select up to 3 weapons to compare their main characteristics.
""",
        "titulo_nolan_especiales": "Nolan Diagram for Specials",
        "explicacion_nolan_especiales": """
The Nolan Diagram represents the performance of different specials across the main game modes.  
Each point or area shows how a special is used in modes like Splat Zones, Tower Control, Rainmaker, and Clam Blitz, helping you understand its popularity and relative effectiveness.
""",
        "titulo_nolan_subs": "Nolan Diagram for Subs",
        "explicacion_nolan_subs": """
Similar to the specials diagram, this chart shows the usage and performance of sub weapons across different game modes.  
Analyze which subs are most frequent or effective by mode, helping you understand the strategy behind their selection.
""",
        "seleccionar_todos_especiales": "Select all specials",
        "seleccionar_todos_subs": "Select all subs",
        "selecciona_especiales": "Select Specials to compare:",
        "selecciona_subs": "Select Subs to compare:",
        "info_seleccion_especiales": "Please select at least one special to display.",
        "info_seleccion_subs": "Please select at least one sub to display."
    }
}

# --- Obtener idioma desde sidebar ---
idioma = sidebar()
textos_actuales = textos[idioma]

# --- Configuración general ---
st.set_page_config(page_title=textos_actuales["page_title"], layout="wide", page_icon="images/narval_logo.png")
mostrar_video_fondo("videos/fondo.mp4")
mostrar_logo_inferior_derecho("images/smogon_logo.png")
aplicar_estilos_transparentes_selectbox()

# --- Carga de datos ---
if "merged_df" not in st.session_state:
    (st.session_state.merged_df,
     st.session_state.allowed_weapons_df,
     _, _) = load_and_prepare_data()

merged_df = st.session_state.merged_df
allowed_weapons_df = st.session_state.allowed_weapons_df

# --- Título principal ---
st.title(textos_actuales["titulo_principal"])

# --- Descripción principal ---
st.markdown(textos_actuales["page_description"])


# --- Sección: Comparación múltiple de armas ---
st.markdown("---")
st.header(textos_actuales["titulo_radar"])
st.markdown(textos_actuales["explicacion_radar"])

armas_seleccionadas = st.multiselect(
    textos_actuales["selecciona_armas"],
    allowed_weapons_df["WEAPON"].unique(),
    max_selections=3
)

if not armas_seleccionadas:
    st.info(textos_actuales["sin_seleccion"])
else:
    cols = st.columns(len(armas_seleccionadas))
    for i, arma in enumerate(armas_seleccionadas):
        fig, stats_text = plot_radar_arma(allowed_weapons_df, arma, color_manager)
        with cols[i]:
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                if stats_text:
                    st.markdown(textos_actuales["estadisticas_arma"])
                    st.markdown(stats_text)
            else:
                st.warning(stats_text)

if idioma == "Español":
    textos_actuales_nolan = textos_es_nolan
    textos_modos_actuales_nolan = textos_modos_es_nolan
else:
    textos_actuales_nolan = textos_en_nolan
    textos_modos_actuales_nolan = textos_modos_en_nolan

st.markdown("---")
st.header(textos_actuales["titulo_nolan_especiales"])
st.markdown(textos_actuales["explicacion_nolan_especiales"])

modos = ["SPLAT ZONES", "TOWER CONTROL", "RAINMAKER", "CLAM BLITZ"]
especiales = sorted(allowed_weapons_df["SPECIAL"].dropna().unique())

seleccionar_todos = st.checkbox(textos_actuales["seleccionar_todos_especiales"])

if seleccionar_todos:
    seleccionadas = especiales
else:
    seleccionadas = st.multiselect(textos_actuales["selecciona_especiales"], especiales)

if seleccionadas:
    fig = plot_nolan(allowed_weapons_df, seleccionadas, modos, textos_actuales_nolan, textos_modos_actuales_nolan, img_column="SpecialImage")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(textos_actuales["info_seleccion_especiales"])

# --- Sección: Diagrama de Nolan para Subs ---

if idioma == "Español":
    textos_actuales_nolan = textos_es_nolan
    textos_modos_actuales_nolan = textos_modos_es_nolan
else:
    textos_actuales_nolan = textos_en_nolan
    textos_modos_actuales_nolan = textos_modos_en_nolan

st.markdown("---")
st.header(textos_actuales["titulo_nolan_subs"])
st.markdown(textos_actuales["explicacion_nolan_subs"])

subs = sorted(allowed_weapons_df["SUB"].dropna().unique())

seleccionar_todos_subs = st.checkbox(textos_actuales["seleccionar_todos_subs"])

if seleccionar_todos_subs:
    seleccionadas_subs = subs
else:
    seleccionadas_subs = st.multiselect(textos_actuales["selecciona_subs"], subs)

if seleccionadas_subs:
    fig = plot_nolan_subs(allowed_weapons_df, seleccionadas_subs, modos, textos_actuales_nolan, textos_modos_actuales_nolan, img_column="SubImage")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(textos_actuales["info_seleccion_subs"])
