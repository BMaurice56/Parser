from extract import TextComparer
import pathlib
import sys
import os

if __name__ == "__main__":
    if len(sys.argv) > 2:
        raise ValueError("Erreur nombre argument")

    argv = sys.argv[1]
    if argv != "-t" and argv != "-x":
        raise ValueError("Erreur argument rentré")

    # Chemin du dossier
    path_test = str(pathlib.Path(__file__).parent.resolve())
    path_paser = path_test[:path_test.rfind('/')]

    res_attendu_path = f"{path_test}/solution"
    folder_path = f"{path_paser}/Corpus_2023_FINAL/analyse_pdf/"

    if argv == "-t":
        res_attendu_path += "Txt.txt"

    elif argv == "-x":
        res_attendu_path += "Xml.xml"

    os.system(f"python3 {path_paser}/main.py {argv} {path_paser}/Corpus_2023_FINAL/ --all")

    comparer = TextComparer(res_attendu_path, argv)
    comparer.compare_files(folder_path)
