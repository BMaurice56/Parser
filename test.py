import os
import unittest
import re

def isTXT(nomFichier : str) ->bool:
    if not os.path.isfile(nomFichier) or nomFichier[-4:] != ".txt":
        return False
def isTXTFiles(path: str) -> bool:
    """
    Vérifie si il y a que des txt dans le dossier fourni

    :param path du dossier
    :return: True ou False
    """

    for element in os.listdir(path):
        if isTXT(path + element):
            return False
    return True

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

def read_text_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        return f"Une erreur s'est produite lors de la lecture du fichier : {str(e)}"


class TestComparison(unittest.TestCase):

    path_d="/home/arthur/Documents/L3/semestre_4/Parser/Corpus_2022/analyse_pdf"
    def test_isTxt(self):
        self.assertEqual(isTXTFiles(self.path_d),True)

    def test_Boudin(self):
        titre = "A Scalable MMR Approach to Sentence Scoring for Multi-Document Update Summarization"
        Nom = "Boudin-Torres-2006.pdf"
        auteur = "" #TO DO
        abstract = "We present S MMR , a scalable sentence ..."

        result = extract_information(self.path_d+"/Boudin-Torres-2006.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre , "Auteurs": auteur,"Abstract":abstract}

        self.assertEqual(result, dict2)


    def test_Das_Martin(self):
        titre = "Das_Martins.pdf"
        Nom = "A Survey on Automatic Text Summarization"
        auteur = ""
        abstract = "The increasing availability of online information ..."
        result = extract_information(self.path_d+"/Das_Martins.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def test_Gonzalez_2018_Wisebe(self):
        titre = "Gonzalez_2018_Wisebe.pdf"
        Nom = "WiSeBE: Window-Based Sentence Boundary Evaluation"
        auteur = ""
        abstract = "Sentence Boundary Detection (SBD) has been a ..."
        result = extract_information(self.path_d+"/Gonzalez_2018_Wisebe.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def test_Iria_Juan_Manuel_Gerardo(self):
        titre = "Iria_Juan-Manuel_Gerardo.pdf"
        Nom = "On the Development of the RST Spanish Treebank"
        auteur = ""
        abstract = "In this article we present the RST Spanish  ..."
        result = extract_information(self.path_d+"/Iria_Juan-Manuel_Gerardo.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def test_jing_cutepaste(self):
        titre = "jing-cutepaste.pdf"
        Nom = "Cut and Paste Based Text Summarization"
        auteur = ""
        abstract = "We present a cut and paste based text summa-  ..."
        result = extract_information(self.path_d+"/jing-cutepaste.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def kessler94715(self):
        titre = ""
        Nom = ""
        auteur = ""
        abstract = ""
        result = extract_information(self.path_d+"/kessler94715.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def kesslerMETICS_ICDIM2019(self):
        titre = ""
        Nom = ""
        auteur = ""
        abstract = ""
        result = extract_information(self.path_d+"/kesslerMETICS-ICDIM2019.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def mikheev_J02_3002(self):
        titre = ""
        Nom = ""
        auteur = ""
        abstract = ""
        result = extract_information(self.path_d+"/mikheev J02-3002.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def Mikolov(self):
        titre = ""
        Nom = ""
        auteur = ""
        abstract = ""
        result = extract_information(self.path_d+"/Mikolov.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def Nasr(self):
        titre = ""
        Nom = ""
        auteur = ""
        abstract = ""
        result = extract_information(self.path_d+"/Nasr.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def Torres(self):
        titre = ""
        Nom = ""
        auteur = ""
        abstract = ""
        result = extract_information(self.path_d+"/Torres.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def Torres_moreno1998(self):
        titre = ""
        Nom = ""
        auteur = ""
        abstract = ""
        result = extract_information(self.path_d+"/Torres-moreno1998.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)