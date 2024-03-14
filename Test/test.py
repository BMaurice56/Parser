from Test import extract
import pathlib
import sys
import os

if __name__ == "__main__":
    path = str(pathlib.Path(__file__).parent.resolve())
    path_dir = path[:path.rfind('/')]

    os.system(f"python3 {path_dir}/main.py -t {path_dir}/Corpus_2022/ --all")

    resAttendu_path = f"{path}/solution.txt"
    folder_path = f"{path_dir}/Corpus_2022/analyse_pdf/"

    comparer = extract.TextComparer(resAttendu_path)
    comparer.compare_files(folder_path)
