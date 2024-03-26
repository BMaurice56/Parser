import Levenshtein
import affichage
import re
import os


class TextComparer:
    """
    -Test si le contenu des txt créé par la Parser.py sont corrects
    """

    def __init__(self, res_attendu_path: str, type_file: str):
        """
        Constructeur

        :param res_attendu_path: Emplacement du fichier des solutions
        :param type_file: Type de fichier à analyser (-t ou -x)
        """
        self.res_attendu_path = res_attendu_path
        self.type_file = type_file

        with open(self.res_attendu_path, "r") as f:
            self.text = f.read()

    def extract_text_txt_related_to_pdf(self, txt_filename: str, keyword: str) -> str:
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
        if keyword.lower() in self.text.lower():
            # Position du mot clef dans le texte
            keyword_start = self.text.lower().find(keyword.lower())

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
            print(f"Le mot clé '{keyword}' n'a pas été trouvé dans {txt_filename}.")

    def extract_text_xml_related_to_pdf(self, xml_filename: str, keyword: str) -> str:
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
        if keyword.lower() in self.text.lower():
            # Position du mot clef dans le texte
            keyword_start = self.text.lower().find(keyword.lower())

            self.text = self.text.replace('<article>', '').replace('</article>', '')

            # Trouve l'occurrence qui correspond au premier nom de fichier présent dans le xml des solutions attendues
            next_filename_match = re.search("<preamble>", self.text)

            if next_filename_match:
                # Indique à combien de caractères se trouve la fin du mot cle dans le xml des solutions attendues
                snippet_end = keyword_start + next_filename_match.end()
            else:
                snippet_end = len(self.text)

            # Trouve le prochain nom de fichier, en part du mot clé sélectionné dans le xml des solutions attendues
            next_filename_match = re.search("<preamble>", self.text[snippet_end:])

            if next_filename_match:
                # Indique à combien de caractères se trouve le prochain nom de fichier dans le xml des solutions
                # attendues
                snippet_end += next_filename_match.start()
            else:
                snippet_end = len(self.text)

            # Prend le max entre 0 et la valeur du début du mot clé
            snippet_start = max(0, keyword_start)

            # Retourne le text qui se trouve entre le mot clé et la prochaine nom de fichier
            return self.text[snippet_start:snippet_end]

        else:
            print(f"Le mot clé '{keyword}' n'a pas été trouvé dans {xml_filename}.")

    @staticmethod
    def extract_element_xml(xml_filename: str) -> tuple[str, str, str, str, str, str, str, str]:

        start_title = xml_filename.find('<titre>')

        end_title = xml_filename.find('<auteurs>')

        title = xml_filename[start_title:end_title]

        start_autor = xml_filename.find('<auteurs>')

        end_autor = xml_filename.find('<abstract>')

        autor = xml_filename[start_autor:end_autor]

        start_abstract = xml_filename.find('<abstract>')

        end_abstract = xml_filename.find('<introduction>')

        abstract = xml_filename[start_abstract:end_abstract]

        start_introduction = xml_filename.find('<introduction>')

        end_introduction = xml_filename.find('<corps>')

        introduction = xml_filename[start_introduction:end_introduction]

        start_corps = xml_filename.find('<corps>')

        end_corps = xml_filename.find('<conclusion>')

        corps = xml_filename[start_corps:end_corps]

        start_conclusion = xml_filename.find('<conclusion>')

        end_conclusion = xml_filename.find('<discussion>')

        conclusion = xml_filename[start_conclusion:end_conclusion]

        start_discussion = xml_filename.find('<discussion>')

        end_discussion = xml_filename.find('<bibliographie>')

        discussion = xml_filename[start_discussion:end_discussion]

        start_bibliographie = xml_filename.find('<bibliographie>')

        end_bibliographie = xml_filename.find('</bibliographie>')

        bibliographie = xml_filename[start_bibliographie:end_bibliographie] + "</bibliographie>"

        # print(title, autor, abstract, introduction, corps, conclusion, discussion, bibliographie)

        return title, autor, abstract, introduction, corps, conclusion, discussion, bibliographie

    def compare_files(self, directory_path: str) -> dict:
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

        return {}

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
                    found_text = self.extract_text_txt_related_to_pdf(self.res_attendu_path, title)

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
                    # Indique à combien de caractères se trouve le début le titre du xml
                    start_index = xml_file.find('<preamble>') + 1
                    # Indique à combien de caractères se trouve la fin du titre du xml
                    end_index = xml_file.find('</preamble>') - 3
                    # Permet de construire correctement le titre
                    title = '<preamble>' + xml_file[start_index:end_index] + '.pdf</preamble>'

                    # Trouve le texte dans le xml des solutions attendues qui correspond au titre du fichier sélectionné
                    # dans analyse_pdf
                    found_text = self.extract_text_xml_related_to_pdf(self.res_attendu_path, title)

                    # Enlève la balise <article>
                    file_content = file.read().replace('<article>', '').replace('</article>', '')


                    start_title = found_text.find('<titre>')

                    end_title = found_text.find('<auteurs>')

                    title_sol = found_text[start_title:end_title]

                    start_autor = found_text.find('<auteurs>')

                    end_autor = found_text.find('<abstract>')

                    autor_sol = found_text[start_autor:end_autor]

                    start_abstract = found_text.find('<abstract>')

                    end_abstract = found_text.find('<introduction>')

                    abstract_sol = found_text[start_abstract:end_abstract]

                    start_introduction = found_text.find('<introduction>')

                    end_introduction = found_text.find('<corps>')

                    introduction_sol = found_text[start_introduction:end_introduction]

                    start_corps = found_text.find('<corps>')

                    end_corps = found_text.find('<conclusion>')

                    corps_sol = found_text[start_corps:end_corps]

                    start_conclusion = found_text.find('<conclusion>')

                    end_conclusion = found_text.find('<discussion>')

                    conclusion_sol = found_text[start_conclusion:end_conclusion]

                    start_discussion = found_text.find('<discussion>')

                    end_discussion = found_text.find('<bibliographie>')

                    discussion_sol = found_text[start_discussion:end_discussion]

                    start_bibliographie = found_text.find('<bibliographie>')

                    end_bibliographie = found_text.find('</bibliographie>')

                    bibliographie_sol = found_text[start_bibliographie:end_bibliographie] + "</bibliographie>"

                    start_title = file_content.find('<titre>')

                    end_title = file_content.find('<auteurs>')

                    title = file_content[start_title:end_title]

                    start_autor = file_content.find('<auteurs>')

                    end_autor = file_content.find('<abstract>')

                    autor = file_content[start_autor:end_autor]

                    start_abstract = file_content.find('<abstract>')

                    end_abstract = file_content.find('<introduction>')

                    abstract = file_content[start_abstract:end_abstract]

                    start_introduction = file_content.find('<introduction>')

                    end_introduction = file_content.find('<corps>')

                    introduction = file_content[start_introduction:end_introduction]

                    start_corps = file_content.find('<corps>')

                    end_corps = file_content.find('<conclusion>')

                    corps = file_content[start_corps:end_corps]

                    start_conclusion = file_content.find('<conclusion>')

                    end_conclusion = file_content.find('<discussion>')

                    conclusion = file_content[start_conclusion:end_conclusion]

                    start_discussion = file_content.find('<discussion>')

                    end_discussion = file_content.find('<bibliographie>')

                    discussion = file_content[start_discussion:end_discussion]

                    start_bibliographie = file_content.find('<bibliographie>')

                    end_bibliographie = file_content.find('</bibliographie>')

                    bibliographie = file_content[start_bibliographie:end_bibliographie] + "</bibliographie>"

                    percentage_title = self.levenshtein_distance_percentage(title, title_sol)

                    percentage_autor = self.levenshtein_distance_percentage(autor, autor_sol)

                    percentage_abstract = self.levenshtein_distance_percentage(abstract, abstract_sol)

                    percentage_introduction = self.levenshtein_distance_percentage(introduction, introduction_sol)

                    percentage_corps = self.levenshtein_distance_percentage(corps, corps_sol)

                    percentage_conclusion = self.levenshtein_distance_percentage(conclusion, conclusion_sol)

                    percentage_discussion = self.levenshtein_distance_percentage(discussion, discussion_sol)

                    percentage_bibliographie = self.levenshtein_distance_percentage(bibliographie, bibliographie_sol)

                    if found_text is not None:
                        # Appelle de la methode qui retourne un pourcentage qui correspond à la distance de levenshtein
                        percentage = self.levenshtein_distance_percentage(file_content, found_text)

                        # Affiche le pourcentage
                        affichage.afficher_barre_pourcentage(percentage)
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

        print(percentage)

        return percentage
