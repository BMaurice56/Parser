from Test import extract
import sys

if __name__ == "__main__":
    if len(sys.argv) == 3:
        resAttendu_path = sys.argv[1]
        folder_path = sys.argv[2]

        comparer = extract.TextComparer(resAttendu_path)
        comparer.compare_files(folder_path)
    elif len(sys.argv) != 3:
        print(f"Vous n'avez pas rentre le bon nombre d'argument, vous en avez rentre {len(sys.argv)-1} et non 2, voici le modele d'utilisation:")
        print("test.py [/path/to/the/resAttendu.txt, /path/to/the/analyse_pdf/]")


