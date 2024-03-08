from multiprocessing import Process
from time import perf_counter
from src.Parser import Parser
from src.menu import menu_pdf
from src.Utils import Utils
import traceback
import shutil
import sys
import os
import io


def my_process(parser_object: Parser, argument: str, name_file: str):
    try:
        parser_object.pdf_to_file(argument)
        print(f"Analyse effectué sur : {name_file}")

    except Exception:
        print(f"Impossible d'analyser le pdf : {name_file}")
        print("Les causes possibles sont un mauvais encoder utilisé pour créer le pdf.\n")


if __name__ == '__main__':
    try:
        if len(sys.argv) > 4:
            raise ValueError("Erreur nombre argument")

        argv = sys.argv[1]
        pathToFile = sys.argv[2]
        choix = ""
        if len(sys.argv) == 4:
            choix = sys.argv[3]

        if argv != "-t" and argv != "-x":
            raise ValueError("Erreur argument rentré")

        if not os.path.exists(pathToFile):
            raise FileNotFoundError("Le fichier ou dossier fourni n'existe pas.")

        if choix != "--all" and choix != "":
            raise ValueError("Erreur argument numéro 3 ne peut avoir que --all")

        # Check si dossier ou fichier
        if os.path.isdir(pathToFile):
            # Check si / à la fin
            if pathToFile[-1] != "/":
                pathToFile += "/"

            # Chemin du dossier de sortie
            nomDossier = pathToFile + "analyse_pdf/"

            # Si existence du dossier → on le supprime
            if os.path.exists(nomDossier):
                try:
                    os.rmdir(nomDossier)

                except OSError:
                    try:
                        shutil.rmtree(nomDossier)

                    except Exception:
                        message = (
                            "\nImpossible de supprimer le dossier analyse_pdf\nCe dossier est nécessaire pour la "
                            "bonne exécution du programme")

                        raise Exception(message)

            # Création du dossier
            os.makedirs(nomDossier)

            liste_process = []

            element_in_dir = os.listdir(pathToFile)

            if not element_in_dir:
                raise Exception("Le dossier fourni est vide.")

            # Sauvegarde de la sortie standard et création d'une nouvelle
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            """
            Le basculement vers une autre sortie était nécessaire car 
            à chaque pdf sélectionné, le menu était reaffiché
            """

            # si choix all, on va chercher itéré sur tous les pdf
            if choix == "--all":
                pdfs = [file for file in element_in_dir if Utils.is_pdf_file(pathToFile + file)]
            else:  # sinon on affiche le menu
                pdfs = menu_pdf(element_in_dir)

                os.system("clear")

            # Puis, on rebascule sur celle d'origine
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout

            if pdfs:
                t1 = perf_counter()

                for element in pdfs:
                    liste_process.append(
                        Process(target=my_process, args=(Parser(pathToFile, element, nomDossier), argv, element)))

                for element in liste_process:
                    element.start()

                for elt in liste_process:
                    elt.join()

                t2 = perf_counter()

                print(f"\nTemps d'exécution : {round(t2 - t1, 2)} secondes")

        else:
            t1 = perf_counter()

            last_slash = pathToFile.rfind("/")

            chemin_fichier = pathToFile[:last_slash + 1]
            nom_fichier = pathToFile[last_slash + 1:]

            parser = Parser(chemin_fichier, nom_fichier)

            parser.pdf_to_file(argv)

            print(f"Analyse effectué sur : {nom_fichier}")

            t2 = perf_counter()

            print(f"\nTemps d'exécution : {round(t2 - t1, 2)} secondes")

    except Exception as e:
        print(traceback.format_exc())

        if type(e) is ValueError:
            print("Impossible d'analyser ce pdf.")
            print("Les causes possibles sont un mauvais encoder utilisé pour créer le pdf.\n")

        print("main.py -outputfile [/path/to/the/file.pdf, /path/to/the/dir/]")
        print("outputfile : -t text")
        print("             -x xml")
