import PyPDF2
import shutil
import sys
import os


class Parser:
    pathToFile = ""
    nomFichier = ""
    directoryTxtFile = ""
    pdfReader = PyPDF2.PdfReader

    def __init__(self, path: str, nomFichier: str, directoryTxtFile: str = None):
        self.pathToFile = path
        self.nomFichier = nomFichier

        if not self.isPDFFile(self.pathToFile + self.nomFichier):
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

    def getAuthor(self) -> list | str:
        """
        Renvoi la liste des auteurs

        :return: List des auteurs
        """
        auteurs = self.pdfReader.metadata.author

        # Soit les auteurs sont dans les méta données
        if auteurs is not None and len(auteurs) > 0:
            auteurs = auteurs.split(";")

            # Enlève les espaces au début et à la fin
            for i in range(len(auteurs)):
                if len(auteurs[i]) > 1:
                    if auteurs[i][0] == " ":
                        auteurs[i] = auteurs[i][1:]

                    if auteurs[i][-1] == " ":
                        auteurs[i] = auteurs[i][:-1]

            return auteurs

        else:
            content = self.pdfReader.pages[0].extract_text()

            # On enlève le titre
            content = content[content.find("\n") + 1:]

            # On ne garde que la ligne des auteurs
            content = content[:content.find("\n")]

            return content

    def getTitle(self) -> str | None:
        """
        Renvoie le titre du pdf

        :return: Titre
        """
        titre = self.pdfReader.metadata.title

        if titre is None:
            content = self.pdfReader.pages[0].extract_text()
            return content[:content.find("\n")]

        return titre

    def getAbstract(self) -> str | None:
        """
        Renvoie l'abstract du pdf

        :return: String ou None si non trouvée
        """
        numero_page = 0
        number_of_pages = len(self.pdfReader.pages)

        # Recherche l'abstract dans le fichier
        while numero_page < number_of_pages:
            page = self.pdfReader.pages[numero_page]

            # Récupération du texte
            content = page.extract_text()

            # Position des mots clefs
            pos_abstract = content.find("Abstract")
            pos_introduction = content.find("Introduction")

            # Si trouvé, alors on peut renvoyer l'abstract
            if pos_abstract != -1 and pos_introduction != -1:
                return content[pos_abstract + len("Abstract") + 1:pos_introduction - 2]

            # Sinon absence du mot abstract
            elif pos_abstract == -1 and pos_introduction != -1:

                dernier_point = content[:pos_introduction].rfind(".")

                i = 0
                for i in range(dernier_point, 1, -1):
                    if ord(content[i]) < 20:
                        if ord(content[i - 1]) != 45:
                            break

                return content[i + 1:dernier_point]

            numero_page += 1

    def writeValueInFile(self) -> None:
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
            f.write(f"Nom du fichier pdf : {self.nomFichier}\n")
            f.write("\nTitre :\n")
            f.write(f"    {self.getTitle()}\n\n")

            f.write("Auteurs :\n")
            auteurs = self.getAuthor()

            if type(auteurs) is str:
                f.write(f"    {auteurs}\n")
            else:
                for auteur in auteurs:
                    f.write(f"    {auteur}\n")

            f.write("\nAbstract :\n")

            abstract = self.getAbstract()
            if abstract is not None:
                pos_backslash = abstract.find("\n")

                if len(abstract) < len_max:
                    f.write(f"    {abstract}\n")

                elif pos_backslash < len_max:
                    f.write(f"    {abstract[:pos_backslash]} ...\n")

                else:
                    f.write(f"    {abstract[:abstract[:len_max].rfind(' ')]} ...\n")

            else:
                f.write("Pas d'abstract\n")


if __name__ == '__main__':
    pathToFile = sys.argv[1]

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
                    message = """
                    Impossible de supprimer le dossier analyse_pdf
                    Ce dossier est nécessaire pour la bonne exécution du programme
                    """

                    raise Exception(message)

        # Création du dossier
        os.makedirs(nomDossier)

        for element in os.listdir(pathToFile):
            if Parser.isPDFFile(pathToFile + element):
                Parser(pathToFile, element, nomDossier).writeValueInFile()

    else:
        last_slash = pathToFile.rfind("/")

        chemin = pathToFile[:last_slash + 1]
        nom = pathToFile[last_slash + 1:]

        parser = Parser(chemin, nom)

        parser.writeValueInFile()
