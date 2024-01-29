import os

nomFichierTexte = "fichier.txt"


def checkPDFFile(nomFichier: str) -> None:
    """
    Vérifie si le nom de fichier fourni est bien un pdf
    """
    if not os.path.exists(nomFichier):
        raise FileNotFoundError("Le fichier n'existe pas ")

    if not os.path.isfile(nomFichier) or nomFichier[-4:] != ".pdf":
        raise FileExistsError(f"{nomFichier} n'est pas un fichier .pdf")


def createTxtFileFromPdf(nomFichier: str) -> None:
    """
    Crée le fichier texte depuis le fichier pdf
    nomFichier : nom du fichier

    Nom du fichier de sortie → fichier.txt
    """
    checkPDFFile(nomFichier)

    if os.system(f"pdftotext -raw {nomFichier} {nomFichierTexte}") != 0:
        raise OSError("Impossible de transformer le fichier pdf en texte")


def openTXTFile() -> str:
    """
    Ouvre le fichier txt et renvoie son contenu sans caractère inconnu
    :return: Contenu du fichier
    """
    with open(nomFichierTexte, "f") as f:
        content = f.read()

    return content


if __name__ == '__main__':
    file = "/home/benoit/Documents/cours/Parser/Corpus_2022/Boudin-Torres-2006.pdf"
    createTxtFileFromPdf(file)
