import xml.etree.ElementTree as ETree
from functools import wraps
from src.Utils import Utils
import Levenshtein
import PyPDF2
import re


class Parser:
    __pdfReader = PyPDF2.PdfReader
    __pathToFile = ""
    __nomFichier = ""
    __directoryTxtFile = ""
    __text_first_page = ""
    __titre = ""
    __auteurs = []
    __emails = []
    __abstract = ""
    __bibliographie = ""
    __dico_nom_mail = {}
    __dico_nom_univ = {}
    __type_pdf = -1
    __type_mail = -1
    """
    Différent type de pdf : 
    -1 : non trouvé
    0 : nom - université - mail
    1 : nom sur une seul ligne - université - mail entre parenthèse ou accolade
    2 : nom - université et mail autre part
    3 : nom et mail - université autre part
    
    Le type des mails aident aussi à connaitre le type de pdf
    -1 : non trouvé
    0 : normal ???????
    1 : entre parenthèse ou accolade
    2 : normal mais dans la page et non au niveau des auteurs
    3 : entre parenthèse ou accolade et non au niveau des auteurs
    """

    def __init__(self, path: str, nom_fichier: str, directory_txt_file: str = None):
        self.__pathToFile = path
        self.__nomFichier = nom_fichier

        if not Utils.is_pdf_file(path + nom_fichier):
            print(f"Nom du fichier : {nom_fichier}")
            raise FileNotFoundError("Le fichier fourni n'est pas un pdf ou n'a pas été trouvé")

        self.__pdfReader = self.__open_pdf()

        if directory_txt_file is not None:
            self.__directoryTxtFile = directory_txt_file

        # On vient récupérer la première page et remplacer les accents
        self.__text_first_page = self.__pdfReader.pages[0].extract_text()
        self.__text_first_page = Utils.replace_accent(self.__text_first_page)

    def __open_pdf(self) -> PyPDF2.PdfReader:
        """
        Ouvre le pdf et renvoi l'objet de lecture

        :return: Objet de lecture du pdf
        """
        pdf_file_obj = open(self.__pathToFile + self.__nomFichier, 'rb')

        return PyPDF2.PdfReader(pdf_file_obj)

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
        emails3 = [x.strip() for x in re.findall(r"[({a-z0-9., \-+_})]+@[a-z0-9.\n\-+_]+\.[a-z]+", texte)]
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
                emails = []
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
                emails = []
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
            emails[i] = emails[i].replace("(", "")
            emails[i] = emails[i].replace("{", "")
            emails[i] = emails[i].replace(")", "")
            emails[i] = emails[i].replace("}", "")
            emails[i] = emails[i].strip()
        ######################################################################

        return emails

    def __separate_authors(f):
        """
        Séparer les auteurs selon certains marqueurs
        """

        # noinspection PyCallingNonCallable
        @wraps(f)
        def wrapper(self):
            f(self)

            separate_element = [",", " and "]

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

                        for i in range(difference):
                            value = liste_noms.pop()

                            liste_noms[-1] = liste_noms[-1] + " " + value
                    ######################################################################

                    # On repasse les noms dans l'attribut de la classe
                    self.__auteurs = liste_noms
                    ######################################################################
                ######################################################################

            for elt in ["", " ", "  "]:
                if elt in self.__auteurs:
                    self.__auteurs.remove(elt)

            return

        return wrapper

    __separate_authors = staticmethod(__separate_authors)

    def __make_pair_mail_name(self, call_get_author: bool = True) -> None:
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

        # Appelle la fonction au besoin
        if call_get_author:
            self._get_author()
        ######################################################################

        self.__dico_nom_mail = {}
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

            return
        ######################################################################

    @__separate_authors
    def _get_author(self) -> None:
        """
        Renvoi la liste des auteurs (Nom, mail)

        :return: List des auteurs
        """
        self.__auteurs = []

        page = self.__text_first_page

        self._get_title()
        self._get_abstract()

        # Position des éléments dans le texte
        pos_titre = page.find(self.__titre)
        pos_abstract = page.find(self.__abstract[:20])
        pos_resume = max(page.find("ésumé") - 1, page.find("esume") - 1)

        if 0 < pos_resume < pos_abstract:
            pos_abstract = pos_resume
        ######################################################################

        # On garde que la section correspondant aux auteurs
        section_auteurs = page[pos_titre + len(self.__titre): pos_abstract]
        ######################################################################

        # Enlèvement des mots clefs
        if "bstract" in section_auteurs.strip():
            section_auteurs = section_auteurs[:section_auteurs.find("bstract") - 1].strip()
        ######################################################################

        # Enlèvement des caractères spéciaux
        for string in ["/natural", "/flat", "1st", "2nd", "3rd", "4rd", "5rd", "6rd", "7rd", "8rd", "1,2", "(B)", "  "]:
            if string in section_auteurs:
                section_auteurs = section_auteurs.replace(string, " ")
        ######################################################################

        # Recherche dans la section auteurs et si non trouvé, recherche dans toute la page
        self.__emails = self.__find_emails(section_auteurs)

        if not self.__emails:
            self.__emails = self.__find_emails(page)

            # Si on a bien trouvé de mails dans le reste de la page, on ajuste la valeur du type de mail
            if self.__emails:
                self.__type_mail += 2
            ######################################################################
        ######################################################################

        # Si ce caractère est trouvé, les auteurs sont sur une seule ligne
        pos_asterisk = section_auteurs.find("∗")

        if pos_asterisk != -1:
            self.__auteurs = [section_auteurs[:pos_asterisk]]
            return
        ######################################################################

        # Stock temporairement les auteurs
        auteurs = []
        ######################################################################

        # S'il y a 0 mail, on récupère les auteurs à tatillon
        if len(self.__emails) == 0:
            auth = section_auteurs.split("\n")

            for elt in auth:
                value = elt.strip()
                if value.find("partement") != -1 or value.find("niversity") != -1 or value.find(
                        "partment") != -1 or value.find("aculty") != -1:
                    break
                else:
                    auteurs.append(elt)
        ######################################################################

        # Sinon, on ne récupère que le seul auteur
        elif len(self.__emails) == 1:
            auteurs.append(section_auteurs.split("\n")[0])
        ######################################################################

        # Sinon, on parcourt les mails et on sépare les auteurs
        else:
            """
            En général, les articles sont sous la forme :
            - nom
            - université
            - mail
            et les auteurs se suivent
            Donc on vient séparer le texte des auteurs selon les mails en gardant le nom
            Et enfin on garde le bloc de texte avec le nom et mails en moins du précédent auteur
            """
            for mail in self.__emails:
                if mail in section_auteurs.strip():
                    result = section_auteurs.split(mail)
                    auteurs.append(result[0].split("\n")[0].strip())

                    pos_mail = section_auteurs.find(mail)
                    section_auteurs = section_auteurs[pos_mail + len(mail):].strip()
        ######################################################################

        # On ne garde que les informations pertinentes
        for i in range(len(auteurs)):
            if len(auteurs[i]) > 0 and auteurs[i][-1] == ",":
                auteurs[i] = auteurs[i][:-1].strip()

            if len(auteurs[i]) > 1 and "@" not in auteurs[i] and "1,2" not in auteurs[i] and "1" not in auteurs[i]:
                self.__auteurs.append(auteurs[i])
        ######################################################################

        # Si la liste des auteurs est vide, cela veut dire qu'aucun mail a été trouvé
        # On parcourt le texte en enlevant les caractères vides et on garde le seul auteur
        if not self.__auteurs:
            auteurs = page[pos_titre + len(self.__titre): pos_abstract].split("\n")
            for aut in auteurs:
                if aut == "":
                    auteurs.remove(aut)

            self.__auteurs.append(auteurs[0].strip())
        ######################################################################

    def _get_title(self, minimum_y=650, maximum_y=770) -> None:
        """
        Renvoie le titre du pdf

        :param minimum_y position minimal en y
        :param maximum_y position maximal en y
        :return: Titre
        """
        self.__titre = ""
        page = self.__pdfReader.pages[0]

        parties = []
        parties_tries = []

        def visitor_body(text, cm, tm, font_dict, font_size):
            if text not in ["", " "] and text != "\n":
                y = tm[5]
                if minimum_y < y < maximum_y:
                    parties.append(text)

        # Extraction des premières lignes
        page.extract_text(visitor_text=visitor_body)

        for elt in parties:
            value = elt.lower().strip()
            if "letter" not in value and "communicated by" not in value:
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
        self.__abstract = ""

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
        ######################################################################

        # S'il y a une section mot-clefs dans le début du pdf, on l'enlève
        if 0 < pos_keywords < pos_introduction:
            pos_introduction = pos_keywords
        ######################################################################

        # S'il y a une section index terms dans le début du pdf, on l'enlève
        if 0 < pos_index_terms < pos_introduction:
            pos_introduction = pos_index_terms
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

    def _get_bibliography(self) -> None:
        """
        Renvoie la bibliographie de l'article

        :return: None
        """
        self.__bibliographie = ""

        number_of_pages = len(self.__pdfReader.pages) - 1
        numero_page = number_of_pages

        while numero_page > -1:
            page = self.__pdfReader.pages[numero_page]

            # Récupération du texte
            content = page.extract_text()
            content_copy = content[:].lower()
            ######################################################################

            pos_references = max(content_copy.find("references"), content.find("References"),
                                 content.find("REFERENCES"))

            if pos_references != -1:
                self.__bibliographie = f"{content[pos_references + len('references'):]}{self.__bibliographie}"
                break

            else:
                self.__bibliographie = f"{content}{self.__bibliographie}"

            numero_page -= 1

    def _get_affiliation(self):
        self._get_title()
        self._get_abstract()
        self.__make_pair_mail_name(False)

        page = self.__text_first_page

        pos_titre = page.find(self.__titre)
        pos_abstract = page.find(self.__abstract[1:10])
        pos_resume = max(page.find("ésumé") - 1, page.find("esume") - 1)

        if 0 < pos_resume < pos_abstract:
            pos_abstract = pos_resume
        ######################################################################

        # On garde que la section correspondant aux auteurs
        section_auteurs = page[pos_titre + len(self.__titre): pos_abstract]
        ######################################################################

        # Enlèvement des mots clefs
        if "bstract" in section_auteurs.strip():
            section_auteurs = section_auteurs[:section_auteurs.find("bstract") - 1].strip()
        ######################################################################
        print()
        print(section_auteurs)
        print()

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
            self._get_title()
            self._get_abstract()
            self._get_author()
            # self.__getAffiliation()
            self.__make_pair_mail_name(False)
            self._get_bibliography()
            self.__bibliographie = Utils.replace_accent(self.__bibliographie)

            if type_output_file == "-t":
                f.write(f"Nom du fichier pdf : {self.__nomFichier}\n\nTitre :\n    {self.__titre}\n\nAuteurs :\n")
                f.writelines([f"    {key} : {value}\n" for key, value in self.__dico_nom_mail.items()])
                f.write(f"\nAbstract :\n    {self.__abstract}\n\nBibliographie : \n    {self.__bibliographie}\n")

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
                ######################################################################

                # Ajout de l'abstract
                abstract = ETree.SubElement(tree, 'abstract')
                abstract.text = self.__abstract
                ######################################################################

                # Ajout de la bibliographie
                abstract = ETree.SubElement(tree, 'bibliographie')
                abstract.text = self.__bibliographie
                ######################################################################

                # Ajout de l'indentation
                ETree.indent(tree)
                ######################################################################

                # Écrire dans le fichier XML
                f.write(ETree.tostring(tree, encoding="utf-8").decode("utf-8"))
                ######################################################################
