import re
import os
import Levenshtein
import affichage


class TextComparer:
    """
    -Test si le contenu des txt créé par la Parser.py sont corrects
    """

    def __init__(self, resAttendu_path):
        self.resAttendu_path = resAttendu_path
        with open(self.resAttendu_path, "r") as f:
            self.text = f.read()

    @staticmethod
    def read_text_files_in_directory(directory_path):
        """
        Méthode qui permet d'extraire les textes du dossier analyse.pdf.

        Args :
        - directory_path (str) : Chemin du répertoire contenant les fichiers .txt créer par le parser.

        Returns :
        - dict : Dictionnaire contenant le contenu de chaque fichier texte.
        """
        try:
            # Ouvre un fichier contenu dans analyse_pdf que s'il est au format txt
            text_files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]
            # variable qui va servir de dictionnaire
            text_contents = {}

            for text_file in text_files:
                # Prend un fichier txt qui se trouve dans analyse_pdf
                file_path = os.path.join(directory_path, text_file)

                # Ouvre le txt sélectionné
                with open(file_path, 'r', encoding='utf-8') as file:
                    # Lit le contenu du txt
                    content = file.read()
                    # Ajoute le txt au dictionnaire qui correspond au txt sélectionné
                    text_contents[text_file] = content

            return text_contents
        except Exception as e:
            raise Exception(f"Erreur lors de la lecture des fichiers:{e}")

    def find_and_display_keyword(self, txt_filename, keyword):
        """
        Méthode qui trouve et affiche un extrait de texte contenant un mot-clé dans le fichier
        contenant les résultats attendus.

        Args :
        - txt_filename (str) : Chemin du fichier contenant les résultats attendus.
        - keyword (str) : Mot-clé à rechercher.

        Returns :
        - str : Extraction du résultat attendue correspondant au mot cle entre en paramètre.
        """
        # Text des solutions attendues
        extracted_text = self.text

        # Met les caractères de cle et le text des solutions attendues en minuscule et vérifie si la cle est presente
        # dans le text des solutions attendues
        if keyword.lower() in extracted_text.lower():
            # Indique à combien de caractères se trouve le début du mot clé dans le txt des solutions attendues
            keyword_start = extracted_text.lower().find(keyword.lower())
            # Trouve l'occurrence qui correspond au premier nom de fichier présent dans le txt des solutions attendues
            next_filename_match = re.search(r"Nom du fichier pdf : (.+?)\n", extracted_text)

            if next_filename_match:
                # Indique à combien de caractères se trouve la fin du mot cle dans le txt des solutions attendues
                snippet_end = keyword_start + next_filename_match.end()
            else:
                snippet_end = len(extracted_text)

            # Trouve le prochain nom de fichier, en part du mot clé sélectionné dans le txt des solutions attendues
            next_filename_match = re.search(r"Nom du fichier pdf : (.+?)\n", extracted_text[snippet_end:])

            if next_filename_match:
                # Indique à combien de caractères se trouve le prochain nom de fichier dans le txt des solutions
                # attendues
                snippet_end += next_filename_match.start()
            else:
                snippet_end = len(extracted_text)

            # Prend le max entre 0 et la valeur du début du mot clé
            snippet_start = max(0, keyword_start)

            # Retourne le text qui se trouve entre le mot clé et la prochaine nom de fichier
            return extracted_text[snippet_start:snippet_end]
        else:
            print(f"Le mot clé '{keyword}' n'a pas été trouvé dans {txt_filename}.")

    def compare_files(self, directory_path):
        """
        Méthode qui compare les fichiers du résultat attendu avec celui du résultat obtenu.

        Args :
        - directory_path (str) : Chemin du répertoire contenant les fichiers .txt créer par le parser.

        Returns :
        - None
        """
        try:
            # Ouvre un fichier contenu dans analyse_pdf que s'il est au format txt
            text_files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]

            for text_file in text_files:
                print(f"Analyse du fichier : {text_file}")
                # Prend un fichier txt qui se trouve dans analyse_pdf
                file_path = os.path.join(directory_path, text_file)

                # Ouvre le fichier sélectionné
                with open(file_path, 'r', encoding='utf-8') as file:
                    # Prend le titre du fichier
                    keyword = file.readline().strip()
                    # Contenu du fichier sélectionné
                    content = file.read()

                    # Trouve le texte dans le txt des solutions attendues qui correspond au titre du fichier sélectionné
                    # dans analyse_pdf
                    found_text = self.find_and_display_keyword(self.resAttendu_path, keyword)

                    if found_text is not None:
                        # Appelle de la methode qui retourne un pourcentage qui correspond à la distance de levenshtein
                        percentage = self.levenshtein_distance_percentage(content, found_text)
                        # Affiche le pourcentage
                        affichage.afficher_barre_pourcentage(percentage)
                    else:
                        print(f"Ignorer {text_file} car le mot-clé n'a pas été trouvé.")
                    print()

        except Exception as e:
            raise Exception(f"Erreur lors de la lecture des fichiers : {e}")

    def levenshtein_distance_percentage(self, s1, s2):
        """
        Méthode qui traduit la distance de Levenshtein en pourcentage de ressemblance.

        Args :
        - s1 (str) : Première chaîne de caractères.
        - s2 (str) : Deuxième chaîne de caractères.

        Returns :
        - float : Pourcentage de ressemblance entre les deux chaînes.
        """
        if len(s1) < len(s2):
            return self.levenshtein_distance_percentage(s2, s1)

        # Variable qui prend le maximum entre la taille du texte du fichier analyse_pdf selection et celui du texte des
        # solutions attendues
        max_length = max(len(s1), len(s2))

        if max_length == 0:
            return 100

        # Appelle de la distance de Levenshtein
        distance = Levenshtein.distance(s1, s2)
        # Normalise la distance en la divisant par la taille maximum sélectionnée
        normalized_distance = distance / max_length
        # Change la distance en pourcentage
        percentage = (1 - normalized_distance) * 100

        return percentage
