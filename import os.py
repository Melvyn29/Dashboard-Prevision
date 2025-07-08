from pathlib import Path
import shutil
import textwrap

# Chemins d’entrée et de sortie
base_path = Path(r"C:\Users\m446003\OneDrive - Air France KLM\Bureau")
source_dir = base_path / "données"
target_root = base_path / "forecast_dashboard"

# Mapping des fichiers vers leurs dossiers cibles
file_mapping = {
    "app.py": target_root,
    "requirements.txt": target_root,
    "mappings.py": target_root / "config",
    "styles.py": target_root / "config",
    "data_utils.py": target_root / "utils",
    "forecast_utils.py": target_root / "utils",
    "plot_utils.py": target_root / "utils",
    "pdf_utils.py": target_root / "utils",
    "dashboard.py": target_root / "components",
    "add_pn.py": target_root / "components",
    "modify_pn.py": target_root / "components",
    "analysis.py": target_root / "components",
    "comparison.py": target_root / "components",
    "report.py": target_root / "components",
}

# Fonction pour reformater le contenu avec une indentation cohérente (optionnel)
def clean_indentation(file_path):
    try:
        content = file_path.read_text(encoding='utf-8')
        cleaned = textwrap.dedent(content).strip()
        return cleaned + "\n"
    except Exception as e:
        print(f"❌ Erreur lors du traitement de {file_path.name} : {e}")
        return None

# Déplacement des fichiers
for file_name, dest_folder in file_mapping.items():
    src_file = source_dir / file_name
    dest_file = dest_folder / file_name

    if src_file.exists():
        dest_folder.mkdir(parents=True, exist_ok=True)
        content = clean_indentation(src_file)
        if content:
            dest_file.write_text(content, encoding='utf-8')
            print(f"✅ {file_name} déplacé et nettoyé → {dest_file}")
    else:
        print(f"⚠️ {file_name} non trouvé dans {source_dir}")
