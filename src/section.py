from src.content_pdf import Content


class Section:

    def __init__(self, content: Content, pos_title_keywords: dict):
        """
        Constructeur

        :param content: contenue du pdf
        :param pos_title_keywords: position des mots clefs dans le pdf
        """

        self.__texte = content.get_text()
        self.__position_title_keywords = pos_title_keywords

        self.__conclusion = self._get_section("onclusion").strip()
        self.__discussion = self._get_section("iscussion").strip()
        self.__references = self._get_section("eferences").strip()

    @staticmethod
    def get_pos_word_after(mot: str, position_title_keywords: dict) -> int:
        """
        Fonction qui renvoi l'indice dans le text du mot à suivre
        dans le dictionnaire des mots clefs

        :param mot: Mot de base
        :param position_title_keywords: position des mots clefs dans le pdf
        :return: int Position du mot d'après, -1 si aucun mot après
        """
        try:
            # Récupération des clefs + indice du mot suivant
            keys = list(position_title_keywords.keys())
            pos_word_after_plus_one = keys.index(mot) + 1
            ######################################################################

            # Récupération du mot + son indice dans le texte
            word_after = keys[pos_word_after_plus_one]

            return position_title_keywords[word_after]
            ######################################################################

        except IndexError:
            return -1

    def _get_section(self, nom_section: str) -> str:
        """
        Renvoi le texte de la section correspondante

        :param nom_section: section voulu
        :return: string valeur
        """
        pos_mot_section = self.__position_title_keywords[nom_section]

        if pos_mot_section != -1:
            pos_word_after = self.get_pos_word_after(nom_section, self.__position_title_keywords)

            # Récupération du texte
            texte = self.__texte[pos_mot_section + len(nom_section):pos_word_after].strip()

            if nom_section != "eferences":
                # Si présence d'un "and", on le retire
                if texte[:4].lower() == "and " or texte[:6].lower() == "s and ":
                    texte = texte[texte.find("\n"):]
                ######################################################################

                # On retire le "s" de conclusion s'il y en a un
                if texte[0].lower() == "s":
                    texte = texte[1:]

                # On enlève les caractères du titre suivant la discussion
                texte = texte[:texte.rfind("\n")].strip()
                ######################################################################

                # On enlève tout élément inutile à la fin de chaque section
                while texte[-1] != ".":
                    texte = texte[:-1]
                ######################################################################

                pos = texte.find("Table 4\nComparison")

                if pos != -1:
                    texte = f"{texte[:pos - 3]}{texte[pos + 401:]}"

            else:
                pos = texte.find("RF0 RF1 RF2 RF3")
                if pos != -1:
                    texte = f"{texte[:pos]}{texte[pos + 325:]}"

            return texte

        else:
            return "N/A"

    def get_conclusion(self) -> str:
        """
        Renvoi la conclusion

        :return: string valeur
        """

        return self.__conclusion

    def get_discussion(self) -> str:
        """
        Renvoi la discussion

        :return: string valeur
        """

        return self.__discussion

    def get_references(self) -> str:
        """
        Renvoi la bibliographie

        :return: string valeur
        """

        return self.__references
