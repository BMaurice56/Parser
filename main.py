import xml.etree.ElementTree as ET
import Levenshtein
import traceback
import PyPDF2
import shutil
import sys
import os
import re


class Parser:
    pdfReader = PyPDF2.PdfReader
    pathToFile = ""
    nomFichier = ""
    directoryTxtFile = ""
    titre = ""
    auteurs = []
    emails = []
    abstract = ""
    bibliographie = ""
    dico_nom_mail = {}

    def __init__(self, path: str, nomFichier: str, directoryTxtFile: str = None):
        self.pathToFile = path
        self.nomFichier = nomFichier

        if not self.isPDFFile(path + nomFichier):
            print(f"Nom du fichier : {nomFichier}")
            raise FileNotFoundError("Le fichier fourni n'est pas un pdf")

        self.pdfReader = self.openPDF()

        if directoryTxtFile is not None:
            self.directoryTxtFile = directoryTxtFile

    @staticmethod
    def isPDFFile(nomFichier: str) -> bool:
        """
        Vérifie si le nom de fichier fourni est bien un pdf

        :param nomFichier: Nom du fichier
        :return: True ou False
        """
        if not os.path.isfile(nomFichier) or nomFichier[-4:] != ".pdf":
            return False

        return True

    def openPDF(self) -> PyPDF2.PdfReader:
        """
        Ouvre le pdf et renvoi l'objet de lecture

        :return: Objet de lecture du pdf
        """
        pdfFileObj = open(self.pathToFile + self.nomFichier, 'rb')

        return PyPDF2.PdfReader(pdfFileObj)

    @staticmethod
    def retrievePreviousOrder(liste: list, dico_ordre: dict) -> None:
        """
        Remet les éléments dans la liste dans l'ordre du dictionnaire

        :param liste: Liste contenant les éléments de base
        :param dico_ordre: Contient l'ordre des éléments
        :return: None
        """
        for x, y in dico_ordre.items():
            liste[x] = y

    def replaceAccent(self) -> None:
        """
        Remplace tous les accents mal lus dans les noms

        :return: None
        """
        dictionnaire_lettre = {
            " ´e": 'é',
            " `e": 'è',
            " ´a": 'á',
            " `a": 'à',
            " ˆe": 'ê',
            " ´i": 'í',
            " `i": 'ì',
            " ˆi": 'î',
            " ~n": 'ñ',
            " ´o": 'ó',
            " `o": 'ò',
            " ^o": 'ô',
            " ´u": 'ú',
            " `u": 'ù',
            " ˆu": 'û',
            " ¨u": 'ü',
            " ´y": 'ý',
            " `y": 'ỳ',
            " ˆy": 'ŷ',
            "´e": 'é',
            "`e": 'è',
            "´a": 'á',
            "`a": 'à',
            "^e": 'ê',
            "´i": 'í',
            "`i": 'ì',
            "ˆi": 'î',
            "~n": 'ñ',
            "´o": 'ó',
            "`o": 'ò',
            "^o": 'ô',
            "´u": 'ú',
            "`u": 'ù',
            "^u": 'û',
            "¨u": 'ü',
            "´y": 'ý',
            "`y": 'ỳ',
            "^y": 'ŷ',
            "c ¸": "ç",
            "c¸": "ç",
            " ˆı": "î"
        }

        for key, value in dictionnaire_lettre.items():
            for i in range(len(self.auteurs)):
                self.auteurs[i] = self.auteurs[i].replace(key, value)

    def findEmails(self, texte: str) -> list:
        """
        Trouve les mails dans le texte donné

        :param texte: texte contenant des mails
        :return: Liste des mails
        """
        self.emails = []

        # Récupération des emails
        emails = [x.strip() for x in re.findall(r"[a-z0-9.\-+_]+@[a-z0-9\n\-+_]+\.[a-z]+", texte)]
        emails2 = [x.strip() for x in re.findall(r"[a-z0-9.\-+_]+@[a-z0-9.\n\-+_]+\.[a-z]+", texte)]
        emails3 = [x.strip() for x in re.findall(r"[({a-z0-9., \-+_})]+@[a-z0-9.\n\-+_]+\.[a-z]+", texte)]
        emails4 = [x.strip() for x in re.findall(r"[({a-z0-9., \-+_})]+\n@[a-z0-9.\n\-+_]+\.[a-z]+", texte)]
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
            if len(emails) < len(emails2):
                self.retrievePreviousOrder(emails, position_emails2)
            elif len(emails) > len(emails2):
                self.retrievePreviousOrder(emails, position_emails)
            else:
                i = 0
                for mail, mail2 in zip(emails, emails2):
                    if mail != mail2:
                        if mail[-5:] == ".univ" or mail[-6:] == ".univ-" or len(mail) < len(mail2):
                            emails[i] = mail2
                            position_emails[i] = mail2

                    i += 1

                self.retrievePreviousOrder(emails, position_emails)

        else:
            self.retrievePreviousOrder(emails, position_emails)

        # S'il y a des mails dans la troisième regex, on regarde s'il y a plusieurs mails
        if len(emails3) != 0:
            if "," in emails3[0]:
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
                emails = []
                emails4_separer = emails4[0].split(",")
                dernier_mail, nom_domaine = emails4_separer[-1].split("@")

                for elt in emails4_separer[:-1]:
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

    def separateAuthors(self) -> None:
        """
        Séparer les auteurs selon certains marqueurs

        :return: None
        """
        separate_element = [",", " and "]

        # On sépare les auteurs selon les séparateurs connus
        for split in separate_element:
            for auth in self.auteurs:
                if split in auth:
                    auteurs_separer = auth.split(split)

                    self.auteurs.remove(auth)
                    self.auteurs += auteurs_separer
        ######################################################################

        # On enlève les espaces de début et de fin
        for i in range(len(self.auteurs)):
            self.auteurs[i] = self.auteurs[i].strip()
        ######################################################################

    def makePairMailName(self, callGetAuthor: bool = True) -> None:
        """
        Effectue la paire mail et nom des auteurs

        :return: None
        """
        # Appelle la fonction au besoin
        if callGetAuthor:
            self.getAuthor()
        ######################################################################

        self.dico_nom_mail = {}
        taille_auteurs = len(self.auteurs)
        taille_mails = len(self.emails)
        levenshtein_distance = []
        dico_nom_mail_distance = {}

        # On enlève les caractères de retour à la ligne
        for i in range(len(self.auteurs)):
            if "\n" in self.auteurs[i]:
                self.auteurs[i] = self.auteurs[i].replace("\n", "")
        ######################################################################

        # Si les tailles sont équivalentes, on associe les mails aux noms
        if taille_auteurs == taille_mails:
            # D'abord, on calcule les distances
            for nom in self.auteurs:
                for mail in self.emails:
                    levenshtein_distance.append([nom, mail, Levenshtein.distance(nom, mail.split("@")[0])])
            ######################################################################

            # Puis, on ne garde que les distances les plus faibles
            for nom, mail, distance in levenshtein_distance:
                distance_in_dict = dico_nom_mail_distance.get(nom, ["", 10 ** 6])
                if distance_in_dict[1] >= distance:
                    dico_nom_mail_distance[nom] = [mail, distance]
            ######################################################################

            # Enfin, on passe les noms et mails dans le dictionnaire final
            for key, value in dico_nom_mail_distance.items():
                self.dico_nom_mail[key] = value[0]
            ######################################################################

        elif taille_auteurs > taille_mails:
            for nom in self.auteurs:
                self.dico_nom_mail[nom] = "Pas d'adresse mail"

            return

        else:
            # On enlève les lettres uniques
            auteurs = self.auteurs[0]
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
            self.auteurs = liste_noms
            ######################################################################

            # Puis, on rappelle la fonction comme on a le même nombre de mails et de noms
            self.makePairMailName(False)
            ######################################################################

    def getAuthor(self) -> None:
        """
        Renvoi la liste des auteurs (Nom, mail)

        :return: List des auteurs
        """
        self.auteurs = []

        page = self.pdfReader.pages[0].extract_text()

        self.getTitle()
        self.getAbstract()

        # Position des éléments dans le texte
        pos_titre = page.find(self.titre)
        pos_abstract = page.find(self.abstract)
        ######################################################################

        # On garde que la section correspondant aux auteurs
        section_auteurs = page[pos_titre + len(self.titre): pos_abstract]
        ######################################################################

        # Enlèvement des mots clefs
        if "Abstract" in section_auteurs.strip():
            section_auteurs = section_auteurs[:section_auteurs.find("Abstract") - 1].strip()
        ######################################################################

        # Enlèvement des caractères spéciaux
        for string in ["/natural", "/flat", "1st", "2nd", "3rd", "4rd", "5rd", "6rd", "7rd", "8rd", "1,2", "(B)", "  "]:
            if string in section_auteurs:
                section_auteurs = section_auteurs.replace(string, " ")
        ######################################################################

        # Recherche dans la section auteurs et si non trouvé, recherche dans toute la page
        self.emails = self.findEmails(section_auteurs)

        if not self.emails:
            self.emails = self.findEmails(page)
        ######################################################################

        # Si ce caractère est trouvé, les auteurs sont sur une seule ligne
        pos_asterisk = section_auteurs.find("∗")

        if pos_asterisk != -1:
            self.auteurs = [section_auteurs[:pos_asterisk]]
            return
        ######################################################################

        # Stock temporairement les auteurs
        auteurs = []

        # S'il y a 1 seul mail, on récupère le seul auteur
        if len(self.emails) <= 1:
            auteurs.append(section_auteurs.split("\n")[0])
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
            for mail in self.emails:
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

            if auteurs[i] not in ["", "."] and "@" not in auteurs[i]:
                self.auteurs.append(auteurs[i])
        ######################################################################

        # Si la liste des auteurs est vide, cela veut dire qu'aucun mail a été trouvé
        # On parcourt le texte en enlevant les caractères vides et on garde le seul auteur
        if not self.auteurs:
            auteurs = page[pos_titre + len(self.titre): pos_abstract].split("\n")
            for aut in auteurs:
                if aut == "":
                    auteurs.remove(aut)

            self.auteurs.append(auteurs[0].strip())
        ######################################################################

        # On sépare les auteurs
        self.separateAuthors()
        ######################################################################

        # On enlève les caractères vides
        if "" in self.auteurs:
            self.auteurs.remove("")
        ######################################################################

    def getTitle(self, minimum_y=650, maximum_y=750) -> None:
        """
        Renvoie le titre du pdf

        :param minimum_y position minimal en y
        :param maximum_y position maximal en y
        :return: Titre
        """
        self.titre = ""

        page = self.pdfReader.pages[0]

        parties = []
        parties_tries = []

        def visitor_body(text, cm, tm, fontDict, fontSize):
            if text != "" and text != " " and text != "\n":
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
                self.titre = ""
                self.getTitle(minimum_y - 10, maximum_y - 10)
            else:
                self.titre += parties_tries[0]

            return
            ######################################################################

        # Soit le titre est en deux parties
        elif taille_parties == 2:
            for elt in parties_tries:
                self.titre += elt

            return
        ######################################################################

        # Soit, on commence à itérer sur le texte et à ce moment-là, on ne garde que les premières lignes
        elif len(parties_tries) > 10:
            self.titre += parties_tries[0]
            if parties_tries[0][-1] == "\n":
                self.titre += parties_tries[1]
            return
        ######################################################################

        # Soit, on n'a rien trouvé, ou on se trouve à moins de 10 éléments
        else:
            self.titre = ""
            self.getTitle(minimum_y - 10, maximum_y - 10)
        ######################################################################

    def getAbstract(self) -> None:
        """
        Renvoie l'abstract du pdf

        :return: String
        """
        self.abstract = ""

        numero_page = 0
        number_of_pages = len(self.pdfReader.pages)

        # Recherche l'abstract dans le fichier
        while numero_page < number_of_pages:
            page = self.pdfReader.pages[numero_page]

            # Récupération du texte
            content = page.extract_text()
            content_copy = content[:].lower()
            ######################################################################

            # Position des mots clefs
            pos_abstract = max(content_copy.find("abstract"), content_copy.find("bstract") - 1)
            pos_introduction = max(content_copy.find("introduction"), content_copy.find("ntroduction") - 1)
            pos_keywords = max(content_copy.find("keywords"), content_copy.find("eywords") - 1)
            pos_index_terms = max(content_copy.find("index terms"), content_copy.find("ndex terms") - 1)
            ######################################################################

            # S'il y a une section mot-clefs dans le début du pdf, on l'enlève
            if pos_keywords != -1 and pos_keywords < pos_introduction:
                pos_introduction = pos_keywords
            ######################################################################

            # S'il y a une section index terms dans le début du pdf, on l'enlève
            if pos_index_terms != -1 and pos_index_terms < pos_introduction:
                pos_introduction = pos_index_terms
            ######################################################################

            # Si trouvé, alors on peut renvoyer l'abstract
            if pos_abstract != -1 and pos_introduction != -1:
                swift = 1
                if content[pos_abstract + len("Abstract") + swift] in [" ", "\n", "-", "—"]:
                    swift += 1

                self.abstract = content[pos_abstract + len("Abstract") + swift:pos_introduction - 2]
                break
            ######################################################################

            # Sinon absence du mot abstract
            elif pos_abstract == -1 and pos_introduction != -1:
                dernier_point = content[:pos_introduction - 2].rfind(".")

                i = 0

                for i in range(dernier_point, 1, -1):
                    if ord(content[i]) < 20:
                        if ord(content[i - 1]) != 45:
                            break

                self.abstract = content[i + 1:dernier_point]
                break
            ######################################################################

            numero_page += 1
        ######################################################################

        # Si présence du 1 de l'introduction, on l'enlève
        pos_i_introduction = self.abstract.rfind("I.")

        if pos_i_introduction != -1:
            self.abstract = self.abstract[:pos_i_introduction - 1]
        ######################################################################

        # Permet d'enlever les espaces et retour à la ligne à la fin pour vérifier la présence du point
        while self.abstract[-1] in ["\n", " "]:
            self.abstract = self.abstract[:-1]

        if self.abstract[-1] != ".":
            self.abstract += "."
        ######################################################################

    def getBibliography(self) -> None:
        """
        Renvoie la bibliographie de l'article

        :return: None
        """
        self.bibliographie = ""

        number_of_pages = len(self.pdfReader.pages) - 1
        numero_page = number_of_pages

        while numero_page > -1:
            page = self.pdfReader.pages[numero_page]

            # Récupération du texte
            content = page.extract_text()
            content_copy = content[:].lower()
            ######################################################################

            pos_references = max(content_copy.find("references"), content.find("References"),
                                 content.find("REFERENCES"))

            if pos_references != -1:
                self.bibliographie = f"{content[pos_references + len('references'):]}{self.bibliographie}"
                break

            else:
                self.bibliographie = f"{content}{self.bibliographie}"

            numero_page -= 1

    def writeValueInFile(self, typeOutputFile: str) -> None:
        """
        Écrit dans un fichier txt l'analyse du pdf

        :return: None
        """
        if self.directoryTxtFile == "":
            file = f"{self.pathToFile}{self.nomFichier[:-4]}"

        else:
            file = f"{self.directoryTxtFile}{self.nomFichier[:-4]}"

        if typeOutputFile == "-t":
            file += ".txt"

        elif typeOutputFile == "-x":
            file += ".xml"

        with open(file, "w", encoding="utf-8") as f:
            self.getTitle()
            self.getAbstract()
            self.getAuthor()
            self.replaceAccent()
            self.makePairMailName(False)
            self.getBibliography()

            if typeOutputFile == "-t":
                f.write(f"Nom du fichier pdf : {self.nomFichier}\n")
                f.write("\nTitre :\n")
                f.write(f"    {self.titre}\n\n")

                f.write("Auteurs :\n")
                for key, value in self.dico_nom_mail.items():
                    f.write(f"    {key} : {value}\n")

                f.write("\nAbstract :\n")
                f.write(f"    {self.abstract}\n")

                f.write("\nBibliographie : \n")
                f.write(f"    {self.bibliographie}\n")

            elif typeOutputFile == "-x":
                # Ajout de l'arbre article
                tree = ET.Element("article")
                ######################################################################

                # Ajout du preamble
                preamble = ET.SubElement(tree, 'preamble')
                preamble.text = self.nomFichier

                # Ajout du titre
                titre = ET.SubElement(tree, 'titre')
                titre.text = self.titre
                ######################################################################

                # Ajout du tag auteurs
                auteurs = ET.SubElement(tree, 'auteurs')
                ######################################################################

                # Ajout de chaque auteur avec son nom et mail
                for key, value in self.dico_nom_mail.items():
                    auteur = ET.SubElement(auteurs, 'auteur')

                    nom = ET.SubElement(auteur, 'name')
                    nom.text = key

                    mail = ET.SubElement(auteur, 'mail')
                    mail.text = value
                ######################################################################

                # Ajout de l'abstract
                abstract = ET.SubElement(tree, 'abstract')
                abstract.text = self.abstract
                ######################################################################

                # Ajout de la bibliographie
                abstract = ET.SubElement(tree, 'bibliographie')
                abstract.text = self.bibliographie
                ######################################################################

                # Ajout de l'indentation
                ET.indent(tree)
                ######################################################################

                # Écrire dans le fichier XML
                f.write(ET.tostring(tree, encoding="utf-8").decode("utf-8"))
                ######################################################################

            else:
                raise Exception("Erreur type de fichier sortie")


