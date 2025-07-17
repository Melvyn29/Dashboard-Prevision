"""
Application principale - Tableau de bord de prévisions pneumatiques Air France Industries
Développé par Melvyn Brichet - Projet de stage
"""

import streamlit as st
import base64
from datetime import datetime
from pathlib import Path

# Imports des modules locaux
from config.styles import apply_styles
from config.constants import APP_NAME, APP_VERSION, APP_AUTHOR
from components.navigation import render_sidebar, render_active_section
from utils.session_manager import SessionManager


def set_custom_favicon():
    """Configure une favicon personnalisée pour l'application"""
    try:
        logo_path = Path("assets/airfrance-logo.png")
        if logo_path.exists():
            with open(logo_path, "rb") as f:
                logo_base64 = base64.b64encode(f.read()).decode()
            
            st.markdown(
                f"""
                <link rel="icon" type="image/png" href="data:image/png;base64,{logo_base64}">
                <link rel="shortcut icon" type="image/png" href="data:image/png;base64,{logo_base64}">
                """,
                unsafe_allow_html=True
            )
        else:
            # Fallback vers un emoji si l'image n'existe pas
            st.markdown(
                """
                <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>✈️</text></svg>">
                """,
                unsafe_allow_html=True
            )
    except Exception:
        # En cas d'erreur, l'application continue sans favicon personnalisée
        pass


def initialize_session_state():
    """Initialise l'état de session avec les données par défaut"""
    SessionManager.initialize()


def render_header():
    """Affiche l'en-tête de l'application"""
    st.markdown(
        """
        <div class="header-container">
            <div class="header-content">
                <h1 class="main-title">Tableau de bord - Prévisions</h1>
                <p class="subtitle">Outils avancés d'analyse et prévision de la demande de pneumatique<br>Air France industries - Atelier Roues et Pneus - MSEO</p>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )


def render_footer():
    """Affiche le footer de l'application"""
    current_year = datetime.now().year
    st.markdown(
        f"""
        <div class="footer">
            <p>Tableau de bord - Prévision de la demande | Version {APP_VERSION} | Développé par {APP_AUTHOR} - Projet de stage - Forcast | © {current_year}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def main():
    """Fonction principale de l'application"""
    # Configuration initiale
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Appliquer la favicon et les styles
    set_custom_favicon()
    apply_styles()

    # Initialisation
    initialize_session_state()

    # Interface utilisateur
    render_header()
    render_sidebar()
    render_active_section()
    render_footer()


if __name__ == "__main__":
    main()
