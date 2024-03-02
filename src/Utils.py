# Fichier contenant des fonctions utiles
import json
import os


class Utils:
    @staticmethod
    def replace_accent(texte: list | dict | str) -> None | str:
        """
        Remplace tous les accents mal lus dans les noms

        :param: texte string à checker
        :return: texte corrigé
        """
        with open("src/letters_accent.json", "r") as f:
            dictionnaire_lettre = json.load(f)

            if type(texte) is list:
                for key, value in dictionnaire_lettre.items():
                    for i in range(len(texte)):
                        texte[i] = texte[i].replace(key, value)
                return

            elif type(texte) is str:
                for key, value in dictionnaire_lettre.items():
                    texte = texte.replace(key, value)

                return texte

            else:
                raise TypeError("Type non reconnue")

    @staticmethod
    def retrieve_previous_order(liste: list, dico_ordre: dict) -> None:
        """
        Remet les éléments dans la liste dans l'ordre du dictionnaire

        :param liste: Liste contenant les éléments de base
        :param dico_ordre: Contient l'ordre des éléments
        :return: None
        """
        for x, y in dico_ordre.items():
            liste[x] = y

    @staticmethod
    def is_pdf_file(nom_fichier: str) -> bool:
        """
        Vérifie si le nom de fichier fourni est bien un pdf

        :param nom_fichier: Nom du fichier
        :return: True ou False
        """
        if not os.path.isfile(nom_fichier) or nom_fichier[-4:] != ".pdf":
            return False

        return True
