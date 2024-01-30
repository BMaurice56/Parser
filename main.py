import os
import PyPDF2


def checkPDFFile(nomFichier: str) -> None:
    """
    Vérifie si le nom de fichier fourni est bien un pdf
    """
    if not os.path.exists(nomFichier):
        raise FileNotFoundError("Le fichier n'existe pas ")

    if not os.path.isfile(nomFichier) or nomFichier[-4:] != ".pdf":
        raise FileExistsError(f"{nomFichier} n'est pas un fichier .pdf")


if __name__ == '__main__':
    file = "/home/benoit/Documents/cours/Parser/Corpus_2022/Boudin-Torres-2006.pdf"

    checkPDFFile(file)

    # createTxtFileFromPdf(file)

    # print(openTXTFile())

    pdfFileObj = open(file, 'rb')

    # creating a pdf reader object
    pdfReader = PyPDF2.PdfReader(pdfFileObj)

    print(pdfReader.metadata)
