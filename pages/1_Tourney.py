import streamlit as st
from utils.data_loader import load_and_prepare_data
from utils.viz import mostrar_arma_grid, color_manager, barplot_armas_con_imagenes, mapa_dominancia_por_clase
from utils.ui import (
    mostrar_logo_inferior_derecho,
    mostrar_video_fondo,
    aplicar_estilos_transparentes_selectbox,
    sidebar,
)

# --- Obtener idioma desde sidebar ---
idioma = sidebar()

textos_es_barplot = {
    "all_modes": "Todos los modos",
    "splat_zones": "Pintazonas",
    "tower_control": "Torreón",
    "rainmaker": "Pez Dorado",
    "clam_blitz": "Asalto Ameja",
    "top_label": "Selecciona el top de armas para",
    "no_data_warning": "No hay datos para el tipo seleccionado.",
    "xaxis_title": "Armas",
    "yaxis_title": "Usos totales en",
    "top_title": "Top",
    "top_title_suffix": "armas en",
    "selectbox_label": "Selecciona el tipo de uso:"
}

textos_en_barplot = {
    "all_modes": "All Modes",
    "splat_zones": "Splat Zones",
    "tower_control": "Tower Control",
    "rainmaker": "Rainmaker",
    "clam_blitz": "Clam Blitz",
    "top_label": "Select top weapons for",
    "no_data_warning": "No data for the selected type.",
    "xaxis_title": "Weapons",
    "yaxis_title": "Total uses in",
    "top_title": "Top",
    "top_title_suffix": "weapons in",
    "selectbox_label": "Select usage type:"
}

textos_es_dominance = {
    "title": "Dominancia por clase en",
    "no_data_warning": "No hay datos de uso para este mapa.",
    "uses": "usos"
}

textos_en_dominance = {
    "title": "Dominance by class on",
    "no_data_warning": "No usage data for this map.",
    "uses": "uses"
}

# --- Diccionario de textos por idioma ---
textos = {
    "Español": {
        "page_title": "Smogon Starlight - Torneo General",
        "titulo": "📊 Torneo General",
        "intro": """
Esta página muestra un resumen general del torneo **Smogon Starlight**:  
Explora las armas permitidas y baneadas, su uso a lo largo del evento, y el desempeño general de cada clase de arma.

Aquí podrás visualizar cómo se comportaron las distintas armas en el contexto del torneo, y cómo influyeron en las estrategias del metajuego.""",
        "expander_baneadas": "🔒 Armas Baneadas",
        "desc_baneadas": "Estas son las armas que fueron clasificadas como **OverUsed (OU)** y por lo tanto fueron **baneadas** del torneo. No estuvieron disponibles para los equipos participantes.",
        "expander_permitidas": "✅ Armas Permitidas",
        "desc_permitidas": "Estas son las armas **UnderUsed (UU)** y **NeverUsed (NU)** que sí estuvieron **permitidas** en el torneo. Puedes ver su aspecto y compararlas visualmente.",
        "sub_burbujas": "🧙 Gráfico de barras con imágenes de armas",
        "desc_burbujas": "Este gráfico muestra la frecuencia de uso de las armas permitidas mediante barras. Sobre cada barra se muestra la imagen del arma para facilitar su identificación visual.",
        "sub_dominancia": "🎯 Dominancia por clase en un mapa específico",
        "desc_dominancia": "Selecciona un mapa para ver qué **clase de arma** dominó en él. Las clases se representan con colores y las armas con sus íconos. Puedes ajustar la transparencia para facilitar la visualización.",
        "selectbox_label": "Selecciona un mapa:",
        "opciones_viz": "##### Opciones de Visualización",
        "slider_bloques": "Transparencia de Bloques de Color",
        "slider_bloques_help": "Ajusta la opacidad de los bloques de color que representan cada clase de arma en el mapa.",
        "slider_armas": "Transparencia de Imágenes de Armas",
        "slider_armas_help": "Ajusta la opacidad de las imágenes de armas que aparecen superpuestas en el mapa.",
    },
    "English": {
        "page_title": "Smogon Starlight - General Tournament",
        "titulo": "📊 General Tournament",
        "intro": """
This page offers a general overview of the **Smogon Starlight** tournament:  
Explore allowed and banned weapons, their usage during the event, and overall performance of each weapon class.

You'll get insight into how the different weapons behaved and how they shaped the tournament’s metagame strategies.""",
        "expander_baneadas": "🔒 Banned Weapons",
        "desc_baneadas": "These are the weapons classified as **OverUsed (OU)** and therefore were **banned** from the tournament. Teams could not use them.",
        "expander_permitidas": "✅ Allowed Weapons",
        "desc_permitidas": "These are the **UnderUsed (UU)** and **NeverUsed (NU)** weapons that were **allowed**. You can visually explore and compare them here.",
        "sub_burbujas": "🧙 Bar Chart with Weapon Images",
        "desc_burbujas": "This chart shows the usage frequency of allowed weapons with bars. On top of each bar is the weapon’s image to facilitate visual identification.",
        "sub_dominancia": "🎯 Dominance by Class on a Specific Map",
        "desc_dominancia": "Choose a map to see which **weapon class** dominated it. Classes are shown in color blocks and weapon icons are overlaid. You can adjust transparency settings to improve visibility.",
        "selectbox_label": "Select a map:",
        "opciones_viz": "##### Display Options",
        "slider_bloques": "Color Block Transparency",
        "slider_bloques_help": "Adjust the opacity of the colored blocks representing each weapon class on the map.",
        "slider_armas": "Weapon Image Transparency",
        "slider_armas_help": "Adjust the opacity of the weapon images overlaid on the map.",
    }
}

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title=textos[idioma]["page_title"], layout="wide", page_icon="images/narval_logo.png")
mostrar_video_fondo("videos/fondo.mp4")
mostrar_logo_inferior_derecho("images/smogon_logo.png")
aplicar_estilos_transparentes_selectbox()

