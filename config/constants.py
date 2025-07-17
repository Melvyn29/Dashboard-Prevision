"""
Constantes de l'application
Centralise toutes les constantes utilisées dans l'application
"""

# Informations de l'application
APP_NAME = "Air France Industries - Prévisions Pneumatiques"
APP_VERSION = "2.0"
APP_AUTHOR = "Melvyn Brichet"
APP_DEPARTMENT = "Air France industries - Atelier Roues et Pneus - MSEO"

# Configuration des fichiers
DATA_FILE = "pn_data.json"
LOGO_PATH = "assets/airfrance-logo.png"
BACKUP_DIR = "backups"

# Configuration par défaut
DEFAULT_TREND_YEAR = 2025
DEFAULT_TREND_PERCENTAGE = 0.0
DEFAULT_DATA_LINK = "https://example.com"

# Messages utilisateur
MESSAGES = {
    'no_pn_available': "Aucun PN disponible. Ajoutez un PN pour commencer.",
    'file_loading': "Chargement du fichier Excel...",
    'trend_info': "Les tendances personnalisées sont désormais gérées dans l'onglet dédié 'Trend perso'.",
    'format_info': (
        "Le fichier Excel doit contenir les colonnes suivantes :\n"
        "- **Année** : L'année des données (ex : 2025).\n"
        "- **Mois** : Le mois des données (ex : Janvier ou janvier).\n"
        "- **Quantité** : La quantité associée au PN pour ce mois.\n"
        "\n"
        "Note : Les mois peuvent être écrits avec ou sans majuscule initiale.\n"
        "Assurez-vous que les colonnes soient correctement nommées et que les données soient complètes."
    ),
    'batch_import_info': (
        "Sélectionnez plusieurs fichiers Excel. Le nom de chaque fichier sera analysé pour extraire "
        "le PN et le modèle d'avion selon le format : Export_PN-modèle.xlsx"
    )
}

# Formats de fichier
EXCEL_EXTENSIONS = ["xlsx", "xls"]
REQUIRED_COLUMNS = ["Année", "Mois", "Quantité"]

# Formats de date
DATE_FORMAT = "%Y-%m-%d %H:%M"
DISPLAY_DATE_FORMAT = "%d/%m/%Y"
DISPLAY_TIME_FORMAT = "%H:%M"
