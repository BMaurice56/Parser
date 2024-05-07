from src.content_pdf import Content
from functools import wraps
from src.title import Title
from src.mail import Mail
from src.abstract import Abstract
import Levenshtein
import re


class Author:

    def __init__(self, content: Content, titre: Title, abstract: Abstract, school_word: list):
        self.__text = content.get_text()
        self.__pos_last_character_first_page = content.get_pos_last_character_first_page()
        self.__titre = titre
        self.__abstract = abstract
        self.__school_words = school_word
        self.__auteurs = []
        self.__auteurs_with_numbers_or_symbol = []
        self.__auteurs_order = []
        self.__regex_symbol_auteurs = "[^A-Za-zÀ-ÖØ-öø-ÿ 0-9-;.,/]*"
        self.__emails = []
        self.__dico_nom_mail = {}
        self.__dico_nom_univ = {}
        self.__auteurs_deux_lignes = False
        self.__type_mail = -1
        self.__type_pdf = -1
        """
        Différent type de pdf : 
        -1 : non trouvé
        0 : nom - université - mail pour chaque auteur
        1 : nom sur une seul ligne - université - mail entre parenthèse ou accolade
        2 : (nom - université) et mail autre part
        3 : (nom - université) et PAS de mail

        Le type des mails aident aussi à connaitre le type de pdf
        -1 : non trouvé
        0 : normal (nom et mail)
        1 : entre parenthèse ou accolade
        2 : normal mais dans la page et non au niveau des auteurs
        """

        self._get_author()
        self._get_affiliation()

    def _get_affiliation(self) -> None:
        """
        Récupère les universités des différents auteurs

        :return: None
        """
        pos_titre = self.__text.find(self.__titre.get_title())
        pos_abstract = self.__text.find(self.__abstract.get_abstract()[1:10])
        pos_resume = max(self.__text.find("ésumé") - 1, self.__text.find("esume") - 1)

        if 0 < pos_resume < pos_abstract:
            pos_abstract = pos_resume
        ######################################################################

        # On garde que la section correspondant aux auteurs
        section_auteurs = self.__text[pos_titre + len(self.__titre): pos_abstract].strip()
        ######################################################################

        # Enlèvement des mots clefs
        if "bstract" in section_auteurs:
            section_auteurs = section_auteurs[:section_auteurs.find("bstract") - 1].strip()
        ######################################################################

        # Si présence d'un résumé avant l'abstract, on l'enlève
        if pos_resume != -1:
            word = "ésumé"

            if word not in section_auteurs:
                word = "esume"

            section_auteurs = section_auteurs[:section_auteurs.find(word) - 1].strip()
        ######################################################################

        if self.__type_pdf == 0:
            for key, value in self.__dico_nom_mail.items():
                # Position du nom ainsi que du mail
                # Si mail de type 2 (mail dans le corps) → rechercher le nom de l'auteur en partant de la fin
                if self.__type_mail == 2:
                    pos_key = self.__text.rfind(key, 0, self.__pos_last_character_first_page)
                else:
                    pos_key = self.__text.find(key)
                ######################################################################
                # On localise la position du mail
                pos_value = self.__text.find(value.split("@")[0])
                ######################################################################

                # Puis, on ne garde que l'établissement correspondant à l'auteur
                result = self.__text[pos_key + len(key):pos_value]
                ######################################################################

                # On regarde s'il y a un \n a la fin et on le retire
                last_new_line = result.rfind("\n")

                if len(result) - 10 < last_new_line:
                    result = result[:last_new_line]
                ######################################################################

                self.__dico_nom_univ[key] = result.strip()

        elif self.__type_pdf == 1:
            first_new_line = section_auteurs.find("\n")

            # Si auteurs sur deux lignes, on ressaute une ligne
            if self.__auteurs_deux_lignes:
                first_new_line = section_auteurs.find("\n", first_new_line + 1)
            ######################################################################

            # Si présence d'un @, on récupère la position du premier @
            first_at = section_auteurs.find("@")
            ######################################################################

            if first_at != -1:
                # Si le @ est précédé d'un \n, on refait une recherche d'un \n avant celui-ci
                if section_auteurs[first_at - 1] == "\n":
                    first_at -= 2
                ######################################################################

                second_new_line = section_auteurs[:first_at].rfind("\n")
            else:
                second_new_line = section_auteurs.rfind("\n")
            ######################################################################

            # Récupération de l'établissement
            school = section_auteurs[first_new_line:second_new_line].strip()
            ######################################################################

            # Retrait du mot article info si présent
            if "article info" in school:
                school = school[:school.find("article info")].strip()
            ######################################################################

            # Si présence de lien entre auteurs et école via des lettres en minuscule, on change en symbole
            school_split = school.split("\n")

            if len([x for x in school_split if x[0].islower()]) >= 1:

                liste_symbole = ["@", "#", "$", "%", "&", ">", "<", "(", ")", "[", "]", "°"]
                index = 0

                for i, element in enumerate(school_split):
                    # On récupère les auteurs avec la même lettre
                    auteurs = [x for x in self.__auteurs if x[-1] == element[0]]
                    ######################################################################

                    # On change de lettre à symbole dans la liste des auteurs
                    for elt in auteurs:
                        self.__auteurs_with_numbers_or_symbol.append(f"{elt[:-1]}{liste_symbole[index]}")
                    ######################################################################

                    # On change de lettre à symbole dans les écoles
                    school_split[i] = f"{liste_symbole[index]}{element[1:]}"
                    ######################################################################

                    index += 1

                # On modifie le nom dans les mails suite au retrait de la lettre qui servait pour l'affiliation
                for auth in self.__auteurs:
                    self.__dico_nom_mail[auth[:-1]] = self.__dico_nom_mail[auth]
                    del self.__dico_nom_mail[auth]
                ######################################################################

                # Puis, on enlève cette lettre des auteurs
                self.__auteurs = [x[:-1] for x in self.__auteurs]
                ######################################################################

                # Enfin, on fusionne les écoles
                school = "".join([f"{x}\n" for x in school_split])
                ######################################################################

            # Si on a des auteurs avec des numéros, on les associe à la bonne école
            if self.__auteurs_with_numbers_or_symbol:
                # On sépare les différentes universités
                school = [x for x in school.split("\n") if x != ""]
                ######################################################################

                # Dictionnaire contenant le numéro et l'université correspondante
                dico_school_number = {}
                school_for_all = ""

                for element in school:
                    if element[0].isdigit() or (any(re.findall(self.__regex_symbol_auteurs, element))):
                        dico_school_number[element[0]] = element[1:]
                    else:
                        school_for_all += element
                ######################################################################

                # On trie les auteurs par ordre croissant
                self.__auteurs.sort()
                self.__auteurs_with_numbers_or_symbol.sort()
                ######################################################################

                # Pour chaque auteur, on l'associe à la bonne école selon les marqueurs présents (chiffre ou symbole)
                for nom, nom_number_symbol in zip(self.__auteurs, self.__auteurs_with_numbers_or_symbol):
                    number = re.findall("[0-9]+", nom_number_symbol)
                    symbol = [x for x in re.findall(self.__regex_symbol_auteurs, nom_number_symbol) if x != ""]

                    if not number and symbol:
                        number = symbol

                    school = ""
                    for nombre in number:
                        school += dico_school_number[nombre] + " "

                    school += f"\n{school_for_all}"

                    self.__dico_nom_univ[nom] = school.strip()
                ######################################################################
                ######################################################################

            else:
                # Si on a des auteurs au début, on les enlève
                for aut in self.__auteurs:
                    pos_name = school.find(aut)
                    if pos_name != -1:
                        school = school[pos_name + len(aut):].strip()
                ######################################################################

                for key in self.__dico_nom_mail.keys():
                    self.__dico_nom_univ[key] = school

        else:
            section_auteurs_separate = section_auteurs.split("\n")

            school = ""

            for element in section_auteurs_separate:
                name_in_element = any(element.find(nom) != -1 for nom in self.__auteurs)
                mail_in_element = any(element.find(nom) != -1 for nom in self.__emails)
                link_in_element = any(element.find(link) != -1 for link in ["http", "www"])
                date_in_element = any(element.find(date) != -1 for date in
                                      ["January", "February", "March", "April", "May", "June", "July", "August",
                                       "September", "October", "November", "December"])

                if not name_in_element and not mail_in_element and not link_in_element and not date_in_element:
                    # Si présence d'un chiffre devant, on le remplace
                    if element[0].isdigit() and not element[1].isdigit():
                        element = f"\n{element[1:]}"
                    ######################################################################

                    school = f"{school}{element}"

            for key in self.__dico_nom_mail.keys():
                self.__dico_nom_univ[key] = school

        words_to_remove = ["/natural", "/flat", "1st", "2nd", "3rd", "4rd", "5rd", "6rd", "7rd", "8rd", "1,2",
                           "(B)", "  ", "(1)", "(2)", "(1,2)"]

        # On enlève les caractères inutiles aux affiliations
        for key, value in self.__dico_nom_univ.items():
            for element in words_to_remove:
                value = value.replace(element, "")

            # Si présence d'un retour à la ligne au début, on l'enlève
            first_new_line = value.find("\n")

            if 0 < first_new_line < 4:
                value = value[first_new_line:]
            ######################################################################

            # Si présence de "and" (nom composé) → on l'enlève
            if "and " in value and any(value.find(x) != -1 for x in self.__auteurs):
                value = value[value.find("\n"):]
            ######################################################################

            # Si présence de mail, on l'enlève
            emails = Mail.find_emails(value)[0]

            if emails:
                nom_mail = emails[0].split("@")[0]
                value = value.split(nom_mail)[0]
            ######################################################################

            # Si présence de ces éléments, on les enlève
            for elt in ["*", self.__abstract.get_abstract(), "article history"]:
                if elt.lower() in value.lower():
                    value = value[:value.lower().find(elt)]
            ######################################################################

            result = ""

            for element in value.split("\n"):
                if len(element) > 1:
                    # Si présence d'un chiffre devant, on l'enlève
                    if element[0].isdigit() and not element[1].isdigit():
                        element = element[1:]
                    ######################################################################

                    # Si présence d'un ; à la fin, on l'enlève
                    if element[-1] == ";":
                        element = element[:-1]
                    ######################################################################

                    result = f"{result}\n{element}"

            # Si aucune affiliation -> on met N/A
            if result == "":
                result = "N/A"
            ######################################################################

            self.__dico_nom_univ[key] = result.strip()
        ######################################################################

    def __separate_authors(f):
        """
        Sépare les auteurs selon certains marqueurs

        :return: None
        """

        @wraps(f)
        def wrapper(self):
            f(self)

            separate_element = [",", " and ", "1;2", "1", "2", "3", "∗", "†", "†"]

            # On regarde si on a des séparateurs dans les noms des auteurs
            if any(element in auteur for auteur in self.__auteurs for element in separate_element):
                # On sépare les auteurs selon les séparateurs connus
                for i, split in enumerate(separate_element):
                    for auth in self.__auteurs:
                        # On garde les auteurs avec des numéros ou symbol pour les associés à la bonne école
                        symbol = [x for x in re.findall(self.__regex_symbol_auteurs, auth)]

                        # Si trop peu de symbol, on ne garde pas
                        if len(symbol) <= 1:
                            symbol = []
                        ######################################################################

                        # Si on itère sur des symboles autres que les séparateurs classiques
                        # et que l'on trouve un numéro ou un symbol, alors on ajoute l'auteur
                        # à la liste des auteurs avec symboles pour ensuite les lier avec la bonne affiliation
                        if i >= 2 and len(auth) > 1 and (any(re.findall("[0-9]+", auth)) or any(
                                symbol)) and auth.strip() not in self.__auteurs_with_numbers_or_symbol:
                            self.__auteurs_with_numbers_or_symbol.append(auth.strip())
                        ######################################################################

                        # Si séparateur présent dans l'auteur, on les sépare
                        if split in auth:
                            auteurs_separer = auth.split(split)

                            index = self.__auteurs.index(auth)

                            self.__auteurs.remove(auth)

                            if index == 0:
                                self.__auteurs = auteurs_separer + self.__auteurs

                            else:
                                if len(auteurs_separer) == 1:
                                    self.__auteurs.insert(index, auteurs_separer[0])
                                else:
                                    for element in auteurs_separer:
                                        self.__auteurs.insert(index, element)
                                        index += 1

                        ######################################################################
                ######################################################################

                taille_auteurs = len(self.__auteurs)

                # On enlève les espaces de début et de fin
                for i in range(taille_auteurs):
                    self.__auteurs[i] = self.__auteurs[i].strip()
                ######################################################################

                # On enlève les potentiels chiffres à la fin
                for i in range(taille_auteurs):
                    value = self.__auteurs[i]
                    if value != "" and value[-1].isnumeric():
                        self.__auteurs[i] = value[:-1]
                ######################################################################
            ######################################################################

            else:
                # On vérifie qu'on n'a pas les auteurs sur une seule ligne
                if len(self.__auteurs) == 1:
                    taille_mails = len(self.__emails)

                    # On enlève les lettres uniques
                    auteurs = self.__auteurs[0]
                    for i in range(1, len(auteurs) - 1):
                        if auteurs[i - 1] == " " and auteurs[i + 1] == " ":
                            auteurs = auteurs[:i] + auteurs[i + 1:]
                    ######################################################################

                    auteurs = auteurs.replace("  ", " ")
                    noms = auteurs.split()
                    liste_noms = []

                    # On assemble les noms ensemble
                    i = 0
                    for nom in noms:
                        if i == 0:
                            liste_noms.append(nom)

                        elif i == 1:
                            # Si nom longueur de deux → particule
                            if len(nom) == 2:
                                i -= 1

                            liste_noms[-1] += f" {nom}"

                        elif i >= 2:
                            liste_noms.append(nom)
                            i = 0

                        i += 1
                    ######################################################################

                    # Si on a plus de noms que de mails, on assemble les derniers noms
                    if len(liste_noms) > taille_mails:
                        difference = len(liste_noms) - taille_mails

                        for _ in range(difference):
                            value = liste_noms.pop()

                            liste_noms[-1] = liste_noms[-1] + " " + value
                    ######################################################################

                    # On repasse les noms dans l'attribut de la classe
                    self.__auteurs = liste_noms
                    ######################################################################
                ######################################################################

            presence_star = False

            # Si présence de chiffre, on les enlève
            for aut in self.__auteurs:
                if any(char.isdigit() for char in aut):
                    aut_split = re.findall("[^0-9]+", aut)

                    aut_split = [x for x in aut_split if len(x) > 2]

                    self.__auteurs.remove(aut)
                    self.__auteurs += aut_split
                if "*" in aut:
                    presence_star = True
            ######################################################################

            # Si présence d'une étoile dans le nom, on l'enlève
            if presence_star:
                for auth in self.__auteurs:
                    if "*" in auth:
                        index = self.__auteurs.index(auth)
                        self.__auteurs[index] = self.__auteurs[index][:-1]
            ######################################################################

            # On enlève les espaces et string vide
            for elt in ["", " ", "  ", ",", ";", ".", '', ' ', '  ', ',', ';', '.']:
                if elt in self.__auteurs:
                    self.__auteurs.remove(elt)
            ######################################################################

            # On retire les caractères inutiles
            auteurs_copy = []
            for elt in self.__auteurs:
                if len(elt) >= 2:
                    auteurs_copy.append(elt)

            # Il peut y avoir le "and" collé à un auteur
            for i, elt in enumerate(auteurs_copy):
                if elt.endswith("and"):
                    auteurs_copy[i] = elt[:-3]
            ######################################################################

            # Copy de la liste
            self.__auteurs[:] = auteurs_copy[:]
            ######################################################################

            return

        return wrapper

    def __make_pair_mail_name(f):
        """
        Effectue la paire mail et nom des auteurs

        :return: None
        """

        def mail_in_dict(mail_to_find: str, dico: dict) -> bool:
            """
            Permet de vérifier si le mail est présent dans le dictionnaire
            contenant les noms comme clefs et [mail, distance] comme valeurs

            :param mail_to_find: mail à trouver
            :param dico: dictionnaire
            :return: True ou False
            """
            for mail_dico, dist in dico.values():
                if mail_dico == mail_to_find:
                    return True

            return False

        @wraps(f)
        def wrapper(self):
            f(self)

            taille_auteurs = len(self.__auteurs)
            taille_mails = len(self.__emails)
            levenshtein_distance = []
            dico_nom_mail_distance = {}

            # On enlève les caractères de retour à la ligne
            for i in range(len(self.__auteurs)):
                if "\n" in self.__auteurs[i]:
                    self.__auteurs[i] = self.__auteurs[i].replace("\n", "")
            ######################################################################

            # Si les tailles sont équivalentes, on associe les mails aux noms
            if taille_auteurs == taille_mails:
                if self.__type_pdf == 0 and self.__type_mail == 0:
                    for nom, mail in zip(self.__auteurs, self.__emails):
                        self.__dico_nom_mail[nom] = mail

                else:
                    # D'abord, on calcule les distances
                    for nom in self.__auteurs:
                        for mail in self.__emails:
                            levenshtein_distance.append([nom, mail, Levenshtein.distance(nom, mail.split("@")[0])])
                    ######################################################################

                    # Puis, on ne garde que les distances les plus faibles
                    for nom, mail, distance in levenshtein_distance:
                        distance_in_dict = dico_nom_mail_distance.get(nom, ["", 10 ** 6])

                        # Si la distance est inférieur et le mail non pris, alors on sauvegarde la paire
                        if distance_in_dict[1] > distance and not mail_in_dict(mail, dico_nom_mail_distance):
                            dico_nom_mail_distance[nom] = [mail, distance]
                        ######################################################################
                    ######################################################################

                    # Enfin, on passe les noms et mails dans le dictionnaire final
                    for key, value in dico_nom_mail_distance.items():
                        self.__dico_nom_mail[key] = value[0]
                    ######################################################################

            # Soit il y a qu'un seul mail → mail de l'équipe
            # Soit on n'en a pas trouvé
            else:
                mention = "N/A"
                if len(self.__emails) == 1:
                    mention = self.__emails[0]

                for nom in self.__auteurs:
                    self.__dico_nom_mail[nom] = mention
            ######################################################################

            return

        return wrapper

    __separate_authors = staticmethod(__separate_authors)
    __make_pair_mail_name = staticmethod(__make_pair_mail_name)

    @__make_pair_mail_name
    @__separate_authors
    def _get_author(self) -> None:
        """
        Renvoi la liste des auteurs (Nom, mail)

        :return: None
        """
        # Position des éléments dans le texte
        pos_titre = self.__text.find(self.__titre.get_title())
        pos_abstract = self.__text.find(self.__abstract.get_abstract()[:20])
        pos_resume = max(self.__text.find("ésumé") - 1, self.__text.find("esume") - 1)

        if 0 < pos_resume < pos_abstract:
            pos_abstract = pos_resume
        ######################################################################

        # On garde que la section correspondant aux auteurs
        section_auteurs = self.__text[pos_titre + len(self.__titre): pos_abstract]
        ######################################################################

        # Enlèvement des mots clefs
        if "bstract" in section_auteurs.strip():
            section_auteurs = section_auteurs[:section_auteurs.find("bstract") - 1].strip()
        ######################################################################

        # Enlèvement des caractères spéciaux
        for string in ["/natural", "/flat", "1st", "2nd", "3rd", "4rd", "5rd", "6rd", "7rd", "8rd", "1,2", "(B)",
                       "*", "  "]:
            if string in section_auteurs:
                section_auteurs = section_auteurs.replace(string, " ")
        ######################################################################

        # Retrait des espaces de début et de fin
        section_auteurs = section_auteurs.strip()
        ######################################################################

        # Recherche dans la section auteurs et si non trouvé, recherche dans toute la page
        self.__emails, self.__type_mail = Mail.find_emails(section_auteurs)

        if not self.__emails:
            self.__emails, self.__type_mail = Mail.find_emails(self.__text)

            # Si on a bien trouvé de mails dans le reste de la page, on ajuste la valeur du type de mail
            if self.__emails:
                self.__type_mail += 2
            else:
                self.__type_pdf = 3
            ######################################################################
        ######################################################################

        # Si ce caractère est trouvé, les auteurs sont sur une seule ligne
        pos_asterisk = section_auteurs.find("∗")

        # Si jamais il y a d'autres auteurs à la suite, on continue dans la fonction
        if pos_asterisk != -1 and section_auteurs[pos_asterisk + 1] == ",":
            pos_asterisk = -1
        ######################################################################

        if pos_asterisk != -1:
            # Si les mails sont sur une seule ligne, pdf de type 1
            if self.__type_mail == 1:
                self.__type_pdf = 1
            else:
                self.__type_pdf = 2
            ######################################################################

            self.__auteurs = [section_auteurs[:pos_asterisk]]
            return
        ######################################################################

        # Stock temporairement les auteurs
        auteurs = []
        ######################################################################

        # S'il y a 0 mail, on récupère les auteurs à tatillon
        if len(self.__emails) == 0:
            auth = section_auteurs.split("\n")

            self.__type_pdf = 3

            # Si apparition de l'affiliation → arrêt
            for elt in auth:
                value = elt.strip()

                if any(value.find(place) != -1 for place in self.__school_words):
                    break

                else:
                    auteurs.append(value)
            ######################################################################
        ######################################################################

        # Sinon, on ne récupère que le seul auteur
        elif len(self.__emails) == 1:
            auteurs.append(section_auteurs.split("\n")[0])
        ######################################################################

        # Sinon, on parcourt les mails et on sépare les auteurs
        elif self.__type_mail == 0:
            """
            En général, les articles sont sous la forme :
            - nom
            - université
            - mail
            et les auteurs se suivent
            Donc on vient séparer le texte des auteurs selon les mails en gardant le nom
            Et enfin on garde le bloc de texte avec le nom et mails en moins du précédent auteur
            """
            self.__type_pdf = 0
            for mail in self.__emails:
                if mail in section_auteurs.strip():
                    result = section_auteurs.split(mail)
                    auteurs.append(result[0].split("\n")[0].strip())

                    pos_mail = section_auteurs.find(mail)
                    section_auteurs = section_auteurs[pos_mail + len(mail):].strip()
        ######################################################################

        # On ne garde que les informations pertinentes
        for auteur in auteurs:
            if auteur and auteur[-1] == ",":
                auteur = auteur[:-1].strip()

            if len(auteur) > 1 and "@" not in auteur and "1,2" not in auteur and "1" not in auteur:
                self.__auteurs.append(auteur)
        ######################################################################

        # Si on a moins d'auteurs que de mails, il est probable que les noms soient sur une seule ligne
        if len(self.__auteurs) == 1 and len(self.__auteurs) < len(self.__emails) and self.__type_mail != 2:
            self.__type_pdf = 1
        ######################################################################

        # Si la liste des auteurs est vide, cela veut dire qu'aucun mail a été trouvé. On parcourt le texte en
        # enlevant les caractères vides et on garde le seul auteur (ou les seuls s'ils sont sur une seule ligne)
        if not self.__auteurs:
            if self.__type_mail == 1:
                self.__type_pdf = 1

            elif self.__type_mail == 2:
                if len(self.__emails) >= 2:
                    pos_first_mail = self.__text.find(self.__emails[0])
                    pos_second_mail = self.__text.find(self.__emails[1])

                    content = self.__text[pos_first_mail:pos_second_mail].strip()

                    if any([x in content for x in self.__school_words]):
                        self.__type_pdf = 0
                    else:
                        self.__type_pdf = 1
                else:
                    self.__type_pdf = 0

            auteurs = self.__text[pos_titre + len(self.__titre): pos_abstract].split("\n")

            for aut in auteurs:
                if aut == "":
                    auteurs.remove(aut)

            self.__auteurs.append(auteurs[0].strip())

            # Si présence d'une virgule à la fin, on rajoute la deuxième ligne des auteurs
            if auteurs[0][-1] == ",":
                self.__auteurs_deux_lignes = True
                self.__auteurs.append(auteurs[1].strip())
            ######################################################################

            # Si on a beaucoup de mails → auteurs sur deux lignes
            if len(self.__emails) >= 6:
                self.__auteurs_deux_lignes = True
                self.__auteurs.append(auteurs[1].strip())
            ######################################################################
        ######################################################################

    def get_authors(self) -> (list, dict, dict):
        """
        Renvoi les informations des auteurs

        :return: liste et dictionnaires des informations (nom, pair nom-mail, pair nom-univ)
        """

        return self.__auteurs, self.__dico_nom_mail, self.__dico_nom_univ
