import os
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


def getAuthor(reader: PyPDF2.PdfReader) -> list:
    """
    Renvoi la liste des auteurs

    :param reader: Objet de lecture
    :return: List des auteurs
    """

    auteurs = reader.metadata["/Author"].__str__().split(";")

    # Enlève les espaces au début et à la fin
    for i in range(len(auteurs)):
        if auteurs[i][0] == " ":
            auteurs[i] = auteurs[i][1:]

        if auteurs[i][-1] == " ":
            auteurs[i] = auteurs[i][:-1]

    return auteurs


def getTitle(reader: PyPDF2.PdfReader) -> str:
    """
    Renvoie le titre du pdf

    :param reader: Objet de lecture
    :return: Titre
    """
    return reader.metadata["/Title"].__str__()


def getAbstract(reader: PyPDF2.PdfReader) -> str:
    """
    Renvoie l'abstract du pdf

    :param reader: Objet de lecture
    :return: String contenue
    """
    numero_page = 0
    number_of_pages = len(reader.pages)

    while numero_page < number_of_pages:
        page = reader.pages[0]

        # Récupération du texte
        content = page.extract_text()

        # Position des mots clefs
        pos_abstract = content.find("Abstract")
        pos_introduction = content.find("Introduction")

        # Si trouvé, alors on peut renvoyer l'abstract
        if pos_abstract != -1 and pos_introduction != -1:
            return content[pos_abstract + len("Abstract") + 1:pos_introduction - 2]

        numero_page += 1


def affichageValeurs(reader: PyPDF2.PdfReader) -> None:
    """
    Affiche les différentes informations à l'écran

    :param reader: Objet de lecture
    :return: None
    """
    len_max = 45

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


if __name__ == '__main__':
    file = "/home/benoit/Documents/cours/Parser/Corpus_2022/Boudin-Torres-2006.pdf"

    checkPDFFile(file)

    pdfFileObj = open(file, 'rb')

    # creating a pdf reader object
    pdfReader = PyPDF2.PdfReader(pdfFileObj)

    affichageValeurs(pdfReader)
