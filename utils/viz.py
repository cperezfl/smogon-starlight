import streamlit as st
import io
from PIL import Image
from io import BytesIO
import base64
from utils.color_manager import ColorManager
import plotly.graph_objects as go
import pandas as pd
import os
from matplotlib.colors import to_rgba
import re
import plotly.express as px
import numpy as np

st.markdown("""
    <style>
    /* Quitar fondo blanco de los captions e imágenes */
    .stImage img {
        background-color: transparent !important;
    }

    .stCaption {
        color: white !important;
        background-color: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

color_clases = {
    "Shooters": "#FF5FA2",
    "Blasters": "#00E1FF",
    "Brellas": "#FCD800",
    "Brushes": "#7CFC00",
    "Chargers": "#FF6600",
    "Dualies": "#A020F0",
    "Rollers": "#FFD700",
    "Sloshers": "#00BFFF",
    "Splatlings": "#FF4500",
    "Stringers": "#9400D3"
}
color_manager = ColorManager(color_clases, variation_strength=0.15, brighten_only=True)

def encode_image_to_base64(imagepath):
    # Asegúrate de que la ruta existe antes de intentar abrirla
    if not imagepath or not os.path.exists(imagepath):
        return None
    with open(imagepath, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return f"data:image/png;base64,{encoded}"

def mostrar_arma_grid(df, title, columns=6, image_size=(100, 100)):
    st.markdown(f"### {title}")
    weapons = df["WEAPON"].tolist()
    images = df["IMAGEPATH"].tolist()

    rows = (len(images) + columns - 1) // columns
    for i in range(rows):
        cols = st.columns(columns)
        for j in range(columns):
            idx = i * columns + j
            if idx < len(images):
                with cols[j]:
                    try:
                        img = Image.open(images[idx])
                        img.thumbnail(image_size)
                        st.image(img)
                        st.caption(weapons[idx])
                    except:
                        st.text(weapons[idx])

def image_to_base64(path):
    try:
        with Image.open(path) as img:
            img.thumbnail((100, 100))
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode()
    except:
        return None

def barplot_armas_con_imagenes(df, color_manager, textos):
    label_to_column = {
        textos["all_modes"]: "TOTAL",
        textos["splat_zones"]: "SPLAT ZONES",
        textos["tower_control"]: "TOWER CONTROL",
        textos["rainmaker"]: "RAINMAKER",
        textos["clam_blitz"]: "CLAM BLITZ"
    }

    modo_amigable = st.selectbox(
        textos.get("selectbox_label", "Selecciona el tipo de uso:"),
        list(label_to_column.keys())
    )
    modo = label_to_column[modo_amigable]

    df_modo = df.copy()
    df_modo = df_modo[df_modo[modo] > 0]
    df_modo = df_modo.sort_values(by=modo, ascending=False).reset_index(drop=True)

    if df_modo.empty:
        st.warning(textos["no_data_warning"])
        return

    max_top = st.slider(
        f"{textos['top_label']} {modo_amigable}",
        min_value=10,
        max_value=min(50, len(df_modo)),
        value=min(10, len(df_modo)),
        step=1,
    )

    df_modo = df_modo.head(max_top)
    df_modo["x_pos"] = df_modo.index

    bar_colors = [
        color_manager.get_color(row["CLASS"], row["WEAPON"])
        for _, row in df_modo.iterrows()
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_modo["x_pos"],
        y=df_modo[modo],
        marker_color=bar_colors,
        text=df_modo["WEAPON"],
        customdata=df_modo[["CLASS", modo]],
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Clase: %{customdata[0]}<br>"
            f"{modo_amigable}<br>"
            "Usos: %{customdata[1]}<extra></extra>"
        ),
        showlegend=False
    ))

    # Añadir imagen encima de cada barra
    for _, row in df_modo.iterrows():
        img_uri = encode_image_to_base64(row["IMAGEPATH"])
        if img_uri:
            fig.add_layout_image(
                dict(
                    source=img_uri,
                    x=row["x_pos"],
                    y=row[modo],
                    xref="x",
                    yref="y",
                    sizex=0.8,
                    sizey=15,
                    xanchor="center",
                    yanchor="bottom",
                    layer="above"
                )
            )

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=df_modo["x_pos"],
            ticktext=df_modo["WEAPON"],
            title=textos["xaxis_title"],
        ),
        yaxis=dict(title=f"{textos['yaxis_title']} {modo_amigable}"),
        height=700,
        margin=dict(t=120),
        title=f"{textos['top_title']} {max_top} {textos['top_title_suffix']} {modo_amigable}",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig, use_container_width=True)

def mapa_dominancia_por_clase(df, mapa, color_manager, opacity_bloque, opacity_arma, textos):
    df_mapa = df[df["MAP"] == mapa].copy()
    df_mapa = df_mapa[(df_mapa["USAGE"] > 0) & (df_mapa["CLASS"].notna())]

    if df_mapa.empty:
        st.warning(textos["no_data_warning"])
        return

    uso_por_clase = df_mapa.groupby("CLASS")["USAGE"].sum().reset_index().rename(columns={"USAGE": "TOTAL_USAGE_CLASS"})
    df_mapa_sorted = df_mapa.sort_values(by="USAGE", ascending=False)
    arma_dominante = df_mapa_sorted.drop_duplicates(subset=["CLASS"], keep="first")[["CLASS", "WEAPON", "IMAGEPATH", "USAGE"]].rename(columns={"USAGE": "WEAPON_USAGE"})

    dominancia = pd.merge(uso_por_clase, arma_dominante, on="CLASS").sort_values(by="TOTAL_USAGE_CLASS", ascending=False)

    total_usos = dominancia["TOTAL_USAGE_CLASS"].sum()
    dominancia["PERCENT"] = dominancia["TOTAL_USAGE_CLASS"] / total_usos if total_usos > 0 else 0

    # Partición en columnas
    num_cols = 3
    cols_data = [[] for _ in range(num_cols)]
    cols_height = [0.0] * num_cols

    for _, row in dominancia.iterrows():
        shortest_col_idx = cols_height.index(min(cols_height))
        cols_data[shortest_col_idx].append(row)
        cols_height[shortest_col_idx] += row["PERCENT"]

    final_coords = []
    col_width = 1.0 / num_cols
    for i, col in enumerate(cols_data):
        y_cursor = 0
        total_col_height = sum(item["PERCENT"] for item in col)
        if total_col_height == 0:
            continue

        for item in col:
            y1 = 1 - y_cursor
            block_height = item["PERCENT"] / total_col_height
            y0 = y1 - block_height
            coords = {
                "CLASS": item["CLASS"],
                "x0": i * col_width, "y0": y0,
                "x1": (i + 1) * col_width, "y1": y1
            }
            final_coords.append(coords)
            y_cursor += block_height

    dominancia = pd.merge(dominancia, pd.DataFrame(final_coords), on="CLASS")

    fig = go.Figure()

    annotations = []
    weapon_images = []

    for _, row in dominancia.iterrows():
        centro_x = (row['x0'] + row['x1']) / 2
        centro_y = (row['y0'] + row['y1']) / 2
        block_width = row['x1'] - row['x0']
        block_height = row['y1'] - row['y0']

        fig.add_shape(type="rect", xref="paper", yref="paper",
                      x0=row['x0'], y0=row['y0'], x1=row['x1'], y1=row['y1'],
                      line=dict(color="rgba(0,0,0,0.5)", width=4),
                      fillcolor=color_manager.get_color(row["CLASS"], row["CLASS"]),
                      opacity=opacity_bloque, layer="below")

        img_size = min(block_width, block_height) * 0.5
        encoded_weapon = encode_image_to_base64(row["IMAGEPATH"])
        if encoded_weapon:
            weapon_images.append(go.layout.Image(
                source=encoded_weapon, xref="paper", yref="paper",
                x=centro_x, y=centro_y,
                sizex=img_size, sizey=img_size,
                xanchor="center", yanchor="middle",
                opacity=opacity_arma, layer="above"
            ))

        text_scale_factor = min(block_width * 3, block_height)

        annotations.append(go.layout.Annotation(
            x=centro_x, y=centro_y + (block_height * 0.3),
            xref="paper", yref="paper",
            text=f"<b>{row['CLASS']}: {int(row['TOTAL_USAGE_CLASS'])} {textos['uses']}</b>",
            showarrow=False, font=dict(color="white", size=max(10, text_scale_factor * 40)),
            align="center",
            xanchor="center"
        ))

        annotations.append(go.layout.Annotation(
            x=centro_x, y=centro_y - (block_height * 0.3),
            xref="paper", yref="paper",
            text=f"<i>{row['WEAPON']}</i><br>({int(row['WEAPON_USAGE'])} {textos['uses']})",
            showarrow=False, font=dict(color="white", size=max(8, text_scale_factor * 30)),
            align="center",
            xanchor="center"
        ))

    all_images = []
    map_image_path = f"images/Maps/{mapa}.png"
    if os.path.exists(map_image_path):
        all_images.append(go.layout.Image(
            source=encode_image_to_base64(map_image_path),
            xref="paper", yref="paper", x=0, y=1, sizex=1, sizey=1,
            xanchor="left", yanchor="top", layer="below", sizing="stretch"
        ))

    all_images.extend(weapon_images)

    fig.update_layout(
        height=720,
        margin=dict(t=60, r=20, l=20, b=20),
        title=dict(text=f"{textos['title']} {mapa}", font=dict(size=24)),
        xaxis=dict(showgrid=False, zeroline=False, visible=False, range=[0, 1]),
        yaxis=dict(showgrid=False, zeroline=False, visible=False, range=[0, 1]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        images=all_images,
        annotations=annotations
    )

    st.plotly_chart(fig, use_container_width=True)

def tuple_to_rgba_string(t):
    # t es (r, g, b, a) con valores entre 0 y 1
    r, g, b, a = t
    return f'rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, {a})'

def plot_radar_arma(df, arma, color_manager):

    def tuple_to_rgba_string(t):
        r, g, b, a = t
        return f'rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, {a})'

    modos = ["SPLAT ZONES", "TOWER CONTROL", "RAINMAKER", "CLAM BLITZ"]
    df_arma = df[df["WEAPON"] == arma]

    if df_arma.empty:
        return None, f"No se encontró información para el arma {arma}."

    valores = [df_arma[modo].values[0] for modo in modos]
    valores += [valores[0]]
    modos_cerrados = modos + [modos[0]]

    color_base = color_manager.get_color(df_arma["CLASS"].values[0], arma)
    fill_color = tuple_to_rgba_string(to_rgba(color_base, alpha=0.4))
    line_color = tuple_to_rgba_string(to_rgba(color_base, alpha=0.8))

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=valores,
        theta=modos_cerrados,
        fill='toself',
        fillcolor=fill_color,
        line=dict(color=line_color, width=3),
        name=arma,
        hoverinfo='all'
    ))


    img_path = df_arma["IMAGEPATH"].values[0]
    if img_path and os.path.exists(img_path):
        with open(img_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
        fig.add_layout_image(
            dict(
                source=f"data:image/png;base64,{encoded}",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                sizex=0.3,
                sizey=0.3,
                xanchor="center",
                yanchor="middle",
                layer="above",
                sizing="contain",
                opacity=1.0
            )
        )

    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, showticklabels=True, linewidth=1, gridcolor='gray', linecolor='gray'),
            angularaxis=dict(tickfont=dict(size=12)),
        ),
        showlegend=False,
        margin=dict(t=50, b=50, l=50, r=50),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white")
    )

    emoji_map = {
        "Range": "📏",
        "Damage": "💥",
        "Fire Rate": "🔥",
        "Charge Speed": "⚡",
        "Mobility": "🏃",
        "Ink Speed": "🖌️",
        "Handling": "🎮",
        "Impact": "🔨",
        "Durability": "🛡️"
    }

    stats_text = f"### 🎯 Estadísticas de {arma} 🛡️\n"
    stats_mostradas = 0
    posibles_stats = ["Range", "Damage", "Fire Rate", "Charge Speed", "Mobility", "Ink Speed", "Handling", "Impact", "Durability"]
    for stat in posibles_stats:
        if stat in df_arma.columns:
            valor = df_arma[stat].values[0]
            if valor is not None and valor != 0 and not pd.isna(valor):
                stats_text += f"- {emoji_map.get(stat, '')} **{stat}**: {valor}\n"
                stats_mostradas += 1
                if stats_mostradas == 3:
                    break

    return fig, stats_text

def pil_image_to_base64(im):
    buffered = BytesIO()
    im.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return "data:image/png;base64," + img_str

def plot_nolan(df, especiales_seleccionadas, modos, textos, textos_modos, img_column="SpecialImage", img_size=3):
    df_filtrado = df[df["SPECIAL"].isin(especiales_seleccionadas)]
    uso_por_especial = df_filtrado.groupby("SPECIAL")[modos].sum()

    # Asegurar que los valores sean positivos antes de hacer resta
    for modo in modos:
        uso_por_especial[modo] = uso_por_especial[modo].apply(lambda x: max(x, 0))

    uso_por_especial["X"] = uso_por_especial[modos[1]] - uso_por_especial[modos[0]]
    uso_por_especial["Y"] = uso_por_especial[modos[2]] - uso_por_especial[modos[3]]

    # Cargar imágenes de los especiales
    imagenes = {}
    for especial in especiales_seleccionadas:
        posibles_imgs = df_filtrado.loc[df_filtrado["SPECIAL"] == especial, img_column].dropna().unique()
        img_path = next((p for p in posibles_imgs if os.path.exists(p)), None)
        if img_path:
            im = Image.open(img_path)
            imagenes[especial] = pil_image_to_base64(im)
        else:
            imagenes[especial] = None

    fig = go.Figure()

    fixed_xrange = [-15, 15]
    fixed_yrange = [-16, 16]

    for especial, row in uso_por_especial.iterrows():
        x, y = row["X"], row["Y"]
        hover_text = f"<b>{especial}</b><br>"
        for modo in modos:
            modo_legible = textos_modos.get(modo.lower().replace(" ", "_"), modo)
            hover_text += f"{modo_legible}: {int(row[modo])}<br>"

        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers',
            marker=dict(size=img_size * 3, color='rgba(0,0,0,0)'),
            hoverinfo='text',
            hovertext=hover_text,
            showlegend=False
        ))

        img_data = imagenes.get(especial)
        if img_data:
            fig.add_layout_image(
                dict(
                    source=img_data,
                    xref="x",
                    yref="y",
                    x=x,
                    y=y,
                    sizex=img_size,
                    sizey=img_size,
                    xanchor="center",
                    yanchor="middle",
                    layer="above",
                    sizing="contain",
                    opacity=1.0,
                )
            )

    # Formatear títulos de ejes con nombres legibles
    xaxis_title = textos["eje_x"].format(
        modo0=textos_modos.get(modos[0].lower().replace(" ", "_"), modos[0]),
        modo1=textos_modos.get(modos[1].lower().replace(" ", "_"), modos[1]),
        modo2=textos_modos.get(modos[2].lower().replace(" ", "_"), modos[2]),
        modo3=textos_modos.get(modos[3].lower().replace(" ", "_"), modos[3]),
    )
    yaxis_title = textos["eje_y"].format(
        modo0=textos_modos.get(modos[0].lower().replace(" ", "_"), modos[0]),
        modo1=textos_modos.get(modos[1].lower().replace(" ", "_"), modos[1]),
        modo2=textos_modos.get(modos[2].lower().replace(" ", "_"), modos[2]),
        modo3=textos_modos.get(modos[3].lower().replace(" ", "_"), modos[3]),
    )

    fig.update_layout(
        title=textos["titulo_nolan_especiales"],
        xaxis=dict(
            title=xaxis_title,
            range=fixed_xrange,
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='gray',
            showgrid=True,
            scaleanchor="y",
            scaleratio=1,
        ),
        yaxis=dict(
            title=yaxis_title,
            range=fixed_yrange,
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='gray',
            showgrid=True,
            scaleanchor="x",
            scaleratio=1,
        ),
        width=700,
        height=700,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40),
    )

    return fig

def pil_image_to_base64_dendo(img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()

def plot_nolan_subs(df, subs_seleccionados, modos, textos, textos_modos, img_column="SubImage", img_size=3):
    df_filtrado = df[df["SUB"].isin(subs_seleccionados)]
    uso_por_sub = df_filtrado.groupby("SUB")[modos].sum()

    for modo in modos:
        uso_por_sub[modo] = uso_por_sub[modo].apply(lambda x: max(x, 0))

    uso_por_sub["X"] = uso_por_sub[modos[1]] - uso_por_sub[modos[0]]
    uso_por_sub["Y"] = uso_por_sub[modos[2]] - uso_por_sub[modos[3]]

    # Cargar imágenes de los subs
    imagenes = {}
    for sub in subs_seleccionados:
        posibles_imgs = df_filtrado.loc[df_filtrado["SUB"] == sub, img_column].dropna().unique()
        img_path = next((p for p in posibles_imgs if os.path.exists(p)), None)
        if img_path:
            im = Image.open(img_path)
            imagenes[sub] = pil_image_to_base64(im)
        else:
            imagenes[sub] = None

    fig = go.Figure()

    fixed_xrange = [-20, 20]
    fixed_yrange = [-20, 20]

    for sub, row in uso_por_sub.iterrows():
        x, y = row["X"], row["Y"]
        hover_text = f"<b>{sub}</b><br>"
        for modo in modos:
            modo_legible = textos_modos.get(modo.lower().replace(" ", "_"), modo)
            hover_text += f"{modo_legible}: {int(row[modo])}<br>"

        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers',
            marker=dict(size=img_size * 3, color='rgba(0,0,0,0)'),
            hoverinfo='text',
            hovertext=hover_text,
            showlegend=False
        ))

        img_data = imagenes.get(sub)
        if img_data:
            fig.add_layout_image(
                dict(
                    source=img_data,
                    xref="x", yref="y",
                    x=x, y=y,
                    sizex=img_size, sizey=img_size,
                    xanchor="center", yanchor="middle",
                    layer="above", sizing="contain", opacity=1.0,
                )
            )

    xaxis_title = textos["eje_x"].format(
        modo0=textos_modos.get(modos[0].lower().replace(" ", "_"), modos[0]),
        modo1=textos_modos.get(modos[1].lower().replace(" ", "_"), modos[1]),
        modo2=textos_modos.get(modos[2].lower().replace(" ", "_"), modos[2]),
        modo3=textos_modos.get(modos[3].lower().replace(" ", "_"), modos[3]),
    )
    yaxis_title = textos["eje_y"].format(
        modo0=textos_modos.get(modos[0].lower().replace(" ", "_"), modos[0]),
        modo1=textos_modos.get(modos[1].lower().replace(" ", "_"), modos[1]),
        modo2=textos_modos.get(modos[2].lower().replace(" ", "_"), modos[2]),
        modo3=textos_modos.get(modos[3].lower().replace(" ", "_"), modos[3]),
    )

    fig.update_layout(
        title=textos["titulo_nolan_subs"],
        xaxis=dict(
            title=xaxis_title,
            range=fixed_xrange,
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='gray',
            showgrid=True,
            scaleanchor="y",
            scaleratio=1,
        ),
        yaxis=dict(
            title=yaxis_title,
            range=fixed_yrange,
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='gray',
            showgrid=True,
            scaleanchor="x",
            scaleratio=1,
        ),
        width=700,
        height=700,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40),
    )

    return fig

def mostrar_mapa_equipos_por_pais(participants_df, idioma):
    flag_map = {
        '🇺🇸': ('USA', 'Estados Unidos'), '🇩🇯': ('DJI', 'Yibuti'), '🇫🇷': ('FRA', 'Francia'),
        '🇦🇮': ('AIA', 'Anguila'), '🇲🇽': ('MEX', 'México'), '🇨🇨': ('CCK', 'Islas Cocos'),
        '🇭🇷': ('HRV', 'Croacia'), '🇦🇷': ('ARG', 'Argentina'), '🇨🇦': ('CAN', 'Canadá'),
        '🇧🇷': ('BRA', 'Brasil'), '🇵🇪': ('PER', 'Perú'), '🇵🇦': ('PAN', 'Panamá'),
        '🇪🇸': ('ESP', 'España'), '🇪🇺': ('EUR', 'Unión Europea'), '🇵🇷': ('PRI', 'Puerto Rico'),
        '🇨🇱': ('CHL', 'Chile'), '🇩🇪': ('DEU', 'Alemania'), '🇮🇲': ('IMN', 'Isla de Man')
    }

    nombres_en = {
        'Estados Unidos': 'United States', 'Yibuti': 'Djibouti', 'Francia': 'France',
        'Anguila': 'Anguilla', 'México': 'Mexico', 'Islas Cocos': 'Cocos Islands',
        'Croacia': 'Croatia', 'Argentina': 'Argentina', 'Canadá': 'Canada',
        'Brasil': 'Brazil', 'Perú': 'Peru', 'Panamá': 'Panama',
        'España': 'Spain', 'Unión Europea': 'European Union', 'Puerto Rico': 'Puerto Rico',
        'Chile': 'Chile', 'Alemania': 'Germany', 'Isla de Man': 'Isle of Man'
    }

    splatoon_colors = {
        '🇺🇸': '#39FF14',  '🇩🇯': '#FF6F00',  '🇫🇷': '#FF00FF',  '🇦🇮': '#00FFFF',
        '🇲🇽': '#1B03A3',  '🇨🇨': '#FF1493',  '🇭🇷': '#1B03A3',  '🇵🇪': '#00FFFF',
        '🇦🇷': '#FF1493',  '🇨🇦': '#00FFFF',  '🇧🇷': '#FF6F00',  '🇵🇦': '#FF1493',
        '🇪🇸': '#1B03A3',  '🇪🇺': '#FF1493',  '🇵🇷': '#FF1493',  '🇨🇱': '#FFFF00',
        '🇩🇪': '#00FFFF',  '🇮🇲': '#FFFF00',
    }

    # Preparar DataFrame
    participants_df['ISO'] = participants_df['Country'].map(lambda c: flag_map.get(c, (None, None))[0])
    participants_df['CountryNameEs'] = participants_df['Country'].map(lambda c: flag_map.get(c, (None, None))[1])

    if idioma == "English":
        participants_df['CountryName'] = participants_df['CountryNameEs'].map(nombres_en).fillna(participants_df['CountryNameEs'])
    else:
        participants_df['CountryName'] = participants_df['CountryNameEs']

    # Agrupar por país
    df_grouped = participants_df.groupby(['ISO', 'CountryName', 'Country']).size().reset_index(name='Team Count')
    df_grouped['Color'] = df_grouped['Country'].map(lambda c: splatoon_colors.get(c, '#CCCCCC'))

    # Mapear cada país a un índice para colorscale
    df_grouped = df_grouped.reset_index(drop=True)
    df_grouped['color_idx'] = df_grouped.index.astype(float)

    # Crear colorscale para que cada índice tenga su color fijo
    colorscale = []
    n = len(df_grouped)
    for i, color in enumerate(df_grouped['Color']):
        position = i / max(n - 1, 1)  # Normalizar entre 0 y 1
        colorscale.append([position, color])

    # Coordenadas para los países
    coords = {
        'USA': (-97, 38), 'DJI': (42.6, 11.8), 'FRA': (2.2, 46.2), 'AIA': (-63, 18.2), 'MEX': (-102, 23),
        'CCK': (96.8, -12.1), 'HRV': (15.2, 45.1), 'ARG': (-63.6, -38.4), 'CAN': (-106.3, 56.1),
        'BRA': (-51.9, -14.2), 'PER': (-75, -9.2), 'PAN': (-80.7, 8.5), 'ESP': (-3.7, 40.4),
        'EUR': (4.3, 50.8), 'PRI': (-66.5, 18.2), 'CHL': (-71.5, -35.6), 'DEU': (10.4, 51.1),
        'IMN': (-4.5, 54.2)
    }

    fig = go.Figure()

    # Choropleth para colorear países
    fig.add_trace(go.Choropleth(
        locations=df_grouped['ISO'],
        z=df_grouped['color_idx'],
        colorscale=colorscale,
        showscale=False,
        marker_line_color='black',
        marker_line_width=0.5,
        hoverinfo='skip'
    ))

    # Agregar puntos con número dentro
    for _, row in df_grouped.iterrows():
        lon, lat = coords.get(row['ISO'], (None, None))
        if lon is None or lat is None:
            continue
        fig.add_trace(go.Scattergeo(
            lon=[lon],
            lat=[lat],
            mode='markers+text',
            text=[row['Team Count']],
            textposition='middle center',
            marker=dict(size=30, color=row['Color'], line=dict(color='white', width=1)),
            textfont=dict(color='black', size=14, family='Arial'),
            name=row['CountryName'],
            hovertemplate=f"<b>{row['CountryName']}</b><br>Equipos: {row['Team Count']}<extra></extra>"
        ))

    fig.update_layout(
        title_text="🌎 Número de equipos por país" if idioma == "Español" else "🌎 Number of teams per country",
        geo=dict(
            showland=True,
            landcolor='rgb(30,30,30)',
            bgcolor='rgba(0,0,0,0)',
            projection_type='natural earth',
            showframe=False,
            showcountries=True,
            countrycolor="white"
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=40, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)

def create_podium_chart(df, title="", idioma="Español"):
    if df.empty:
        st.warning(f"No hay datos para mostrar el podio de {title}.")
        return None

    top_teams = df.nsmallest(8, 'Standing').sort_values('Standing', ascending=False)
    podium_colors = {1: '#FFD700', 2: '#C0C0C0', 3: '#CD7F32'}
    default_color = '#00E1FF'
    colors = [podium_colors.get(rank, default_color) for rank in top_teams['Standing']]
    y_labels = [f"{row['Country']} {row['Team']}" for _, row in top_teams.iterrows()]
    max_rank = top_teams['Standing'].max()

    # Escala proporcional lineal
    bar_values = (max_rank - top_teams['Standing'] + 1) / max_rank
    # O para suavizar diferencias, puedes usar esta línea en lugar de la anterior:
    # bar_values = np.sqrt(bar_values)

    fig = go.Figure(go.Bar(
        x=bar_values,
        y=y_labels,
        orientation='h',
        marker=dict(color=colors, line=dict(color='white', width=1)),
        text=top_teams['Standing'],
        textposition='auto',
        texttemplate='<b>#%{text}</b>',
        hoverinfo='y'
    ))

    fig.update_layout(
        title_text=title or ('Podio de Equipos' if idioma == "Español" else "Team Podium"),
        template="plotly_dark",
        showlegend=False,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    return fig
def parse_swiss_sheet(team_name: str, swiss_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extrae información de partidas y progresión de ranking en la fase suiza para un equipo específico.

    Parámetros:
        team_name (str): Nombre del equipo a analizar.
        swiss_df (pd.DataFrame): DataFrame con los datos crudos de la fase suiza.

    Retorna:
        tuple: Dos DataFrames:
            - matches_df: con columnas ["Ronda", "Oponente", "Resultado"]
            - progression_df: con columnas ["Team", "Ronda", "Rank", "Récord"] (W-T-L)
    """
    matches = []
    progression = []

    # Índices donde aparecen los headers de cada ronda
    round_indices = swiss_df[swiss_df[0].astype(str).str.contains("Round", na=False)].index

    for i, start_round_idx in enumerate(round_indices):
        round_header = swiss_df.loc[start_round_idx, 0]
        current_round_num = int(re.search(r'\d+', round_header).group(0))

        # Definir el bloque de la ronda
        end_round_idx = round_indices[i + 1] if i + 1 < len(round_indices) else len(swiss_df)
        round_block = swiss_df.iloc[start_round_idx:end_round_idx]

        # Buscar índice de partidas y rankings dentro del bloque
        match_header_idx = round_block[round_block[0].astype(str).str.contains("#", na=False)].index
        rank_header_idx = round_block[round_block[0].astype(str).str.contains("Rank", na=False)].index

        # Procesar partidas
        if not match_header_idx.empty and not rank_header_idx.empty:
            matches_table = round_block.loc[match_header_idx[0] + 1: rank_header_idx[0] - 1]
            for _, row in matches_table.iterrows():
                # Comprobar que las columnas necesarias no sean NaN
                if pd.isna(row[2]) or pd.isna(row[4]):
                    continue

                team1, result, team2 = str(row[2]).strip(), str(row[3]).strip(), str(row[4]).strip()

                if team_name == team1:
                    matches.append({"Ronda": current_round_num, "Oponente": team2, "Resultado": result})
                    break
                elif team_name == team2:
                    # Invertir resultado (ejemplo "2:1" a "1:2")
                    try:
                        s1, s2 = result.split(':')
                        inverted_result = f"{s2.strip()}:{s1.strip()}"
                    except Exception:
                        inverted_result = result
                    matches.append({"Ronda": current_round_num, "Oponente": team1, "Resultado": inverted_result})
                    break

        # Procesar ranking y récord
        if not rank_header_idx.empty:
            rank_table = round_block.loc[rank_header_idx[0] + 1:]

            # Buscar el equipo en la tabla
            team_rank_info = rank_table[rank_table[2].astype(str).str.strip() == team_name]

            if not team_rank_info.empty:
                # Acceso por posición para evitar problemas con nombres de columnas
                rank = int(team_rank_info.iloc[0, 0])
                w = int(team_rank_info.iloc[0, 3])  # Wins
                t = int(team_rank_info.iloc[0, 4])  # Ties
                l = int(team_rank_info.iloc[0, 5])  # Losses

                progression.append({
                    "Team": team_name,
                    "Ronda": current_round_num,
                    "Rank": rank,
                    "Récord": f"{w}-{t}-{l}"
                })

    matches_df = pd.DataFrame(matches)
    progression_df = pd.DataFrame(progression)

    return matches_df, progression_df

def crear_grafico_progresion(progresiones_df, titulo_es, titulo_en, colores_equipos, idioma="Español"):
    """
    Crea un gráfico de línea para mostrar la progresión del ranking en la fase suiza,
    con soporte multilingüe y mejor escala en eje Y para los primeros lugares.

    Parámetros:
        progresiones_df (pd.DataFrame): columnas ['Team', 'Ronda', 'Rank', 'Récord'].
        titulo_es (str): Título en español.
        titulo_en (str): Título en inglés.
        colores_equipos (dict): Mapeo equipo -> color.
        idioma (str): "Español" o "English".

    Retorna:
        fig (plotly.graph_objs._figure.Figure)
    """

    titulo = titulo_es if idioma == "Español" else titulo_en
    labels = {
        "Rank": "Posición en el Grupo" if idioma == "Español" else "Group Position",
        "Team": "Equipo" if idioma == "Español" else "Team",
        "Ronda": "Ronda" if idioma == "Español" else "Round"
    }

    fig = px.line(
        progresiones_df,
        x="Ronda",
        y="Rank",
        color="Team",
        title=titulo,
        markers=True,
        labels=labels,
        custom_data=["Récord"],
        color_discrete_map=colores_equipos
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{data.name}</b><br>" +
            ( "Ronda %{x}<br>" if idioma == "Español" else "Round %{x}<br>") +
            "Posición: %{y}<br>" +
            "Récord: %{customdata[0]}<extra></extra>"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        legend_title_text=labels["Team"],
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    if not progresiones_df.empty:
        max_rank = int(progresiones_df['Rank'].max())
        # Crear tickvals para eje Y, con un paso de 1 desde 1 hasta max_rank
        tickvals = list(range(1, max_rank + 1))

        # Ajustar ticktext para posicionar los 3 primeros más juntos (opcional, ejemplo)
        # Aquí simplemente dejamos los ticks iguales pero invertidos
        fig.update_yaxes(
            autorange="reversed",
            tickvals=tickvals,
            tickmode="array",
            title=labels["Rank"],
            dtick=1
        )
    else:
        fig.update_yaxes(autorange="reversed")

    fig.update_xaxes(nticks=5, title=labels["Ronda"])

    return fig