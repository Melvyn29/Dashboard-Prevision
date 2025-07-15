# Instructions pour personnaliser l'icône de l'onglet

## Option 1: Icône en ligne (actuellement configurée)
L'application utilise actuellement la favicon d'Air France depuis leur site web.

## Option 2: Icône locale (recommandée pour la production)

### Étapes pour ajouter une icône locale :

1. **Télécharger l'icône Air France Industries**
   - Format recommandé : PNG ou ICO
   - Taille recommandée : 32x32 pixels ou 16x16 pixels
   - Nommer le fichier : `airfrance-industries.png` ou `airfrance-industries.ico`

2. **Placer le fichier dans le dossier assets**
   ```
   assets/
   └── airfrance-industries.png
   ```

3. **Modifier le code dans app.py**
   Remplacer dans la fonction `set_custom_favicon()` :
   ```python
   def set_custom_favicon():
       """Configure une favicon personnalisée pour l'application"""
       st.markdown(
           """
           <link rel="icon" type="image/png" href="data:image/png;base64,{base64_icon}">
           <link rel="shortcut icon" type="image/png" href="data:image/png;base64,{base64_icon}">
           """.format(base64_icon=get_base64_icon()),
           unsafe_allow_html=True
       )

   def get_base64_icon():
       import base64
       with open("assets/airfrance-industries.png", "rb") as f:
           return base64.b64encode(f.read()).decode()
   ```

## Option 3: Hébergement sur Streamlit Cloud
Si vous déployez sur Streamlit Cloud, assurez-vous que le fichier d'icône est inclus dans votre repository GitHub.

## Titre actuel de l'onglet
"Air France Industries - Prévisions Pneumatiques"

Vous pouvez le modifier dans `st.set_page_config()` si nécessaire.
