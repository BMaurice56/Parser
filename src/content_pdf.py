from src.Utils import Utils
from src.mail import Mail
import unicodedata
import PyPDF2


class Content:

    def __init__(self, pdf_reader: PyPDF2.PdfReader):
        self.__pdfReader = pdf_reader
        self.__index_first_page = 0
        self.__pos_last_character_first_page = -1
        self.__first_page_without_foot = ""

        self.__load_text_attribut()

    def __load_text_attribut(self) -> None:
        """
        Charge le contenu du text dans les deux attributs

        :return: None
        """
        premiere_page = self.__pdfReader.pages[self.__index_first_page].extract_text()

        if premiere_page.startswith("This article") and not Mail.find_emails(premiere_page)[0]:
            self.__index_first_page += 1
            premiere_page = self.__pdfReader.pages[self.__index_first_page].extract_text()

        # On remplace les accents de la première page
        premiere_page = Utils.replace_accent(premiere_page)
        ######################################################################

        self.__pos_last_character_first_page = len(premiere_page) - 1

        # Si on a des éléments en bas de la page qui peuvent poser un problème, on les enlève
        pos_element_end_page = premiere_page.rfind("⇑")

        if pos_element_end_page != -1 and any(Mail.find_emails(premiere_page[pos_element_end_page:])[0]):
            self.__first_page_without_foot = premiere_page[:pos_element_end_page]
        else:
            self.__first_page_without_foot = premiere_page
        ######################################################################

        liste_parties = []
        parties_page = {}
        self.__previous_value = 10_000

        def visitor_body(text: str, _cm, tm, _font_dict, _font_size):
            if text not in ["", " "] and text != "\n":
                # Permet de connaitre l'emplacement des éléments dans la hauteur
                # Dès que la valeur est dépassée, c'est qu'on a changé de page
                # print(text, len(text), tm)
                if len(text) < 500:
                    value = float(tm[5])

                    if self.__previous_value > value:
                        liste_parties.append(parties_page.copy())
                        parties_page.clear()
                        self.__previous_value = 10_000
                    else:
                        self.__previous_value = value

                    parties_page[text + "\n"] = value

                ######################################################################

        for i in range(self.__index_first_page + 1, len(self.__pdfReader.pages)):
            self.__pdfReader.pages[i].extract_text(visitor_text=visitor_body)
            liste_parties.append(parties_page.copy())
            parties_page.clear()

        # Tri des dictionnaires par leurs valeurs (coordonnées du texte dans la page)
        liste_parties_copy = []
        for elt in liste_parties:
            liste_parties_copy.append(
                {k: v for k, v in sorted(elt.items(), key=lambda item: item[1], reverse=True)})
        ######################################################################

        texte_new_order = ""

        for elt in liste_parties_copy:
            texte_new_order += "".join(elt.keys())

        self.__text = premiere_page + Utils.replace_accent(texte_new_order)

        # Filtre les caractères pour ne conserver que les caractères ASCII
        chaine_normalisee = unicodedata.normalize('NFD', self.__text.lower())

        self.__text_lower = ''.join(c for c in chaine_normalisee if unicodedata.category(c) != 'Mn')
        ######################################################################

        # Remplace le mot clef pour mieux le retrouver
        self.__text_lower = self.__text_lower.replace("cknowledgement", "cknowledgment ")
        ######################################################################

    def get_text(self) -> str:
        """
        Renvoi le texte du pdf

        :return: string content
        """
        return self.__text

    def get_text_lower(self) -> str:
        """
        Renvoi le contenu du pdf en minuscule sans accent

        :return: string content
        """
        return self.__text_lower

    def get_pos_last_character_first_page(self) -> int:
        """
        Renvoi la position du dernier caractère de la première page

        :return: int valeur
        """
        return self.__pos_last_character_first_page

    def get_index_first_page(self) -> int:
        """
        Renvoi l'indice de la première page

        :return: int valeur
        """
        return self.__index_first_page

    def get_first_page_without_foot(self) -> str:
        """
        Renvoi la première page sans le pied

        :return: string valeur
        """
        return self.__first_page_without_foot
