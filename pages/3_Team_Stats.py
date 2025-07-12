import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
from utils.data_loader import load_participant_data, load_tournament_journey_data, cargar_datos_participantes
from utils.ui import (
    mostrar_logo_inferior_derecho,
    mostrar_video_fondo,
    aplicar_estilos_transparentes_selectbox,
    sidebar
)
from utils.viz import mostrar_mapa_equipos_por_pais, create_podium_chart, parse_swiss_sheet, crear_grafico_progresion

# --- Textos multilingües ---

textos_es_mapa = {
    "titulo": "Número de equipos por país",
    "equipos": "Equipos"
}

textos_en_mapa = {
    "titulo": "Number of Teams by Country",
    "equipos": "Teams"
}

textos = {
    "es": {
        "page_title": "Smogon Starlight - Participantes y Brackets",
        "main_title": "🌍 Descripción Detallada de Armas",
        "page_description": (
            "Estadísticas y procedencia de los equipos participantes, junto con su **desempeño** en el torneo. "
            "Analiza la progresión en la fase suiza, resultados de brackets y la distribución geográfica de los equipos."
        ),
        "map_section": "🗺️ Mapa de Equipos por País",
        "map_description": "Visualiza la cantidad y ubicación de equipos participantes por país.",
        "swiss_section": "📈 Análisis de la Fase Suiza",
        "team_comparison_section": "🆚 Análisis Comparativo por Equipo",
        "select_teams": "Selecciona uno o más equipos para comparar su progresión:",
        "team_details": "Detalles por Equipo",
        "matches": "Partidas",
        "no_matches": "No se encontraron partidas para este equipo.",
        "final_result": "Resultado Final",
        "eliminated_swiss": "Eliminado en fase suiza.",
        "dnf_swiss": "🚫 No completó la fase suiza.",
        "weezing_bracket_result": "🏆 Clasificó a **Weezing Bracket** y obtuvo el puesto **{standing}**.",
        "koffing_bracket_result": "🏅 Clasificó a **Koffing Bracket** y obtuvo el puesto **{standing}**.",
        "swiss_group_section": "🌐 Análisis por Grupo Suizo",
        "select_group": "Selecciona un grupo para ver la progresión:",
        "group_progression_title": "Progresión de todos los equipos en el Grupo {group}",
        "brackets_section": "🏆 Resultados de los Brackets",
        "select_bracket": "Elige el bracket que quieres visualizar:",
        "bracket_options": ["-- Selecciona un Bracket --", "Weezing Bracket (Superior)", "Koffing Bracket (Inferior)"],
        "no_chart": "No se pudo generar el gráfico para el bracket seleccionado.",
        "tooltip_select_teams": "Elige equipos para visualizar su desempeño en la fase suiza.",
        "tooltip_select_group": "Selecciona el grupo suizo para mostrar su progresión.",
        "tooltip_select_bracket": "Selecciona un bracket para visualizar sus resultados.",
        "podium_title": "Podio de Equipos en",        
    },
    "en": {
        "page_title": "Smogon Starlight - Participants and Brackets",
        "main_title": "🌍 Detailed Weapon Overview",
        "page_description": (
            "Statistics and origins of participating teams, along with their **performance** in the tournament. "
            "Analyze the Swiss phase progression, bracket results, and geographical distribution of teams."
        ),
        "map_section": "🗺️ Teams Map by Country",
        "map_description": "Visualize the number and location of participating teams by country.",
        "swiss_section": "📈 Swiss Phase Analysis",
        "team_comparison_section": "🆚 Comparative Analysis by Team",
        "select_teams": "Select one or more teams to compare their progression:",
        "team_details": "Details by Team",
        "matches": "Matches",
        "no_matches": "No matches found for this team.",
        "final_result": "Final Result",
        "eliminated_swiss": "Eliminated in Swiss phase.",
        "dnf_swiss": "🚫 Did not finish Swiss phase.",
        "weezing_bracket_result": "🏆 Qualified for **Weezing Bracket** and placed **{standing}**.",
        "koffing_bracket_result": "🏅 Qualified for **Koffing Bracket** and placed **{standing}**.",
        "swiss_group_section": "🌐 Analysis by Swiss Group",
        "select_group": "Select a group to view progression:",
        "group_progression_title": "Progression of all teams in Group {group}",
        "brackets_section": "🏆 Bracket Results",
        "select_bracket": "Choose the bracket you want to view:",
        "bracket_options": ["-- Select a Bracket --", "Weezing Bracket (Upper)", "Koffing Bracket (Lower)"],
        "no_chart": "Could not generate chart for the selected bracket.",
        "tooltip_select_teams": "Choose teams to visualize their Swiss phase performance.",
        "tooltip_select_group": "Select the Swiss group to display its progression.",
        "tooltip_select_bracket": "Select a bracket to view its results.",
        "podium_title": "Team Podium in",
    }
}

