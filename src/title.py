from src.Utils import Utils
import PyPDF2


class Title:

    def __init__(self, pdf_reader: PyPDF2.PdfReader, index_first_page: int):
        self.__pdfReader = pdf_reader
        self.__titre = ""
        self.__index_first_page = index_first_page

        self._get_title()
        self.__titre = Utils.replace_accent(self.__titre.strip())

    def _get_title(self, minimum_y: int = 640, maximum_y: int = 770) -> None:
        """
        Renvoie le titre du pdf

        :param minimum_y position minimal en y
        :param maximum_y position maximal en y
        :return: None
        """
        page = self.__pdfReader.pages[self.__index_first_page]

        parties = []
        parties_tries = []

        def visitor_body(text, _cm, tm, _font_dict, _font_size):
            if text not in ["", " "] and text != "\n":
                y = tm[5]
                if minimum_y < y < maximum_y:
                    parties.append(text)

        # Extraction des premières lignes
        page.extract_text(visitor_text=visitor_body)

        word_to_avoid = ["letter", "communicated by", "article", "published"]

        for elt in parties:
            value = elt.lower().strip()
            if not any([value.find(x) != -1 for x in word_to_avoid]) and len(value) > 4:
                parties_tries.append(elt)
        ######################################################################

        taille_parties = len(parties_tries)

        if taille_parties == 1:
            # Si on n'a pas récupéré la deuxième ligne du titre, on augmente la fenêtre
            if parties_tries[0][-1] == "\n":
                self.__titre = ""
                self._get_title(minimum_y - 10, maximum_y)
            else:
                self.__titre += parties_tries[0]

            return
            ######################################################################

        # Soit le titre est en deux parties
        elif taille_parties == 2:
            for elt in parties_tries:
                self.__titre += elt

                if elt[-1] != "\n":
                    break

            return
        ######################################################################

        # Soit, on commence à itérer sur le texte et à ce moment-là, on ne garde que les premières lignes
        elif len(parties_tries) > 10:
            self.__titre += parties_tries[0]

            if parties_tries[0][-1] == "\n" and (not parties_tries[1][0].isupper() or len(parties_tries[1]) >= 15):
                self.__titre += parties_tries[1]

                # Si titre sur trois lignes, on récupère le bout manquant
                if parties_tries[1][-1] == "\n" and len(parties_tries[2].split(" ")) <= 1:
                    self.__titre += parties_tries[2]
                ######################################################################

            return
        ######################################################################

        # Soit, on n'a rien trouvé, ou on se trouve à moins de 10 éléments
        else:
            self.__titre = ""
            self._get_title(minimum_y - 10, maximum_y)
        ######################################################################

    def get_title(self) -> str:
        """
        Renvoi le titre du pdf

        :return: string valeur
        """
        return self.__titre

    def __len__(self) -> int:
        """
        Renvoi la longueur du titre

        :return: int valeur
        """
        return len(self.__titre)
