import plotly.graph_objects as go
import pandas as pd
from config.mappings import PN_MODEL_MAPPING

def generate_forecast_plot(df, forecast_adjusted, selected_pn, forecast_start_date, forecast_end_date, enable_trends):
    """
    Génère un graphique Plotly pour les prévisions.

    Args:
        df (pandas.DataFrame): Données historiques.
        forecast_adjusted (pandas.DataFrame): Prévisions ajustées.
        selected_pn (str): Numéro de pièce.
        forecast_start_date (datetime): Date de début des prévisions.
        forecast_end_date (datetime): Date de fin des prévisions.
        enable_trends (bool): Indique si les tendances personnalisées sont activées.

    Returns:
        plotly.graph_objects.Figure: Graphique Plotly.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['ds'], y=df['y'], mode='lines+markers', name='Données réelles',
        line=dict(color='black'), marker=dict(size=10),
        hovertemplate='Date: %{x|%Y-%m}<br>Quantité: %{y:.0f}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=forecast_adjusted['ds'], y=forecast_adjusted['yhat'], name='Prévision originale',
        line=dict(dash='dash', color='orange'),
        hovertemplate='Date: %{x|%Y-%m}<br>Prévision: %{y:.0f}<extra></extra>'
    ))
    if enable_trends:
        fig.add_trace(go.Scatter(
            x=forecast_adjusted['ds'], y=forecast_adjusted['yhat'], name='Prévision ajustée',
            line=dict(color='#003087'),
            hovertemplate='Date: %{x|%Y-%m}<br>Prévision ajustée: %{y:.0f}<extra></extra>'
        ))
    fig.add_trace(go.Scatter(
        x=forecast_adjusted['ds'], y=forecast_adjusted['yhat_upper'], fill=None, mode='lines', line_color='rgba(0,0,0,0)',
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=forecast_adjusted['ds'], y=forecast_adjusted['yhat_lower'], fill='tonexty', fillcolor='rgba(0,176,246,0.2)',
        mode='lines', line_color='rgba(0,0,0,0)', name='Intervalle de confiance',
        hovertemplate='Date: %{x|%Y-%m}<br>Intervalle: %{y:.0f}<extra></extra>'
    ))
    if not df['ds'].empty:
        last_historical_date = df['ds'].max()
        fig.add_vline(x=last_historical_date.timestamp() * 1000, line=dict(color='#CE1126', dash='dash'),
                      annotation_text="Début des données historiques", annotation_position="top")
    fig.update_layout(
        title=f'Prévisions pour {selected_pn} ({PN_MODEL_MAPPING.get(selected_pn, "Inconnu")})',
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

def generate_trend_plot(trend_forecast, trend_forecast_adjusted, enable_trends):
    """
    Génère un graphique Plotly pour les tendances.

    Args:
        trend_forecast (pandas.DataFrame): Prévisions de tendance originale.
        trend_forecast_adjusted (pandas.DataFrame): Prévisions de tendance ajustée.
        enable_trends (bool): Indique si les tendances personnalisées sont activées.

    Returns:
        plotly.graph_objects.Figure: Graphique Plotly.
    """
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=trend_forecast['ds'], y=trend_forecast['trend'], name='Tendance originale',
        line=dict(dash='dash', color='orange'),
        hovertemplate='Date: %{x|%Y-%m}<br>Tendance: %{y:.0f}<extra></extra>'
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

def generate_seasonality_plot(pns_to_plot, pn_data):
    """
    Génère un graphique Plotly pour la saisonnalité des PN.

    Args:
        pns_to_plot (list): Liste des PN à afficher.
        pn_data (dict): Données des PN.

    Returns:
        plotly.graph_objects.Figure: Graphique Plotly.
    """
    from prophet import Prophet
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
            name=f"{pn} ({PN_MODEL_MAPPING.get(pn, 'Inconnu')})",
            line=dict(color=colors[color_idx % len(colors)]),
            marker=dict(size=10),
            hovertemplate='Mois: %{x}<br>Saisonnalité: %{y:.2f}<extra></extra>'
        ))
        color_idx += 1

    fig_seasonality.update_layout(
        title="Saisonnalité annuelle des PN",
        xaxis_title="Mois",
        yaxis_title="Composante saisonnière",
        height=500,
        showlegend=True,
        xaxis=dict(tickmode='array', tickvals=list(range(12)), ticktext=['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']),
        plot_bgcolor='#F5F7FA',
        paper_bgcolor='#FFFFFF',
        font_color='#003087'
    )
    return fig_seasonality