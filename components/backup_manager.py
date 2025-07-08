import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime as dt, timedelta

def render_backup_manager():
    st.markdown("<h2>Gestion des sauvegardes de données</h2>", unsafe_allow_html=True)
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)

    # Sauvegarde automatique hebdomadaire
    now = dt.now()
    backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.json')], reverse=True)
    last_auto = None
    for bkp in backups:
        if bkp.startswith("auto_"):
            last_auto = bkp
            break
    need_auto = True
    if last_auto:
        date_str = last_auto.split("_")[1].split(".")[0]
        try:
            last_auto_date = dt.strptime(date_str, "%Y%m%d")
            if (now - last_auto_date).days < 7:
                need_auto = False
        except:
            pass
    if need_auto:
        auto_name = f"auto_{now.strftime('%Y%m%d')}.json"
        backup_path = os.path.join(backup_dir, auto_name)
        backup_data = {
            "pn_data": {k: v.to_json(date_format='iso') if hasattr(v, 'to_json') else v for k, v in st.session_state.pn_data.items()},
            "pn_trend": st.session_state.pn_trend,
            "pn_trend_enabled": st.session_state.pn_trend_enabled,
            "pn_last_updated": st.session_state.pn_last_updated,
            "pn_file_name": st.session_state.pn_file_name
        }
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        st.success(f"Sauvegarde automatique hebdomadaire créée : {auto_name}")

    # Sauvegarde manuelle
    if st.button("Sauvegarder maintenant", key="save_backup_manual"):
        now_str = now.strftime("%Y-%m-%d_%Hh%Mmin%S")
        backup_path = os.path.join(backup_dir, f"backup_{now_str}.json")
        backup_data = {
            "pn_data": {k: v.to_json(date_format='iso') if hasattr(v, 'to_json') else v for k, v in st.session_state.pn_data.items()},
            "pn_trend": st.session_state.pn_trend,
            "pn_trend_enabled": st.session_state.pn_trend_enabled,
            "pn_last_updated": st.session_state.pn_last_updated,
            "pn_file_name": st.session_state.pn_file_name
        }
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        st.success(f"Sauvegarde manuelle créée : {backup_path}")

    # Liste des sauvegardes existantes
    backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.json')], reverse=True)
    if backups:
        st.markdown("#### Versions sauvegardées :")
        for bkp in backups:
            col1, col2, col3, col4 = st.columns([3,1,1,1])
            with col1:
                # Affichage nom + date lisible dans le titre (date seule, sans l'heure)
                try:
                    date_part = bkp.replace("backup_", "").replace("auto_", "").replace(".json", "")
                    if "_" in date_part and "h" in date_part:
                        date_obj = dt.strptime(date_part, "%Y-%m-%d_%Hh%Mmin%S")
                        date_str = date_obj.strftime("%d/%m/%Y")  # date only
                    else:
                        date_obj = dt.strptime(date_part, "%Y%m%d")
                        date_str = date_obj.strftime("%d/%m/%Y")
                except:
                    date_str = date_part
                # Titre avec date visible (sans l'heure)
                st.write(f"**{bkp}**  ", f"🗓️ {date_str}")
            with col2:
                if st.button(f"Restaurer", key=f"restore_{bkp}"):
                    with open(os.path.join(backup_dir, bkp), "r", encoding="utf-8") as f:
                        data = json.load(f)
                    pn_data = {k: pd.read_json(v) if isinstance(v, str) else v for k, v in data.get("pn_data", {}).items()}
                    st.session_state.pn_data = pn_data
                    st.session_state.pn_trend = data.get("pn_trend", {})
                    st.session_state.pn_trend_enabled = data.get("pn_trend_enabled", {})
                    st.session_state.pn_last_updated = data.get("pn_last_updated", {})
                    st.session_state.pn_file_name = data.get("pn_file_name", {})
                    st.success(f"Version restaurée depuis {bkp}. Rechargez la page pour voir l'effet.")
            with col3:
                with open(os.path.join(backup_dir, bkp), "rb") as f:
                    st.download_button("Exporter", f, file_name=bkp, mime="application/json", key=f"export_{bkp}")
            with col4:
                # Nouvelle confirmation inline, plus claire
                if st.session_state.get('delete_confirm') == bkp:
                    st.warning(f"Confirmer la suppression de {bkp} ?")
                    confirm_col, cancel_col = st.columns([1,1])
                    with confirm_col:
                        if st.button("✅ Oui, supprimer", key=f"confirm_delete_{bkp}"):
                            os.remove(os.path.join(backup_dir, bkp))
                            st.success(f"Sauvegarde supprimée : {bkp}")
                            st.session_state['delete_confirm'] = None
                    with cancel_col:
                        if st.button("❌ Annuler", key=f"cancel_delete_{bkp}"):
                            st.session_state['delete_confirm'] = None
                else:
                    if st.button("Supprimer", key=f"delete_{bkp}"):
                        st.session_state['delete_confirm'] = bkp
    else:
        st.info("Aucune sauvegarde disponible.")
