import fitz  # PyMuPDF
import re
import os
import Levenshtein

class TextComparer:
    def __init__(self, resAttendu_path):
        self.resAttendu_path = resAttendu_path

    def read_text_files_in_directory(self, directory_path):
        """
        Méthode qui permet d'extraire les textes du dossier analyse.pdf.

        Args:
        - directory_path (str): Chemin du répertoire contenant les fichiers .txt creer par le parser.

        Returns:
        - dict: Dictionnaire contenant le contenu de chaque fichier texte.
        """
        try:
            text_files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]
            text_contents = {}

            for text_file in text_files:
                file_path = os.path.join(directory_path, text_file)

                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    text_contents[text_file] = content

            return text_contents
        except Exception as e:
            return f"Erreur lors de la lecture des fichiers : {e}"

    def extract_text_from_pdf(self, pdf_filename):
        """
        Méthode qui extrait le texte du fichier où se situe les resultats attendus.

        Args:
        - pdf_filename (str): Chemin du fichier contenant les resultats attendus.

        Returns:
        - str: Texte extrait du fichier contenant les résultats attendus.
        """
        try:
            doc = fitz.open(pdf_filename)
            text = ""

            for page_num in range(doc.page_count):
                page = doc[page_num]
                text += page.get_text()

            return text
        except Exception as e:
            return f"Erreur lors de l'extraction du texte : {e}"

    def find_and_display_keyword(self, pdf_filename, keyword):
        """
        Méthode qui trouve et affiche un extrait de texte contenant un mot-clé dans le fichier contenant les resultats attendus.

        Args:
        - pdf_filename (str): Chemin du fichier contenant les resultats attendus.
        - keyword (str): Mot-clé à rechercher.

        Returns:
        - str: EXtraction du resultat attendus correspondant au mot-cle entre en parametre.
        """
        extracted_text = self.extract_text_from_pdf(pdf_filename)

        if keyword.lower() in extracted_text.lower():
            keyword_start = extracted_text.lower().find(keyword.lower())
            next_filename_match = re.search(r"Nom du fichier pdf : (.+?)\n", extracted_text)

            if next_filename_match:
                snippet_end = keyword_start + next_filename_match.end()
            else:
                snippet_end = len(extracted_text)

            next_filename_match = re.search(r"Nom du fichier pdf : (.+?)\n", extracted_text[snippet_end:])

            if next_filename_match:
                snippet_end += next_filename_match.start()
            else:
                snippet_end = len(extracted_text)

            snippet_start = max(0, keyword_start)

            return extracted_text[snippet_start:snippet_end]
        else:
            print(f"Le mot clé '{keyword}' n'a pas été trouvé dans {pdf_filename}.")

    def compare_files(self, directory_path):
        """
        Méthode qui compare les fichiers du resultat attendu avec celui du resultat obtenu.

        Args:
        - directory_path (str): Chemin du répertoire contenant les fichiers .txt creer par le parser.

        Returns:
        - None
        """
        try:
            text_files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]

            for text_file in text_files:
                print(f"Analyse du fichier : {text_file}")
                file_path = os.path.join(directory_path, text_file)

                with open(file_path, 'r', encoding='utf-8') as file:
                    keyword = file.readline().strip()
                    content = file.read()

                    found_text = self.find_and_display_keyword(self.resAttendu_path, keyword)

                    if found_text is not None:
                        percentage = self.levenshtein_distance_percentage(content, found_text)
                        print(f"Pourcentage de ressemblance avec le resultat attendu: {percentage:.2f}%")
                    else:
                        print(f"Ignorer {text_file} car le mot-clé n'a pas été trouvé.")
                    print()

        except Exception as e:
            print(f"Erreur lors de la lecture des fichiers : {e}")

    def levenshtein_distance_percentage(self, s1, s2):
        """
        Méthode qui traduit la distance de Levenshtein en pourcentage de ressemblance.

        Args:
        - s1 (str): Première chaîne de caractères.
        - s2 (str): Deuxième chaîne de caractères.

        Returns:
        - float: Pourcentage de ressemblance entre les deux chaînes.
        """
        if len(s1) < len(s2):
            return self.levenshtein_distance_percentage(s2, s1)

        max_length = max(len(s1), len(s2))

        if max_length == 0:
            return 100

        distance = Levenshtein.distance(s1, s2)
        normalized_distance = distance / max_length
        percentage = (1 - normalized_distance) * 100

        return percentage
