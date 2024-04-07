import xml.etree.ElementTree as ETree
from src.content_pdf import Content
from src.authors import Author
from src.Utils import Utils
from src.title import Title
import PyPDF2
import re
import io


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
        self.__pdf_file_obj = io.TextIOWrapper
        self.__directoryTxtFile = ""
        self.__titre = ""
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
        self.__auteurs = []
        self.__dico_nom_mail = {}
        self.__dico_nom_univ = {}
        self.__no_introduction = False

        self.__pathToFile = path
        self.__nomFichier = nom_fichier

        if not Utils.is_pdf_file(path + nom_fichier):
            print(f"Nom du fichier : {nom_fichier}")
            raise FileNotFoundError("Le fichier fourni n'est pas un pdf ou n'a pas été trouvé")

        self.__pdf_file_obj = None
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

        texte = self.content.get_text()
        texte_lower = self.content.get_text_lower()

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
        self.content = Content(self.__pdfReader)
        self.__index_first_page = self.content.get_index_first_page()
        self.__localisation_keywords()
        self.__titre = Title(self.__pdfReader, self.__index_first_page).get_title()
        self._get_abstract()
        auteurs = Author(self.content, self.__titre, self.__abstract, self.__school_words)
        self.__auteurs, self.__dico_nom_mail, self.__dico_nom_univ = auteurs.get_authors()
        self._get_introduction_and_corps()
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

    def _get_abstract(self) -> None:
        """
        Renvoie l'abstract du pdf

        :return: None
        """
        if self.__abstract == "":
            texte = self.content.get_text()
            texte_lower = self.content.get_text_lower()

            # Position des mots clefs
            pos_abstract = max(texte_lower.find("abstract"), texte_lower.find("bstract") - 1)
            pos_introduction = max(texte_lower.find("introduction"), texte_lower.find("ntroduction") - 1)
            pos_keywords = max(texte_lower.find("keyword"), texte_lower.find("eyword") - 1,
                               texte_lower.find("ey-word") - 1)
            pos_index_terms = max(texte_lower.find("index terms"), texte_lower.find("ndex terms") - 1)
            pos_mot_clefs = max(texte_lower.find("mots-cl"), texte_lower.find("mots cl"))
            pos_abbreviation = texte_lower.find("\nabbreviation")
            ######################################################################

            # S'il y a une section mot-clefs dans le début du pdf, on l'enlève
            if 0 < pos_keywords < pos_introduction and pos_keywords > pos_abstract:
                pos_introduction = pos_keywords
            ######################################################################

            # S'il y a une section index terms dans le début du pdf, on l'enlève
            if 0 < pos_index_terms < pos_introduction and pos_index_terms > pos_abstract:
                pos_introduction = pos_index_terms
            ######################################################################

            # S'il y a une section mots clefs dans le débt du pdf, on l'enlève
            if 0 < pos_mot_clefs < pos_introduction and pos_mot_clefs > pos_abstract:
                pos_introduction = pos_mot_clefs
            ######################################################################

            # S'il y a une section abbreviations dans le débt du pdf, on l'enlève
            if 0 < pos_abbreviation < pos_introduction and pos_abbreviation > pos_abstract:
                pos_introduction = pos_abbreviation
            ######################################################################

            # Si trouvé, alors on peut renvoyer l'abstract
            if pos_abstract != -1 and pos_introduction != -1:
                swift = 1
                if texte[pos_abstract + len("Abstract") + swift] in [" ", "\n", "-", "—"]:
                    swift += 1

                self.__abstract = texte[pos_abstract + len("Abstract") + swift:pos_introduction - 2]
            ######################################################################

            # Sinon absence du mot abstract
            elif pos_abstract == -1 and pos_introduction != -1:
                dernier_point = texte[:pos_introduction - 2].rfind(".")

                i = 0

                for i in range(dernier_point, 1, -1):
                    if ord(texte[i]) < 20:
                        if ord(texte[i - 1]) != 45:
                            break

                self.__abstract = texte[i + 1:dernier_point]
            ######################################################################

            # Sinon il n'y a pas d'introduction
            elif pos_abstract != -1 and pos_introduction == -1:
                self.__no_introduction = True

                pos_first_title = max(texte.find("\n1 "), texte.find("\nI."), texte.find("\nI "))

                if pos_first_title != -1:
                    self.__abstract = texte[pos_abstract + len("abstract"):pos_first_title].strip()
            ######################################################################

            # Si présence du 1 de l'introduction, on l'enlève
            pos_i_introduction = self.__abstract.rfind("I.")

            if pos_i_introduction != -1:
                self.__abstract = self.__abstract[:pos_i_introduction - 1]
            ######################################################################

            # Permet d'enlever les espaces et retour à la ligne à la fin pour vérifier la présence du point
            if self.__abstract != "":
                while self.__abstract[-1] in ["\n", " ", "I"]:
                    self.__abstract = self.__abstract[:-1]

                if self.__abstract[-1] != ".":
                    self.__abstract += "."
            else:
                raise ValueError("Abstract non trouvé")
            ######################################################################

    def _get_introduction_and_corps(self) -> None:
        """
        Récupère l'introduction et le corps du texte

        :return: None
        """
        if self.__introduction == "" and self.__corps == "":
            texte_pdf = self.content.get_text()

            # Position de l'abstract
            pos_abstract = texte_pdf.find(self.__abstract)
            ######################################################################

            # Récupération des positions des mots par ordre croisant != -1
            position_title_keywords = {k: v for k, v in
                                       sorted(self.__position_title_keywords.items(), key=lambda item: item[1]) if
                                       v != -1}
            ######################################################################

            # Récupération de l'indice du premier mot clef
            pos_first_keyword = position_title_keywords[list(position_title_keywords.keys())[0]]
            ######################################################################

            # Récupération du texte en entier
            texte = texte_pdf[pos_abstract + len(self.__abstract):pos_first_keyword]
            texte_lower = texte.lower()
            ######################################################################

            # Position du mot introduction
            if not self.__no_introduction:
                pos_introduction = texte_lower.find("ntroduction")
                ######################################################################

                # Ajoute une marge à cause de la présence d'espace dans le titre
                add_margin_cause_space = 0
                ######################################################################

                # Si présence d'un espace entre le I et ntroduction, on l'enlève
                if texte_lower[pos_introduction - 1] == " ":
                    pos_introduction -= 1
                    add_margin_cause_space += 1
                ######################################################################

                # On vérifie s'il y a un point
                add_point = False

                if texte_lower[pos_introduction - 3] == ".":
                    pos_introduction -= 1
                    add_margin_cause_space += 1
                    add_point = True
                ######################################################################

                # On regarde si c'est un chiffre ou en lettre
                if texte_lower[pos_introduction - 3] == "1":
                    type_indices = "2"
                else:
                    type_indices = "II"
                ######################################################################

                # On rajoute le point si nécessaire
                if add_point:
                    type_indices += ". "
                else:
                    type_indices += " "
                ######################################################################

                # On vient rechercher le deuxième titre dans le texte
                pos_second_title_word = 0

                while pos_second_title_word != -1:
                    pos_second_title_word = texte.find(type_indices, pos_second_title_word)

                    if pos_second_title_word != -1:
                        if texte[pos_second_title_word + len(type_indices) + 2].isdigit():
                            pos_second_title_word += 2
                        else:
                            newline_in_texte = "\n" in texte[pos_second_title_word - 2:pos_second_title_word]
                            domaine_name = any(
                                re.findall("[.][a-zA-Z]+", texte[pos_second_title_word - 5: pos_second_title_word]))

                            if newline_in_texte or domaine_name:
                                break
                            else:
                                pos_second_title_word += 2
                ######################################################################

                # Récupération de l'introduction et du corps du texte
                self.__introduction = texte[
                                      pos_introduction + len(
                                          "ntroduction") + add_margin_cause_space: pos_second_title_word]
                ######################################################################

            else:
                pos_second_title_word = -2

                self.__introduction = "N/A"

            self.__corps = texte[pos_second_title_word + 2:]
            self.__corps = self.__corps[self.__corps.find("\n"):]
            self.__corps = self.__corps[:self.__corps.rfind("\n")].strip()
            ######################################################################

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
                self.__conclusion = self.content.get_text()[pos_conclusion + len(onclusion_word):pos_word_after].strip()

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
                self.__discussion = self.content.get_text()[pos_discussion + len(iscussion_word):pos_word_after].strip()
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
                self.__references = f"{self.content.get_text()[pos_references + len('references'):word_after - 1]}"

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
