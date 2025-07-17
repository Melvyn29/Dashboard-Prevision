"""
Module de validation des données
Centralise toutes les validations de l'application
"""

import pandas as pd
from typing import Union, List, Tuple
from config.constants import REQUIRED_COLUMNS


class DataValidator:
    """Classe pour valider les données de l'application"""
    
    @staticmethod
    def validate_pn_name(pn_name: str) -> Tuple[bool, str]:
        """
        Valide un nom de PN
        
        Args:
            pn_name (str): Nom du PN à valider
            
        Returns:
            Tuple[bool, str]: (est_valide, message_erreur)
        """
        if not pn_name or not pn_name.strip():
            return False, "Le nom du PN ne peut pas être vide"
        
        if len(pn_name.strip()) < 2:
            return False, "Le nom du PN doit contenir au moins 2 caractères"
        
        return True, ""
    
    @staticmethod
    def validate_aircraft_model(model: str) -> Tuple[bool, str]:
        """
        Valide un modèle d'avion
        
        Args:
            model (str): Modèle d'avion à valider
            
        Returns:
            Tuple[bool, str]: (est_valide, message_erreur)
        """
        # Le modèle peut être vide (sera défini comme "Inconnu")
        if model and len(model.strip()) > 100:
            return False, "Le modèle d'avion ne peut pas dépasser 100 caractères"
        
        return True, ""
    
    @staticmethod
    def validate_excel_structure(df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Valide la structure d'un DataFrame Excel
        
        Args:
            df (pd.DataFrame): DataFrame à valider
            
        Returns:
            Tuple[bool, str]: (est_valide, message_erreur)
        """
        # Vérification des colonnes
        if list(df.columns) != REQUIRED_COLUMNS:
            return False, f"Le fichier doit contenir exactement les colonnes : {', '.join(REQUIRED_COLUMNS)}"
        
        # Vérification des valeurs manquantes
        if df[REQUIRED_COLUMNS].isnull().any().any():
            return False, "Le fichier contient des valeurs manquantes"
        
        # Vérification des types de données
        try:
            # Vérifier que les années sont des entiers
            df['Année'].astype(int)
        except (ValueError, TypeError):
            return False, "La colonne 'Année' doit contenir des valeurs numériques entières"
        
        # Vérifier que les quantités sont numériques et non négatives
        try:
            quantities = pd.to_numeric(df['Quantité'], errors='raise')
            if (quantities < 0).any():
                return False, "La colonne 'Quantité' ne peut pas contenir de valeurs négatives"
        except (ValueError, TypeError):
            return False, "La colonne 'Quantité' doit contenir des valeurs numériques non négatives"
        
        return True, ""
    
    @staticmethod
    def validate_year_range(years: List[int], min_year: int = 2000, max_year: int = 2100) -> Tuple[bool, str]:
        """
        Valide une plage d'années
        
        Args:
            years (List[int]): Liste des années à valider
            min_year (int): Année minimum acceptable
            max_year (int): Année maximum acceptable
            
        Returns:
            Tuple[bool, str]: (est_valide, message_erreur)
        """
        for year in years:
            if not isinstance(year, int) or year < min_year or year > max_year:
                return False, f"Les années doivent être comprises entre {min_year} et {max_year}"
        
        return True, ""
    
    @staticmethod
    def validate_percentage(percentage: float) -> Tuple[bool, str]:
        """
        Valide un pourcentage
        
        Args:
            percentage (float): Pourcentage à valider
            
        Returns:
            Tuple[bool, str]: (est_valide, message_erreur)
        """
        if not isinstance(percentage, (int, float)):
            return False, "Le pourcentage doit être un nombre"
        
        if percentage < -100 or percentage > 1000:
            return False, "Le pourcentage doit être compris entre -100% et 1000%"
        
        return True, ""
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, str]:
        """
        Valide une URL
        
        Args:
            url (str): URL à valider
            
        Returns:
            Tuple[bool, str]: (est_valide, message_erreur)
        """
        if not url or not url.strip():
            return False, "L'URL ne peut pas être vide"
        
        url = url.strip()
        if not (url.startswith('http://') or url.startswith('https://')):
            return False, "L'URL doit commencer par http:// ou https://"
        
        if len(url) > 2000:
            return False, "L'URL ne peut pas dépasser 2000 caractères"
        
        return True, ""
