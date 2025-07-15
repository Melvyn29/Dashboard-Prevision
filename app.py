import streamlit as st
from datetime import datetime
from config.styles import apply_styles
from components.dashboard import render_dashboard
from components.add_pn import render_add_pn
from components.modify_pn import render_modify_pn
from components.analysis import render_analysis 
from components.comparison import render_comparison
from components.report import render_report
from utils.data_utils import load_json_data

def set_custom_favicon():
    """Configure une favicon personnalisée pour l'application"""
    import base64
    import os
    
    try:
        # Vérifier si l'image locale existe
        logo_path = "assets/airfrance-logo.png"
        if os.path.exists(logo_path):
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
            # Fallback vers un emoji si l'image n'existe pas encore
            st.markdown(
                """
                <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>✈️</text></svg>">
                """,
                unsafe_allow_html=True
            )
    except Exception:
        # En cas d'erreur, utiliser un emoji
        pass

# Configuration initiale
st.set_page_config(
    page_title="Air France Industries - Prévisions Pneumatiques",
    page_icon="✈️",  # Utilisera l'image locale via set_custom_favicon()
    layout="wide",
    initial_sidebar_state="expanded"
)

# Appliquer la favicon personnalisée
set_custom_favicon()

apply_styles()

# Initialisation de l'état de session
if 'initialized' not in st.session_state:
    json_data = load_json_data()
    st.session_state.pn_data = json_data.get('pn_data', {})
    st.session_state.pn_last_updated = json_data.get('pn_last_updated', {})
    st.session_state.pn_trend = json_data.get('pn_trend', {})
    st.session_state.pn_trend_enabled = json_data.get('pn_trend_enabled', {})
    st.session_state.pn_file_name = json_data.get('pn_file_name', {})
    st.session_state.trend_inputs = [{'year': 2025, 'percentage': 0.0}]
    st.session_state.active_section = "dashboard"
    st.session_state.initialized = True

# En-tête discret et centré
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

# Barre de navigation latérale épurée
with st.sidebar:
    st.markdown("### Navigation")
    
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

    # Initialisation du lien pour le bouton "Données"
    if 'data_link' not in st.session_state:
        import json
        try:
            with open("pn_data.json", "r") as f:
                data = json.load(f)
                st.session_state.data_link = data.get("data_link", "https://example.com")
        except FileNotFoundError:
            st.session_state.data_link = "https://example.com"

    # Bouton "Données" qui ouvre directement le lien
    if st.button("Données"):
        import webbrowser
        webbrowser.open(st.session_state.data_link)

    # Bouton "Paramètre" avec icône pour modifier le lien
    if st.button("Paramètre ⚙️"):
        st.session_state.active_section = "data_link_settings"
    
    st.markdown("---")
    
    # Date et heure
    st.markdown(
        f'<div class="sidebar-datetime">'
        f'{datetime.now().strftime("%d/%m/%Y")}<br>{datetime.now().strftime("%H:%M")}'
        f'</div>', 
        unsafe_allow_html=True
    )

# Affichage de la section active
if st.session_state.active_section == "dashboard":
    render_dashboard()
elif st.session_state.active_section == "add_pn":
    render_add_pn()
elif st.session_state.active_section == "modify_pn":
    render_modify_pn()
elif st.session_state.active_section == "analysis":
    render_analysis()
elif st.session_state.active_section == "comparison":
    render_comparison()
elif st.session_state.active_section == "report":
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
                import json
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

# Footer
st.markdown(
    f"""
    <div class="footer">
        <p>Tableau de bord - Prévision de la demande | Version 2.0 | Développé par Melvyn Brichet - Projet de stage - Forcast | © {datetime.now().year}</p>
    </div>
    """,
    unsafe_allow_html=True
)