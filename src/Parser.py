import xml.etree.ElementTree as ETree
from src.content_pdf import Content
from src.abstract import Abstract
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

    def __localisation_keywords(self) -> None:
        """
        Localise la position des mots clefs

        :return: None
        """
        pos_word = -2

        texte = self.__content.get_text()
        texte_lower = self.__content.get_text_lower()

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
        self.__localisation_keywords()

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

        self._get_discussion()
        self._get_conclusion()
        self._get_references()

    def __get_pos_word_after(self, mot: str) -> int:
        """
        Fonction qui renvoi l'indice dans le text du mot à suivre
        dans le dictionnaire des mots clefs

        :param mot: Mot de base
        :return: int Position du mot d'après, -1 si aucun mot après
        """
        try:
            # Récupération des clefs + indice du mot suivant
            keys = list(self.__position_title_keywords.keys())
            pos_word_after_plus_one = keys.index(mot) + 1
            ######################################################################

            # Récupération du mot + son indice dans le texte
            word_after = keys[pos_word_after_plus_one]

            return self.__position_title_keywords[word_after]
            ######################################################################

        except IndexError:
            return -1

    def _get_conclusion(self) -> None:
        """
        Récupère la conclusion

        :return: None
        """
        if self.__conclusion == "":
            onclusion_word = "onclusion"

            pos_conclusion = self.__position_title_keywords[onclusion_word]

            if pos_conclusion != -1:
                pos_word_after = self.__get_pos_word_after(onclusion_word)

                # Récupération du texte
                self.__conclusion = self.__content.get_text()[
                                    pos_conclusion + len(onclusion_word):pos_word_after].strip()

                # Si présence d'un "and", on le retire
                if self.__conclusion[:4].lower() == "and " or self.__conclusion[:6].lower() == "s and ":
                    self.__conclusion = self.__conclusion[self.__conclusion.find("\n"):]
                ######################################################################

                # On retire le "s" de conclusion s'il y en a un
                if self.__conclusion[0].lower() == "s":
                    self.__conclusion = self.__conclusion[1:]

                # On enlève les caractères du titre suivant la discussion
                self.__conclusion = self.__conclusion[:self.__conclusion.rfind("\n")].strip()
                ######################################################################

            else:
                self.__conclusion = "N/A"

    def _get_discussion(self) -> None:
        """
        Récupère la discussion dans le texte

        :return: None
        """
        if self.__discussion == "":
            iscussion_word = "iscussion"

            pos_discussion = self.__position_title_keywords[iscussion_word]

            if pos_discussion != -1:
                # Récupération de l'indice du mot après dans le texte
                pos_word_after = self.__get_pos_word_after(iscussion_word)
                ######################################################################

                # Récupération du texte
                self.__discussion = self.__content.get_text()[
                                    pos_discussion + len(iscussion_word):pos_word_after].strip()
                ######################################################################

                # Si présence d'un "and", on le retire
                if self.__discussion[:4] == "and ":
                    self.__discussion = self.__discussion[self.__discussion.find("\n"):]
                ######################################################################

                # On enlève les caractères du titre suivant la discussion
                self.__discussion = self.__discussion[:self.__discussion.rfind("\n")].strip()
                ######################################################################

            else:
                self.__discussion = "N/A"

    def _get_references(self) -> None:
        """
        Renvoie la bibliographie de l'article

        :return: None
        """
        if self.__references == "":
            pos_references = self.__position_title_keywords["eferences"]

            # On vérifie s'il y a des éléments après
            word_after = self.__get_pos_word_after("eferences")
            ######################################################################

            if pos_references != -1:
                self.__references = f"{self.__content.get_text()[pos_references + len('references'):word_after - 1]}"

            else:
                self.__references = "N/A"

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
