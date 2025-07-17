"""
Gestionnaire d'état de session
Centralise la gestion de l'état de session Streamlit
"""

import streamlit as st
from utils.data_utils import load_json_data
from config.constants import DEFAULT_TREND_YEAR, DEFAULT_TREND_PERCENTAGE


class SessionManager:
    """Classe pour gérer l'état de session de l'application"""
    
    @staticmethod
    def initialize():
        """Initialise l'état de session avec les données par défaut"""
        if 'initialized' not in st.session_state:
            json_data = load_json_data()
            
            # Données principales
            st.session_state.pn_data = json_data.get('pn_data', {})
            st.session_state.pn_last_updated = json_data.get('pn_last_updated', {})
            st.session_state.pn_trend = json_data.get('pn_trend', {})
            st.session_state.pn_trend_enabled = json_data.get('pn_trend_enabled', {})
            st.session_state.pn_file_name = json_data.get('pn_file_name', {})
            st.session_state.pn_aircraft_model = json_data.get('pn_aircraft_model', {})
            
            # Paramètres d'interface
            st.session_state.trend_inputs = [{'year': DEFAULT_TREND_YEAR, 'percentage': DEFAULT_TREND_PERCENTAGE}]
            st.session_state.active_section = "dashboard"
            
            # Lien de données
            st.session_state.data_link = json_data.get('data_link', "https://example.com")
            
            st.session_state.initialized = True
    
    @staticmethod
    def ensure_aircraft_models():
        """S'assure que le dictionnaire des modèles d'avion existe"""
        if 'pn_aircraft_model' not in st.session_state:
            st.session_state.pn_aircraft_model = {}
    
    @staticmethod
    def get_pn_count():
        """Retourne le nombre de PN chargés"""
        return len(st.session_state.get('pn_data', {}))
    
    @staticmethod
    def pn_exists(pn_name):
        """Vérifie si un PN existe déjà"""
        return pn_name in st.session_state.get('pn_data', {})
    
    @staticmethod
    def set_active_section(section):
        """Définit la section active"""
        st.session_state.active_section = section
    
    @staticmethod
    def get_active_section():
        """Retourne la section active"""
        return st.session_state.get('active_section', 'dashboard')
    
    @staticmethod
    def reset_trend_inputs():
        """Remet à zéro les inputs de tendance"""
        st.session_state.trend_inputs = [{'year': DEFAULT_TREND_YEAR, 'percentage': DEFAULT_TREND_PERCENTAGE}]
