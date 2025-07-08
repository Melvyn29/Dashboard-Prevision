import streamlit as st
import pandas as pd
import json
import os
from io import BytesIO
from config.mappings import MONTH_MAP

def load_json_data():
    """
    Charge les données à partir du fichier JSON.

    Returns:
        dict: Données chargées, ou dictionnaire vide en cas d'erreur.
    """
    json_file = "pn_data.json"
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            for pn in data.get('pn_data', {}):
                df = pd.DataFrame(data['pn_data'][pn])
                if not all(col in df.columns for col in ['Année', 'Mois', 'Quantité', 'ds', 'y']):
                    st.error(f"Données corrompues pour {pn}")
                    return {}
                df['ds'] = pd.to_datetime(df['ds'])
                data['pn_data'][pn] = df
            return data
        except Exception as e:
            st.error(f"Erreur lors du chargement de pn_data.json : {str(e)}")
            return {}
    return {}

def save_json_data(pn_data, pn_last_updated, pn_trend, pn_trend_enabled, pn_file_name):
    """
    Sauvegarde les données dans le fichier JSON.

    Args:
        pn_data (dict): Données des PN.
        pn_last_updated (dict): Dates de mise à jour des PN.
        pn_trend (dict): Tendances personnalisées des PN.
        pn_trend_enabled (dict): Indicateur d'activation des tendances.
        pn_file_name (dict): Noms des fichiers associés aux PN.
    """
    json_file = "pn_data.json"
    try:
        data_to_save = {
            'pn_data': {pn: df.to_dict('records') for pn, df in pn_data.items()},
            'pn_last_updated': pn_last_updated,
            'pn_trend': pn_trend,
            'pn_trend_enabled': pn_trend_enabled,
            'pn_file_name': pn_file_name
        }
        with open(json_file, 'w') as f:
            json.dump(data_to_save, f, indent=4, default=str)
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde de pn_data.json : {str(e)}")

def load_excel(file, file_name=None):
    """
    Charge un fichier Excel et le convertit en DataFrame avec les colonnes nécessaires.

    Args:
        file: Fichier Excel chargé via st.file_uploader.
        file_name (str, optional): Nom du fichier pour les messages d'erreur.

    Returns:
        pandas.DataFrame: DataFrame avec les colonnes 'Année', 'Mois', 'Quantité', 'ds', 'y',
                         ou None en cas d'erreur.
    """
    try:
        df = pd.read_excel(file, header=None, names=['Année', 'Mois', 'Quantité'])
        if list(df.columns) != ['Année', 'Mois', 'Quantité']:
            raise ValueError(f"Le fichier {file_name or 'importé'} doit contenir exactement les colonnes : Année, Mois, Quantité")
        if df[['Année', 'Mois', 'Quantité']].isnull().any().any():
            raise ValueError(f"Le fichier {file_name or 'importé'} contient des valeurs manquantes.")
        if not df['Quantité'].apply(lambda x: isinstance(x, (int, float)) and x >= 0).all():
            raise ValueError(f"La colonne Quantité du fichier {file_name or 'importé'} doit contenir des valeurs numériques non négatives.")
        df['Mois'] = df['Mois'].map(MONTH_MAP)
        if df['Mois'].isnull().any():
            raise ValueError(f"Certains mois dans le fichier {file_name or 'importé'} ne sont pas valides. Utilisez : Janvier, Février, etc.")
        df = df[df['Mois'].between(1, 12)]
        df['ds'] = pd.to_datetime(df['Année'].astype(str) + '-' + df['Mois'].astype(str).str.zfill(2) + '-01')
        df['y'] = df['Quantité']
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier {file_name or 'importé'} : {str(e)}")
        return None

def export_to_excel(df, file_name="export", sheet_name="Données"):
    """
    Exporte un DataFrame vers un fichier Excel.

    Args:
        df (pandas.DataFrame): Données à exporter.
        file_name (str): Nom du fichier.
        sheet_name (str): Nom de la feuille Excel.

    Returns:
        BytesIO: Buffer contenant le fichier Excel.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output