# --- Cargar datos si no están en session_state ---
required_keys = ["merged_df", "allowed_weapons_df", "not_allowed_weapons_df", "mapa_df"]
if not all(key in st.session_state for key in required_keys):
    merged_df, allowed_df, not_allowed_df, mapa_df = load_and_prepare_data()
    st.session_state["merged_df"] = merged_df
    st.session_state["allowed_weapons_df"] = allowed_df
    st.session_state["not_allowed_weapons_df"] = not_allowed_df
    st.session_state["mapa_df"] = mapa_df

merged_df = st.session_state.merged_df
allowed_weapons_df = st.session_state.allowed_weapons_df
not_allowed_weapons_df = st.session_state.not_allowed_weapons_df
mapa_df = st.session_state.mapa_df

# --- Título principal + Introducción ---
st.title(textos[idioma]["titulo"])
st.markdown(textos[idioma]["intro"])

st.markdown("---")
# 🔒 Armas baneadas
st.markdown("### " + textos[idioma]["expander_baneadas"])
st.markdown(textos[idioma]["desc_baneadas"])
with st.expander(textos[idioma]["expander_baneadas"], expanded=False):
    mostrar_arma_grid(not_allowed_weapons_df, title=textos[idioma]["expander_baneadas"])

# ✅ Armas permitidas
st.markdown("### " + textos[idioma]["expander_permitidas"])
st.markdown(textos[idioma]["desc_permitidas"])
with st.expander(textos[idioma]["expander_permitidas"], expanded=False):
    mostrar_arma_grid(allowed_weapons_df, title=textos[idioma]["expander_permitidas"])

# --- Gráfico de barras con imágenes ---
st.markdown("---")
st.subheader(textos[idioma]["sub_burbujas"])
st.markdown(textos[idioma]["desc_burbujas"])
if idioma == "Español":
    textos_grafico = textos_es_barplot
else:
    textos_grafico = textos_en_barplot

barplot_armas_con_imagenes(allowed_weapons_df, color_manager, textos_grafico)

# --- Dominancia por clase en mapa ---
st.markdown("---")
st.subheader(textos[idioma]["sub_dominancia"])
st.markdown(textos[idioma]["desc_dominancia"])

mapas_disponibles = sorted(mapa_df["MAP"].unique())
mapa_seleccionado = st.selectbox(textos[idioma]["selectbox_label"], mapas_disponibles)

# --- Opciones de visualización con ayuda ---
st.markdown(textos[idioma]["opciones_viz"])
col1, col2 = st.columns(2)
with col1:
    opacity_bloque = st.slider(
        textos[idioma]["slider_bloques"],
        min_value=0.0, max_value=1.0,
        value=0.4,
        step=0.05,
        help=textos[idioma]["slider_bloques_help"]
    )
with col2:
    opacity_arma = st.slider(
        textos[idioma]["slider_armas"],
        min_value=0.0, max_value=1.0,
        value=0.65,
        step=0.05,
        help=textos[idioma]["slider_armas_help"]
    )

if idioma == "Español":
    textos_mapa = textos_es_dominance
else:
    textos_mapa = textos_en_dominance

mapa_dominancia_por_clase(
    mapa_df,
    mapa_seleccionado,
    color_manager,
    opacity_bloque,
    opacity_arma,
    textos_mapa
)