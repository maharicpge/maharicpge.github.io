#!/usr/bin/env python3
"""
Transforme dans tous les .qmd :

Variantes d'entrée acceptées :
    [Titre](PDF/xxx.pdf)
    📝 [Titre](PDF/xxx.pdf)
    📝 [**Titre**](PDF/xxx.pdf)
    (et optionnellement un bloc TD existant juste après)

Sortie normalisée :
    📝 [**Titre**](PDF/xxx.pdf)

    # Voir TD {-}
    ✍️ [**TD NN : ...**](../td/xxx.qmd)
"""

import os
import re
import sys
import shutil
from pathlib import Path

# Ligne PDF : 📝 optionnel, [ ou [**, titre, **] ou ], (PDF/<stem>.pdf)
# On capture aussi un éventuel bloc TD existant juste après pour le remplacer.
PATTERN = re.compile(
    r"^(?:📝\s*)?\[\s*(?:\*\*)?(?P<titre>[^\]]+?)(?:\*\*)?\s*\]"
    r"\(PDF/(?P<stem>[^)]+)\.pdf\)[ \t]*"
    r"(?:\s*\n\s*\n?)?"
    r"(?:#\s*Voir TD\s*\{-\}\s*\n\s*✍️\s*\[\s*\*\*[^\]]+\*\*\s*\]\([^)]+\))?",
    re.MULTILINE,
)


def find_project_root(start: Path, td_dirname: str = "td") -> Path:
    for parent in [start] + list(start.parents):
        if (parent / td_dirname).is_dir():
            return parent
    return Path.cwd()


def build_td_link(current_file: Path, root: Path, stem: str) -> str:
    td_target = root / "td" / f"{stem}.qmd"
    rel = os.path.relpath(td_target, current_file.parent)
    return rel.replace(os.sep, "/")


def transform_content(content: str, current_file: Path, root: Path) -> str:
    def repl(m: re.Match) -> str:
        titre = m.group("titre").strip()
        # Retire d'éventuels ** résiduels en fin de titre
        titre = titre.strip("*").strip()
        stem = m.group("stem").strip()

        pdf_path = f"PDF/{stem}.pdf"
        td_path = build_td_link(current_file, root, stem)

        chap_match = re.search(r"chap[_\-]?(\d+)", stem, re.IGNORECASE)
        if chap_match:
            num = chap_match.group(1)
            td_titre = re.sub(r"^Chapitre\s+\d+\s*", f"TD {num} ", titre)
            td_titre = re.sub(r"\s+", " ", td_titre).strip()
        else:
            td_titre = titre

        return (
            f"📝 [**{titre}**]({pdf_path})\n"
            f"\n"
            f"# Voir TD {{-}}\n"
            f"✍️ [**{td_titre}**]({td_path})"
        )

    return PATTERN.sub(repl, content)


def transform_file(path: Path, root: Path, backup: bool = True) -> bool:
    content = path.read_text(encoding="utf-8")
    new_content = transform_content(content, path, root)
    if new_content == content:
        return False
    if backup:
        shutil.copy2(path, str(path) + ".bak")
    path.write_text(new_content, encoding="utf-8")
    return True


def main() -> None:
    root = find_project_root(Path.cwd())
    print(f"Dossier racine détecté (contient td/) : {root}")

    qmds = sorted(p for p in root.rglob("*.qmd") if p.is_file())
    if not qmds:
        print("Aucun fichier .qmd trouvé.")
        return

    changed = 0
    for q in qmds:
        try:
            if transform_file(q, root):
                print(f"✓ Modifié : {q.relative_to(root)}")
                changed += 1
            else:
                print(f"— Inchangé : {q.relative_to(root)}")
        except Exception as e:
            print(f"✗ Erreur sur {q} : {e}")

    print(f"\n{changed} fichier(s) modifié(s) sur {len(qmds)}.")


if __name__ == "__main__":
    main()
