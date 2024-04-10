from src.content_pdf import Content
from src.abstract import Abstract
import re


class Body:

    def __init__(self, content: Content, abstract: Abstract, position_title_keywords: dict):
        self.__introduction = ""
        self.__corps = ""
        self.__content = content
        self.__abstract = abstract
        self.__position_title_keywords = position_title_keywords

        self._get_introduction_and_corps()

    def _get_introduction_and_corps(self) -> None:
        """
        Récupère l'introduction et le corps du texte

        :return: None
        """
        texte_pdf = self.__content.get_text()

        # Position de l'abstract
        pos_abstract = texte_pdf.find(self.__abstract.get_abstract())
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
        texte = texte_pdf[pos_abstract + len(self.__abstract.get_abstract()):pos_first_keyword]
        texte_lower = texte.lower()
        ######################################################################

        # Position du mot introduction
        if self.__abstract.get_presence_introduction():
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
                        # Soit il y a un \n, soit un lien devant le titre, soit le numéro de la page
                        texte_around = texte[pos_second_title_word - 2:pos_second_title_word]
                        newline_in_texte = "\n" in texte_around
                        domaine_name = any(
                            re.findall("[.][a-zA-Z]+", texte[pos_second_title_word - 5: pos_second_title_word]))
                        number_page = any(
                            re.findall("[.][0-9]+", texte[pos_second_title_word - 5: pos_second_title_word]))
                        ######################################################################

                        # On vérifie que le numéro ne se trouve pas dans une liste d'élément
                        number_in_liste = texte[texte.find("\n", pos_second_title_word) + 1:].startswith("3.")
                        ######################################################################

                        if (newline_in_texte or domaine_name or number_page) and not number_in_liste:
                            break
                        else:
                            pos_second_title_word += 2
            ######################################################################

            # Récupération de l'introduction et du corps du texte
            self.__introduction = texte[
                                  pos_introduction + len(
                                      "ntroduction") + add_margin_cause_space: pos_second_title_word]
            ######################################################################

            # fpwf = first page without foot
            len_fpwf = len(self.__content.get_first_page_without_foot())
            difference_page = self.__content.get_pos_last_character_first_page() - len_fpwf

            if difference_page >= 50:
                pos_character = self.__introduction.find("⇑")

                self.__introduction = (self.__introduction[:pos_character].strip() +
                                       self.__introduction[pos_character + difference_page:].strip())

        else:
            pos_second_title_word = texte.find("\n")

            self.__introduction = "N/A"

        self.__corps = texte[pos_second_title_word + 2:]
        self.__corps = self.__corps[self.__corps.find("\n"):]
        self.__corps = self.__corps[:self.__corps.rfind("\n")].strip()
        ######################################################################

    def get_introduction(self) -> str:
        """
        Renvoi l'introduction du corpus

        :return: string valeur
        """

        return self.__introduction

    def get_corps(self) -> str:
        """
        Renvoi le corps du corpus

        :return: string valeur
        """

        return self.__corps
