import os


def replace_in_files():
  print("--- Remplacement Markdown ---")

  target_dir = input(
      "Chemin du dossier (laisser vide pour le dossier courant) : "
  ).strip()
  if not target_dir:
    target_dir = os.getcwd()
  elif not os.path.isdir(target_dir):
    print(f"[ERREUR] Dossier invalide.")
    return

  search_str = "## Document en PDF {-}"
  replace_str = "# Document en PDF {-}"

  print(f"\nRecherche : '{search_str}'")
  print(f"Remplacement : '{replace_str}'\n")

  confirm = (
      input(f"Lancer le remplacement dans '{target_dir}' ? (o/n) : ")
      .strip()
      .lower()
  )
  if confirm not in ["o", "oui", "y", "yes"]:
    print("Opération annulée.")
    return

  modified, skipped, not_found = 0, 0, 0
  script_path = os.path.abspath(__file__)

  for root, dirs, files in os.walk(target_dir):
    for file in files:
      file_path = os.path.join(root, file)
      if os.path.abspath(file_path) == script_path:
        continue

      try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
          content = f.read()

        # On vérifie si la chaîne exacte est là
        if search_str in content:
          if replace_str in content:
            print(
                f"[IGNORÉ] {os.path.relpath(file_path, target_dir)} (le"
                " remplacement y est déjà)"
            )
            skipped += 1
          else:
            new_content = content.replace(search_str, replace_str)
            with open(file_path, "w", encoding="utf-8") as f:
              f.write(new_content)
            print(f"[MODIFIÉ] {os.path.relpath(file_path, target_dir)}")
            modified += 1
        else:
          # Optionnel : décommentez la ligne ci-dessous si vous voulez voir les fichiers qui ne contiennent pas du tout le texte
          # print(f"[NON TROUVÉ] {os.path.relpath(file_path, target_dir)}")
          not_found += 1

      except Exception as e:
        print(f"[ERREUR] {file} : {e}")

  print(
      f"\nBilan : {modified} modifiés | {skipped} ignorés (déjà faits) |"
      f" {not_found} sans correspondance."
  )


if __name__ == "__main__":
  replace_in_files()
