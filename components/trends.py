import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.forecast_utils import run_prophet_forecast, adjust_forecast
from utils.data_utils import save_json_data, load_json_data
from config.mappings import PN_MODEL_MAPPING

def render_trends():
    st.markdown("<h2>Trends personnalisées</h2>", unsafe_allow_html=True)
    st.info("""
    Définissez pour chaque PN un pourcentage de croissance ou décroissance pour chaque année souhaitée. 
    Activez la fonctionnalité pour les PN souhaités. L'impact est plus fort sur les pics de saisonnalité.
    """, icon="⚙️")
    # Lecture du JSON à chaque affichage
    json_data = load_json_data()
    pn_trend = json_data.get('pn_trend', {})
    pn_trend_enabled = json_data.get('pn_trend_enabled', {})
    pn_list = sorted(list(pn_trend.keys()))
    # Récupérer toutes les années présentes dans le JSON pour tous les PN
    all_years = set()
    for pn in pn_list:
        for year in pn_trend.get(pn, {}).keys():
            all_years.add(int(year))
    all_years = sorted(all_years)
    # Sélection du PN
    if 'trend_pn_select' not in st.session_state:
        st.session_state['trend_pn_select'] = pn_list[0] if pn_list else None
    pn_select = st.selectbox("Sélectionnez un PN", pn_list, key="trend_pn_select")
    # Formulaire de saisie
    st.markdown("#### Saisie/activation d'une trend personnalisée")
    with st.form(key="trend_perso_form"):
        active = st.checkbox("Activer la trend personnalisée pour ce PN", value=pn_trend_enabled.get(pn_select, False))
        year_inputs = {}
        for year in all_years:
            year_str = str(year)
            val = pn_trend.get(pn_select, {}).get(year_str, {}).get('values', {}).get(year_str, 0.0)
            year_inputs[year] = st.number_input(f"% {year}", min_value=-100.0, max_value=100.0, value=float(val), step=1.0, key=f"trend_val_{year}")
        submit = st.form_submit_button("Enregistrer pour ce PN")
        if submit:
            pn_trend_clean = pn_trend.copy()
            pn_trend_enabled_clean = pn_trend_enabled.copy()
            if pn_select not in pn_trend_clean:
                pn_trend_clean[pn_select] = {}
            for year in all_years:
                year_str = str(year)
                pn_trend_clean[pn_select][year_str] = {"type": "linéaire", "values": {year_str: float(year_inputs[year])}}
            pn_trend_enabled_clean[pn_select] = bool(active)
            save_json_data(
                st.session_state.pn_data if hasattr(st.session_state, 'pn_data') else {},
                st.session_state.pn_last_updated if hasattr(st.session_state, 'pn_last_updated') else {},
                pn_trend_clean,
                pn_trend_enabled_clean,
                st.session_state.pn_file_name if hasattr(st.session_state, 'pn_file_name') else "pn_data.json"
            )
            st.success(f"Trend personnalisée enregistrée pour {pn_select} !")
            st.rerun()
    # Tableau récapitulatif (toujours à jour)
    st.markdown("#### Récapitulatif de toutes les trends personnalisées")
    recap_data = []
    for pn in pn_list:
        row = {"PN": pn, "Activée": "Oui" if pn_trend_enabled.get(pn, False) else "Non"}
        for year in all_years:
            year_str = str(year)
            row[f"% {year}"] = pn_trend.get(pn, {}).get(year_str, {}).get('values', {}).get(year_str, 0.0)
        recap_data.append(row)
    df_recap = pd.DataFrame(recap_data)
    st.dataframe(df_recap, use_container_width=True, hide_index=True)
    # Bouton de reset global avec confirmation (placé juste après le tableau)
    with st.expander("⚠️ Réinitialiser toutes les trends personnalisées"):
        if 'reset_trends_confirm' not in st.session_state:
            st.session_state['reset_trends_confirm'] = False
        if not st.session_state['reset_trends_confirm']:
            if st.button("Réinitialiser", type="primary"):
                st.session_state['reset_trends_confirm'] = True
                st.rerun()  # Pour afficher le bouton de confirmation
        else:
            st.warning("Êtes-vous sûr de vouloir remettre à zéro toutes les trends personnalisées et désactiver la fonction pour chaque PN ? Cette action est irréversible.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Confirmer la réinitialisation", key="confirm_reset_trends"):
                    pn_trend_reset = {}
                    pn_trend_enabled_reset = {}
                    for pn in pn_list:
                        pn_trend_reset[pn] = {}
                        for year in all_years:
                            year_str = str(year)
                            pn_trend_reset[pn][year_str] = {"type": "linéaire", "values": {year_str: 0.0}}
                        pn_trend_enabled_reset[pn] = False
                    save_json_data(
                        st.session_state.pn_data if hasattr(st.session_state, 'pn_data') else {},
                        st.session_state.pn_last_updated if hasattr(st.session_state, 'pn_last_updated') else {},
                        pn_trend_reset,
                        pn_trend_enabled_reset,
                        st.session_state.pn_file_name if hasattr(st.session_state, 'pn_file_name') else "pn_data.json"
                    )
                    st.success("Toutes les trends personnalisées ont été réinitialisées et désactivées.")
                    st.session_state['reset_trends_confirm'] = False
                    st.rerun()
            with col2:
                if st.button("Annuler", key="cancel_reset_trends"):
                    st.session_state['reset_trends_confirm'] = False
                    st.rerun()
    # Visualisation de la trend pour les PN activés
    st.markdown("#### Visualisation de la trend (PN avec trend personnalisée activée)")
    pn_activated = [pn for pn in pn_list if pn_trend_enabled.get(pn, False)]
    if pn_activated:
        selected_pn = st.selectbox("Sélectionnez un PN à visualiser", pn_activated, key="trend_graph_pn")
        df = st.session_state.pn_data.get(selected_pn)
        if df is not None and not df.empty:
            months = 24
            forecast_start_date = pd.Timestamp.now().replace(day=1)
            model, forecast = run_prophet_forecast(df, months, forecast_start_date)
            trends = {}
            for year in all_years:
                year_str = str(year)
                val = pn_trend.get(selected_pn, {}).get(year_str, {}).get('values', {}).get(year_str, 0.0)
                try:
                    val = float(val)
                except Exception:
                    val = 0.0
                trends[year_str] = {"type": "linéaire", "values": {year_str: val}}
            enable_trend = pn_trend_enabled.get(selected_pn, False)
            all_dates = pd.date_range(start=df['ds'].min(), end=forecast['ds'].max(), freq='MS').to_frame(index=False, name='ds')
            trend_forecast = model.predict(all_dates)
            # Appliquer la trend personnalisée uniquement si activée et non vide
            if enable_trend and any(float(trends[y]['values'][y]) != 0.0 for y in trends):
                trend_forecast_adjusted = adjust_forecast(trend_forecast, df, trends, apply_all_trends=True)
            else:
                trend_forecast_adjusted = trend_forecast
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=trend_forecast['ds'], y=trend_forecast['trend'], name='Trend initiale', line=dict(dash='dash', color='orange')))
            if enable_trend and any(float(trends[y]['values'][y]) != 0.0 for y in trends):
                fig_trend.add_trace(go.Scatter(x=trend_forecast_adjusted['ds'], y=trend_forecast_adjusted['trend'], name='Trend personnalisée', line=dict(color='firebrick')))
            fig_trend.update_layout(title='Trend initiale et trend personnalisée', xaxis_title='Date', yaxis_title='Tendance', height=400, showlegend=True, plot_bgcolor='#F5F7FA', paper_bgcolor='#FFFFFF', font_color='#003087')
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Aucune donnée disponible pour ce PN.")
    else:
        st.info("Aucun PN avec trend personnalisée activée.")
