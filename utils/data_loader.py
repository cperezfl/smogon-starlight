import pandas as pd
import os
import streamlit as st 

def get_class(weapon_name, weapon_class_dict):
    return weapon_class_dict.get(weapon_name, "Unknown")

def get_image_path(weapon_name, base_path, weapon_class_dict):
    weapon_class = weapon_class_dict.get(weapon_name)
    if not weapon_class:
        return None
    image_file = os.path.join(base_path, weapon_class, weapon_name + ".png")
    return image_file if os.path.exists(image_file) else None

def load_and_prepare_data():
    base_dir = os.path.dirname(__file__)  # carpeta /utils
    data_dir = os.path.abspath(os.path.join(base_dir, "..", "data"))
    excel_path = os.path.join(data_dir, "datos.xlsx")
    base_path = os.path.join("images", "Weapons")

    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"No se encontró el archivo Excel en: {excel_path}")
    if not os.path.exists(base_path):
        raise FileNotFoundError(f"No se encontró la carpeta 'Weapons' en: {base_path}")

    xls = pd.ExcelFile(excel_path)
    allowed_df = xls.parse('ALLOWED WEAPONS')
    stats_armas_df = xls.parse('STATS ARMAS')
    stats_mapas_df = xls.parse('STATS MAPAS')

    # Limpieza de nombres de columnas y valores
    allowed_df.columns = allowed_df.columns.str.strip()
    allowed_df = allowed_df.rename(columns={allowed_df.columns[0]: 'WEAPON', allowed_df.columns[1]: 'ALLOWED'}) 
    allowed_df['WEAPON'] = allowed_df['WEAPON'].str.strip()

    stats_armas_df.columns = stats_armas_df.columns.str.strip()
    stats_armas_df = stats_armas_df.rename(columns={stats_armas_df.columns[0]: 'WEAPON'}) 
    stats_armas_df['WEAPON'] = stats_armas_df['WEAPON'].str.strip()

    stats_mapas_df.columns = stats_mapas_df.columns.str.strip()
    stats_mapas_df = stats_mapas_df.rename(columns={stats_mapas_df.columns[0]: 'WEAPON'}) 
    stats_mapas_df['WEAPON'] = stats_mapas_df['WEAPON'].astype(str).str.strip()

    # Recortar hasta la fila de Totales
    end_of_weapons_idx = stats_mapas_df['WEAPON'].str.contains("Total", case=False, na=False).idxmax()
    weapon_usage_df = stats_mapas_df.iloc[:end_of_weapons_idx + 1].copy()

    # Construir diccionario de clases a partir de las carpetas
    weapon_class_dict = {}
    for weapon_class in os.listdir(base_path):
        class_folder = os.path.join(base_path, weapon_class)
        if os.path.isdir(class_folder):
            for f in os.listdir(class_folder):
                name, _ = os.path.splitext(f)
                weapon_class_dict[name.strip()] = weapon_class

    def get_class(weapon_name):
        return weapon_class_dict.get(weapon_name, "Unknown")

    def get_image_path(weapon_name):
        weapon_class = weapon_class_dict.get(weapon_name)
        if not weapon_class:
            return None
        image_file = os.path.join(base_path, weapon_class, weapon_name + ".png")
        return image_file if os.path.exists(image_file) else None

    # Enriquecer allowed_df con clase e imagen
    allowed_df["CLASS"] = allowed_df["WEAPON"].apply(get_class)
    allowed_df["IMAGEPATH"] = allowed_df["WEAPON"].apply(get_image_path)

    # Merge inicial
    merged_df = (
        allowed_df
        .merge(stats_armas_df, on="WEAPON", how="left")
        .merge(weapon_usage_df, on="WEAPON", how="left")
    )
    merged_df["CLASS"] = merged_df["WEAPON"].apply(get_class)
    merged_df["IMAGEPATH"] = merged_df["WEAPON"].apply(get_image_path)

    allowed_weapons_df = merged_df[merged_df['ALLOWED'] == 1].copy()
    not_allowed_weapons_df = merged_df[merged_df['ALLOWED'] == 0].copy()

    # ----------------------------------------
    # Añadir info desde weapons.xlsx (sub y especial + stats)
    # ----------------------------------------
    import re
    from collections import defaultdict

    weapons_path = os.path.join(data_dir, "weapons.xlsx")
    if not os.path.exists(weapons_path):
        raise FileNotFoundError(f"No se encontró el archivo de armas en: {weapons_path}")

    df_weapons = pd.read_excel(weapons_path)

    # Rellenar valores faltantes
    df_weapons["Name"] = df_weapons["Name"].ffill()
    df_weapons["Sub"] = df_weapons["Sub"].ffill()
    df_weapons["Special"] = df_weapons["Special"].ffill()

    # Extraer todos los parámetros dinámicamente
    all_params = defaultdict(dict)
    for i, row in df_weapons.iterrows():
        weapon = row["Name"]
        if isinstance(row["Parameters"], str):
            for line in row["Parameters"].split("\n"):
                match = re.match(r"([\w\s]+):\s*(\d+)", line.strip())
                if match:
                    param_name, value = match.groups()
                    all_params[weapon][param_name.strip()] = int(value)

    # Crear lista única de parámetros encontrados
    all_param_names = sorted({param for params in all_params.values() for param in params})

    # Agregar columnas al dataframe
    for param in all_param_names:
        df_weapons[param] = df_weapons["Name"].map(lambda w: all_params[w].get(param))

    # Eliminar columna original Parameters si está
    df_weapons = df_weapons.drop(columns=["Parameters"], errors="ignore")

    # Agrupar para dejar una fila por arma
    weapons_info_df = df_weapons.groupby(["Name", "Sub", "Special"]).first().reset_index()
    weapons_info_df.rename(columns={"Name": "WEAPON", "Sub": "SUB", "Special": "SPECIAL"}, inplace=True)

    # Añadir imágenes Sub y Special
    specials_path = os.path.abspath(os.path.join(base_dir, "..", "images", "Specials"))
    subs_path = os.path.abspath(os.path.join(base_dir, "..", "images", "Subs"))

    weapons_info_df["SpecialImage"] = weapons_info_df["SPECIAL"].apply(
        lambda s: os.path.join("images", "Specials", f"{s}.png")
        if pd.notna(s) and os.path.exists(os.path.join(specials_path, f"{s}.png"))
        else None
    )
    weapons_info_df["SubImage"] = weapons_info_df["SUB"].apply(
        lambda s: os.path.join("images", "Subs", f"{s}.png")
        if pd.notna(s) and os.path.exists(os.path.join(subs_path, f"{s}.png"))
        else None
    )

    # Hacer merge con los dataframes principales
    merged_df = merged_df.merge(weapons_info_df, on="WEAPON", how="left")
    allowed_weapons_df = allowed_weapons_df.merge(weapons_info_df, on="WEAPON", how="left")
    not_allowed_weapons_df = not_allowed_weapons_df.merge(weapons_info_df, on="WEAPON", how="left")

    # ------------------------------
    # Crear dataframe largo por mapa
    # ------------------------------
    mapa_df = weapon_usage_df.melt(id_vars=["WEAPON"], var_name="MAP", value_name="USAGE")
    mapa_df["MAP"] = mapa_df["MAP"].astype(str).str.strip()
    mapa_df["CLASS"] = mapa_df["WEAPON"].map(weapon_class_dict)
    mapa_df["IMAGEPATH"] = mapa_df["WEAPON"].apply(get_image_path)

    return merged_df, allowed_weapons_df, not_allowed_weapons_df, mapa_df

