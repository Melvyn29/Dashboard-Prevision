import streamlit as st
from datetime import datetime
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from utils.forecast_utils import run_prophet_forecast, adjust_forecast
from utils.data_utils import get_aircraft_model
from prophet.diagnostics import cross_validation, performance_metrics

def generate_pdf_report(selected_pns, months, forecast_start_date, kpis_to_include, pn_data, pn_last_updated, pn_trend, pn_trend_enabled, pn_aircraft_model=None):
    """
    Génère un rapport PDF pour les PN sélectionnés.

    Args:
        selected_pns (list): Liste des PN à inclure.
        months (int): Nombre de mois à prévoir.
        forecast_start_date (datetime): Date de début des prévisions.
        kpis_to_include (list): Indicateurs clés à inclure.
        pn_data (dict): Données des PN.
        pn_last_updated (dict): Dates de mise à jour des PN.
        pn_trend (dict): Tendances personnalisées des PN.
        pn_trend_enabled (dict): Indicateur d'activation des tendances.

    Returns:
        bytes: Contenu du fichier PDF, ou None en cas d'erreur.
    """
    forecast_start = pd.to_datetime(forecast_start_date)
    forecast_end_date = (forecast_start + pd.offsets.MonthEnd(months)).normalize()
    period_str = f"{forecast_start.strftime('%B %Y').capitalize()} à {forecast_end_date.strftime('%B %Y').capitalize()}"
    current_datetime = datetime.now().strftime('%d %B %Y, %H:%M')

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)
    # Première page du rapport
    elements = []
    # Styles personnalisés
    title_style = ParagraphStyle(
        name='TitleStyle', fontSize=22, alignment=TA_CENTER, leading=28, spaceAfter=18, fontName='Helvetica-Bold', textColor=colors.HexColor('#1B263B'), underlineWidth=1
    )
    normal_style = ParagraphStyle(
        name='NormalStyle', fontSize=12, leading=18, spaceAfter=12, fontName='Helvetica', alignment=TA_LEFT, textColor=colors.HexColor('#22223B')
    )
    heading_style = ParagraphStyle(
        name='HeadingStyle', fontSize=15, spaceAfter=12, spaceBefore=14, fontName='Helvetica-Bold', textColor=colors.HexColor('#415A77'), alignment=TA_LEFT
    )
    table_header_style = ParagraphStyle(
        name='TableHeader', fontSize=12, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER, backColor=colors.HexColor('#415A77')
    )
    table_cell_style = ParagraphStyle(
        name='TableCell', fontSize=12, fontName='Helvetica', alignment=TA_CENTER, textColor=colors.HexColor('#22223B')
    )
    # Titre
    elements.append(Paragraph("Rapport de Prévision Pneumatique – Atelier Roues et pneus MSEO – Air France industries", title_style))
    elements.append(Spacer(1, 0.6*cm))
    # Introduction (une seule fois)
    intro = ("Ce rapport présente les prévisions de la demande des pneumatiques de l’atelier roues et pneus d’airfrance industries. "
             "Les résultats sont issus d'analyses statistiques fondées sur les données historiques disponibles et l'application de modèles prédictifs. "
             "Ce document est destiné à appuyer les décisions en matière de planification des stocks et d'approvisionnement.")
    elements.append(Paragraph(intro, normal_style))
    elements.append(Spacer(1, 0.6*cm))
    # Tableau des PN
    pn_table_data = [[Paragraph("PN", table_header_style), Paragraph("Modèle", table_header_style)]]
    for pn in selected_pns:
        pn_table_data.append([Paragraph(pn, table_cell_style), Paragraph(get_aircraft_model(pn, pn_aircraft_model), table_cell_style)])
    pn_table = Table(pn_table_data, colWidths=[7*cm, 7*cm])
    pn_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#415A77')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E0E1DD')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#415A77')),
    ]))
    elements.append(pn_table)
    elements.append(Spacer(1, 0.6*cm))
    # Avertissement (en bas de la première page uniquement)
    elements.append(Paragraph("Avertissement", heading_style))
    disclaimer = ("Les prévisions présentées dans ce rapport sont générées à partir de modèles statistiques fondés sur des données historiques. "
                  "Elles sont sujettes à des incertitudes liées à des événements imprévus, des changements de contexte opérationnel ou des variations dans les comportements de consommation. "
                  "Il est recommandé de les utiliser comme support d'aide à la décision, et non comme valeur absolue.")
    elements.append(Paragraph(disclaimer, normal_style))
    elements.append(PageBreak())

    for idx, pn in enumerate(selected_pns):
        # Titre PN
        pn_title = f"Rapport de Prévision de la Demande PN : {pn} ({get_aircraft_model(pn, pn_aircraft_model)})"
        elements.append(Paragraph(pn_title, title_style))
        elements.append(Spacer(1, 0.4*cm))
        # Introduction supprimée ici (n’est plus répétée)
        elements.append(Paragraph("Informations Générales", heading_style))
        general_info = f"PN : {pn} ({get_aircraft_model(pn, pn_aircraft_model)})<br/>Dernière mise à jour : {pn_last_updated.get(pn, 'N/A')}"
        elements.append(Paragraph(general_info, normal_style))
        elements.append(Spacer(1, 0.6*cm))

        df = pn_data.get(pn)
        if df is None or df.empty:
            elements.append(Paragraph(f"Aucune donnée disponible pour {pn}.", normal_style))
            continue

        model, forecast = run_prophet_forecast(df, months, forecast_start_date)
        trends = pn_trend.get(pn, {})
        enable_trends = pn_trend_enabled.get(pn, False)
        forecast_adjusted = forecast.copy()
        if enable_trends and trends:
            forecast_adjusted = adjust_forecast(forecast, df, trends, forecast_start_year=forecast_start_date.year)

        df_cv = cross_validation(model, horizon='365 days', initial='730 days', period='180 days')
        mae = performance_metrics(df_cv)['mae'].mean() if not df_cv.empty else None

        yearly_totals = df.groupby(df['ds'].dt.year)['y'].sum()
        current_year = datetime.now().year
        complete_years = yearly_totals[yearly_totals.index < current_year]
        reference_year = complete_years.index.min() if not complete_years.empty else None
        last_complete_year = complete_years.index.max() if not complete_years.empty else None
        total_growth = 0
        if reference_year is not None and last_complete_year is not None and reference_year != last_complete_year:
            reference_total = complete_years.get(reference_year, 0)
            last_complete_total = complete_years.get(last_complete_year, 0)
            total_growth = ((last_complete_total - reference_total) / reference_total * 100) if reference_total != 0 else 0

        previous_year = forecast_start_date.year - 1
        total_previous_year = yearly_totals.get(previous_year, 0)
        total_forecast_period = forecast_adjusted['yhat'].sum() if not forecast_adjusted.empty else 0
        monthly_avg_forecast_period = total_forecast_period / months if total_forecast_period != 0 else 0

        if kpis_to_include:
            kpi_data = [["Indicateur", "Valeur"]]
            if "Croissance totale" in kpis_to_include:
                kpi_data.append([f"Croissance totale ({reference_year} à {last_complete_year})", f"{total_growth:.1f}%"])
            if "Total précédent" in kpis_to_include:
                kpi_data.append([f"Total {previous_year}", f"{total_previous_year:.0f}"])
            if "Total prévu" in kpis_to_include:
                kpi_data.append([f"Total prévu ({period_str})", f"{total_forecast_period:.0f}"])
            if "Moyenne mensuelle" in kpis_to_include:
                kpi_data.append([f"Moyenne mensuelle ({period_str})", f"{monthly_avg_forecast_period:.0f}"])
            if "MAE" in kpis_to_include:
                kpi_data.append(["Fiabilité (MAE)", f"{mae:.1f}" if mae is not None else "N/A"])

            kpi_table = Table(kpi_data, colWidths=[8*cm, 8*cm])
            kpi_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#415A77')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F7FA')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(kpi_table)
            elements.append(Spacer(1, 0.6*cm))

        forecast_out = forecast_adjusted[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
        forecast_out['Année'] = forecast_out['ds'].dt.year
        forecast_out['Mois'] = forecast_out['ds'].dt.strftime('%B')
        forecast_out = forecast_out[['Année', 'Mois', 'yhat', 'yhat_lower', 'yhat_upper']]
        forecast_out.columns = ['Année', 'Mois', 'Prévision', 'Valeur basse', 'Valeur haute']
        forecast_out['Prévision'] = forecast_out['Prévision'].round(0).astype(int)
        forecast_out['Valeur basse'] = forecast_out['Valeur basse'].round(0).astype(int)
        forecast_out['Valeur haute'] = forecast_out['Valeur haute'].round(0).astype(int)

        forecast_data = [['Année', 'Mois', 'Prévision', 'Valeur basse', 'Valeur haute']]
        for _, row in forecast_out.iterrows():
            forecast_data.append([str(row['Année']), row['Mois'], str(row['Prévision']), str(row['Valeur basse']), str(row['Valeur haute'])])

        forecast_table = Table(forecast_data, colWidths=[3*cm, 4*cm, 3*cm, 3*cm, 3*cm])
        forecast_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#415A77')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F7FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(forecast_table)
        elements.append(Spacer(1, 0.6*cm))
        # Saut de page sauf pour le dernier PN
        if idx < len(selected_pns) - 1:
            elements.append(PageBreak())

    def add_footer(canvas, doc):
        canvas.saveState()
        footer_text = f"Rapport généré le {current_datetime} | Export du tableau de bord d'Air France Industries pour les prévisions de la demande"
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(A4[0]/2, 1.5*cm, footer_text)
        canvas.restoreState()

    if elements:
        doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
        pdf_data = buffer.getvalue()
        buffer.close()
        return pdf_data
    else:
        buffer.close()
        return None