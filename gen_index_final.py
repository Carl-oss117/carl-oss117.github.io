import os
import html
import ctypes

ROOT_PATH = r"D:\\"
OUTPUT_FILE = "index.html"

# Dossiers système à ignorer
IGNORED_DIRS = {
    "$Recycle.Bin",
    "System Volume Information",
    "Recovery",
    "found.000",
    "Config.Msi"
}

# Icônes par type de fichier
FILE_ICONS = {
    "pdf": "📄",
    "jpg": "🖼️", "jpeg": "🖼️", "png": "🖼️", "gif": "🖼️", "webp": "🖼️",
    "mp4": "🎬", "mkv": "🎬", "avi": "🎬", "mov": "🎬",
    "mp3": "🎵", "wav": "🎵", "flac": "🎵",
    "zip": "📦", "rar": "📦", "7z": "📦",
    "txt": "📃", "doc": "📃", "docx": "📃", "odt": "📃",
}

def get_icon(filename):
    ext = filename.lower().split(".")[-1]
    return FILE_ICONS.get(ext, "📄")

# Vérifie si un fichier/dossier est caché ou système (Windows)
def is_hidden_or_system(path):
    try:
        attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
        if attrs == -1:
            return True
        return bool(attrs & 0x2 or attrs & 0x4)
    except:
        return True

# Formate la taille en unités lisibles
def format_size(bytes_size):
    for unit in ["o", "Ko", "Mo", "Go", "To"]:
        if bytes_size < 1024:
            return f"{bytes_size:.0f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.0f} To"

def build_tree(path):
    tree = {}
    for root, dirs, files in os.walk(path, topdown=True, onerror=None):

        # Filtrer les dossiers système et cachés
        dirs[:] = [
            d for d in dirs
            if d not in IGNORED_DIRS
            and not is_hidden_or_system(os.path.join(root, d))
        ]

        rel_root = os.path.relpath(root, path)
        parts = [] if rel_root == "." else rel_root.split(os.sep)

        node = tree
        for part in parts:
            node = node.setdefault(part, {"_files": []})

        clean_files = []
        for f in files:
            full_path = os.path.join(root, f)
            if not is_hidden_or_system(full_path) and not f.startswith("."):
                try:
                    size = os.path.getsize(full_path)
                    clean_files.append((f, size))
                except:
                    pass

        node.setdefault("_files", []).extend(clean_files)

    return tree

def render_tree(tree, indent=2):
    html_lines = []
    space = " " * indent

    for name, content in sorted(tree.items()):
        if name == "_files":
            for f, size in sorted(content):
                size_str = format_size(size)
                icon = get_icon(f)
                html_lines.append(
                    f"{space}<div class='file'>{icon} {html.escape(f)} "
                    f"<span class='size'>({size_str})</span></div>"
                )
        else:
            html_lines.append(f"{space}<details>")
            html_lines.append(f"{space}  <summary>📁 {html.escape(name)}</summary>")
            html_lines.extend(render_tree(content, indent + 4))
            html_lines.append(f"{space}</details>")

    return html_lines

def main():
    tree = build_tree(ROOT_PATH)

    html_head = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Fichiers du disque</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {
  font-family: system-ui, sans-serif;
  margin: 0;
  padding: 10px;
  background: #ffffff;
  color: #222;
}
h1 {
  font-size: 1.2rem;
  text-align: center;
  margin-bottom: 10px;
}
summary {
  font-weight: 600;
  cursor: pointer;
  padding: 4px 0;
}
.file {
  margin-left: 20px;
  font-size: 0.9rem;
  color: #444;
}
.size {
  color: #888;
  font-size: 0.8rem;
}
details {
  margin-left: 10px;
  margin-bottom: 4px;
}

/* Thème sombre automatique */
@media (prefers-color-scheme: dark) {
  body {
    background: #121212;
    color: #e5e5e5;
  }
  summary {
    color: #f0f0f0;
  }
  .file {
    color: #ddd;
  }
  .size {
    color: #aaa;
  }
  details {
    border-left: 1px solid #333;
    padding-left: 6px;
  }
}
</style>
</head>
<body>
<h1>📁 Contenu du disque</h1>
"""

    html_footer = """
</body>
</html>
"""

    lines = [html_head]
    lines.extend(render_tree(tree, indent=0))
    lines.append(html_footer)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✔ Fichier HTML final généré : {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
