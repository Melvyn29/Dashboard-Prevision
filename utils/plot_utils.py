import plotly.graph_objects as go
import pandas as pd
from utils.data_utils import get_aircraft_model
import streamlit as st
from prophet import Prophet

def generate_forecast_plot(df, forecast_adjusted, selected_pn, forecast_start_date, forecast_end_date, enable_trends, pn_aircraft_model=None):
    """
    Génère un graphique Plotly pour les prévisions.

    Args:
        df (pandas.DataFrame): Données historiques.
        forecast_adjusted (pandas.DataFrame): Prévisions ajustées.
        selected_pn (str): PN sélectionné.
        forecast_start_date (datetime): Date de début des prévisions.
        forecast_end_date (datetime): Date de fin des prévisions.
        enable_trends (bool): Activation des tendances personnalisées.
        pn_aircraft_model (dict): Dictionnaire des modèles d'avion personnalisés.

    Returns:
        plotly.graph_objects.Figure: Graphique Plotly.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['ds'], y=df['y'], name='Données historiques', mode='lines+markers',
        line=dict(color='#003087'), marker=dict(size=6),
        hovertemplate='Date: %{x|%Y-%m}<br>Quantité: %{y:.0f}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=forecast_adjusted['ds'], y=forecast_adjusted['yhat'], name='Prévisions',
        line=dict(color='#CE1126', dash='dash'),
        hovertemplate='Date: %{x|%Y-%m}<br>Prévision: %{y:.0f}<extra></extra>'
    ))
    if 'yhat_lower' in forecast_adjusted.columns and 'yhat_upper' in forecast_adjusted.columns:
        fig.add_trace(go.Scatter(
            x=forecast_adjusted['ds'], y=forecast_adjusted['yhat_upper'],
            fill=None, mode='lines', line_color='rgba(0,0,0,0)', showlegend=False
        ))
    fig.add_trace(go.Scatter(
        x=forecast_adjusted['ds'], y=forecast_adjusted['yhat_lower'],
        fill='tonexty', mode='lines', line_color='rgba(0,0,0,0)', name='Intervalle de confiance',
        fillcolor='rgba(206, 17, 38, 0.2)',
        hovertemplate='Date: %{x|%Y-%m}<br>Intervalle: %{y:.0f}<extra></extra>'
    ))
    if not df['ds'].empty:
        last_historical_date = df['ds'].max()
        fig.add_vline(x=last_historical_date.timestamp() * 1000, line=dict(color='#CE1126', dash='dash'),
                      annotation_text="Début des données historiques", annotation_position="top")
    fig.update_layout(
        title=f'Prévisions pour {selected_pn} ({get_aircraft_model(selected_pn, pn_aircraft_model)})',
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
    return fig

def plot_forecast(forecast, df, selected_pn):
    """
    Affiche un graphique des prévisions avec Plotly.

    Args:
        forecast (pandas.DataFrame): Prévisions générées par Prophet.
        df (pandas.DataFrame): Données historiques.
        selected_pn (str): PN sélectionné.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['ds'], y=df['y'], mode='lines+markers', name='Données historiques',
        line=dict(color='blue'), marker=dict(size=6)
    ))
    fig.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Prévisions',
        line=dict(color='red', dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat_upper'], 
        fill=None, mode='lines', line_color='rgba(0,0,0,0)', showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat_lower'], 
        fill='tonexty', mode='lines', line_color='rgba(0,0,0,0)', 
        name='Intervalle de confiance', fillcolor='rgba(255,0,0,0.2)'
    ))
    fig.update_layout(
        title=f'Prévisions pour {selected_pn}',
        xaxis_title='Date',
        yaxis_title='Quantité',
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

def generate_trend_plot(trend_forecast, trend_forecast_adjusted, enable_trends):
    """
    Génère un graphique de tendance.

    Args:
        trend_forecast (pandas.DataFrame): Prévisions de tendance originale.
        trend_forecast_adjusted (pandas.DataFrame): Prévisions de tendance ajustée.
        enable_trends (bool): Indicateur d'activation des tendances.

    Returns:
        plotly.graph_objects.Figure: Graphique Plotly.
    """
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=trend_forecast['ds'], y=trend_forecast['trend'], name='Tendance originale',
        line=dict(color='#4A90E2'),
        hovertemplate='Date: %{x|%Y-%m}<br>Tendance originale: %{y:.0f}<extra></extra>'
    ))
    if enable_trends:
        fig_trend.add_trace(go.Scatter(
            x=trend_forecast_adjusted['ds'], y=trend_forecast_adjusted['trend'], name='Tendance ajustée',
            line=dict(color='#003087'),
            hovertemplate='Date: %{x|%Y-%m}<br>Tendance ajustée: %{y:.0f}<extra></extra>'
        ))
    fig_trend.update_layout(
        title='Tendances originale et ajustée' if enable_trends else 'Tendance originale',
        xaxis_title='Date',
        yaxis_title='Tendance',
        height=400,
        showlegend=True,
        plot_bgcolor='#F5F7FA',
        paper_bgcolor='#FFFFFF',
        font_color='#003087'
    )
    return fig_trend

def generate_seasonality_plot(pns_to_plot, pn_data, pn_aircraft_model=None):
    """
    Génère un graphique Plotly pour la saisonnalité des PN.

    Args:
        pns_to_plot (list): Liste des PN à afficher.
        pn_data (dict): Données des PN.
        pn_aircraft_model (dict): Dictionnaire des modèles d'avion personnalisés.

    Returns:
        plotly.graph_objects.Figure: Graphique Plotly.
    """
    fig_seasonality = go.Figure()
    colors = ['#003087', '#4A90E2', '#CE1126'] + ['#4682B4', '#87CEEB', '#B22222']
    color_idx = 0

    for pn in pns_to_plot:
        df = pn_data[pn]
        if df.empty:
            continue
        model = Prophet(yearly_seasonality=True)
        model.fit(df[['ds', 'y']])
        future = pd.date_range(start='2025-01-01', periods=12, freq='MS').to_frame(index=False, name='ds')
        forecast = model.predict(future)
        monthly_seasonality = forecast[['ds', 'yearly']].copy()
        monthly_seasonality['Month'] = monthly_seasonality['ds'].dt.strftime('%b')
        monthly_seasonality['yearly'] = monthly_seasonality['yearly'].clip(lower=0)

        fig_seasonality.add_trace(go.Scatter(
            x=monthly_seasonality['Month'],
            y=monthly_seasonality['yearly'],
            mode='lines+markers',
            name=f"{pn} ({get_aircraft_model(pn, pn_aircraft_model)})",
            line=dict(color=colors[color_idx % len(colors)]),
            marker=dict(size=8),
            hovertemplate=f'Mois: %{{x}}<br>Saisonnalité: %{{y:.2f}}<br>PN: {pn}<extra></extra>'
        ))
        color_idx += 1

    fig_seasonality.update_layout(
        title='Comparaison de la saisonnalité annuelle',
        xaxis_title='Mois',
        yaxis_title='Effet saisonnier',
        height=500,
        showlegend=True,
        plot_bgcolor='#F5F7FA',
        paper_bgcolor='#FFFFFF',
        font_color='#003087'
    )
    return fig_seasonality
