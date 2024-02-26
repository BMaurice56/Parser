# Fichier contenant des fonctions utiles
import os


class Utils:
    @staticmethod
    def replaceAccent(texte: list | dict | str) -> None | str:
        """
        Remplace tous les accents mal lus dans les noms

        :param texte string à checker
        :return: texte corrigé
        """
        dictionnaire_lettre = {
            "´ e": 'é',
            "` e": 'è',
            "´ a": 'á',
            "` a": 'à',
            "^ e": 'ê',
            "´ i": 'í',
            "` i": 'ì',
            "ˆ i": 'î',
            "~ n": 'ñ',
            "´ o": 'ó',
            "` o": 'ò',
            "^ o": 'ô',
            "´ u": 'ú',
            "` u": 'ù',
            "^ u": 'û',
            "¨ u": 'ü',
            "´ y": 'ý',
            "` y": 'ỳ',
            "^ y": 'ŷ',
            " ´e": 'é',
            " `e": 'è',
            " ´a": 'á',
            " `a": 'à',
            " ˆe": 'ê',
            " ´i": 'í',
            " `i": 'ì',
            " ˆi": 'î',
            " ~n": 'ñ',
            " ´o": 'ó',
            " `o": 'ò',
            " ^o": 'ô',
            " ´u": 'ú',
            " `u": 'ù',
            " ˆu": 'û',
            " ¨u": 'ü',
            " ´y": 'ý',
            " `y": 'ỳ',
            " ˆy": 'ŷ',
            " c ¸": "ç",
            " c¸": "ç",
            "ˆ ı": "î",
            "´e": 'é',
            "`e": 'è',
            "´a": 'á',
            "`a": 'à',
            "^e": 'ê',
            "´i": 'í',
            "`i": 'ì',
            "ˆi": 'î',
            "~n": 'ñ',
            "´o": 'ó',
            "`o": 'ò',
            "^o": 'ô',
            "´u": 'ú',
            "`u": 'ù',
            "^u": 'û',
            "¨u": 'ü',
            "´y": 'ý',
            "`y": 'ỳ',
            "^y": 'ŷ',
            "c ¸": "ç",
            "c¸": "ç",
            " ˆı": "î"
        }
        if type(texte) is list:
            for key, value in dictionnaire_lettre.items():
                for i in range(len(texte)):
                    texte[i] = texte[i].replace(key, value)
            return

        elif type(texte) is str:
            for key, value in dictionnaire_lettre.items():
                texte = texte.replace(key, value)

            return texte

        elif type(texte) is dict:
            for key, value in dictionnaire_lettre.items():
                for i in range(len(texte.keys())):
                    ""

        else:
            raise TypeError("Type non reconnue")

    @staticmethod
    def retrievePreviousOrder(liste: list, dico_ordre: dict) -> None:
        """
        Remet les éléments dans la liste dans l'ordre du dictionnaire

        :param liste: Liste contenant les éléments de base
        :param dico_ordre: Contient l'ordre des éléments
        :return: None
        """
        for x, y in dico_ordre.items():
            liste[x] = y

    @staticmethod
    def isPDFFile(nomFichier: str) -> bool:
        """
        Vérifie si le nom de fichier fourni est bien un pdf

        :param nomFichier: Nom du fichier
        :return: True ou False
        """
        if not os.path.isfile(nomFichier) or nomFichier[-4:] != ".pdf":
            return False

        return True
