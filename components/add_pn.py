"""
Composant d'ajout de PN
Permet d'ajouter des PN individuellement ou par lot via import Excel
"""

import streamlit as st
from datetime import datetime
from utils.data_utils import load_excel, save_json_data, get_aircraft_model, extract_model_from_filename
from utils.validators import DataValidator
from utils.session_manager import SessionManager
from config.constants import MESSAGES, EXCEL_EXTENSIONS, DATE_FORMAT


def _initialize_aircraft_models():
    """Initialise le dictionnaire des modèles d'avion s'il n'existe pas"""
    SessionManager.ensure_aircraft_models()


def _save_pn_data():
    """Sauvegarde les données des PN dans le fichier JSON"""
    save_json_data(
        st.session_state.pn_data,
        st.session_state.pn_last_updated,
        st.session_state.pn_trend,
        st.session_state.pn_trend_enabled,
        st.session_state.pn_file_name,
        st.session_state.pn_aircraft_model
    )


def _add_single_pn(pn_name, aircraft_model, uploaded_file):
    """
    Ajoute un PN individuel
    
    Args:
        pn_name (str): Nom du PN
        aircraft_model (str): Modèle d'avion
        uploaded_file: Fichier Excel uploadé
        
    Returns:
        bool: True si l'ajout a réussi, False sinon
    """
    # Validation des données
    is_valid_pn, pn_error = DataValidator.validate_pn_name(pn_name)
    if not is_valid_pn:
        st.error(pn_error)
        return False
    
    is_valid_model, model_error = DataValidator.validate_aircraft_model(aircraft_model)
    if not is_valid_model:
        st.error(model_error)
        return False
    
    if SessionManager.pn_exists(pn_name):
        st.error(f"Le PN {pn_name} existe déjà.")
        return False
    
    with st.spinner(MESSAGES['file_loading']):
        df = load_excel(uploaded_file, file_name=pn_name)
    
    if df is None:
        return False
    
    # Ajout des données
    st.session_state.pn_data[pn_name] = df
    st.session_state.pn_last_updated[pn_name] = datetime.now().strftime(DATE_FORMAT)
    st.session_state.pn_trend[pn_name] = {}
    st.session_state.pn_trend_enabled[pn_name] = False
    st.session_state.pn_file_name[pn_name] = uploaded_file.name
    
    # Sauvegarde du modèle d'avion
    model_value = aircraft_model.strip() if aircraft_model.strip() else "Inconnu"
    st.session_state.pn_aircraft_model[pn_name] = model_value
    
    return True


def _process_batch_files(uploaded_files):
    """
    Traite un lot de fichiers pour l'import multiple
    
    Args:
        uploaded_files: Liste des fichiers uploadés
        
    Returns:
        tuple: (nombre de succès, liste des avertissements)
    """
    success_count = 0
    warnings = []
    
    for file in uploaded_files:
        # Extraire PN et modèle du nom de fichier
        pn_name, model = extract_model_from_filename(file.name)
        
        if pn_name in st.session_state.pn_data:
            warnings.append(f"Le PN {pn_name} existe déjà. Il sera ignoré.")
            continue
            
        with st.spinner(f"Chargement du fichier {file.name}..."):
            df = load_excel(file, file_name=file.name)
            
        if df is not None:
            st.session_state.pn_data[pn_name] = df
            st.session_state.pn_last_updated[pn_name] = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.session_state.pn_trend[pn_name] = {}
            st.session_state.pn_trend_enabled[pn_name] = False
            st.session_state.pn_file_name[pn_name] = file.name
            st.session_state.pn_aircraft_model[pn_name] = model if model else "Inconnu"
            success_count += 1
    
    return success_count, warnings


def _render_single_pn_form():
    """Affiche le formulaire d'ajout d'un PN individuel"""
    st.markdown("### Ajouter un PN individuellement")
    
    with st.form(key="add_pn_form"):
        pn_name = st.text_input("Nom du PN")
        
        # Saisie libre du modèle d'avion
        current_model = get_aircraft_model(pn_name, st.session_state.get('pn_aircraft_model', {}))
        aircraft_model = st.text_input(
            "Modèle d'avion", 
            value=current_model if current_model != "Inconnu" else "",
            placeholder="Ex: A320 NEO, B777-300, TAV A350...",
            help="Saisissez librement le modèle d'avion correspondant à ce PN"
        )
        
        uploaded_file = st.file_uploader(
            "Importer un fichier Excel (colonnes : Année, Mois, Quantité)", 
            type=EXCEL_EXTENSIONS,
            help="Les mois peuvent être écrits avec ou sans majuscule (ex: Janvier ou janvier)"
        )
        submit_button = st.form_submit_button("Ajouter le PN")

        if submit_button and pn_name and uploaded_file:
            if _add_single_pn(pn_name, aircraft_model, uploaded_file):
                _save_pn_data()
                SessionManager.set_active_section("dashboard")
                model_text = aircraft_model.strip() if aircraft_model.strip() else "modèle non spécifié"
                st.success(f"PN {pn_name} ajouté avec succès avec le modèle {model_text} !")
                st.rerun()


def _render_batch_import_form():
    """Affiche le formulaire d'import multiple de PN"""
    st.markdown("### Importer plusieurs PN")
    st.info(MESSAGES['batch_import_info'])
    
    st.markdown("**Format attendu des noms de fichier :**")
    st.markdown("- `Export_M01103-02-A320NEO.xlsx` → PN: M01103-02, Modèle: A320NEO")
    st.markdown("- `Export_M17701-B777300.xlsx` → PN: M17701, Modèle: B777300")
    st.markdown("- Si le format n'est pas respecté, le nom complet sera utilisé comme PN et le modèle sera 'Inconnu'")
    
    with st.form(key="batch_add_pn_form"):
        uploaded_files = st.file_uploader(
            "Importer plusieurs fichiers Excel", 
            type=EXCEL_EXTENSIONS, 
            accept_multiple_files=True
        )
        batch_submit_button = st.form_submit_button("Importer plusieurs PN")

        if batch_submit_button and uploaded_files:
            success_count, warnings = _process_batch_files(uploaded_files)
            
            # Afficher les avertissements
            for warning in warnings:
                st.warning(warning)
                
            if success_count > 0:
                _save_pn_data()
                SessionManager.set_active_section("dashboard")
                st.success(f"{success_count} PN(s) ajouté(s) avec succès ! Les modèles d'avion ont été extraits automatiquement des noms de fichier.")
                st.rerun()
            else:
                st.error("Aucun PN n'a pu être ajouté. Vérifiez les fichiers importés.")


def _render_format_info():
    """Affiche les informations sur le format attendu"""
    st.markdown("### Format attendu pour l'import des données")
    st.info(MESSAGES['format_info'])


def render_add_pn():
    """Affiche la section 'Ajouter un PN'"""
    st.subheader("Ajouter un nouveau PN")
    st.info(MESSAGES['trend_info'])

    # Initialisation
    _initialize_aircraft_models()
    
    # Formulaires
    _render_single_pn_form()
    _render_batch_import_form()
    _render_format_info()