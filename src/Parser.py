import xml.etree.ElementTree as ETree
from functools import wraps
from src.Utils import Utils
import Levenshtein
import unicodedata
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
        self.__auteurs = []
        self.__emails = []
        self.__abstract = ""
        self.__introduction = ""
        self.__corps = ""
        self.__acknowledgments = ""
        self.__conclusion = ""
        self.__appendix = ""
        self.__discussion = ""
        self.__references = ""
        self.__dico_nom_mail = {}
        self.__dico_nom_univ = {}
        self.__school_words = ["partement", "niversit", "partment", "acult", "laborato", "nstitute", "campus",
                               "academy", "school"]
        self.__title_keywords = {"iscussion": "D",
                                 "onclusion": "C",
                                 "ppendix": "A",
                                 "cknowledgment": "A",
                                 "eferences": "R",
                                 "ollow-up work": "F"}

        self.__position_title_keywords = {}
        self.__text_first_page = ""
        self.__text_rest = ""
        self.__text_rest_lower = ""
        self.__auteurs_deux_lignes = False
        self.__type_pdf = -1
        self.__type_mail = -1
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

    def __load_text_attribut(self) -> None:
        """
        Charge le contenu du text dans les deux attributs

        :return: None
        """
        self.__text_first_page = self.__pdfReader.pages[0].extract_text()
        self.__text_rest = "".join(
            self.__pdfReader.pages[x].extract_text() for x in range(1, len(self.__pdfReader.pages)))

        self.__text_first_page = Utils.replace_accent(self.__text_first_page)
        self.__text_rest = Utils.replace_accent(self.__text_rest)

        # Filtre les caractères pour ne conserver que les caractères ASCII
        chaine_normalisee = unicodedata.normalize('NFD', self.__text_rest.lower())

        self.__text_rest_lower = ''.join(c for c in chaine_normalisee if unicodedata.category(c) != 'Mn')
        ######################################################################

        # Remplace le mot clef pour mieux le retrouver
        self.__text_rest_lower = self.__text_rest_lower.replace("cknowledgement", "cknowledgment ")
        ######################################################################

    def __localisation_keywords(self) -> None:
        """
        Localise la position des mots clefs

        :return: None
        """
        pos_word = -2

        for word, first_letter in self.__title_keywords.items():
            while pos_word != -1:
                pos_word = self.__text_rest_lower[:pos_word].rfind(word)

                if pos_word != -1:
                    # On regarde s'il y a un \n devant ou un . + présence de la lettre en majuscule (titre)
                    content_around_word = self.__text_rest[
                                          pos_word - 8:pos_word]

                    check_title = "\n" in content_around_word or f".{first_letter}" in content_around_word

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
        self.__load_text_attribut()
        self.__localisation_keywords()
        self._get_title()
        self.__titre = Utils.replace_accent(self.__titre)
        self._get_abstract()
        self._get_author()
        self._get_affiliation()
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

    def __find_emails(self, texte: str) -> list:
        """
        Trouve les mails dans le texte donné

        :param texte: texte contenant des mails
        :return: Liste des mails
        """
        self.__emails = []

        # Récupération des emails
        emails = [x.strip() for x in re.findall(r"[a-z0-9.\-+_]+@[a-z0-9\n\-+_]+\.[a-z]+", texte)]
        emails2 = [x.strip() for x in re.findall(r"[a-z0-9.\-+_]+@[a-z0-9.\n\-+_]+\.[a-z]+", texte)]
        emails3 = [x.strip() for x in re.findall(r"[({a-z0-9., \-+_})]+@[a-z0-9.\n\- +_]+\.[a-z]+", texte)]
        emails4 = [x.strip() for x in re.findall(r"[({a-z0-9., \-+_})]+\n@[a-z0-9.\n\-+_]+\.[a-z]+", texte)]
        emails5 = [x.strip() for x in re.findall(r"[({a-z0-9., \-+_})]+Q[a-z0-9.\n\-+_]+\.[a-z]+", texte)]
        ######################################################################

        # Dictionnaire qui permet de retrouver l'ordre après tri
        position_emails = dict((x, y) for x, y in enumerate(emails, 0))
        position_emails2 = dict((x, y) for x, y in enumerate(emails2, 0))
        ######################################################################

        # Tri les listes pour pouvoir les comparer
        emails.sort()
        emails2.sort()
        ######################################################################

        if emails and emails != emails2:
            self.__type_mail = 0
            if len(emails) < len(emails2):
                Utils.retrieve_previous_order(emails, position_emails2)
            elif len(emails) > len(emails2):
                Utils.retrieve_previous_order(emails, position_emails)
            else:
                i = 0
                for mail, mail2 in zip(emails, emails2):
                    if mail != mail2:
                        if mail[-5:] == ".univ" or mail[-6:] == ".univ-" or len(mail) < len(mail2):
                            emails[i] = mail2
                            position_emails[i] = mail2

                    i += 1

                Utils.retrieve_previous_order(emails, position_emails)

        else:
            self.__type_mail = 0
            Utils.retrieve_previous_order(emails, position_emails)

        # S'il y a des mails dans la troisième regex, on regarde s'il y a plusieurs mails
        if len(emails3) != 0:
            if "," in emails3[0]:
                self.__type_mail = 1

                emails3_separer = emails3[0].split(",")
                dernier_mail, nom_domaine = emails3_separer[-1].split("@")

                for elt in emails3_separer[:-1]:
                    emails.append(f"{elt.strip()}@{nom_domaine}")

                emails.append(f"{dernier_mail}@{nom_domaine}")
        ######################################################################

        # S'il y a des mails dans la quatrième regex, on regarde s'il y a plusieurs mails
        if len(emails4) != 0:
            if "," in emails4[0]:
                self.__type_mail = 1

                emails4_separer = emails4[0].split(",")
                dernier_mail, nom_domaine = emails4_separer[-1].split("@")

                for elt in emails4_separer[:-1]:
                    emails.append(f"{elt.strip()}@{nom_domaine}")

                emails.append(f"{dernier_mail}@{nom_domaine}")
        ######################################################################

        # Soit, le @ a été lu comme un Q et donc on sépare les mails
        if not emails and len(emails5) > 0:
            if "," in emails5[0]:
                self.__type_mail = 1
                emails5_separer = emails5[0].split(",")
                dernier_mail, nom_domaine = emails5_separer[-1].split("Q")

                for elt in emails5_separer[:-1]:
                    emails.append(f"{elt.strip()}@{nom_domaine}")

                emails.append(f"{dernier_mail}@{nom_domaine}")
        ######################################################################

        # Pour chaque mail, on enlève différents caractères
        for i in range(len(emails)):
            emails[i] = emails[i].replace("\n", "")
            emails[i] = emails[i].replace("(", "").replace(")", "")
            emails[i] = emails[i].replace("{", "").replace("}", "")
            emails[i] = emails[i].strip()
        ######################################################################

        # Si le mail est trop petit(erreur) -> on l'enlève
        for element in emails:
            if len(element.split("@")[0]) < 2:
                emails.remove(element)
        ######################################################################

        return emails

    def __separate_authors(f):
        """
        Sépare les auteurs selon certains marqueurs

        :return: None
        """

        @wraps(f)
        def wrapper(self):
            f(self)

            separate_element = [",", " and ", "1;2", "1", "2", "3"]

            # On regarde si on a des séparateurs dans les noms des auteurs
            if any(element in auteur for auteur in self.__auteurs for element in separate_element):
                # On sépare les auteurs selon les séparateurs connus
                for split in separate_element:
                    for auth in self.__auteurs:
                        if split in auth:
                            auteurs_separer = auth.split(split)

                            self.__auteurs.remove(auth)
                            self.__auteurs += auteurs_separer
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
                # D'abord, on calcule les distances
                for nom in self.__auteurs:
                    for mail in self.__emails:
                        levenshtein_distance.append([nom, mail, Levenshtein.distance(nom, mail.split("@")[0])])
                ######################################################################

                # Puis, on ne garde que les distances les plus faibles
                for nom, mail, distance in levenshtein_distance:
                    distance_in_dict = dico_nom_mail_distance.get(nom, ["", 10 ** 6])

                    # Si la distance est inférieur et le mail non pris, alors on sauvegarde la paire
                    if distance_in_dict[1] >= distance and not mail_in_dict(mail, dico_nom_mail_distance):
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
                mention = "Pas d'adresse mail"
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
        if not self.__auteurs and self.__dico_nom_mail == {}:
            # Position des éléments dans le texte
            pos_titre = self.__text_first_page.find(self.__titre)
            pos_abstract = self.__text_first_page.find(self.__abstract[:20])
            pos_resume = max(self.__text_first_page.find("ésumé") - 1, self.__text_first_page.find("esume") - 1)

            if 0 < pos_resume < pos_abstract:
                pos_abstract = pos_resume
            ######################################################################

            # On garde que la section correspondant aux auteurs
            section_auteurs = self.__text_first_page[pos_titre + len(self.__titre): pos_abstract]
            ######################################################################

            # Enlèvement des mots clefs
            if "bstract" in section_auteurs.strip():
                section_auteurs = section_auteurs[:section_auteurs.find("bstract") - 1].strip()
            ######################################################################

            # Enlèvement des caractères spéciaux
            for string in ["/natural", "/flat", "1st", "2nd", "3rd", "4rd", "5rd", "6rd", "7rd", "8rd", "1,2", "(B)",
                           "  "]:
                if string in section_auteurs:
                    section_auteurs = section_auteurs.replace(string, " ")
            ######################################################################

            # Recherche dans la section auteurs et si non trouvé, recherche dans toute la page
            self.__emails = self.__find_emails(section_auteurs)

            if not self.__emails:
                self.__emails = self.__find_emails(self.__text_first_page)

                # Si on a bien trouvé de mails dans le reste de la page, on ajuste la valeur du type de mail
                if self.__emails:
                    self.__type_mail += 2
                else:
                    self.__type_pdf = 3
                ######################################################################
            ######################################################################

            # Si ce caractère est trouvé, les auteurs sont sur une seule ligne
            pos_asterisk = section_auteurs.find("∗")
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
            if len(self.__auteurs) == 1 and len(self.__auteurs) < len(self.__emails):
                if self.__type_mail != 2:
                    self.__type_pdf = 1
            ######################################################################

            # Si la liste des auteurs est vide, cela veut dire qu'aucun mail a été trouvé On parcourt le texte en
            # enlevant les caractères vides et on garde le seul auteur (ou les seuls s'ils sont sur une seule ligne)
            if not self.__auteurs:
                if self.__type_mail == 1:
                    self.__type_pdf = 1

                elif self.__type_mail == 2:
                    self.__type_pdf = 0

                auteurs = self.__text_first_page[pos_titre + len(self.__titre): pos_abstract].split("\n")

                for aut in auteurs:
                    if aut == "":
                        auteurs.remove(aut)

                self.__auteurs.append(auteurs[0].strip())

                # Si on a beaucoup de mails → auteurs sur deux lignes
                if len(self.__emails) >= 6:
                    self.__auteurs_deux_lignes = True
                    self.__auteurs.append(auteurs[1].strip())
                ######################################################################
            ######################################################################

    def _get_affiliation(self) -> None:
        """
        Récupère les universités des différents auteurs

        :return: None
        """
        if self.__dico_nom_univ == {}:
            pos_titre = self.__text_first_page.find(self.__titre)
            pos_abstract = self.__text_first_page.find(self.__abstract[1:10])
            pos_resume = max(self.__text_first_page.find("ésumé") - 1, self.__text_first_page.find("esume") - 1)

            if 0 < pos_resume < pos_abstract:
                pos_abstract = pos_resume
            ######################################################################

            # On garde que la section correspondant aux auteurs
            section_auteurs = self.__text_first_page[pos_titre + len(self.__titre): pos_abstract].strip()
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
                        pos_key = self.__text_first_page.rfind(key)
                    else:
                        pos_key = self.__text_first_page.find(key)
                    ######################################################################

                    # On localise la position du mail
                    pos_value = self.__text_first_page.find(value.split("@")[0])
                    ######################################################################

                    # Puis, on ne garde que l'établissement correspondant à l'auteur
                    result = self.__text_first_page[pos_key + len(key):pos_value]
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
                    first_new_line = section_auteurs[first_new_line + 1:].find("\n") + first_new_line
                ######################################################################

                # Si présence d'un @, on récupère la position du dernier \n
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

                for key in self.__dico_nom_mail.keys():
                    self.__dico_nom_univ[key] = school

            else:
                section_auteurs_separate = section_auteurs.split("\n")

                school = ""

                for element in section_auteurs_separate:
                    name_in_element = any(element.find(nom) != -1 for nom in self.__auteurs)
                    mail_in_element = any(element.find(nom) != -1 for nom in self.__emails)
                    link_in_element = any(element.find(link) != -1 for link in ["http", "www"])

                    if not name_in_element and not mail_in_element and not link_in_element:
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
                emails = self.__find_emails(value)

                if emails:
                    nom_mail = emails[0].split("@")[0]
                    value = value.split(nom_mail)[0]
                ######################################################################

                # Si présence d'une étoile, on l'enlève
                if "*" in value:
                    value = value[:value.find("*")]
                ######################################################################

                result = ""

                for element in value.split("\n"):
                    if len(element) > 1:
                        # Si présence d'un chiffre devant, on l'enlève
                        if element[0].isdigit() and not element[1].isdigit():
                            element = element[1:]
                        ######################################################################

                        result = f"{result}\n{element}"

                self.__dico_nom_univ[key] = result.strip()
            ######################################################################

    def _get_title(self, minimum_y: int = 650, maximum_y: int = 770) -> None:
        """
        Renvoie le titre du pdf

        :param minimum_y position minimal en y
        :param maximum_y position maximal en y
        :return: None
        """
        if self.__titre == "":
            page = self.__pdfReader.pages[0]

            parties = []
            parties_tries = []

            def visitor_body(text, _cm, tm, _font_dict, _font_size):
                if text not in ["", " "] and text != "\n":
                    y = tm[5]
                    if minimum_y < y < maximum_y:
                        parties.append(text)

            # Extraction des premières lignes
            page.extract_text(visitor_text=visitor_body)

            word_to_avoid = ["letter", "communicated by", "article", "published", "/"]

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

                return
            ######################################################################

            # Soit, on commence à itérer sur le texte et à ce moment-là, on ne garde que les premières lignes
            elif len(parties_tries) > 10:
                self.__titre += parties_tries[0]
                if parties_tries[0][-1] == "\n":
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

    def _get_abstract(self) -> None:
        """
        Renvoie l'abstract du pdf

        :return: None
        """
        if self.__abstract == "":
            # Récupération du texte
            content = self.__text_first_page
            content_copy = content[:].lower()
            ######################################################################

            # Position des mots clefs
            pos_abstract = max(content_copy.find("abstract"), content_copy.find("bstract") - 1)
            pos_introduction = max(content_copy.find("introduction"), content_copy.find("ntroduction") - 1)
            pos_keywords = max(content_copy.find("keyword"), content_copy.find("eyword") - 1,
                               content_copy.find("ey-word") - 1)
            pos_index_terms = max(content_copy.find("index terms"), content_copy.find("ndex terms") - 1)
            pos_mot_clefs = max(content_copy.find("mots-cl"), content_copy.find("mots cl"))
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

            # Si trouvé, alors on peut renvoyer l'abstract
            if pos_abstract != -1 and pos_introduction != -1:
                swift = 1
                if content[pos_abstract + len("Abstract") + swift] in [" ", "\n", "-", "—"]:
                    swift += 1

                self.__abstract = content[pos_abstract + len("Abstract") + swift:pos_introduction - 2]
            ######################################################################

            # Sinon absence du mot abstract
            elif pos_abstract == -1 and pos_introduction != -1:
                dernier_point = content[:pos_introduction - 2].rfind(".")

                i = 0

                for i in range(dernier_point, 1, -1):
                    if ord(content[i]) < 20:
                        if ord(content[i - 1]) != 45:
                            break

                self.__abstract = content[i + 1:dernier_point]
            ######################################################################

            # Si présence du 1 de l'introduction, on l'enlève
            pos_i_introduction = self.__abstract.rfind("I.")

            if pos_i_introduction != -1:
                self.__abstract = self.__abstract[:pos_i_introduction - 1]
            ######################################################################

            # Permet d'enlever les espaces et retour à la ligne à la fin pour vérifier la présence du point
            if self.__abstract != "":
                while self.__abstract[-1] in ["\n", " "]:
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
            # Position de l'abstract
            pos_abstract = self.__text_first_page.find(self.__abstract)
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
            texte = self.__text_first_page[pos_abstract + len(self.__abstract):] + self.__text_rest[:pos_first_keyword]
            texte_lower = texte.lower()
            ######################################################################

            # Position du mot introduction
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
                                  pos_introduction + len("ntroduction") + add_margin_cause_space: pos_second_title_word]

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
                self.__conclusion = self.__text_rest[pos_conclusion + len(onclusion_word):pos_word_after].strip()

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
                self.__conclusion = "Aucune conclusion"

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
                self.__discussion = self.__text_rest[pos_discussion + len(iscussion_word):pos_word_after].strip()
                ######################################################################

                # Si présence d'un "and", on le retire
                if self.__discussion[:4] == "and ":
                    self.__discussion = self.__discussion[self.__discussion.find("\n"):]
                ######################################################################

                # On enlève les caractères du titre suivant la discussion
                self.__discussion = self.__discussion[:self.__discussion.rfind("\n")].strip()
                ######################################################################

            else:
                self.__discussion = "Aucune discussion"

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
                self.__references = f"{self.__text_rest[pos_references + len('references'):word_after - 1]}"

            else:
                self.__references = "Aucune bibliographie"

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
                corps = ETree.SubElement(tree, 'corps')
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
                abstract = ETree.SubElement(tree, 'bibliographie')
                abstract.text = self.__references
                ######################################################################

                # Ajout de l'indentation
                ETree.indent(tree)
                ######################################################################

                # Écrire dans le fichier XML
                f.write(ETree.tostring(tree, encoding="utf-8").decode("utf-8"))
                ######################################################################
