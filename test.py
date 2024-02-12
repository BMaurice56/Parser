import os
import unittest

def isTXT(nomFichier : str) ->bool:
    if not os.path.isfile(nomFichier) or nomFichier[-4:] != ".txt":
        return False
def isTXTFiles(path: str) -> bool:
    """
    Vérifie si il y a que des txt dans le dossier fourni

    :param nom du dossier
    :return: True ou False
    """

    for element in os.listdir(path):
        if not isTXT(path + element):
            return False
    return True


import re

def extract_information(path):
    text = read_text_file(path)
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
    authors_match = re.search(r'Auteurs :\s+(.+)', text)

    if authors_match:
        authors_text = authors_match.group(1)
        print(authors_text)
        authors_list = [author.strip() for author in authors_text.split('\n') if author.strip()]
        result['Auteurs'] = authors_list

    # Extraction de l'abstract
    abstract_match = re.search(r'Abstract :\s+(.+)', text)
    if abstract_match:
        result['Abstract'] = abstract_match.group(1).strip()

    return result

def read_text_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        return f"Une erreur s'est produite lors de la lecture du fichier : {str(e)}"


information = extract_information("/home/arthur/Documents/L3/semestre_4/Parser/Corpus_2022/analyse_pdf/Boudin-Torres-2006.txt")


# Affichage des résultats
for key, value in information.items():
    print(f"{key} :\n    {value}")




class TestDictionaryComparison(unittest.TestCase):

    def test_Boudin(self):
        titre = "A Scalable MMR Approach to Sentence Scoring for Multi-Document Update Summarization"
        Nom = "Boudin-Torres-2006.pdf"

        result = extract_information("/home/arthur/Documents/L3/semestre_4/Parser/Corpus_2022/analyse_pdf/Boudin-Torres-2006.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre :": titre , "Auteurs :": 3,"Abstract :":"We present S MMR , a scalable sentence ..."}
        self.assertEqual(result, dict2)

    def test_dictionaries_not_equal(self):
        dict1 = {'a': 1, 'b': 2, 'c': 3}
        dict2 = {'a': 1, 'b': 2, 'c': 4}
        self.assertNotEqual(dict1, dict2)