# --- CONFIGURACIÓN DE LA PÁGINA ---

# --- Obtener idioma desde sidebar ---
idioma_map = {
    "Español": "es",
    "English": "en"
}

idioma = sidebar()
clave_idioma = idioma_map[idioma]

textos_actuales = textos[clave_idioma]# --- Configuración general ---
st.set_page_config(page_title=textos_actuales["page_title"], layout="wide", page_icon="images/narval_logo.png")
mostrar_video_fondo("videos/fondo.mp4")
mostrar_logo_inferior_derecho("images/smogon_logo.png")
aplicar_estilos_transparentes_selectbox()


# --- Configuración página ---
st.set_page_config(
    page_title=textos_actuales["page_title"],
    layout="wide",
    page_icon="images/narval_logo.png"
)

# --- Mostrar título con emoji ---
st.markdown(f"# {textos_actuales['page_title']}", unsafe_allow_html=True)

# --- Descripción visible siempre ---
st.markdown(f"### {textos_actuales['page_description']}")

# --- Carga de datos (con caché) ---
@st.cache_data
def load_all_data():
    return cargar_datos_participantes()

try:
    participants_df, weezing_df, koffing_df, seeding_df, swiss_data, team_color_map = load_all_data()
except Exception as e:
    st.error(f"Error fatal al cargar los datos: {e}")
    st.stop()

# --- Mapa ---

st.markdown("---")
st.header(textos_actuales["map_section"])
st.markdown(textos_actuales["map_description"])

if idioma == "Español":
    mostrar_mapa_equipos_por_pais(participants_df, idioma="Español")
else:
    mostrar_mapa_equipos_por_pais(participants_df, idioma="English") 

# --- Análisis fase suiza ---
st.markdown("---")
st.header(textos_actuales["swiss_section"])

# Análisis comparativo por equipo
st.subheader(textos_actuales["team_comparison_section"])
st.markdown(textos_actuales["select_teams"])
selected_teams = st.multiselect(
    label="",
    options=sorted(participants_df['Team'].unique().tolist()),
    help=textos_actuales["tooltip_select_teams"]
)
all_progressions = []

if selected_teams:
    for team in selected_teams:
        team_seeding = seeding_df[seeding_df['Team'] == team]
        if team_seeding.empty:
            continue
        swiss_group = team_seeding['Swiss'].iloc[0]
        swiss_df = swiss_data.get(f"{swiss_group}Swiss")
        if swiss_df is None:
            continue
        _, progression_df = parse_swiss_sheet(team, swiss_df)
        if not progression_df.empty:
            all_progressions.append(progression_df)

