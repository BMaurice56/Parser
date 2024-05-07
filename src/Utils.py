# Fichier contenant des fonctions utiles
import pathlib
import json
import os
import re


class Utils:

    def __init__(self):
        """
        Constructeur
        """
        path = str(pathlib.Path(__file__).parent.resolve())
        path_dir = path[:path.rfind('/')]

        with open(f"{path_dir}/src/letters_accent_uppercase.json", "r") as f:
            self.__dictionnaire_lettre = json.load(f)

        with open(f"{path_dir}/src/letters_accent_lowercase.json", "r") as f:
            self.__dictionnaire_lettre = self.__dictionnaire_lettre | json.load(f)

        with open(f"{path_dir}/src/letters_accent_others.json", "r") as f:
            self.__dictionnaire_lettre = self.__dictionnaire_lettre | json.load(f)

    def replace_accent(self, texte: str) -> None | str:
        """
        Remplace certains éléments du texte passé en argument

        :param texte: string
        :return: str nouveau texte
        """
        if type(texte) is str:
            for key, value in self.__dictionnaire_lettre.items():
                texte = texte.replace(key, value)

            for elt in re.findall(r"\.[A-Z][a-z]", texte):
                texte = texte.replace(elt, f". {elt[1:3]}")

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
