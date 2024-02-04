import os
import sys

import PyPDF2


def checkPDFFile(nomFichier: str) -> None:
    """
    Vérifie si le nom de fichier fourni est bien un pdf

    :param nomFichier: Nom du fichier
    :return: None
    """
    if not os.path.exists(nomFichier):
        raise FileNotFoundError("Le fichier n'existe pas ")

    if not os.path.isfile(nomFichier) or (nomFichier[-4:] != ".pdf"):
        raise FileExistsError(f"{nomFichier} n'est pas un fichier .pdf")


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


def getIntroduction(reader: PyPDF2.PdfReader) -> str | None:
    """
    Renvoi l'introduction du pdf

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

        # Position du mot clef
        pos_introduction = content.find("Introduction")

        if pos_introduction != -1:
            return content[pos_introduction + len("Introduction") + 1:pos_introduction + 200]

        numero_page += 1

    return None


def getCorps(reader: PyPDF2.PdfReader) -> str | None:
    """
    Renvoie le corps du pdf

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
        pos_2 = content.find("2")

        # Tant qu'on trouve un 2
        while pos_2 != -1:
            # Si on trouve le 2 du nom du chapitre, alors on peut récupérer le corps
            if pos_2 != -1 and content[pos_2 - 1] == "\n" and content[pos_2 + 1] == " ":

                # Recherche du deuxième \n du début du corps
                pos_backslash = pos_2 + 1

                for i in range(len(content[pos_backslash:])):
                    # Si on le trouve, on renvoie les 200 premiers caractères du corps
                    if content[pos_backslash + i] == "\n":
                        pos_backslash = pos_backslash + i + 1
                        return content[pos_backslash:pos_backslash + 200]

            content = content[pos_2 + 1:]
            pos_2 = content.find("2")

        numero_page += 1


def affichageValeurs(reader: PyPDF2.PdfReader) -> None:
    """
    Affiche les différentes informations à l'écran

    :param reader: Objet de lecture
    :return: None
    """
    len_max = 50

    print("Titre :")
    print(f"    {getTitle(reader)}")

    print("\nAuteurs :")
    for auteur in getAuthor(reader):
        print(f"    {auteur}")

    print("\nAbstract :")

    abstract = getAbstract(reader)
    pos_backslash = abstract.find("\n")

    if len(abstract) < len_max:
        print(f"    {abstract}")

    elif pos_backslash < len_max:
        print(f"    {abstract[:pos_backslash]} ...")

    else:
        print(f"    {abstract[:abstract[:len_max].rfind(' ')]} ...")

    print("\nIntroduction :")
    intro = getIntroduction(reader)

    pos_backslash = intro.find("\n")

    if len(intro) < len_max:
        print(f"    {intro}")

    elif pos_backslash < len_max:
        print(f"    {intro[:pos_backslash]} ...")

    else:
        print(f"    {intro[:intro[:len_max].rfind(' ')]} ...")

    print("\nCorps :")
    corps = getCorps(reader)

    pos_backslash = corps.find("\n")

    if len(corps) < len_max:
        print(f"    {corps}")

    elif pos_backslash < len_max:
        print(f"    {corps[:pos_backslash]} ...")

    else:
        print(f"    {corps[:corps[:len_max].rfind(' ')]} ...")


if __name__ == '__main__':
    file = sys.argv[1]

    checkPDFFile(file)

    pdfFileObj = open(file, 'rb')

    # creating a pdf reader object
    pdfReader = PyPDF2.PdfReader(pdfFileObj)

    affichageValeurs(pdfReader)
