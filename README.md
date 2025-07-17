# Dashboard-Prévision - Air France Industries

Application Streamlit pour l'analyse et la prévision de la demande de pneumatiques pour Air France Industries.

## 🚀 Fonctionnalités

- **Tableau de bord interactif** : Vue d'ensemble des PN avec métriques et filtrage
- **Import de données** : Ajout individuel ou en lot de PN via fichiers Excel
- **Analyse avancée** : Prévisions avec Prophet et tendances personnalisées
- **Comparaison** : Analyse comparative entre différents PN
- **Rapports** : Génération de rapports PDF détaillés
- **Gestion de données** : Sauvegarde, modification et suivi des performances

## 📁 Structure du projet

```
📁 Structure optimisée
├── 🎯 app.py (Point d'entrée simplifié)
├── 🧩 components/ (Composants UI modulaires)
├── ⚙️ config/ (Configuration centralisée)
├── 🛠️ utils/ (Utilitaires réutilisables)
└── 📊 assets/ (Ressources statiques)
```

## 🛠️ Installation

1. **Cloner le repository**
   ```bash
   git clone [URL_DU_REPOSITORY]
   cd Dashboard-Prevision
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer l'application**
   ```bash
   streamlit run app.py
   ```

## 📊 Format des données

Les fichiers Excel doivent contenir les colonnes suivantes :
- **Année** : Année des données (ex: 2025)
- **Mois** : Mois en français (ex: Janvier, Février...)
- **Quantité** : Quantité du PN pour ce mois

### Format des noms de fichier (import en lot)
- `Export_PN-Modèle.xlsx` → PN et modèle d'avion extraits automatiquement
- Exemple : `Export_M01103-02-A320NEO.xlsx`

## 🔧 Architecture technique

### Composants principaux

- **SessionManager** : Gestion centralisée de l'état Streamlit
- **DataValidator** : Validation des données d'entrée
- **Navigation** : Routage et navigation entre les sections
- **Constants** : Centralisation des constantes

### Patterns appliqués

- **Séparation des responsabilités** : Chaque module a une responsabilité claire
- **Validation centralisée** : Toutes les validations dans un module dédié
- **Configuration externalisée** : Constantes et messages dans des fichiers séparés
- **Code réutilisable** : Fonctions utilitaires partagées

## 🚀 Améliorations apportées

### Structure et organisation
- ✅ Séparation claire des composants
- ✅ Modules utilitaires centralisés
- ✅ Configuration externalisée
- ✅ Validation des données

### Qualité du code
- ✅ Documentation des fonctions
- ✅ Noms de variables explicites
- ✅ Gestion d'erreurs améliorée
- ✅ Code DRY (Don't Repeat Yourself)

### Maintenabilité
- ✅ Structure modulaire
- ✅ Constantes centralisées
- ✅ Fonctions réutilisables
- ✅ Commentaires pertinents

## 👥 Auteur

**Melvyn Brichet** - Projet de stage - Air France Industries
- Atelier Roues et Pneus - MSEO
- Version 2.0

## 📝 License

© 2025 Air France Industries. Tous droits réservés.