def load_participant_data():
    base_dir = os.path.dirname(__file__)
    excel_path = os.path.abspath(os.path.join(base_dir, "..", "data", "participants.xlsx"))

    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"No se encontró el archivo de participantes en: {excel_path}")

    xls = pd.ExcelFile(excel_path)
    
    # Usar la primera hoja como fuente principal de equipos y países
    participants_df = xls.parse('SwissBrackets')
    participants_df.columns = participants_df.columns.str.strip()
    participants_df['Team'] = participants_df['Team'].str.strip()

    # Carga de brackets
    weezing_df_raw = xls.parse('WeezingBracket')
    koffing_df_raw = xls.parse('KoffingBracket')

    for df in [weezing_df_raw, koffing_df_raw]:
        df.columns = df.columns.str.strip()
        df.rename(columns={'Rank': 'Standing'}, inplace=True)
        df['Team'] = df['Team'].str.strip()

    # Merge para añadir países a los brackets
    country_lookup = participants_df[['Team', 'Country']].copy().drop_duplicates(subset=['Team'])
    weezing_df = pd.merge(weezing_df_raw, country_lookup, on='Team', how='left')
    koffing_df = pd.merge(koffing_df_raw, country_lookup, on='Team', how='left')
    weezing_df['Country'].fillna('❓', inplace=True)
    koffing_df['Country'].fillna('❓', inplace=True)
    
    # --- LÓGICA DE COLORES (IMPORTANTE) ---
    splatoon_colors = {
        '🇺🇸': '#39FF14',  '🇩🇯': '#FF6F00',  '🇫🇷': '#FF00FF',  '🇦🇮': '#00FFFF', 
        '🇲🇽': '#1B03A3',  '🇨🇨': '#FF1493',  '🇭🇷': '#1B03A3',  '🇵🇪': '#00FFFF',
        '🇦🇷': '#FF1493',  '🇨🇦': '#00FFFF',  '🇧🇷': '#FF6F00',  '🇵🇦': '#FF1493',
        '🇪🇸': '#1B03A3',  '🇪🇺': '#FF1493',  '🇵🇷': '#FF1493',  '🇨🇱': '#FFFF00',
        '🇩🇪': '#00FFFF',  '🇮🇲': '#FFFF00',
    }
    participants_df['SplatoonColor'] = participants_df['Country'].map(lambda c: splatoon_colors.get(c, '#CCCCCC'))

    return participants_df, weezing_df, koffing_df

