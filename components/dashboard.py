import streamlit as st
import pandas as pd
from config.mappings import PN_MODEL_MAPPING
from utils.plot_utils import generate_seasonality_plot

def render_dashboard():
    """
    Affiche la section "Tableau de bord global".
    """
    if st.session_state.pn_data:
        col_metric, col_empty1, col_empty2 = st.columns([1, 2, 2])
        with col_metric:
            total_pns = len(st.session_state.pn_data)
            st.metric("Nombre de PN", total_pns, help="Nombre total de PN chargés")

        col_filter, col_search = st.columns([2, 2])
        with col_filter:
            model_options = ["Tous les modèles"] + sorted(set(PN_MODEL_MAPPING.values()))
            selected_model = st.selectbox("Filtrer par modèle d’avion", model_options, key="dashboard_model_filter")
        with col_search:
            search_query = st.text_input("Rechercher un PN", "", key="dashboard_search")

        summary_data = pd.DataFrame({
            "PN": list(st.session_state.pn_data.keys()),
            "Modèle d’avion": [PN_MODEL_MAPPING.get(pn, "Inconnu") for pn in st.session_state.pn_data],
            "Dernière mise à jour": [st.session_state.pn_last_updated.get(pn, "N/A") for pn in st.session_state.pn_data],
            "Fichier": [st.session_state.pn_file_name.get(pn, "N/A") for pn in st.session_state.pn_data],
            "Tendances activées": [st.session_state.pn_trend_enabled.get(pn, False) for pn in st.session_state.pn_data]
        })

        if selected_model != "Tous les modèles":
            summary_data = summary_data[summary_data["Modèle d’avion"] == selected_model]
        if search_query:
            summary_data = summary_data[
                summary_data["PN"].str.contains(search_query, case=False) |
                summary_data["Modèle d’avion"].str.contains(search_query, case=False)
            ]

        summary_data["Sort_Key"] = summary_data.apply(
            lambda row: (row["Modèle d’avion"], row["PN"]), axis=1
        )
        summary_data = summary_data.sort_values("Sort_Key").drop(columns="Sort_Key")
        summary_data.index = range(1, len(summary_data) + 1)

        summary_data["Tendances activées"] = summary_data["Tendances activées"].map(lambda x: "OUI" if x else "NON")

        st.dataframe(
            summary_data[["PN", "Modèle d’avion", "Dernière mise à jour", "Fichier", "Tendances activées"]],
            use_container_width=True,
            column_config={
                "PN": st.column_config.TextColumn("PN"),
                "Modèle d’avion": st.column_config.TextColumn("Modèle d’avion"),
                "Dernière mise à jour": st.column_config.TextColumn("Dernière mise à jour"),
                "Fichier": st.column_config.TextColumn("Fichier"),
                "Tendances activées": st.column_config.TextColumn("Tendances activées")
            }
        )

        st.markdown("#### Saisonnalité des PN")
        pn_options = ["Tous les PN"] + sorted(
            [f"{pn} ({PN_MODEL_MAPPING.get(pn, 'Inconnu')})" for pn in st.session_state.pn_data.keys()],
            key=lambda x: (
                PN_MODEL_MAPPING.get(x.split(" (")[0], "Inconnu"),
                x.split(" (")[0]
            )
        )
        selected_pn_display = st.selectbox("Sélectionner un PN pour la saisonnalité", pn_options, key="seasonality_select")
        pns_to_plot = [selected_pn_display.split(" (")[0]] if selected_pn_display != "Tous les PN" else st.session_state.pn_data.keys()
        fig_seasonality = generate_seasonality_plot(pns_to_plot, st.session_state.pn_data)
        st.plotly_chart(fig_seasonality, use_container_width=True)
    else:
        st.info("Aucun PN disponible. Ajoutez un PN pour commencer.")