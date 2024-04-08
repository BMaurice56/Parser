from src.content_pdf import Content


class Abstract:

    def __init__(self, content: Content):
        self.__content = content
        self.__abstract = ""
        self.__no_introduction = False

        self._get_abstract()

    def _get_abstract(self) -> None:
        """
        Renvoie l'abstract du pdf

        :return: None
        """
        texte = self.__content.get_text()
        texte_lower = self.__content.get_text_lower()

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

    def get_abstract(self) -> str:
        """
        Renvoi l'abstract du pdf

        :return: string valeur
        """

        return self.__abstract

    def get_presence_introduction(self) -> bool:
        """
        Renvoi s'il y a présence d'une introduction sur le pdf
        True → présence d'une introduction
        False → absence

        :return: boolean valeur
        """

        return not self.__no_introduction
