import fitz  # PyMuPDF
import re
import os
import Levenshtein

#methode qui permet d'extraire les txt du dosier analyse.pdf
def read_text_files_in_directory(directory_path):
    try:
        # Liste tous les fichiers dans le répertoire avec l'extension .txt
        text_files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]

        # Initialiser un dictionnaire pour stocker le contenu de chaque fichier
        text_contents = {}

        for text_file in text_files:
            file_path = os.path.join(directory_path, text_file)

            print(file_path)

            # Ouvrir et lire le contenu du fichier texte
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                text_contents[text_file] = content
                print(text_contents)

        return text_contents
    except Exception as e:
        return f"Erreur lors de la lecture des fichiers : {e}"


#methode qui permet d'extraire le texte du txt resAttendu.txt
def extract_text_from_pdf(pdf_filename):
    try:
        doc = fitz.open(pdf_filename)
        text = ""
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text()
        return text
    except Exception as e:
        return f"Erreur lors de l'extraction du texte : {e}"


#methode qui permet d'extraire du fichier resAttendu.txt un txt en entrant le pdf en question en parametre
def find_and_display_keyword(pdf_filename, keyword):
    extracted_text = extract_text_from_pdf(pdf_filename)

    if keyword.lower() in extracted_text.lower():

        # Trouver la position du mot clé
        keyword_start = extracted_text.lower().find(keyword.lower())

        # Trouver le prochain "Nom du fichier pdf"
        next_filename_match = re.search(r"Nom du fichier pdf : (.+?)\n", extracted_text)

        if next_filename_match:
            snippet_end = keyword_start + next_filename_match.end()
        else:
            # Si le prochain "Nom du fichier pdf" n'est pas trouvé, utiliser la fin du texte
            snippet_end = len(extracted_text)

        # Trouver le prochain "Nom du fichier pdf" après le snippet_end jusqu'à la fin du texte
        next_filename_match = re.search(r"Nom du fichier pdf : (.+?)\n", extracted_text[snippet_end:])

        if next_filename_match:
            snippet_end += next_filename_match.start()
        else:
            # Si le prochain "Nom du fichier pdf" n'est pas trouvé, utiliser la fin du texte
            snippet_end = len(extracted_text)

        snippet_start = max(0, keyword_start)

        return extracted_text[snippet_start:snippet_end]
    else:
        print(f"Le mot clé '{keyword}' n'a pas été trouvé dans {pdf_filename}.")


#Permet de prendre les 2 résultats et de les comparer en appelant la fonction levenshtein_distance_percentage(s1, s2)
def compare_files(directory_path):
    try:
        resAttendu_path = "/home/benjamin/Documents/L3/Semestre_2/Projet_de_developpement/pythonProject/resAttendu.txt"
        text_files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]

        for text_file in text_files:
            print(f"Analyse du fichier : {text_file}")
            file_path = os.path.join(directory_path, text_file)

            with open(file_path, 'r', encoding='utf-8') as file:
                keyword = file.readline().strip()
                content = file.read()

                found_text = find_and_display_keyword(resAttendu_path, keyword)

                if found_text is not None:
                    # Appliquer la fonction levenshtein_distance
                    percentage = levenshtein_distance_percentage(content, found_text)

                    # Afficher les résultats pour le fichier en cours
                    print(f"{text_file}: {percentage:.2f}%")
                else:
                    print(f"Ignorer {text_file} car le mot-clé n'a pas été trouvé.")
                print()

    except Exception as e:
        print(f"Erreur lors de la lecture des fichiers : {e}")


#Traduit la distance de levenshtein en pourcentage
def levenshtein_distance_percentage(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance_percentage(s2, s1)

    max_length = max(len(s1), len(s2))

    if max_length == 0:
        return 100  # Les deux chaînes sont vides, la distance est nulle

    distance = Levenshtein.distance(s1, s2)

    # Utilisation de la distance maximale possible pour normaliser
    normalized_distance = distance / max_length

    # Calcul du pourcentage de ressemblance
    percentage = (1 - normalized_distance) * 100

    return percentage

if __name__ == "__main__":
    folder_path = "/home/benjamin/Documents/L3/Semestre_2/Projet_de_developpement/pythonProject/Corpus_2022/analyse_pdf"
    texts = compare_files(folder_path)


