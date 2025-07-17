import streamlit as st
from datetime import datetime
from utils.data_utils import load_excel, save_json_data, get_aircraft_model
import os

def render_modify_pn():
    """
    Affiche la section "Modifier un PN" (sans gestion de tendance personnalisée).
    """
    st.subheader("Modifier un PN")
    # Réinitialisation déplacée en bas avec confirmation
    show_confirm = False
    if 'show_reset_confirm' not in st.session_state:
        st.session_state['show_reset_confirm'] = False

    if st.session_state.pn_data:
        # Initialiser le dictionnaire des modèles s'il n'existe pas
        if 'pn_aircraft_model' not in st.session_state:
            st.session_state.pn_aircraft_model = {}
            
        pn_options = sorted(
            [f"{pn} ({get_aircraft_model(pn, st.session_state.pn_aircraft_model)})" for pn in st.session_state.pn_data.keys()],
            key=lambda x: (
                get_aircraft_model(x.split(" (")[0], st.session_state.pn_aircraft_model),
                x.split(" (")[0]
            )
        )
        selected_pn_display = st.session_state.get('selected_pn', st.selectbox("Sélectionner un PN à modifier", pn_options, key="modify_pn_select"))
        selected_pn = selected_pn_display.split(" (")[0]
        if selected_pn:
            current_model = get_aircraft_model(selected_pn, st.session_state.pn_aircraft_model)
            with st.expander(f"PN: {selected_pn} ({current_model})", expanded=True):
                st.markdown(f"**Fichier associé** : {st.session_state.pn_file_name.get(selected_pn, 'N/A')} | **Modèle** : {current_model}")
                
                # Section pour modifier le modèle d'avion
                st.markdown("#### Modifier le modèle d'avion")
                
                # Saisie libre du modèle d'avion
                new_aircraft_model = st.text_input(
                    "Nouveau modèle d'avion", 
                    value=current_model if current_model != "Inconnu" else "",
                    placeholder="Ex: A320 NEO, B777-300, TAV A350...",
                    help="Saisissez librement le modèle d'avion correspondant à ce PN",
                    key=f"model_input_{selected_pn}"
                )
                
                new_file = st.file_uploader(f"Nouveau fichier pour {selected_pn}", type=["xlsx"], key=f"update_file_{selected_pn}")
                with st.form(key=f"modify_pn_form_{selected_pn}"):
                    col_update, col_delete = st.columns(2)
                    with col_update:
                        if st.form_submit_button(f"Mettre à jour {selected_pn}"):
                            trends = {}
                            if new_file:
                                with st.spinner(f"Chargement du fichier pour {selected_pn}..."):
                                    df = load_excel(new_file, file_name=selected_pn)
                                if df is not None:
                                    st.session_state.pn_data[selected_pn] = df
                                    st.session_state.pn_file_name[selected_pn] = new_file.name
                            
                            # Mettre à jour le modèle d'avion
                            final_model = new_aircraft_model.strip() if new_aircraft_model.strip() else "Inconnu"
                            st.session_state.pn_aircraft_model[selected_pn] = final_model
                            
                            st.session_state.pn_trend[selected_pn] = trends
                            st.session_state.pn_trend_enabled[selected_pn] = False
                            st.session_state.pn_last_updated[selected_pn] = datetime.now().strftime("%Y-%m-%d %H:%M")
                            save_json_data(
                                st.session_state.pn_data,
                                st.session_state.pn_last_updated,
                                st.session_state.pn_trend,
                                st.session_state.pn_trend_enabled,
                                st.session_state.pn_file_name,
                                st.session_state.pn_aircraft_model
                            )
                            st.session_state.active_section = "dashboard"
                            st.success(f"PN {selected_pn} mis à jour avec succès ! Modèle : {final_model}")
                            st.rerun()
                    with col_delete:
                        if st.form_submit_button(f"Supprimer {selected_pn}"):
                            del st.session_state.pn_data[selected_pn]
                            del st.session_state.pn_last_updated[selected_pn]
                            del st.session_state.pn_trend[selected_pn]
                            del st.session_state.pn_trend_enabled[selected_pn]
                            del st.session_state.pn_file_name[selected_pn]
                            if selected_pn in st.session_state.pn_aircraft_model:
                                del st.session_state.pn_aircraft_model[selected_pn]
                            save_json_data(
                                st.session_state.pn_data,
                                st.session_state.pn_last_updated,
                                st.session_state.pn_trend,
                                st.session_state.pn_trend_enabled,
                                st.session_state.pn_file_name,
                                st.session_state.pn_aircraft_model
                            )
                            st.session_state.active_section = "dashboard"
                            st.success(f"PN {selected_pn} supprimé.")
                            st.rerun()
    else:
        st.info("Aucun PN disponible pour modification.")
    # Fin de page : bouton réinitialiser
    st.markdown('---')
    if st.button("Réinitialiser toutes les données", key="reset_all_data_bottom"):
        st.session_state['show_reset_confirm'] = True
    if st.session_state['show_reset_confirm']:
        st.warning("Êtes-vous sûr de vouloir réinitialiser toutes les données ? Cette action est irréversible.")
        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.button("Confirmer la réinitialisation", key="confirm_reset"):
                import os
                if os.path.exists("pn_data.json"):
                    os.remove("pn_data.json")
                st.session_state.clear()
                st.session_state.active_section = "dashboard"
                st.success("Toutes les données ont été réinitialisées !")
                st.rerun()
        with col_cancel:
            if st.button("Annuler", key="cancel_reset"):
                st.session_state['show_reset_confirm'] = False