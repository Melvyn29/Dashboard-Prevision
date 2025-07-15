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
    
    # Si aucune année n'est définie, utiliser par défaut 2025-2027
    if not all_years:
        all_years = {2025, 2026, 2027}
    
    all_years = sorted(all_years)
    # Sélection du PN
    if 'trend_pn_select' not in st.session_state:
        st.session_state['trend_pn_select'] = pn_list[0] if pn_list else None
    pn_select = st.selectbox("Sélectionnez un PN", pn_list, key="trend_pn_select")
    
    # Gestion des années
    st.markdown("#### Gestion des années")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_year = st.number_input("Ajouter une nouvelle année", min_value=2020, max_value=2040, value=2025, step=1)
    with col2:
        if st.button("Ajouter année"):
            if new_year not in all_years:
                all_years.append(new_year)
                all_years.sort()
                # Initialiser la nouvelle année pour tous les PN existants
                for pn in pn_list:
                    if pn not in pn_trend:
                        pn_trend[pn] = {}
                    year_str = str(new_year)
                    if year_str not in pn_trend[pn]:
                        pn_trend[pn][year_str] = {"type": "linéaire", "values": {year_str: 0.0}}
                
                save_json_data(
                    st.session_state.pn_data if hasattr(st.session_state, 'pn_data') else {},
                    st.session_state.pn_last_updated if hasattr(st.session_state, 'pn_last_updated') else {},
                    pn_trend,
                    pn_trend_enabled,
                    st.session_state.pn_file_name if hasattr(st.session_state, 'pn_file_name') else "pn_data.json"
                )
                st.success(f"Année {new_year} ajoutée !")
                st.rerun()
    
    if all_years:
        year_to_remove = st.selectbox("Supprimer une année", [""] + [str(y) for y in all_years], key="year_to_remove")
        if year_to_remove and st.button("Supprimer année sélectionnée"):
            year_int = int(year_to_remove)
            all_years.remove(year_int)
            # Supprimer l'année de tous les PN
            for pn in pn_list:
                if pn in pn_trend and year_to_remove in pn_trend[pn]:
                    del pn_trend[pn][year_to_remove]
            
            save_json_data(
                getattr(st.session_state, 'pn_data', {}),
                getattr(st.session_state, 'pn_last_updated', {}),
                pn_trend,
                pn_trend_enabled,
                getattr(st.session_state, 'pn_file_name', "pn_data.json")
            )
            st.success(f"Année {year_to_remove} supprimée !")
            st.rerun()
    # Formulaire de saisie
    st.markdown("#### Saisie/activation d'une trend personnalisée")
    
    if not all_years:
        st.warning("Aucune année configurée. Utilisez la section 'Gestion des années' ci-dessus pour ajouter des années.")
    else:
        with st.form(key="trend_perso_form"):
            active = st.checkbox("Activer la trend personnalisée pour ce PN", value=pn_trend_enabled.get(pn_select, False))
            
            st.markdown("**Pourcentages de croissance/décroissance par année :**")
            st.info("Valeurs positives = croissance, valeurs négatives = décroissance")
            
            year_inputs = {}
            
            # Organiser les champs d'entrée en colonnes pour une meilleure présentation
            cols = st.columns(min(3, len(all_years)))
            for i, year in enumerate(all_years):
                year_str = str(year)
                val = pn_trend.get(pn_select, {}).get(year_str, {}).get('values', {}).get(year_str, 0.0)
                
                with cols[i % len(cols)]:
                    year_inputs[year] = st.number_input(
                        f"% {year}", 
                        min_value=-100.0, 
                        max_value=100.0, 
                        value=float(val), 
                        step=1.0, 
                        key=f"trend_val_{year}",
                        help=f"Pourcentage d'ajustement pour l'année {year}"
                    )
            
            submit = st.form_submit_button("Enregistrer pour ce PN", type="primary")
            
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
                    getattr(st.session_state, 'pn_data', {}),
                    getattr(st.session_state, 'pn_last_updated', {}),
                    pn_trend_clean,
                    pn_trend_enabled_clean,
                    getattr(st.session_state, 'pn_file_name', "pn_data.json")
                )
                st.success(f"Trend personnalisée enregistrée pour {pn_select} !")
                st.rerun()
    # Tableau récapitulatif (toujours à jour)
    st.markdown("#### Récapitulatif de toutes les trends personnalisées")
    
    if all_years:
        recap_data = []
        for pn in pn_list:
            row = {"PN": pn, "Activée": "✅ Oui" if pn_trend_enabled.get(pn, False) else "❌ Non"}
            for year in all_years:
                year_str = str(year)
                val = pn_trend.get(pn, {}).get(year_str, {}).get('values', {}).get(year_str, 0.0)
                if val > 0:
                    row[f"% {year}"] = f"+{val}%"
                elif val < 0:
                    row[f"% {year}"] = f"{val}%"
                else:
                    row[f"% {year}"] = "0%"
            recap_data.append(row)
        
        df_recap = pd.DataFrame(recap_data)
        st.dataframe(df_recap, use_container_width=True, hide_index=True)
        
        # Afficher un résumé des PN activés
        activated_pns = [pn for pn in pn_list if pn_trend_enabled.get(pn, False)]
        if activated_pns:
            st.success(f"Trends personnalisées activées pour {len(activated_pns)} PN(s) : {', '.join(activated_pns)}")
        else:
            st.info("Aucune trend personnalisée n'est actuellement activée.")
    else:
        st.info("Aucune année configurée pour afficher le récapitulatif.")
    # Fonctionnalités avancées
    st.markdown("#### Fonctionnalités avancées")
    
    # Copier les tendances d'un PN vers un autre
    with st.expander("📋 Copier les tendances d'un PN vers un autre"):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            source_pn = st.selectbox("PN source", pn_list, key="source_pn")
        with col2:
            target_pn = st.selectbox("PN cible", pn_list, key="target_pn")
        with col3:
            if st.button("Copier tendances", type="secondary"):
                if source_pn != target_pn:
                    # Copier les tendances
                    if source_pn in pn_trend:
                        pn_trend[target_pn] = pn_trend[source_pn].copy()
                    pn_trend_enabled[target_pn] = pn_trend_enabled.get(source_pn, False)
                    
                    save_json_data(
                        getattr(st.session_state, 'pn_data', {}),
                        getattr(st.session_state, 'pn_last_updated', {}),
                        pn_trend,
                        pn_trend_enabled,
                        getattr(st.session_state, 'pn_file_name', "pn_data.json")
                    )
                    st.success(f"Tendances copiées de {source_pn} vers {target_pn} !")
                    st.rerun()
                else:
                    st.error("Le PN source et le PN cible doivent être différents.")
    
    # Appliquer la même tendance à plusieurs PN
    with st.expander("📊 Appliquer la même tendance à plusieurs PN"):
        selected_pns = st.multiselect("Sélectionnez les PN", pn_list, key="bulk_pns")
        
        if selected_pns and all_years:
            st.markdown("**Définir les tendances :**")
            bulk_year_inputs = {}
            cols = st.columns(min(3, len(all_years)))
            for i, year in enumerate(all_years):
                with cols[i % len(cols)]:
                    bulk_year_inputs[year] = st.number_input(
                        f"% {year}", 
                        min_value=-100.0, 
                        max_value=100.0, 
                        value=0.0, 
                        step=1.0, 
                        key=f"bulk_trend_val_{year}"
                    )
            
            bulk_active = st.checkbox("Activer la trend pour tous les PN sélectionnés", key="bulk_active")
            
            if st.button("Appliquer à tous les PN sélectionnés", type="primary"):
                for pn in selected_pns:
                    if pn not in pn_trend:
                        pn_trend[pn] = {}
                    
                    for year in all_years:
                        year_str = str(year)
                        pn_trend[pn][year_str] = {"type": "linéaire", "values": {year_str: float(bulk_year_inputs[year])}}
                    
                    pn_trend_enabled[pn] = bulk_active
                
                save_json_data(
                    getattr(st.session_state, 'pn_data', {}),
                    getattr(st.session_state, 'pn_last_updated', {}),
                    pn_trend,
                    pn_trend_enabled,
                    getattr(st.session_state, 'pn_file_name', "pn_data.json")
                )
                st.success(f"Tendances appliquées à {len(selected_pns)} PN(s) !")
                st.rerun()

    # Bouton de reset global avec confirmation (placé juste après le tableau)
    with st.expander("⚠️ Réinitialiser toutes les trends personnalisées"):
        st.warning("Cette action supprimera toutes les tendances personnalisées et désactivera la fonction pour tous les PN.")
        if 'reset_trends_confirm' not in st.session_state:
            st.session_state['reset_trends_confirm'] = False
        if not st.session_state['reset_trends_confirm']:
            if st.button("Réinitialiser", type="primary"):
                st.session_state['reset_trends_confirm'] = True
                st.rerun()  # Pour afficher le bouton de confirmation
        else:
            st.error("Êtes-vous sûr de vouloir remettre à zéro toutes les trends personnalisées et désactiver la fonction pour chaque PN ? Cette action est irréversible.")
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
                        getattr(st.session_state, 'pn_data', {}),
                        getattr(st.session_state, 'pn_last_updated', {}),
                        pn_trend_reset,
                        pn_trend_enabled_reset,
                        getattr(st.session_state, 'pn_file_name', "pn_data.json")
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
        
        # Obtenir les données de session de manière sécurisée
        pn_data = getattr(st.session_state, 'pn_data', {})
        df = pn_data.get(selected_pn)
        
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
            fig_trend.update_layout(
                title=f'Comparaison des trends pour {selected_pn}', 
                xaxis_title='Date', 
                yaxis_title='Tendance', 
                height=400, 
                showlegend=True, 
                plot_bgcolor='#F5F7FA', 
                paper_bgcolor='#FFFFFF', 
                font_color='#003087'
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Afficher un résumé des tendances appliquées
            if enable_trend:
                st.markdown("**Tendances appliquées :**")
                trends_summary = []
                for year in all_years:
                    year_str = str(year)
                    val = pn_trend.get(selected_pn, {}).get(year_str, {}).get('values', {}).get(year_str, 0.0)
                    if val != 0:
                        trends_summary.append(f"• {year}: {val:+.1f}%")
                
                if trends_summary:
                    for summary in trends_summary:
                        st.text(summary)
                else:
                    st.info("Aucune tendance non-nulle définie pour ce PN.")
        else:
            st.warning(f"Aucune donnée disponible pour le PN {selected_pn}. Assurez-vous que les données ont été chargées dans l'application.")
    else:
        st.info("Aucun PN avec trend personnalisée activée. Activez au moins une trend pour un PN pour voir la visualisation.")
