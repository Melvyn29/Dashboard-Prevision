import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.forecast_utils import run_prophet_forecast
from datetime import datetime

def render_performance():
    st.markdown("# Suivi de la performance du modèle")
    pn_list = list(st.session_state.pn_data.keys())
    if not pn_list:
        st.info("Aucun PN disponible pour le suivi de performance.")
        return
    pn_select = st.selectbox("Sélectionnez un PN à suivre", pn_list)
    df = st.session_state.pn_data.get(pn_select)
    if df is None or df.empty:
        st.warning("Aucune donnée réelle disponible pour ce PN.")
        return
    # Sélection de la période à comparer
    min_year = int(df['ds'].dt.year.min())
    max_year = int(df['ds'].dt.year.max())
    year_range = st.slider("Période à comparer (prédiction vs réel)", min_year, max_year, (max_year-1, max_year))
    
    # Calcul du nombre de mois pour couvrir toute la période sélectionnée
    start_date = datetime(year_range[0], 1, 1)
    end_date = datetime(year_range[1], 12, 31)
    months = (year_range[1] - year_range[0] + 1) * 12  # Nombre de mois pour toute la période
    
    # Récupération des prévisions pour toute la période
    model, forecast = run_prophet_forecast(df, months, start_date)
    # On suppose que la colonne 'yhat' est la prévision, 'y' la réalité
    df_compare = pd.merge(
        forecast[['ds', 'yhat']],
        df[['ds', 'y']],
        on='ds',
        how='inner'
    )
    # Calcul des erreurs AVANT filtrage
    df_compare['erreur'] = df_compare['yhat'] - df_compare['y']
    df_compare['abs_erreur'] = df_compare['erreur'].abs()
    # Filtrer sur toute la période sélectionnée (du début à la fin)
    mask = (df_compare['ds'] >= pd.Timestamp(year_range[0], 1, 1)) & (df_compare['ds'] <= pd.Timestamp(year_range[1], 12, 31))
    df_compare = df_compare[mask]
    if df_compare.empty:
        st.warning("Aucune donnée disponible pour la période sélectionnée.")
        return
    # --- Nouvelle synthèse agrégée par mois ---
    df_compare['YYYY-MM'] = df_compare['ds'].dt.strftime('%Y-%m')
    synthese = df_compare.groupby('YYYY-MM').agg({
        'y': 'mean',
        'yhat': 'mean',
        'erreur': 'mean',
        'abs_erreur': 'mean'
    }).reset_index()
    synthese = synthese.rename(columns={
        'YYYY-MM': 'Date',
        'y': 'Réel',
        'yhat': 'Prévu',
        'erreur': 'Erreur',
        'abs_erreur': 'Erreur absolue'
    })
    # Affichage graphique
    st.markdown("### Comparaison prévision vs réel")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_compare['ds'], y=df_compare['y'], mode='lines+markers', name='Réel', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=df_compare['ds'], y=df_compare['yhat'], mode='lines+markers', name='Prévision', line=dict(color='orange')))
    fig.update_layout(xaxis_title='Date', yaxis_title='Quantité', height=400, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
    # Tableau de synthèse agrégé
    st.markdown("### Tableau de synthèse")
    st.dataframe(synthese, use_container_width=True, hide_index=True)
    # Indicateurs globaux
    mae = df_compare['abs_erreur'].mean()
    rmse = (df_compare['erreur']**2).mean()**0.5
    biais = df_compare['erreur'].mean()
    st.markdown("### Indicateurs de performance")
    col1, col2, col3 = st.columns(3)
    col1.metric("MAE (erreur absolue moyenne)", f"{mae:.1f}")
    col2.metric("RMSE", f"{rmse:.1f}")
    col3.metric("Biais", f"{biais:.1f}")
    # Conclusion automatique
    st.markdown("### Conclusion automatique")
    if mae < 10:
        st.success("Prédiction très fiable sur la période sélectionnée.")
    elif mae < 30:
        st.info("Prédiction globalement correcte, quelques écarts à surveiller.")
    else:
        st.warning("Prédiction peu fiable sur cette période, revoir le modèle ou les données.")
    # Ajout d'une explication pédagogique
    st.markdown("""
    <div style='background-color:#F5F7FA; padding:16px; border-radius:8px; margin-top:24px;'>
    <b>Comment interpréter ces résultats ?</b><br>
    <ul>
        <li><b>MAE</b> (erreur absolue moyenne) : plus elle est faible, plus la prévision est précise.</li>
        <li><b>RMSE</b> : sensible aux grosses erreurs ponctuelles, à surveiller si très supérieur au MAE.</li>
        <li><b>Biais</b> : positif = tendance à surestimer, négatif = tendance à sous-estimer.</li>
    </ul>
    <i>Le graphique permet de visualiser si le modèle suit bien la réalité ou s'il y a des décalages importants.</i>
    </div>
    """, unsafe_allow_html=True)
