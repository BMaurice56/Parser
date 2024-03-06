import os
import re

class Extract :
    def read_text_file(file_path):
        """
            Lit le contenu d'un fichier texte.

            Paramètre :
            - file_path (str) : Le chemin d'accès au fichier texte.

            Retourne :
            - str : Le contenu du fichier texte, ou un message d'erreur si une exception se produit.
        """
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return content
        except Exception as e:
            return f"Une erreur s'est produite lors de la lecture du fichier : {str(e)}"

    def getList(path: str):
        """
            Obtient une liste de fichiers et répertoires dans le chemin spécifié.

            Paramètre :
            - path (str) : Le chemin du répertoire.

            Retourne :
            - list : Une liste de fichiers et répertoires dans le chemin spécifié.
        """
        return os.listdir(path)


    def extract_information(path):
        """
            Extrait des informations d'un fichier texte, incluant le nom du fichier PDF, le titre, les auteurs et l'abstract.

            Paramètre :
            - path (str) : Le chemin du fichier texte.

            Retourne :
            - dict : Un dictionnaire contenant les informations extraites.
        """
        text = Extract.read_text_file(path)

        result = {}

        # Extraction du nom du fichier pdf
        file_match = re.search(r'Nom du fichier pdf : (.+)', text)
        if file_match:
            result['Nom du fichier pdf'] = file_match.group(1).strip()

        # Extraction du titre
        title_match = re.search(r'Titre :\s+(.+)', text)
        if title_match:
            result['Titre'] = title_match.group(1).strip()

        # Extraction des auteurs
        i_t = text.find("Auteurs :") + 10

        if i_t >= 0:
            auteurs_t = ""
            while i_t < len(text) - 1 and text[i_t:i_t + 2] != '\n\n':
                auteurs_t += text[i_t]
                i_t += 1

            words = auteurs_t.split('\n')
            filtered_words = [word.strip() for word in words if word.strip() != '']
            auteurs = ' '.join(filtered_words)
            result['Auteurs'] = auteurs




        # Extraction de l'abstract
        abstract_match = re.search(r'Abstract :\s+(.+)', text)
        if abstract_match:
            result['Abstract'] = abstract_match.group(1).strip()

        return result

    def isTextFiles(folder_path: str) -> bool:
        """
            Vérifie si le dossier contient des fichiers texte ('.txt').

            Paramètre :
            - folder_path (str) : Chemin du dossier à vérifier.

            Retourne :
            - Bool : 'True' si des fichiers texte sont présents, 'False' sinon.
        """
        # Vérifie si le chemin correspond à un dossier existant
        if not os.path.isdir(folder_path):
            raise ValueError("Le chemin spécifié n'est pas un dossier valide.")

        # Liste les fichiers dans le dossier
        files = os.listdir(folder_path)

        # Vérifie si au moins un fichier a l'extension .txt
        for file in files:
            if file.endswith(".txt"):
                return True

        return False

    def calculate_precision(file_path, extracted_info, expected_info) -> float:
        """
            Calcule la précision de l'analyse et l'extraction des données.

            Paramètres :
            - file_path (str) : Le chemin du fichier analysé.
            - extracted_info (dict) : Les informations extraites.
            - expected_info (dict) : Les informations attendues.

            Retourne :
            - float : La précision
        """
        analyse_correcte = 0
        analyse_incorrecte = 0

        for k in expected_info:
            if (k in extracted_info[k]) and (extracted_info[k] == expected_info[k]):
                analyse_correcte += 1
            else:
                analyse_incorrecte += 1

        if analyse_correcte + analyse_incorrecte == 0:
            return 0

        return analyse_correcte / (analyse_correcte + analyse_incorrecte)

