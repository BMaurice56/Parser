import sys

from Test import extract
import pathlib
import os

if __name__ == "__main__":
    path_test = str(pathlib.Path(__file__).parent.resolve())
    path_paser = path_test[:path_test.rfind('/')]

    if len(sys.argv) > 2:
        raise ValueError("Erreur nombre argument")

    argv = sys.argv[1]
    if argv != "-t" and argv != "-x":
        raise ValueError("Erreur argument rentré")

    if argv == "-t":

        os.system(f"python3 {path_paser}/main.py -t {path_paser}/Corpus_2022/ --all")

        resAttendu_path = f"{path_test}/solutionTxt.txt"
        folder_path = f"{path_paser}/Corpus_2022/analyse_pdf/"

        comparer = extract.TextComparer(resAttendu_path)
        comparer.compare_files(folder_path)

    if argv == "-x":

        os.system(f"python3 {path_paser}/main.py -x {path_paser}/Corpus_2022/ --all")

        resAttendu_path = f"{path_test}/solutionXml.xml"
        folder_path = f"{path_paser}/Corpus_2022/analyse_pdf/"

        comparer = extract.TextComparer(resAttendu_path)
        comparer.compare_files(folder_path)
