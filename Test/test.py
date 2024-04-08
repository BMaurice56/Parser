from extract import TextComparer
import pathlib
import os

if __name__ == "__main__":
    # Chemin du dossier
    path_test = str(pathlib.Path(__file__).parent.resolve())
    path_paser = path_test[:path_test.rfind('/')]

    res_attendu_path = f"{path_test}/solution2023.xml"
    folder_path = f"{path_paser}/Corpus_2023_FINAL/analyse_pdf/"

    os.system(f"python3.10 {path_paser}/main.py -x {path_paser}/Corpus_2023_FINAL/ --all")

    comparer = TextComparer(res_attendu_path, "-x")
    comparer.compare_files(folder_path)
