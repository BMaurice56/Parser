import xml.etree.ElementTree as ETree
from src.content_pdf import Content
from src.abstract import Abstract
from src.section import Section
from src.authors import Author
from src.Utils import Utils
from src.title import Title
from src.body import Body
import PyPDF2


class Parser:
    """
    Classe Parser :
        - Analyse un pdf donner en argument dans le constructeur
        - Ressort une analyse sous forme .txt ou .xml des différentes sections du pdf
    """

    def __init__(self, path: str, nom_fichier: str, directory_txt_file: str = None):
        """
        Constructeur

        :param path: Chemin du fichier ou dossier
        :param nom_fichier: Nom du fichier du pdf
        :param directory_txt_file: Emplacement du dossier de sortie si plusieurs pdfs analysés
        """
        self.__directoryTxtFile = ""
        self.__titre = ""
        self.__auteurs = []
        self.__dico_nom_mail = {}
        self.__dico_nom_univ = {}
        self.__no_introduction = False
        self.__abstract = ""
        self.__introduction = ""
        self.__corps = ""
        self.__acknowledgments = ""
        self.__conclusion = ""
        self.__discussion = ""
        self.__references = ""
        self.__school_words = ["partement", "niversit", "partment", "acult", "laborato", "nstitute", "campus",
                               "academy", "school"]
        self.__title_keywords = {"iscussion": "D",
                                 "onclusion": "C",
                                 "ppendix": "A",
                                 "cknowledgment": "A",
                                 "eferences": "R",
                                 "ollow-up work": "F"}

        self.__position_title_keywords = {}

        self.__pathToFile = path
        self.__nomFichier = nom_fichier

        if not Utils.is_pdf_file(path + nom_fichier):
            print(f"Nom du fichier : {nom_fichier}")
            raise FileNotFoundError("Le fichier fourni n'est pas un pdf ou n'a pas été trouvé")

        self.__pdfReader = self.__open_pdf()

        if directory_txt_file is not None:
            self.__directoryTxtFile = directory_txt_file

    def __open_pdf(self) -> PyPDF2.PdfReader:
        """
        Ouvre le pdf et renvoi l'objet de lecture

        :return: Objet de lecture du pdf
        """
        self.__pdf_file_obj = open(self.__pathToFile + self.__nomFichier, 'rb')

        return PyPDF2.PdfReader(self.__pdf_file_obj)

    def __del__(self) -> None:
        """
        Permet à la terminaison du programme de couper l'ouverture du pdf

        :return: None
        """
        self.__pdf_file_obj.close()

    def __localisation_keywords(self, content: Content) -> None:
        """
        Localise la position des mots clefs

        :return: None
        """
        pos_word = -2

        texte = content.get_text()
        texte_lower = content.get_text_lower()

        for word, first_letter in self.__title_keywords.items():
            while pos_word != -1:
                pos_word = texte_lower[:pos_word].rfind(word)

                if pos_word != -1:
                    # On regarde s'il y a un \n devant ou un . + présence de la lettre en majuscule (titre)
                    content_around_word = texte[pos_word - 8:pos_word]

                    pos_word_in_content_around = content_around_word.find(word)

                    check_title = "\n" in content_around_word or f".{first_letter}" in content_around_word or \
                                  content_around_word[pos_word_in_content_around - 1].isdigit() or (
                                          content_around_word[pos_word_in_content_around - 2].isdigit() and
                                          content_around_word[pos_word_in_content_around - 1].isspace())

                    if check_title and content_around_word.find(first_letter) != -1:
                        self.__position_title_keywords[word] = pos_word
                        pos_word = -2
                        break
                    else:
                        pos_word -= 5
                    ######################################################################
                else:
                    self.__position_title_keywords[word] = -1
                    pos_word = -2
                    break

        # On ne garde que les mots clefs ayant été trouvé
        self.__position_title_keywords = {k: v for k, v in
                                          sorted(self.__position_title_keywords.items(), key=lambda item: item[1])}
        ######################################################################

    def _call_function(self) -> None:
        """
        Appelle toutes les fonctions utiles au Parser

        :return: None
        """
        # !!! ORDRE A CONSERVER
        content = Content(self.__pdfReader)
        self.__index_first_page = content.get_index_first_page()
        self.__localisation_keywords(content)

        # Titre
        titre = Title(self.__pdfReader, self.__index_first_page)
        self.__titre = titre.get_title()
        ######################################################################

        # Abstract
        abstract = Abstract(content)
        self.__abstract = abstract.get_abstract()
        self.__no_introduction = abstract.get_presence_introduction()
        ######################################################################

        # Auteurs
        auteurs = Author(content, titre, abstract, self.__school_words)
        self.__auteurs, self.__dico_nom_mail, self.__dico_nom_univ = auteurs.get_authors()
        ######################################################################

        # Introduction et corps
        body = Body(content, abstract, self.__position_title_keywords)
        self.__introduction = body.get_introduction()
        self.__corps = body.get_corps()
        ######################################################################

        # Sections du pdf
        section = Section(content, self.__position_title_keywords)
        self.__conclusion = section.get_conclusion()
        self.__discussion = section.get_discussion()
        self.__references = section.get_references()

    def pdf_to_file(self, type_output_file: str) -> None:
        """
        Écrit dans un fichier txt l'analyse du pdf

        :return: None
        """
        if type_output_file not in ["-t", "-x"]:
            raise ValueError("Erreur type de fichier sortie")

        if self.__directoryTxtFile == "":
            file = f"{self.__pathToFile}{self.__nomFichier[:-4]}"

        else:
            file = f"{self.__directoryTxtFile}{self.__nomFichier[:-4]}"

        file += ".txt" if type_output_file == "-t" else ".xml"

        with open(file, "w", encoding="utf-8") as f:
            self._call_function()

            if type_output_file == "-t":
                f.write(f"Nom du fichier pdf : {self.__nomFichier}\n\nTitre :\n    {self.__titre}\n\nAuteurs :\n")
                f.writelines([f"    {key} : {value}\n" for key, value in self.__dico_nom_mail.items()])
                f.write(f"\nAbstract :\n    {self.__abstract}\n\nBibliographie : \n    {self.__references}\n")

            elif type_output_file == "-x":
                # Ajout de l'arbre article
                tree = ETree.Element("article")
                ######################################################################

                # Ajout du preamble
                preamble = ETree.SubElement(tree, 'preamble')
                preamble.text = self.__nomFichier

                # Ajout du titre
                titre = ETree.SubElement(tree, 'titre')
                titre.text = self.__titre
                ######################################################################

                # Ajout du tag auteurs
                auteurs = ETree.SubElement(tree, 'auteurs')
                ######################################################################

                # Ajout de chaque auteur avec son nom et mail
                for key, value in self.__dico_nom_mail.items():
                    auteur = ETree.SubElement(auteurs, 'auteur')

                    nom = ETree.SubElement(auteur, 'name')
                    nom.text = key

                    mail = ETree.SubElement(auteur, 'mail')
                    mail.text = value

                    school = ETree.SubElement(auteur, 'affiliation')
                    school.text = self.__dico_nom_univ.get(key, "Pas d'affiliation trouvée")
                ######################################################################

                # Ajout de l'abstract
                abstract = ETree.SubElement(tree, 'abstract')
                abstract.text = self.__abstract
                ######################################################################

                # Ajout de l'introduction
                introduction = ETree.SubElement(tree, 'introduction')
                introduction.text = self.__introduction
                ######################################################################

                # Ajout de l'introduction
                corps = ETree.SubElement(tree, 'body')
                corps.text = self.__corps
                ######################################################################

                # Ajout de la conclusion
                conclusion = ETree.SubElement(tree, 'conclusion')
                conclusion.text = self.__conclusion
                ######################################################################

                # Ajout de la discussion
                discussion = ETree.SubElement(tree, 'discussion')
                discussion.text = self.__discussion
                ######################################################################

                # Ajout de la bibliographie
                abstract = ETree.SubElement(tree, 'biblio')
                abstract.text = self.__references
                ######################################################################

                # Ajout de l'indentation
                ETree.indent(tree)
                ######################################################################

                # Écrire dans le fichier XML
                f.write(ETree.tostring(tree, encoding="utf-8").decode("utf-8"))
                ######################################################################