@st.cache_data
def load_tournament_journey_data():
    """Carga todas las hojas necesarias para el seguimiento de la trayectoria de un equipo."""
    base_dir = os.path.dirname(__file__)
    excel_path = os.path.abspath(os.path.join(base_dir, "..", "data", "participants.xlsx"))

    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"No se encontró el archivo de participantes en: {excel_path}")

    xls = pd.ExcelFile(excel_path)

    seeding_df = xls.parse('SeedingOriginal')
    seeding_df.columns = seeding_df.columns.str.strip()
    seeding_df['Team'] = seeding_df['Team'].str.strip()

    swiss_sheets = ['GrassSwiss', 'FireSwiss', 'ElectricSwiss', 'WaterSwiss']
    swiss_data = {}
    for sheet in swiss_sheets:
        df = xls.parse(sheet, header=None)
        swiss_data[sheet] = df

    return seeding_df, swiss_data

def cargar_datos_participantes():
    """
    Carga los datos de participantes, brackets y fase suiza.
    Devuelve todos los DataFrames y un diccionario con los colores por equipo.
    """
    participants_df, weezing_df, koffing_df = load_participant_data()
    seeding_df, swiss_data = load_tournament_journey_data()

    # Crear diccionario de colores por equipo (usado en los gráficos)
    color_map = pd.Series(participants_df.SplatoonColor.values, index=participants_df.Team).to_dict()

    return participants_df, weezing_df, koffing_df, seeding_df, swiss_data, color_map

def load_weapons_info():
    import re

    base_dir = os.path.dirname(__file__)
    weapons_path = os.path.abspath(os.path.join(base_dir, "..", "data", "weapons.xlsx"))

    if not os.path.exists(weapons_path):
        raise FileNotFoundError(f"No se encontró el archivo de armas en: {weapons_path}")

    raw_df = pd.read_excel(weapons_path)
    raw_df.columns = raw_df.columns.str.strip()

    # Creamos una nueva lista para armar el DataFrame limpio
    weapons_data = []
    current_weapon = {}

    for _, row in raw_df.iterrows():
        if pd.notna(row['Name']):
            # Si ya tenemos un arma previa, la guardamos
            if current_weapon:
                weapons_data.append(current_weapon)
            # Iniciamos nuevo arma
            current_weapon = {
                "Name": row["Name"].strip(),
                "Sub": row["Sub"].strip() if pd.notna(row["Sub"]) else None,
                "Special": row["Special"].strip() if pd.notna(row["Special"]) else None,
                "Range": None,
                "Damage": None,
                "Fire Rate": None
            }

            # Extraer primer parámetro de la fila actual
            param_text = str(row.get("Parameters", ""))
        else:
            param_text = str(row.get("Parameters", ""))

        # Extraer valores de estadísticas
        for stat in ["Range", "Damage", "Fire Rate"]:
            match = re.search(fr"{stat}:\s*([0-9]+)", param_text)
            if match:
                current_weapon[stat] = int(match.group(1))

    # No olvidar guardar la última arma procesada
    if current_weapon:
        weapons_data.append(current_weapon)

    weapons_df = pd.DataFrame(weapons_data)

    # Agregar imágenes
    subs_path = os.path.abspath(os.path.join(base_dir, "..", "images", "Subs"))
    specials_path = os.path.abspath(os.path.join(base_dir, "..", "images", "Specials"))

    weapons_df["SubImage"] = weapons_df["Sub"].apply(
        lambda s: os.path.join("images", "Subs", f"{s}.png") if pd.notna(s) and os.path.exists(os.path.join(subs_path, f"{s}.png")) else None
    )
    weapons_df["SpecialImage"] = weapons_df["Special"].apply(
        lambda s: os.path.join("images", "Specials", f"{s}.png") if pd.notna(s) and os.path.exists(os.path.join(specials_path, f"{s}.png")) else None
    )

    return weapons_df