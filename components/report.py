import streamlit as st
from datetime import datetime
from utils.pdf_utils import generate_pdf_report
from utils.data_utils import get_aircraft_model

def render_report():
    """
    Affiche la section "Générer un rapport".
    """
    st.subheader("Générer un rapport")
    if st.session_state.pn_data:
        # Initialiser le dictionnaire des modèles s'il n'existe pas
        if 'pn_aircraft_model' not in st.session_state:
            st.session_state.pn_aircraft_model = {}
            
        pn_options = sorted(
            [f"{pn} ({get_aircraft_model(pn, st.session_state.pn_aircraft_model)})" for pn in st.session_state.pn_data.keys()],
            key=lambda x: (
                get_aircraft_model(x.split(" (")[0], st.session_state.pn_aircraft_model),
                x.split(" (")[0]
            )
        )
        selected_pns = st.multiselect("Sélectionner les PN pour le rapport", pn_options)
        selected_pns = [pn.split(" (")[0] for pn in selected_pns]

        if not selected_pns:
            st.info("Veuillez sélectionner au moins un PN pour générer un rapport.")
            return

        months = st.slider("Mois à prévoir", 1, 24, 12, key="report_months")
        default_start_date = min(
            st.session_state.pn_data[pn]['ds'].max() if not st.session_state.pn_data[pn].empty else datetime(2025, 1, 1)
            for pn in selected_pns
        )
        forecast_start_date = st.date_input(
            "Date de début des prévisions",
            value=default_start_date,
            min_value=datetime(2020, 1, 1),
            max_value=datetime(2030, 12, 31),
            key="report_start_date"
        )

        kpis_to_include = st.multiselect(
            "Sélectionner les indicateurs clés à inclure dans le rapport",
            ["Croissance totale", "Total précédent", "Total prévu", "Moyenne mensuelle", "MAE"],
            default=["Croissance totale", "Total prévu", "Moyenne mensuelle"]
        )

        if st.button("Générer le rapport PDF"):
            with st.spinner("Génération du rapport PDF..."):
                pdf_data = generate_pdf_report(
                    selected_pns,
                    months,
                    forecast_start_date,
                    kpis_to_include,
                    st.session_state.pn_data,
                    st.session_state.pn_last_updated,
                    st.session_state.pn_trend,
                    st.session_state.pn_trend_enabled
                )
                if pdf_data:
                    st.download_button(
                        "Télécharger le rapport PDF",
                        data=pdf_data,
                        file_name="Rapport_Prévision_Demande.pdf",
                        mime="application/pdf"
                    )
                    # Aperçu PDF
                    import streamlit.components.v1 as components
                    import base64
                    pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
                    pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="100%" height="800px" type="application/pdf"></iframe>'
                    st.markdown("### Aperçu du rapport PDF")
                    st.markdown(pdf_display, unsafe_allow_html=True)
                    st.success("Rapport généré avec succès !")
                else:
                    st.error("Erreur lors de la génération du rapport. Vérifiez les données.")
    else:
        st.info("Ajoutez un PN pour générer un rapport.")