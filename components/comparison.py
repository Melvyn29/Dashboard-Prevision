import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from utils.forecast_utils import run_prophet_forecast, adjust_forecast
from config.mappings import PN_MODEL_MAPPING
from prophet.diagnostics import cross_validation, performance_metrics

def render_comparison():
    """
    Affiche la section "Comparaison d’analyse" avec un graphique comparatif clair et un tableau synthétique simple.
    """
    st.subheader("Comparaison d’analyse")
    if st.session_state.pn_data:
        pn_options = sorted(
            [f"{pn} ({PN_MODEL_MAPPING.get(pn, 'Inconnu')})" for pn in st.session_state.pn_data.keys()],
            key=lambda x: (
                PN_MODEL_MAPPING.get(x.split(" (")[0], "Inconnu"),
                x.split(" (")[0]
            )
        )
        col1, col2 = st.columns(2)
        with col1:
            pn1_display = st.selectbox("Sélectionner le premier PN", pn_options, key="pn1_select")
        with col2:
            pn2_options = [opt for opt in pn_options if opt != pn1_display]
            pn2_display = st.selectbox("Sélectionner le second PN", pn2_options, key="pn2_select")

        selected_pns = [pn1_display.split(" (")[0], pn2_display.split(" (")[0]] if pn1_display and pn2_display else []

        if len(selected_pns) != 2 or selected_pns[0] == selected_pns[1]:
            st.warning("Veuillez sélectionner deux PN distincts pour la comparaison.")
        else:
            months = st.slider("Mois à prévoir", 1, 24, 12, key="comparison_months")
            default_start_date = min(
                st.session_state.pn_data[selected_pns[0]]['ds'].max() if not st.session_state.pn_data[selected_pns[0]].empty else datetime(2025, 1, 1),
                st.session_state.pn_data[selected_pns[1]]['ds'].max() if not st.session_state.pn_data[selected_pns[1]].empty else datetime(2025, 1, 1)
            )
            forecast_start_date = st.date_input(
                "Date de début des prévisions",
                value=default_start_date,
                min_value=datetime(2020, 1, 1),
                max_value=datetime(2030, 12, 31),
                key="comparison_start_date"
            )
            period_str = f"{forecast_start_date.strftime('%B %Y').capitalize()}"

            # Nouveau tableau synthétique simple
            synthese = []
            fig = go.Figure()
            colors = ['#003087', '#4A90E2']
            for i, pn in enumerate(selected_pns):
                df = st.session_state.pn_data[pn]
                if df.empty:
                    st.error(f"Les données pour {pn} sont vides. Veuillez charger un fichier valide.")
                    continue
                model, forecast = run_prophet_forecast(df, months, forecast_start_date)
                trends = st.session_state.pn_trend.get(pn, {})
                enable_trends = st.session_state.pn_trend_enabled.get(pn, False)
                forecast_adjusted = forecast.copy()
                if enable_trends and trends:
                    forecast_adjusted = adjust_forecast(forecast, df, trends, forecast_start_year=forecast_start_date.year)
                # Indicateurs simples
                total_prevu = forecast_adjusted['yhat'].sum() if not forecast_adjusted.empty else 0
                moyenne_mensuelle = total_prevu / months if total_prevu != 0 else 0
                mae = None
                try:
                    df_cv = cross_validation(model, horizon='365 days', initial='730 days', period='180 days')
                    mae = performance_metrics(df_cv)['mae'].mean() if not df_cv.empty else None
                except Exception:
                    mae = None
                synthese.append({
                    "PN": f"{pn} ({PN_MODEL_MAPPING.get(pn, 'Inconnu')})",
                    "Total prévu": f"{total_prevu:.0f}",
                    "Moyenne mensuelle": f"{moyenne_mensuelle:.0f}",
                    "MAE": f"{mae:.1f}" if mae is not None else "N/A"
                })
                # Graphe
                fig.add_trace(go.Scatter(
                    x=df['ds'], y=df['y'], mode='lines+markers', name=f'Données réelles ({pn})',
                    line=dict(color=colors[i]), marker=dict(size=10),
                    hovertemplate=f'{pn}: Date: %{{x|%Y-%m}}<br>Quantité: %{{y:.0f}}<extra></extra>'
                ))
                fig.add_trace(go.Scatter(
                    x=forecast_adjusted['ds'], y=forecast_adjusted['yhat'], name=f'Prévision ({pn})',
                    line=dict(color=colors[i], dash='dash' if not enable_trends else None),
                    hovertemplate=f'{pn}: Date: %{{x|%Y-%m}}<br>Prévision: %{{y:.0f}}<extra></extra>'
                ))
            fig.update_layout(
                title='Comparaison des prévisions',
                xaxis_title='Date',
                yaxis_title='Quantité',
                height=600,
                showlegend=True,
                margin=dict(l=50, r=50, t=50, b=50),
                xaxis=dict(type='date'),
                plot_bgcolor='#F5F7FA',
                paper_bgcolor='#FFFFFF',
                font_color='#003087'
            )
            st.plotly_chart(fig, use_container_width=True)
            if len(synthese) == 2:
                st.markdown("#### Synthèse comparative")
                synthese_df = pd.DataFrame(synthese).set_index("PN")
                st.dataframe(synthese_df, use_container_width=True)
    else:
        st.info("Ajoutez au moins deux PN pour comparer.")