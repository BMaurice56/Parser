import PyPDF2
import shutil
import sys
import os


class Parser:
    pdfReader = PyPDF2.PdfReader
    pathToFile = ""
    nomFichier = ""
    directoryTxtFile = ""
    titre = ""
    auteurs = ""
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

    def getAuthor(self) -> str:
        """
        Renvoi la liste des auteurs

        :return: List des auteurs
        """
        metadata = self.pdfReader.metadata.author

        if metadata is not None and metadata != "" and "@" not in metadata:
            return metadata

        page = self.pdfReader.pages[0].extract_text()

        self.getTitle()
        self.getAbstract()

        pos_titre = page.find(self.titre)
        pos_abstract = page.find(self.abstract)

        self.auteurs = page[pos_titre + len(self.titre): pos_abstract]

        if "Abstract" in self.auteurs.strip():
            self.auteurs = self.auteurs[:self.auteurs.find("Abstract") - 1]

        return self.auteurs

    def old_getAuthor(self, minimum_y=530, maximum_y=720, last_char=150) -> str:
        """
        Renvoi la liste des auteurs

        :return: List des auteurs
        """
        metadata = self.pdfReader.metadata.author

        if metadata is not None and metadata != "" and "@" not in metadata:
            return metadata

        page = self.pdfReader.pages[0]

        parts = []

        def visitor_body(text, cm, tm, fontDict, fontSize):
            if text != "" and text != " " and text != "\n":

                y = tm[5]

                # Permet de vérifier si la valeur n'est pas trop basse
                if "/LastChar" in fontDict:
                    if self.previous_number_last_char != fontDict["/LastChar"]:
                        if self.numbers_last_char < 0:
                            self.numbers_last_char = -float("inf")
                        else:
                            self.numbers_last_char = 0

                        self.previous_number_last_char = fontDict["/LastChar"]
                    else:
                        self.numbers_last_char += 1

                    if self.numbers_last_char > 15:
                        raise Exception()

                if minimum_y < y < maximum_y and fontDict["/LastChar"] <= last_char:
                    parts.append(text)

        try:
            page.extract_text(visitor_text=visitor_body)

        except:
            parts.clear()
            last_char = self.previous_number_last_char
            self.numbers_last_char = -float("inf")
            page = self.pdfReader.pages[0]

            page.extract_text(visitor_text=visitor_body)

        # content = page.extract_text()

        # print(content)
        print(parts)

        # Récupère le titre
        if self.titre == "" or self.titre is None:
            self.titre = self.getTitle()

        # Si le titre est présent dans le texte récupéré, on l'enlève
        for elt in parts:
            if elt.strip() in self.titre.strip() or "@" in elt:
                # Si des éléments se trouvent devant le titre, on les enlève
                indice = parts.index(elt)
                if indice != 0:
                    for i in range(indice):
                        parts.pop(0)

                parts.remove(elt)

        print(parts)
        # Si aucun élément n'a été récupérer, on augmente la fenêtre
        if len(parts) == 0:
            self.auteurs = self.old_getAuthor(minimum_y - 10, maximum_y + 10, last_char + 20)

        else:
            for elt2 in parts:
                if "∗" in elt2:
                    break
                if "\n" in elt2:
                    elt2 = elt2[:-1]
                self.auteurs += elt2 + " ; "

            self.auteurs = self.auteurs[:-2]

        return self.auteurs

    def getTitle(self, minimum_y=600) -> str | None:
        """
        Renvoie le titre du pdf

        :param minimum_y position minimal en y
        :return: Titre
        """
        # Vérifie les métadonnées
        self.titre = self.pdfReader.metadata.title

        if self.titre is None or "/" in self.titre:
            self.titre = ""

            page = self.pdfReader.pages[0]

            parts = []

            def visitor_body(text, cm, tm, fontDict, fontSize):
                if text != "" and text != " " and text != "\n":
                    y = tm[5]
                    if minimum_y < y < 700:
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
                    self.titre = self.getTitle(minimum_y - 10)

            else:
                self.titre = self.getTitle(minimum_y - 10)

            return self.titre

        return self.titre

    def getAbstract(self) -> str:
        """
        Renvoie l'abstract du pdf

        :return: String
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
                swift = 1
                if content[pos_abstract + len("Abstract") + swift] in [" ", "\n"]:
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

        return self.abstract

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
            f.write(f"    {self.getAuthor()}\n")

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
                    message = ("\nImpossible de supprimer le dossier analyse_pdf\nCe dossier est nécessaire pour la "
                               "bonne exécution du programme")

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
