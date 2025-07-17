"""
Utilitaires pour la gestion des données
Fonctions de chargement, sauvegarde et manipulation des données PN
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from io import BytesIO
from config.mappings import MONTH_MAP, PN_MODEL_MAPPING


def load_json_data():
    """
    Charge les données à partir du fichier JSON.

    Returns:
        dict: Données chargées, ou dictionnaire vide en cas d'erreur.
    """
    json_file = Path("pn_data.json")
    if not json_file.exists():
        return {}
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validation et conversion des données PN
        for pn in data.get('pn_data', {}):
            df = pd.DataFrame(data['pn_data'][pn])
            required_columns = ['Année', 'Mois', 'Quantité', 'ds', 'y']
            if not all(col in df.columns for col in required_columns):
                st.error(f"Données corrompues pour {pn} - colonnes manquantes")
                return {}
            
            df['ds'] = pd.to_datetime(df['ds'])
            data['pn_data'][pn] = df
        
        # Assurer la compatibilité avec les anciennes versions
        data.setdefault('pn_aircraft_model', {})
        
        return data
    
    except Exception as e:
        st.error(f"Erreur lors du chargement de pn_data.json : {str(e)}")
        return {}


def save_json_data(pn_data, pn_last_updated, pn_trend, pn_trend_enabled, 
                  pn_file_name, pn_aircraft_model=None):
    """
    Sauvegarde les données dans le fichier JSON.

    Args:
        pn_data (dict): Données des PN.
        pn_last_updated (dict): Dates de mise à jour des PN.
        pn_trend (dict): Tendances personnalisées des PN.
        pn_trend_enabled (dict): Indicateur d'activation des tendances.
        pn_file_name (dict): Noms des fichiers associés aux PN.
        pn_aircraft_model (dict): Modèles d'avion personnalisés par PN.
    """
    json_file = Path("pn_data.json")
    
    try:
        data_to_save = {
            'pn_data': {pn: df.to_dict('records') for pn, df in pn_data.items()},
            'pn_last_updated': pn_last_updated,
            'pn_trend': pn_trend,
            'pn_trend_enabled': pn_trend_enabled,
            'pn_file_name': pn_file_name,
            'pn_aircraft_model': pn_aircraft_model or {}
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=4, default=str, ensure_ascii=False)
            
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde de pn_data.json : {str(e)}")


def _validate_excel_data(df, file_name=None):
    """
    Valide les données d'un fichier Excel.
    
    Args:
        df (pd.DataFrame): DataFrame à valider
        file_name (str): Nom du fichier pour les messages d'erreur
        
    Raises:
        ValueError: Si les données ne sont pas valides
    """
    file_ref = file_name or 'importé'
    
    # Vérification des colonnes
    if list(df.columns) != ['Année', 'Mois', 'Quantité']:
        raise ValueError(f"Le fichier {file_ref} doit contenir exactement les colonnes : Année, Mois, Quantité")
    
    # Vérification des valeurs manquantes
    if df[['Année', 'Mois', 'Quantité']].isnull().any().any():
        raise ValueError(f"Le fichier {file_ref} contient des valeurs manquantes.")
    
    # Vérification des quantités
    invalid_quantities = ~df['Quantité'].apply(lambda x: isinstance(x, (int, float)) and x >= 0)
    if invalid_quantities.any():
        raise ValueError(f"La colonne Quantité du fichier {file_ref} doit contenir des valeurs numériques non négatives.")


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
        # Lecture du fichier Excel
        df = pd.read_excel(file, header=None, names=['Année', 'Mois', 'Quantité'])
        
        # Validation des données
        _validate_excel_data(df, file_name)
        
        # Conversion des mois
        df['Mois'] = df['Mois'].map(MONTH_MAP)
        if df['Mois'].isnull().any():
            raise ValueError(f"Certains mois dans le fichier {file_name or 'importé'} ne sont pas valides. "
                           "Utilisez : Janvier/janvier, Février/février, Mars/mars, etc.")
        
        # Filtrage des mois valides
        df = df[df['Mois'].between(1, 12)]
        
        # Création des colonnes de date et de valeur
        df['ds'] = pd.to_datetime(
            df['Année'].astype(str) + '-' + df['Mois'].astype(str).str.zfill(2) + '-01'
        )
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


def get_aircraft_model(pn, pn_aircraft_model=None):
    """
    Obtient le modèle d'avion pour un PN donné.
    
    Args:
        pn (str): Le PN à rechercher.
        pn_aircraft_model (dict): Dictionnaire des modèles personnalisés.
    
    Returns:
        str: Le modèle d'avion ou "Inconnu" si non trouvé.
    """
    # Priorité : modèle personnalisé > mapping statique > "Inconnu"
    if pn_aircraft_model and pn in pn_aircraft_model:
        return pn_aircraft_model[pn]
    return PN_MODEL_MAPPING.get(pn, "Inconnu")


def extract_model_from_filename(filename):
    """
    Extrait le modèle d'avion du nom de fichier selon le format Export_PN-modele.
    
    Args:
        filename (str): Nom du fichier (ex: "Export_M01103-02-A320NEO.xlsx")
    
    Returns:
        tuple: (pn, model) ou (pn, None) si le format n'est pas respecté
    """
    # Enlever l'extension
    base_name = filename.replace('.xlsx', '').replace('.xls', '')
    
    # Vérifier le format Export_
    if not base_name.startswith('Export_'):
        return base_name, None
    
    # Enlever "Export_"
    content = base_name[7:]  # len("Export_") = 7
    
    # Chercher le dernier tiret pour séparer PN et modèle
    if '-' in content:
        parts = content.rsplit('-', 1)  # Split à partir de la droite, 1 seule fois
        if len(parts) == 2:
            pn, model = parts
            return pn.strip(), model.strip() if model.strip() else None
    
    return content, None