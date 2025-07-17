"""
Gestionnaire de navigation de l'application
Contient toute la logique de navigation et de routage
"""

import streamlit as st
import json
import webbrowser
from datetime import datetime


def initialize_data_link():
    """Initialise le lien de données depuis le fichier JSON"""
    if 'data_link' not in st.session_state:
        try:
            with open("pn_data.json", "r") as f:
                data = json.load(f)
                st.session_state.data_link = data.get("data_link", "https://example.com")
        except FileNotFoundError:
            st.session_state.data_link = "https://example.com"


def render_navigation_buttons():
    """Affiche les boutons de navigation dans la sidebar"""
    # Section principale
    st.markdown("#### **Analyse & Visualisation**")
    if st.button("Tableau de bord"):
        st.session_state.active_section = "dashboard"
    if st.button("Analyse"):
        st.session_state.active_section = "analysis"
    if st.button("Comparaison d'analyse"):
        st.session_state.active_section = "comparison"
    if st.button("Générer un rapport"):
        st.session_state.active_section = "report"
    
    st.markdown("---")
    
    # Section configuration
    st.markdown("#### **Configuration**")
    if st.button("Trends personnalisées"):
        st.session_state.active_section = "trends"
        st.session_state.trend_inputs = [{'year': 2025, 'percentage': 0.0}]
    if st.button("Ajouter un PN"):
        st.session_state.active_section = "add_pn"
        st.session_state.trend_inputs = [{'year': 2025, 'percentage': 0.0}]
    if st.button("Modifier un PN"):
        st.session_state.active_section = "modify_pn"
    
    st.markdown("---")
    
    # Section outils
    st.markdown("#### **Outils**")
    if st.button("Suivi de la performance"):
        st.session_state.active_section = "performance"
    if st.button("Sauvegardes"):
        st.session_state.active_section = "backup_manager"


def render_data_buttons():
    """Affiche les boutons de données et paramètres"""
    # Bouton "Données" qui ouvre directement le lien
    if st.button("Données"):
        webbrowser.open(st.session_state.data_link)

    # Bouton "Paramètre" avec icône pour modifier le lien
    if st.button("Paramètre ⚙️"):
        st.session_state.active_section = "data_link_settings"


def render_sidebar():
    """Affiche la barre latérale complète"""
    with st.sidebar:
        st.markdown("### Navigation")
        
        render_navigation_buttons()
        
        initialize_data_link()
        render_data_buttons()
        
        st.markdown("---")
        
        # Date et heure
        current_time = datetime.now()
        st.markdown(
            f'<div class="sidebar-datetime">'
            f'{current_time.strftime("%d/%m/%Y")}<br>{current_time.strftime("%H:%M")}'
            f'</div>', 
            unsafe_allow_html=True
        )


def render_data_link_settings():
    """Affiche la section de paramétrage du lien de données"""
    st.subheader("Paramètres du lien de données")
    st.markdown("Configurez le lien qui s'ouvrira lorsque vous cliquez sur le bouton 'Données'.")
    
    new_link = st.text_input(
        "URL du lien de données", 
        value=st.session_state.get('data_link', "https://example.com"),
        placeholder="https://example.com"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sauvegarder"):
            if new_link:
                st.session_state.data_link = new_link
                # Sauvegarder dans le fichier JSON
                try:
                    with open("pn_data.json", "r") as f:
                        data = json.load(f)
                except FileNotFoundError:
                    data = {}
                data["data_link"] = new_link
                with open("pn_data.json", "w") as f:
                    json.dump(data, f, indent=4)
                st.success("Lien sauvegardé avec succès!")
            else:
                st.error("Veuillez entrer un lien valide.")
    
    with col2:
        if st.button("Retour au tableau de bord"):
            st.session_state.active_section = "dashboard"


def render_active_section():
    """Affiche la section active selon le choix de l'utilisateur"""
    if st.session_state.active_section == "dashboard":
        from components.dashboard import render_dashboard
        render_dashboard()
    elif st.session_state.active_section == "add_pn":
        from components.add_pn import render_add_pn
        render_add_pn()
    elif st.session_state.active_section == "modify_pn":
        from components.modify_pn import render_modify_pn
        render_modify_pn()
    elif st.session_state.active_section == "analysis":
        from components.analysis import render_analysis
        render_analysis()
    elif st.session_state.active_section == "comparison":
        from components.comparison import render_comparison
        render_comparison()
    elif st.session_state.active_section == "report":
        from components.report import render_report
        render_report()
    elif st.session_state.active_section == "trends":
        from components.trends import render_trends
        render_trends()
    elif st.session_state.active_section == "backup_manager":
        from components.backup_manager import render_backup_manager
        render_backup_manager()
    elif st.session_state.active_section == "performance":
        from components.performance import render_performance
        render_performance()
    elif st.session_state.active_section == "data_link_settings":
        render_data_link_settings()