if __name__ == '__main__':
    try:
        if len(sys.argv) != 3:
            raise Exception("Erreur nombre argument")

        argv = sys.argv[1]
        pathToFile = sys.argv[2]

        if argv != "-t" and argv != "-x":
            raise Exception("Erreur argument rentré")

        # Check si dossier ou fichier
        if os.path.isdir(pathToFile):
            # Check si / à la fin
            if pathToFile[-1] != "/":
                pathToFile += "/"

            # Chemin du dossier de sortie
            nomDossier = pathToFile + "analyse_pdf/"

            # Si existence du dossier → on le supprime
            if os.path.exists(nomDossier):
                try:
                    os.rmdir(nomDossier)

                except OSError:
                    try:
                        shutil.rmtree(nomDossier)

                    except Exception:
                        message = (
                            "\nImpossible de supprimer le dossier analyse_pdf\nCe dossier est nécessaire pour la "
                            "bonne exécution du programme")

                        raise Exception(message)

            # Création du dossier
            os.makedirs(nomDossier)

            for element in os.listdir(pathToFile):
                if Parser.isPDFFile(pathToFile + element):
                    Parser(pathToFile, element, nomDossier).writeValueInFile(argv)
                    print(f"Analyse efféctué sur : {element}")

        else:
            last_slash = pathToFile.rfind("/")

            chemin_fichier = pathToFile[:last_slash + 1]
            nom_fichier = pathToFile[last_slash + 1:]

            parser = Parser(chemin_fichier, nom_fichier)

            parser.writeValueInFile(argv)

            print(f"Analyse efféctué sur : {nom_fichier}")

    except Exception as e:
        print(traceback.format_exc())
        print("main.py -outputfile [/path/to/the/file.pdf, /path/to/the/dir/]")
        print("outputfile : -t text")
        print("             -x xml")
