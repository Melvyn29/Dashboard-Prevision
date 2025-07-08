import streamlit as st
import pandas as pd
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics

@st.cache_data
def run_prophet_forecast(df, periods, start_date):
    """
    Exécute une prévision avec Prophet.

    Args:
        df (pandas.DataFrame): Données historiques avec colonnes 'ds' et 'y'.
        periods (int): Nombre de mois à prévoir.
        start_date (datetime): Date de début des prévisions.

    Returns:
        tuple: Modèle Prophet et DataFrame des prévisions.
    """
    model = Prophet()
    model.fit(df[['ds', 'y']])
    future = pd.date_range(start=start_date, periods=periods, freq='MS').to_frame(index=False, name='ds')
    return model, model.predict(future)

def adjust_forecast(forecast, df, trends, forecast_start_year=None, apply_all_trends=False):
    """
    Ajuste les prévisions en appliquant des tendances personnalisées avancées.
    L'impact de la tendance est proportionnel à la saisonnalité :
    - Les points hauts de la saison sont plus impactés que les points bas.
    """
    forecast_adjusted = forecast.copy()
    if not trends:
        return forecast_adjusted
    for year, trend_info in trends.items():
        try:
            year = int(year)
        except ValueError:
            st.error(f"Erreur : L'année {year} dans les tendances n'est pas valide.")
            continue
        if not (apply_all_trends or (forecast_start_year is not None and year >= forecast_start_year)):
            continue
        pct = 0.0
        if isinstance(trend_info, dict):
            # On prend la dernière valeur de l'année
            values = trend_info.get("values", {})
            if values:
                pct = list(values.values())[-1]
        else:
            pct = float(trend_info)
        # Application proportionnelle à la saisonnalité
        mask = (forecast_adjusted['ds'].dt.year == year)
        if not mask.any():
            continue
        # On prend la colonne de saisonnalité (si existante), sinon on approxime par la série 'yhat' ou 'trend'
        if 'seasonal' in forecast_adjusted.columns:
            seasonal = forecast_adjusted.loc[mask, 'seasonal']
        elif 'yhat' in forecast_adjusted.columns:
            # Approximation : saisonnalité = yhat - trend
            if 'trend' in forecast_adjusted.columns:
                seasonal = forecast_adjusted.loc[mask, 'yhat'] - forecast_adjusted.loc[mask, 'trend']
            else:
                seasonal = forecast_adjusted.loc[mask, 'yhat']
        else:
            seasonal = pd.Series(0, index=forecast_adjusted.loc[mask].index)
        # On normalise la saisonnalité entre 0 et 1
        min_season = seasonal.min()
        max_season = seasonal.max()
        if max_season - min_season == 0:
            coef = pd.Series(1, index=seasonal.index)
        else:
            coef = (seasonal - min_season) / (max_season - min_season)
        # L'impact est plus fort sur les points hauts
        impact = 1 + (coef * pct / 100)
        for col in ['yhat', 'yhat_lower', 'yhat_upper', 'trend']:
            if col in forecast_adjusted.columns:
                forecast_adjusted.loc[mask, col] = forecast_adjusted.loc[mask, col] * impact.values
    return forecast_adjusted