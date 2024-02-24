# from bs4 import BeautifulSoup
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
            " ^e": 'ê',
            " ´i": 'í',
            " `i": 'ì',
            " ^i": 'î',
            " ~n": 'ñ',
            " ´o": 'ó',
            " `o": 'ò',
            " ^o": 'ô',
            " ´u": 'ú',
            " `u": 'ù',
            " ^u": 'û',
            " ¨u": 'ü',
            " ´y": 'ý',
            " `y": 'ỳ',
            " ^y": 'ŷ',
            "´e": 'é',
            "`e": 'è',
            "´a": 'á',
            "`a": 'à',
            "^e": 'ê',
            "´i": 'í',
            "`i": 'ì',
            "^i": 'î',
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
        }

        for key, value in dictionnaire_lettre.items():
            for i in range(len(self.auteurs)):
                self.auteurs[i] = self.auteurs[i].replace(key, value)

    def findEmails(self, texte: str) -> list:
        # Récupération des emails
        emails = re.findall(r"[a-z0-9.\-+_]+@[a-z0-9\n\-+_]+\.[a-z]+", texte)
        emails2 = re.findall(r"[a-z0-9.\-+_]+@[a-z0-9.\n\-+_]+\.[a-z]+", texte)

        # Dictionnaire qui permet de retrouver l'ordre après tri
        position_emails = dict((x, y) for x, y in enumerate(emails, 0))
        position_emails2 = dict((x, y) for x, y in enumerate(emails2, 0))

        # Tri les listes pour pouvoir les comparer
        emails.sort()
        emails2.sort()

        if emails and emails != emails2:
            if len(emails) < len(emails2):
                self.retrievePreviousOrder(emails, position_emails2)
            elif len(self.emails) > len(emails2):
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

        # Pour chaque mail, on enlève les retours à la ligne
        for i in range(len(emails)):
            emails[i] = emails[i].replace("\n", "")

        return emails

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

        # On garde que la section correspondant aux auteurs
        section_auteurs = page[pos_titre + len(self.titre): pos_abstract]

        # Enlèvement des mots clefs
        if "Abstract" in section_auteurs.strip():
            section_auteurs = section_auteurs[:section_auteurs.find("Abstract") - 1].strip()

        # Enlèvement des caractères spéciaux
        for string in ["/natural", "/flat", "1st", "2nd", "3rd", "4rd", "5rd", "6rd", "7rd", "8rd", "1,2", "(B)", "  "]:
            if string in section_auteurs:
                section_auteurs = section_auteurs.replace(string, " ")

        # Recherche dans la section auteurs et si non trouvé, recherche dans toute la page
        self.emails = self.findEmails(section_auteurs)

        if not self.emails:
            self.emails = self.findEmails(page)

        # Si ce caractère est trouvé, les auteurs sont sur une seule ligne
        pos_asterisk = section_auteurs.find("∗")

        if pos_asterisk != -1:
            self.auteurs = [section_auteurs[:pos_asterisk]]
            return

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
                result = section_auteurs.split(mail)
                auteurs.append(result[0].split("\n")[0].strip())

                pos_mail = section_auteurs.find(mail)
                section_auteurs = section_auteurs[pos_mail + len(mail):].strip()

        # On ne garde que les informations pertinentes
        for i in range(len(auteurs)):
            if len(auteurs[i]) > 0 and auteurs[i][-1] == ",":
                auteurs[i] = auteurs[i][:-1].strip()

            if auteurs[i] not in ["", "."] and "@" not in auteurs[i]:
                self.auteurs.append(auteurs[i])

        # Si la liste des auteurs est vide, cela veut dire qu'aucun mail a été trouvé
        # On parcourt le texte en enlevant les caractères vides et on garde le seul auteur
        if not self.auteurs:
            auteurs = page[pos_titre + len(self.titre): pos_abstract].split("\n")
            for aut in auteurs:
                if aut == "":
                    auteurs.remove(aut)

            self.auteurs.append(auteurs[0].strip())

        self.replaceAccent()

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

        elif taille_parties == 2:
            for elt in parties_tries:
                self.titre += elt

            return

        elif len(parties_tries) > 10:
            self.titre += parties_tries[0]
            if parties_tries[0][-1] == "\n":
                self.titre += parties_tries[1]
            return

        else:
            self.titre = ""
            self.getTitle(minimum_y - 10, maximum_y - 10)

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

            # Position des mots clefs
            pos_abstract = max(content_copy.find("abstract"), content_copy.find("bstract") - 1)
            pos_introduction = max(content_copy.find("introduction"), content_copy.find("ntroduction") - 1)
            pos_keywords = max(content_copy.find("keywords"), content_copy.find("eywords") - 1)
            pos_index_terms = max(content_copy.find("index terms"), content_copy.find("ndex terms") - 1)

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

    def writeValueInFile(self, typeOutputFile: str) -> None:
        """
        Écrit dans un fichier txt l'analyse du pdf

        :return: None
        """
        if self.directoryTxtFile == "":
            file = f"{self.pathToFile}{self.nomFichier[:-4]}.txt"

        else:
            file = f"{self.directoryTxtFile}{self.nomFichier[:-4]}.txt"

        with open(file, "w") as f:
            if typeOutputFile == "-t":
                self.getTitle()
                self.getAbstract()
                self.getAuthor()

                f.write(f"Nom du fichier pdf : {self.nomFichier}\n")
                f.write("\nTitre :\n")
                f.write(f"    {self.titre}\n\n")

                f.write("Auteurs :\n")
                for aut in self.auteurs:
                    f.write(f"    {aut}\n")

                for mail in self.emails:
                    f.write(f"    {mail}\n")

                f.write("\nAbstract :\n")

                f.write(f"    {self.abstract}\n")


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

        else:
            last_slash = pathToFile.rfind("/")

            chemin = pathToFile[:last_slash + 1]
            nom = pathToFile[last_slash + 1:]

            parser = Parser(chemin, nom)

            parser.writeValueInFile(argv)

    except Exception as e:
        print(traceback.format_exc())
        print("main.py -outputfile [/path/to/the/file.pdf, /path/to/the/dir/]")
        print("outputfile : -t text")
        print("             -x xml")
