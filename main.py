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
    numbers_last_char = previous_number_last_char = 0

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

    def getAuthor(self) -> None:
        """
        Renvoi la liste des auteurs

        :return: List des auteurs
        """
        self.auteurs = ""

        page = self.pdfReader.pages[0].extract_text()

        self.getTitle()
        self.getAbstract()

        # Position des éléments dans le texte
        pos_titre = page.find(self.titre)
        pos_abstract = page.find(self.abstract)

        # On garde que la section correspondant aux auteurs
        self.auteurs = page[pos_titre + len(self.titre): pos_abstract]

        # Récupération des emails
        self.emails = re.findall(r"[a-z0-9.\-+_]+@[a-z0-9.\-+_]+\.[a-z]+", self.auteurs)

        # Enlèvement des mots clefs
        if "Abstract" in self.auteurs.strip():
            self.auteurs = self.auteurs[:self.auteurs.find("Abstract") - 1].strip()

        # Enlèvement des caractères spéciaux
        for string in ["/natural", "/flat"]:
            if string in self.auteurs:
                self.auteurs = self.auteurs.replace(string, " ")

        auteurs = []

        if len(self.emails) <= 1:
            auteurs.append(self.auteurs.split("\n")[0])

        else:
            for mail in self.emails:
                result = self.auteurs.split(mail)
                auteurs.append(result[0].split("\n")[0].strip())

                pos_mail = self.auteurs.find(mail)
                self.auteurs = self.auteurs[pos_mail + len(mail):]

        self.auteurs = []
        for i in range(len(auteurs)):
            if len(auteurs[i]) > 0 and auteurs[i][-1] == ",":
                auteurs[i] = auteurs[i][:-1].strip()

            if auteurs[i] != "":
                self.auteurs.append(auteurs[i])

        if not self.auteurs:
            auteurs = page[pos_titre + len(self.titre): pos_abstract].split("\n")
            for aut in auteurs:
                if aut == "":
                    auteurs.remove(aut)

            self.auteurs.append(auteurs[0].strip())

        for i in range(len(self.auteurs)):
            self.auteurs[i] = self.auteurs[i].replace("´e", "é").strip()
            self.auteurs[i] = self.auteurs[i].replace("`e", "è")

        # print(self.auteurs)
        # print(self.emails)

    def getTitle(self, minimum_y=650) -> None:
        """
        Renvoie le titre du pdf

        :param minimum_y position minimal en y
        :return: Titre
        """
        self.titre = ""

        page = self.pdfReader.pages[0]

        parts = []

        def visitor_body(text, cm, tm, fontDict, fontSize):
            if text != "" and text != " " and text != "\n":
                y = tm[5]
                if minimum_y < y < 750:
                    parts.append(text)

        # Extraction des premières lignes
        page.extract_text(visitor_text=visitor_body)

        if len(parts) > 0:
            i = 0
            while parts[i][-1] == "\n":
                self.titre += parts[0]
                i += 1

            self.titre += parts[i]

            # Si on n'a pas récupéré la deuxième ligne du titre, on augmente la fenêtre
            if self.titre[-1] == "\n":
                self.getTitle(minimum_y - 10)

        else:
            self.getTitle(minimum_y - 10)

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

            # Si trouvé, alors on peut renvoyer l'abstract
            if pos_abstract != -1 and pos_introduction != -1:
                swift = 1
                if content[pos_abstract + len("Abstract") + swift] in [" ", "\n", "-", "—"]:
                    swift += 1

                self.abstract = content[pos_abstract + len("Abstract") + swift:pos_introduction - 2]
                break

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

            numero_page += 1

    def writeValueInFile(self, typeOutputFile: str) -> None:
        """
        Écrit dans un fichier txt l'analyse du pdf

        :return: None
        """
        len_max = 50
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
        print(e.__str__())
        print("main.py -outputfile [/path/to/the/file.pdf, /path/to/the/dir/]")
        print("outputfile : -t text")
        print("             -x xml")