if all_progressions:
    combined_progression_df = pd.concat(all_progressions, ignore_index=True)
    fig = crear_grafico_progresion(
        progresiones_df=combined_progression_df,
        titulo_es=textos["es"]["swiss_section"],
        titulo_en=textos["en"]["swiss_section"],
        colores_equipos=team_color_map,
        idioma=idioma  # O la variable que uses para el idioma actual, "Español" o "English"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"##### {textos_actuales['team_details']}")
    for team in selected_teams:
        with st.expander(f"{textos_actuales['team_details']}: {team}"):
            matches_df, _ = parse_swiss_sheet(team, swiss_data[f"{seeding_df[seeding_df.Team == team]['Swiss'].iloc[0]}Swiss"])
            st.markdown(f"###### {textos_actuales['matches']}")
            if not matches_df.empty:
                st.dataframe(matches_df.set_index('Ronda'), use_container_width=True)
            else:
                st.info(textos_actuales["no_matches"])
            st.markdown(f"###### {textos_actuales['final_result']}")
            final_status = textos_actuales["eliminated_swiss"]
            if not participants_df[participants_df['Team'] == team].empty and participants_df[participants_df['Team'] == team]['Standing'].iloc[0] == 74:
                final_status = textos_actuales["dnf_swiss"]
            elif not weezing_df[weezing_df['Team'] == team].empty:
                standing = weezing_df[weezing_df['Team'] == team]['Standing'].iloc[0]
                medal_map = {1: "🥇", 2: "🥈", 3: "🥉"}
                final_status = textos_actuales["weezing_bracket_result"].format(standing=medal_map.get(standing, standing))
            elif not koffing_df[koffing_df['Team'] == team].empty:
                standing = koffing_df[koffing_df['Team'] == team]['Standing'].iloc[0]
                final_status = textos_actuales["koffing_bracket_result"].format(standing=standing)
            st.write(final_status)

# --- Análisis por grupo suizo ---
st.markdown("---")
st.subheader(textos_actuales["swiss_group_section"])
st.markdown(textos_actuales["select_group"])

selected_group = st.selectbox(
    label="",
    options=["Grass", "Fire", "Water", "Electric"],
    help=textos_actuales["tooltip_select_group"]
)

if selected_group:
    teams_in_group = seeding_df[seeding_df['Swiss'] == selected_group]['Team'].tolist()
    swiss_df_group = swiss_data.get(f"{selected_group}Swiss")

    if swiss_df_group is not None:
        all_group_progressions = []
        for team in teams_in_group:
            _, progression_df = parse_swiss_sheet(team, swiss_df_group)
            if not progression_df.empty:
                all_group_progressions.append(progression_df)

        if all_group_progressions:
            combined_group_df = pd.concat(all_group_progressions, ignore_index=True)
            fig_group = crear_grafico_progresion(
                progresiones_df=combined_group_df,
                titulo_es=textos["es"]["group_progression_title"].format(group=selected_group),
                titulo_en=textos["en"]["group_progression_title"].format(group=selected_group),
                colores_equipos=team_color_map,
                idioma=idioma
            )
            st.plotly_chart(fig_group, use_container_width=True)
        else:
            st.warning(textos_actuales.get("no_progression", "No hay progresión para mostrar."))

# --- Brackets ---
st.markdown("---")
st.header(textos_actuales["brackets_section"])

selected_bracket = st.selectbox(
    textos_actuales["select_bracket"],
    textos_actuales["bracket_options"],
    help=textos_actuales["tooltip_select_bracket"],
    index=0
)

if selected_bracket != textos_actuales["bracket_options"][0]:
    st.balloons()

    # Construir título dinámico según idioma
    if idioma == "Español":
        title_prefix = textos_actuales["podium_title"]  # "Podio de Equipos en"
    else:
        title_prefix = textos_actuales["podium_title"]  # "Team Podium in"

    # Si está en el nombre del bracket, para tener un título bonito:
    if "Weezing Bracket" in selected_bracket:
        title = f"{title_prefix} {selected_bracket}"
        chart = create_podium_chart(weezing_df, title=title, idioma=idioma)
    elif "Koffing Bracket" in selected_bracket:
        title = f"{title_prefix} {selected_bracket}"
        chart = create_podium_chart(koffing_df, title=title, idioma=idioma)
    else:
        chart = None

    if chart:
        st.plotly_chart(chart, use_container_width=True)
    else:
        st.warning(textos_actuales["no_chart"])