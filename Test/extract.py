import Levenshtein
import affichage
import re
import os


class TextComparer:
    """
    -Test si le contenu des txt créé par la Parser.py sont corrects
    """

    def __init__(self, chemin_fichier_solution: str, type_file: str):
        """
        Constructeur

        :param chemin_fichier_solution: Emplacement du fichier des solutions
        :param type_file: Type de fichier à analyser (-t ou -x)
        """
        self.chemin_fichier_solution = chemin_fichier_solution
        self.type_file = type_file

        with open(self.chemin_fichier_solution, "r") as f:
            self.text = f.read().replace('<article>', '').replace('</article>', '')

    def extract_text_txt_related_to_pdf(self, txt_filename: str, nom_fichier: str) -> str:
        """
        Méthode qui trouve et affiche un extrait de texte contenant un mot-clé dans le fichier
        contenant les résultats attendus.

        Args :
        :param: txt_filename Chemin du fichier contenant les résultats attendus
        :param: keyword Mot-clé à rechercher

        Returns :
        :return: Extraction du résultat attendue correspondant au mot cle entre en paramètre.
        """
        # Vérifie si la clef est présente dans le texte
        if nom_fichier.lower() in self.text.lower():
            # Position du mot clef dans le texte
            keyword_start = self.text.lower().find(nom_fichier.lower())

            # Trouve l'occurrence qui correspond au premier nom de fichier présent dans le txt des solutions attendues
            next_filename_match = re.search(r"Nom du fichier pdf : (.+?)\n", self.text)

            if next_filename_match:
                # Indique à combien de caractères se trouve la fin du mot cle dans le txt des solutions attendues
                snippet_end = keyword_start + next_filename_match.end()
            else:
                snippet_end = len(self.text)

            # Trouve le prochain nom de fichier, en part du mot clé sélectionné dans le txt des solutions attendues
            next_filename_match = re.search(r"Nom du fichier pdf : (.+?)\n", self.text[snippet_end:])

            if next_filename_match:
                # Indique à combien de caractères se trouve le prochain nom de fichier dans le txt des solutions
                # attendues
                snippet_end += next_filename_match.start()
            else:
                snippet_end = len(self.text)

            # Prend le max entre 0 et la valeur du début du mot clé
            snippet_start = max(0, keyword_start)

            # Retourne le text qui se trouve entre le mot clé et la prochaine nom de fichier
            return self.text[snippet_start:snippet_end]

        else:
            print(f"Le mot clé '{nom_fichier}' n'a pas été trouvé dans {txt_filename}.")

    def extract_text_xml_related_to_pdf(self, nom_fichier_preamble: str) -> str:
        """
        Méthode qui trouve et affiche un extrait de texte contenant un mot-clé dans le fichier
        contenant les résultats attendus.

        Args :
        :param: nom_fichier_preamble Mot-clé à rechercher

        Returns :
        :return: Extraction du résultat attendue correspondant au mot cle entre en paramètre.
        """
        # Position du nom du fichier pdf dans celui des solutions
        position_nom = self.text.find(nom_fichier_preamble)

        if position_nom != -1:
            second_file_solution = self.text.find("<preamble>", position_nom + len(nom_fichier_preamble))

            # Retourne le text qui se trouve entre le mot clé et la prochaine nom de fichier
            return self.text[position_nom:second_file_solution]

        else:
            print(f"Le mot clé '{nom_fichier_preamble}' n'a pas été trouvé dans {self.chemin_fichier_solution}.")

    def percentage_difference_each_section_xml(self, solution: str, file_content: str) -> dict:
        """
        Renvoi un dictionnaire des différences en pourcentage de chaque section

        :param solution: solution à avoir
        :param file_content: contenu généré par le parser
        :return: dictionnaire des pourcentages
        """
        elements = ["titre", "auteurs", "abstract", "introduction", "corps", "conclusion", "discussion",
                    "bibliographie", "/bibliographie"]

        # Dictionnaire contenant la position de chaque titre de section
        pos_element_solution = {}
        pos_element_file_content = {}
        previous_pos_solution = 0
        previous_pos_file_content = 0

        for elt in elements:
            previous_pos_solution = solution.find(elt, previous_pos_solution)
            previous_pos_file_content = file_content.find(elt, previous_pos_file_content)

            pos_element_solution[elt] = previous_pos_solution
            pos_element_file_content[elt] = previous_pos_file_content
        ######################################################################

        results = {}
        for i, elt in enumerate(elements):
            if i == len(elements) - 1:
                break
            else:
                # Récupération des deux sections à comparer
                texte1 = solution[pos_element_solution[elt]:pos_element_solution[elements[i + 1]]]
                texte2 = file_content[pos_element_file_content[elt]: pos_element_file_content[elements[i + 1]]]

                results[elt] = self.levenshtein_distance_percentage(texte1, texte2)

        return results

    def compare_files(self, directory_path: str) -> None:
        """
        Méthode qui compare les fichiers du résultat attendu avec celui du résultat obtenu.

        Args :
        :param: directory_path Chemin du répertoire contenant les fichiers .txt ou xml créer par le parser.

        Returns :
        :return: None
        """
        if self.type_file == "-t":
            self.compares_txt_files(directory_path)

        elif self.type_file == "-x":
            self.compares_xml_files(directory_path)

    def compares_txt_files(self, directory_path: str) -> None:
        """
        Compare les fichiers txt du résultat attendu avec celui du résultat obtenu.

        Args :
        :param: directory_path Chemin du répertoire contenant les fichiers .txt ou xml créer par le parser.

        Returns :
        :return: None
        """
        try:
            # Ouvre un fichier contenu dans analyse_pdf que s'il est au format txt
            txt_files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]

            for txt_file in txt_files:
                print(f"Analyse du fichier : {txt_file}")
                # Chemin du fichier
                file_path = os.path.join(directory_path, txt_file)

                # Ouvre le fichier sélectionné
                with open(file_path, encoding='utf-8') as file:
                    # Titre du fichier
                    title = file.readline().strip()

                    # Trouve le texte dans le txt des solutions attendues qui correspond au titre du fichier sélectionné
                    # dans analyse_pdf
                    found_text = self.extract_text_txt_related_to_pdf(self.chemin_fichier_solution, title)

                    if found_text is not None:
                        # Appelle de la methode qui retourne un pourcentage qui correspond à la distance de levenshtein
                        percentage = self.levenshtein_distance_percentage(file.read(), found_text)
                        # Affiche le pourcentage
                        affichage.afficher_barre_pourcentage(percentage)
                    else:
                        print(f"Ignorer {txt_file} car le mot-clé n'a pas été trouvé.")
                    print()

        except Exception as e:
            raise Exception(f"Erreur lors de la lecture des fichiers : {e}")

    def compares_xml_files(self, directory_path: str) -> None:
        """
        Compare les fichiers xml du résultat attendu avec celui du résultat obtenu.

        Args :
        :param: directory_path Chemin du répertoire contenant les fichiers .txt ou xml créer par le parser.

        Returns :
        :return: None
        """
        try:
            # Ouvre un fichier contenu dans analyse_pdf que s'il est au format xml
            xml_files = [f for f in os.listdir(directory_path) if f.endswith('.xml')]

            for xml_file in xml_files:
                print(f"Analyse du fichier : {xml_file}")
                # Chemin du fichier
                file_path = os.path.join(directory_path, xml_file)

                # Ouvre le fichier sélectionné
                with open(file_path, 'r', encoding='utf-8') as file:
                    # Contenu du fichier
                    file_content = file.read().replace('<article>', '').replace('</article>', '')

                    # nom du fichier
                    nom_fichier = f"<preamble>{xml_file[:-4]}.pdf</preamble>"

                    # Récupère la solution correspondant au pdf actuel
                    found_text = self.extract_text_xml_related_to_pdf(nom_fichier)

                    # Dictionnaire des pourcentages
                    percentage_dict_element = self.percentage_difference_each_section_xml(found_text, file_content)

                    if found_text is not None:
                        affichage.afficher_barre_pourcentage(percentage_dict_element)
                    else:
                        print(f"Ignorer {xml_file} car le mot-clé n'a pas été trouvé.")

                    print()

        except Exception as e:
            raise Exception(f"Erreur lors de la lecture des fichiers : {e}")

    def levenshtein_distance_percentage(self, s1: str, s2: str) -> float:
        """
        Méthode qui traduit la distance de Levenshtein en pourcentage de ressemblance.

        Args :
        - s1 (str) : Première chaîne de caractères.
        - s2 (str) : Deuxième chaîne de caractères.

        Returns :
        - float : Pourcentage de ressemblance entre les deux chaînes.
        """
        if len(s1) < len(s2):
            return self.levenshtein_distance_percentage(s2, s1)

        # Variable qui prend le maximum entre la taille du texte du fichier analyse_pdf selection et celui du texte des
        # solutions attendues
        max_length = max(len(s1), len(s2))

        if max_length == 0:
            return 100

        # Appelle de la distance de Levenshtein
        distance = Levenshtein.distance(s1, s2)

        # Normalise la distance en la divisant par la taille maximum sélectionnée
        normalized_distance = distance / max_length

        # Change la distance en pourcentage
        percentage = (1 - normalized_distance) * 100

        return percentage
