import os
import re

class Extract :
    def read_text_file(file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return content
        except Exception as e:
            return f"Une erreur s'est produite lors de la lecture du fichier : {str(e)}"

    def getList(path: str):


        return os.listdir(path)


    def extract_information(path):
        text = Extract.read_text_file(path)

        result = {}

        # Extraction du nom du fichier pdf
        file_match = re.search(r'Nom du fichier pdf : (.+)', text)
        if file_match:
            result['Nom du fichier pdf'] = file_match.group(1).strip()

        # Extraction du titre
        title_match = re.search(r'Titre :\s+(.+)', text)
        if title_match:
            result['Titre'] = title_match.group(1).strip()

        # Extraction des auteurs
        i_t = text.find("Auteurs :") + 10

        if i_t >= 0:
            auteurs_t = ""
            while i_t < len(text) - 1 and text[i_t:i_t + 2] != '\n\n':
                auteurs_t += text[i_t]
                i_t += 1

            words = auteurs_t.split('\n')
            filtered_words = [word.strip() for word in words if word.strip() != '']
            auteurs = ' '.join(filtered_words)
            result['Auteurs'] = auteurs




        # Extraction de l'abstract
        abstract_match = re.search(r'Abstract :\s+(.+)', text)
        if abstract_match:
            result['Abstract'] = abstract_match.group(1).strip()

        return result