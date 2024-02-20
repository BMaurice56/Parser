import os
import unittest
from extract import *


class TestComparison(unittest.TestCase):

    path_d= "/Corpus_2022/analyse_pdf"
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