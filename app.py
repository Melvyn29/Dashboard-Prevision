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

# Configuration initiale
st.set_page_config(page_title="Prévision de la demande", layout="wide")
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

# Titre
st.markdown('<h1 class="title">Tableau de bord - Prévision de la demande</h1>', unsafe_allow_html=True)

# Barre de navigation latérale
with st.sidebar:
    st.markdown("### Navigation")
    if st.button("Tableau de bord"):
        st.session_state.active_section = "dashboard"
    if st.button("Analyse"):
        st.session_state.active_section = "analysis"
    if st.button("Comparaison d’analyse"):
        st.session_state.active_section = "comparison"
    if st.button("Générer un rapport"):
        st.session_state.active_section = "report"
    if st.button("Trends personnalisées"):
        st.session_state.active_section = "trends"
    if st.button("Ajouter un PN"):
        st.session_state.active_section = "add_pn"
        st.session_state.trend_inputs = [{'year': 2025, 'percentage': 0.0}]
    if st.button("Modifier un PN"):
        st.session_state.active_section = "modify_pn"
    if st.button("Suivi de la performance"):
        st.session_state.active_section = "performance"
    if st.button("Sauvegardes"):
        st.session_state.active_section = "backup_manager"
    st.markdown(f'<p class="datetime-display">{datetime.now().strftime("%A %d %B %Y, %H:%M %Z")}</p>', unsafe_allow_html=True)

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

# Footer
st.markdown(
    f"""
    <div class="footer">
        <p>Tableau de bord - Prévision de la demande | Version 1.0 | Développé par Melvyn Brichet - Projet de stage | © {datetime.now().year}</p>
    </div>
    """,
    unsafe_allow_html=True
)