import streamlit as st
from datetime import datetime
from utils.data_utils import load_excel, save_json_data
import os

def render_add_pn():
    """
    Affiche la section "Ajouter un PN".
    """
    st.subheader("Ajouter un nouveau PN")
    st.info("Importez un fichier Excel pour ajouter un PN. Les tendances personnalisées sont désormais gérées dans l'onglet dédié 'Trend perso'.")

    st.markdown("### Ajouter un PN individuellement")
    # Suppression de toute option de trend perso ici
    with st.form(key="add_pn_form"):
        pn_name = st.text_input("Nom du PN")
        uploaded_file = st.file_uploader("Importer un fichier Excel (colonnes : Année, Mois, Quantité)", type=["xlsx"])
        submit_button = st.form_submit_button("Ajouter le PN")

        if submit_button and pn_name and uploaded_file:
            with st.spinner("Chargement du fichier Excel..."):
                df = load_excel(uploaded_file, file_name=pn_name)
            if df is not None:
                st.session_state.pn_data[pn_name] = df
                st.session_state.pn_last_updated[pn_name] = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.pn_trend[pn_name] = {}  # plus de trend ici
                st.session_state.pn_trend_enabled[pn_name] = False
                st.session_state.pn_file_name[pn_name] = uploaded_file.name
                save_json_data(
                    st.session_state.pn_data,
                    st.session_state.pn_last_updated,
                    st.session_state.pn_trend,
                    st.session_state.pn_trend_enabled,
                    st.session_state.pn_file_name
                )
                st.session_state.active_section = "dashboard"
                st.success(f"PN {pn_name} ajouté avec succès !")
                st.rerun()

    st.markdown("### Importer plusieurs PN")
    st.info("Sélectionnez plusieurs fichiers Excel. Le nom de chaque fichier (sans .xlsx) sera utilisé comme nom du PN. Les tendances personnalisées sont désactivées par défaut.")
    with st.form(key="batch_add_pn_form"):
        uploaded_files = st.file_uploader("Importer plusieurs fichiers Excel", type=["xlsx"], accept_multiple_files=True)
        batch_submit_button = st.form_submit_button("Importer plusieurs PN")

        if batch_submit_button and uploaded_files:
            success_count = 0
            for file in uploaded_files:
                pn_name = os.path.splitext(file.name)[0]
                if pn_name in st.session_state.pn_data:
                    st.warning(f"Le PN {pn_name} existe déjà. Il sera ignoré.")
                    continue
                with st.spinner(f"Chargement du fichier {file.name}..."):
                    df = load_excel(file, file_name=file.name)
                if df is not None:
                    st.session_state.pn_data[pn_name] = df
                    st.session_state.pn_last_updated[pn_name] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    st.session_state.pn_trend[pn_name] = {}
                    st.session_state.pn_trend_enabled[pn_name] = False
                    st.session_state.pn_file_name[pn_name] = file.name
                    success_count += 1
            if success_count > 0:
                save_json_data(
                    st.session_state.pn_data,
                    st.session_state.pn_last_updated,
                    st.session_state.pn_trend,
                    st.session_state.pn_trend_enabled,
                    st.session_state.pn_file_name
                )
                st.session_state.active_section = "dashboard"
                st.success(f"{success_count} PN(s) ajouté(s) avec succès !")
                st.rerun()
            else:
                st.error("Aucun PN n'a pu être ajouté. Vérifiez les fichiers importés.")

    st.markdown("### Format attendu pour l'import des données")
    st.info(
        "Le fichier Excel doit contenir les colonnes suivantes :\n"
        "- **Année** : L'année des données (ex : 2025).\n"
        "- **Mois** : Le mois des données (ex : Janvier).\n"
        "- **Quantité** : La quantité associée au PN pour ce mois.\n"
        "\n"
        "Assurez-vous que les colonnes soient correctement nommées et que les données soient complètes."
    )