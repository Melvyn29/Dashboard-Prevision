"""
Composant tableau de bord principal
Affiche les métriques, la liste des PN et les graphiques de saisonnalité
"""

import streamlit as st
import pandas as pd
from utils.plot_utils import generate_seasonality_plot
from utils.data_utils import get_aircraft_model
from utils.session_manager import SessionManager
from config.constants import MESSAGES


def _initialize_aircraft_models():
    """Initialise le dictionnaire des modèles d'avion s'il n'existe pas"""
    SessionManager.ensure_aircraft_models()


def _get_all_aircraft_models():
    """Récupère tous les modèles d'avion disponibles"""
    all_models = set()
    for pn in st.session_state.pn_data.keys():
        model = get_aircraft_model(pn, st.session_state.pn_aircraft_model)
        if model != "Inconnu":
            all_models.add(model)
    return ["Tous les modèles"] + sorted(list(all_models))


def _create_summary_dataframe():
    """Crée le DataFrame de résumé des PN"""
    return pd.DataFrame({
        "PN": list(st.session_state.pn_data.keys()),
        "Modèle d'avion": [
            get_aircraft_model(pn, st.session_state.pn_aircraft_model) 
            for pn in st.session_state.pn_data
        ],
        "Dernière mise à jour": [
            st.session_state.pn_last_updated.get(pn, "N/A") 
            for pn in st.session_state.pn_data
        ],
        "Fichier": [
            st.session_state.pn_file_name.get(pn, "N/A") 
            for pn in st.session_state.pn_data
        ],
        "Tendances activées": [
            st.session_state.pn_trend_enabled.get(pn, False) 
            for pn in st.session_state.pn_data
        ]
    })


def _filter_summary_data(summary_data, selected_model, search_query):
    """Applique les filtres au DataFrame de résumé"""
    # Filtrage par modèle
    if selected_model != "Tous les modèles":
        summary_data = summary_data[summary_data["Modèle d'avion"] == selected_model]
    
    # Filtrage par recherche
    if search_query:
        summary_data = summary_data[
            summary_data["PN"].str.contains(search_query, case=False) |
            summary_data["Modèle d'avion"].str.contains(search_query, case=False)
        ]
    
    return summary_data


def _format_summary_data(summary_data):
    """Formate les données du résumé pour l'affichage"""
    # Tri par modèle puis par PN
    summary_data["Sort_Key"] = summary_data.apply(
        lambda row: (row["Modèle d'avion"], row["PN"]), axis=1
    )
    summary_data = summary_data.sort_values("Sort_Key").drop(columns="Sort_Key")
    summary_data.index = range(1, len(summary_data) + 1)
    
    # Formatage des tendances
    summary_data["Tendances activées"] = summary_data["Tendances activées"].map(
        lambda x: "OUI" if x else "NON"
    )
    
    return summary_data


def _render_metrics():
    """Affiche les métriques principales"""
    col_metric, col_empty1, col_empty2 = st.columns([1, 2, 2])
    with col_metric:
        total_pns = SessionManager.get_pn_count()
        st.metric("Nombre de PN", total_pns, help="Nombre total de PN chargés")


def _render_filters():
    """Affiche les filtres de recherche et de modèle"""
    col_filter, col_search = st.columns([2, 2])
    
    with col_filter:
        model_options = _get_all_aircraft_models()
        selected_model = st.selectbox(
            "Filtrer par modèle d'avion", 
            model_options, 
            key="dashboard_model_filter"
        )
    
    with col_search:
        search_query = st.text_input("Rechercher un PN", "", key="dashboard_search")
    
    return selected_model, search_query


def _render_summary_table(summary_data):
    """Affiche le tableau de résumé des PN"""
    st.dataframe(
        summary_data[["PN", "Modèle d'avion", "Dernière mise à jour", "Fichier", "Tendances activées"]],
        use_container_width=True,
        column_config={
            "PN": st.column_config.TextColumn("PN"),
            "Modèle d'avion": st.column_config.TextColumn("Modèle d'avion"),
            "Dernière mise à jour": st.column_config.TextColumn("Dernière mise à jour"),
            "Fichier": st.column_config.TextColumn("Fichier"),
            "Tendances activées": st.column_config.TextColumn("Tendances activées")
        }
    )


def _render_seasonality_section():
    """Affiche la section de saisonnalité"""
    st.markdown("#### Saisonnalité des PN")
    
    # Options de PN avec modèles
    pn_options = ["Tous les PN"] + sorted(
        [
            f"{pn} ({get_aircraft_model(pn, st.session_state.pn_aircraft_model)})" 
            for pn in st.session_state.pn_data.keys()
        ],
        key=lambda x: (
            get_aircraft_model(x.split(" (")[0], st.session_state.pn_aircraft_model),
            x.split(" (")[0]
        )
    )
    
    selected_pn_display = st.selectbox(
        "Sélectionner un PN pour la saisonnalité", 
        pn_options, 
        key="seasonality_select"
    )
    
    # Déterminer les PN à afficher
    if selected_pn_display != "Tous les PN":
        pns_to_plot = [selected_pn_display.split(" (")[0]]
    else:
        pns_to_plot = list(st.session_state.pn_data.keys())
    
    # Générer et afficher le graphique
    fig_seasonality = generate_seasonality_plot(
        pns_to_plot, 
        st.session_state.pn_data, 
        st.session_state.pn_aircraft_model
    )
    st.plotly_chart(fig_seasonality, use_container_width=True)


def render_dashboard():
    """Affiche la section 'Tableau de bord global'"""
    if not st.session_state.pn_data:
        st.info(MESSAGES['no_pn_available'])
        return
    
    # Initialisation
    _initialize_aircraft_models()
    
    # Métriques
    _render_metrics()
    
    # Filtres
    selected_model, search_query = _render_filters()
    
    # Création et filtrage des données
    summary_data = _create_summary_dataframe()
    summary_data = _filter_summary_data(summary_data, selected_model, search_query)
    summary_data = _format_summary_data(summary_data)
    
    # Affichage du tableau
    _render_summary_table(summary_data)
    
    # Section saisonnalité
    _render_seasonality_section()
