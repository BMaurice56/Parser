import PyPDF2
import time
import sys
import os


def isPDFFile(nomFichier: str) -> bool:
    """
    Vérifie si le nom de fichier fourni est bien un pdf

    :param nomFichier: Nom du fichier
    :return: True ou False
    """
    if not os.path.isfile(nomFichier) or nomFichier[-4:] != ".pdf":
        return False

    return True


def openPDF(nomFichier: str) -> PyPDF2.PdfReader:
    """
    Ouvre le pdf et renvoi l'objet de lecture

    :param nomFichier: Nom du fichier
    :return: Objet de lecture du pdf
    """
    pdfFileObj = open(nomFichier, 'rb')

    return PyPDF2.PdfReader(pdfFileObj)


def getAuthor(reader: PyPDF2.PdfReader) -> list | None:
    """
    Renvoi la liste des auteurs

    :param reader: Objet de lecture
    :return: List des auteurs
    """
    auteurs = reader.metadata.author

    if auteurs is not None:
        auteurs = auteurs.split(";")

        # Enlève les espaces au début et à la fin
        for i in range(len(auteurs)):
            if auteurs[i][0] == " ":
                auteurs[i] = auteurs[i][1:]

            if auteurs[i][-1] == " ":
                auteurs[i] = auteurs[i][:-1]

    return auteurs


def getTitle(reader: PyPDF2.PdfReader) -> str | None:
    """
    Renvoie le titre du pdf

    :param reader: Objet de lecture
    :return: Titre
    """
    return reader.metadata.title


def getAbstract(reader: PyPDF2.PdfReader) -> str | None:
    """
    Renvoie l'abstract du pdf

    :param reader: Objet de lecture
    :return: String ou None si non trouvé
    """
    numero_page = 0
    number_of_pages = len(reader.pages)

    # Recherche l'abstract dans le fichier
    while numero_page < number_of_pages:
        page = reader.pages[numero_page]

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


def writeValueInFile(nameFile: str, pathDir: str, reader: PyPDF2.PdfReader) -> None:
    """
    Écrit dans un fichier txt l'analyse du pdf

    :param nameFile: Nom du fichier
    :param pathDir: Chemin
    :param reader: Objet de lecture
    :return:
    """
    len_max = 50
    file = f"{pathDir}{nameFile[:-4]}.txt"

    with open(file, "w") as f:
        f.write(f"Nom du fichier pdf : {nameFile}\n")
        f.write("\nTitre :\n")
        f.write(f"    {getTitle(reader)}\n\n")

        f.write("Auteurs :\n")
        for auteur in getAuthor(reader):
            f.write(f"    {auteur}\n")

        f.write("\nAbstract :\n")

        abstract = getAbstract(reader)
        pos_backslash = abstract.find("\n")

        if len(abstract) < len_max:
            f.write(f"    {abstract}\n")

        elif pos_backslash < len_max:
            f.write(f"    {abstract[:pos_backslash]} ...\n")

        else:
            f.write(f"    {abstract[:abstract[:len_max].rfind(' ')]} ...\n")


if __name__ == '__main__':
    path = sys.argv[1]

    # Check si dossier ou fichier
    if os.path.isdir(path):
        # Check si / à la fin
        if path[-1] != "/":
            path += "/"

        # Chemin du dossier de sortie
        nomDossier = path + "analyse_pdf/"

        # Si existence du dossier → on le supprime
        if os.path.exists(nomDossier):
            os.rmdir(nomDossier)

        # Création du dossier
        os.makedirs(nomDossier)

        for element in os.listdir(path):
            if isPDFFile(path + element):
                print(element)
            else:
                print("autre fichier")
    else:
        pdfReader = openPDF(path)

        last_slash = path.rfind("/")

        writeValueInFile(path[last_slash + 1:], path[:last_slash + 1], pdfReader)
