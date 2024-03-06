import os
import unittest
from extract import *


class TestComparison(unittest.TestCase):

    path_d= "/Corpus_2022/analyse_pdf"
    def test_isTxt(self):
        self.assertEqual(Extract.isTextFiles(self.path_d),True)

    def test_Boudin_Torres(self):
        titre = "A Scalable MMR Approach to Sentence Scoring for Multi-Document Update Summarization"
        Nom = "Boudin-Torres-2006.pdf"
        auteur = ("Juan-Manuel Torres-Moreno : juan-manuel.torres@univ-avignon.fr\n"
                  "Florian Boudin : florian.boudin@univ-avignon.fr\n"
                  "Marc El-Bèze : marc.elbeze@univ-avignon.fr\n") #TODO
        abstract = "We present S MMR , a scalable sentence"

        result = Extract.extract_information(self.path_d+"/Boudin-Torres-2006.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre , "Auteurs": auteur,"Abstract":abstract}

        self.assertEqual(result, dict2)


    def test_Das_Martin(self):
        titre = "Das_Martins.pdf"
        Nom = "A Survey on Automatic Text Summarization"
        auteur = ("Dipanjan Das : fdipanjan@cs.cmu.edu\n"
                  "André F.T. Martins : afmg@cs.cmu.edu") #TODO
        abstract = "The increasing availability of online information has necessitated intensive"
        result = extract_information(self.path_d+"/Das_Martins.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def test_Gonzalez_2018_Wisebe(self):
        titre = "Gonzalez_2018_Wisebe.pdf"
        Nom = "WiSeBE: Window-Based Sentence Boundary Evaluation"
        auteur = ("Carlos-Emiliano González-Gallardo : carlos-emiliano.gonzalez-gallardo@alumni.univ-avignon.fr\n"
                  "Juan-Manuel Torres-Moreno : juan-manuel.torres@univ-avignon.fr") #TODO
        abstract = "Sentence Boundary Detection (SBD) has been a major"
        result = extract_information(self.path_d+"/Gonzalez_2018_Wisebe.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def test_Iria_Juan_Manuel_Gerardo(self):
        titre = "Iria_Juan-Manuel_Gerardo.pdf"
        Nom = "On the Development of the RST Spanish Treebank"
        auteur = ("Iria da Cunha : iria.dacunha@upf.edu\n"
                  "Juan-Manuel Torres-Moreno : juan-manuel.torres@univ-avignon.fr\n"
                  "Gerardo Sierra : gsierram@iingen.unam") #TODO
        abstract = "In this article we present the RST Spanish"
        result = extract_information(self.path_d+"/Iria_Juan-Manuel_Gerardo.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def test_jing_cutepaste(self):
        titre = "jing-cutepaste.pdf"
        Nom = "Cut and Paste Based Text Summarization"
        auteur = ("Hongyan Jing : hjing@cs.columbia.edu\n"
                  "Kathleen R. McKeown : kathy@cs.columbia.edu") #TODO
        abstract = "We present a cut and paste based text summa-"
        result = extract_information(self.path_d+"/jing-cutepaste.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def kessler94715(self):
        titre = "Extraction of terminology in the field of construction" #TODO
        Nom = "kessler94715.pdf" #TODO
        auteur = ("Rémy Kessler : remy.kessler@univ-ubs.fr\n"
                  "Nicolas Béchet : nicolas.bechet@irisa.fr\n"
                  "Giuseppe Berio : giuseppe.berio@univ-ubs.fr\n") #TODO
        abstract = "We describe a corpus analysis method to extract" #TODO
        result = extract_information(self.path_d+"/kessler94715.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def kesslerMETICS_ICDIM2019(self):
        titre = "A word embedding approach to explore a collection of discussions of people in psychological distress" #TODO
        Nom = "kesslerMETICS-ICDIM2019.pdf" #TODO
        auteur = ("Rémy Kessler : remy.kessler@univ-ubs.fr\n"
                  "Nicolas Béchet : nicolas.bechet@irisa.fr\n"
                  "Gudrun Ledegen : gudrun.ledegen@univ-rennes2.fr\n"
                  "Frederic Pugnière-Saavedra : frederic.pugniere-saavedra@univ-ubs.fr\n")  #TODO
        abstract = "In order to better adapt to society, an association" #TODO
        result = extract_information(self.path_d+"/kesslerMETICS-ICDIM2019.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def mikheev_J02_3002(self):
        titre = "Periods, Capitalized Words, etc." #TODO
        Nom = "mikheev J02-3002.pdf" #TODO
        auteur = "Andrei Mikheev : mikheev@cogsci.ed.ac.uk" #TODO
        abstract = "In this article we present an approach for tackling three important aspects of text normaliza-" #TODO
        result = extract_information(self.path_d+"/mikheev J02-3002.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def Mikolov(self):
        titre = "Efficient Estimation of Word Representations in Vector Space" #TODO
        Nom = "Mikolov.pdf" #TODO
        auteur = ("Tomas Mikolov : tmikolov@google.com\n"
                  "Kai Chen : kaichen@google.com\n"
                  "Greg Corrado : gcorrado@google.com\n"
                  "Jeffrey Dean : jeff@google.com") #TODO
        abstract = "We propose two novel model architectures for computing continuous vector repre-" #TODO
        result = extract_information(self.path_d+"/Mikolov.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def Nasr(self):
        titre = "MACAON An NLP Tool Suite for Processing Word Lattices" #TODO
        Nom = "Nasr.pdf" #TODO
        auteur = ("Alexis Nasr : alexis.nasr@lif.univ-mrs.fr\n"
                  "Frédéric Béchet : frederic.bechet@lif.univ-mrs.fr\n"
                  "Jean-François Rey : jean-francois.rey@lif.univ-mrs.fr\n"
                  "Benoît Favre : benoit.favre@lif.univ-mrs.fr\n"
                  "Joseph Le Roux : joseph.le.roux@lif.univ-mrs.fr") #TODO
        abstract = "MACAON is a tool suite for standard NLP tasks" #TODO
        result = extract_information(self.path_d+"/Nasr.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def Torres(self):
        titre = "Summary Evaluation with and without References" #TODO
        Nom = "Torres.pdf" #TODO
        auteur = ("Juan-Manuel Torres-Moreno : juan-manuel.torres@univ-avignon.fr\n"
                  "Horacio Saggion : horacio.saggion@upf.edu\n"
                  "Iria da Cunha : iria.dacunha@upf.edu\n"
                  "Eric SanJuan : eric.sanjuan@univ-avignon.fr\n"
                  "Patricia Velázquez-Morales : velazquez@yahoo.com") #TODO
        abstract = "We study a new content-based method for" #TODO
        result = extract_information(self.path_d+"/Torres.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)

    def Torres_moreno1998(self):
        titre = "Efficient Adaptive Learning for Classification Tasks with Binary Units" #TODO
        Nom = "Torres-moreno1998.pdf" #TODO
        auteur = ("J. Manuel Torres Moreno : Pas d'adresse mail\n"
                  "Mirta B. Gordon : Pas d'adresse mail") #TODO
        abstract = "This article presents a new incremental learning algorithm for classi-" #TODO
        result = extract_information(self.path_d+"/Torres-moreno1998.txt")

        dict2 = {"Nom du fichier pdf": Nom, "Titre": titre, "Auteurs": auteur, "Abstract": abstract}
        self.assertEqual(result, dict2)