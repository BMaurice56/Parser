from src.Utils import Utils
import re


class Mail:
    @staticmethod
    def find_emails(texte: str) -> (list, int):
        """
        Trouve les mails dans le texte donné

        :param texte: texte contenant des mails
        :return: Liste des mails
        """
        emails_copy = []

        # Récupération des emails
        emails = [x.strip() for x in re.findall(r"[a-z0-9.\-+_]+@[a-z0-9\n\-+_]+\.[a-z]+", texte)]
        emails2 = [x.strip() for x in re.findall(r"[a-z0-9.\-+_]+@[a-z0-9.\n\-+_]+\.[a-z]+", texte)]
        emails3 = [x.strip() for x in re.findall(r"[({a-zA-Z0-9., \-+_})]+@[a-z0-9.\n\- +_]+\.[a-z]+", texte)]
        emails4 = [x.strip() for x in re.findall(r"[({a-z0-9., \-+_})]+\n@[a-z0-9.\n\-+_]+\.[a-z]+", texte)]
        emails5 = [x.strip() for x in re.findall(r"[({a-z0-9., \-+_})]+Q[a-z0-9.\n\-+_]+\.[a-z]+", texte)]
        emails6 = [x.strip() for x in re.findall(r"[({a-zA-Z0-9., \n\-+_})]+@[a-z0-9.\- +_]+\.[a-z]+", texte)]
        ######################################################################

        # Dictionnaire qui permet de retrouver l'ordre après tri
        position_emails = dict((x, y) for x, y in enumerate(emails, 0))
        position_emails2 = dict((x, y) for x, y in enumerate(emails2, 0))
        ######################################################################

        # Tri les listes pour pouvoir les comparer
        emails.sort()
        emails2.sort()
        ######################################################################

        if emails and emails != emails2:
            type_mail = 0
            if len(emails) < len(emails2):
                Utils.retrieve_previous_order(emails, position_emails2)
            elif len(emails) > len(emails2):
                Utils.retrieve_previous_order(emails, position_emails)
            else:
                i = 0
                for mail, mail2 in zip(emails, emails2):
                    if mail != mail2:
                        if mail[-5:] == ".univ" or mail[-6:] == ".univ-" or len(mail) < len(mail2):
                            pos = list(position_emails.keys())[list(position_emails.values()).index(emails[i])]
                            emails[i] = mail2
                            position_emails[pos] = mail2

                    i += 1

                Utils.retrieve_previous_order(emails, position_emails)

        else:
            type_mail = 0
            Utils.retrieve_previous_order(emails, position_emails)

        # S'il y a des mails dans la troisième regex, on regarde s'il y a plusieurs mails
        if len(emails3) != 0:
            if "," in emails3[0]:
                type_mail = 1
                if emails:
                    emails_copy[:] = emails[:]

                emails = []

                emails3_separer = emails3[0].split(",")
                dernier_mail, nom_domaine = emails3_separer[-1].split("@")

                # Si présence d'un \n dans le nom de domaine, on le retire
                pos_newline = nom_domaine.find("\n")

                if pos_newline != -1:
                    nom_domaine = nom_domaine[:pos_newline]
                ######################################################################

                for elt in emails3_separer[:-1]:
                    emails.append(f"{elt.strip()}@{nom_domaine}")

                emails.append(f"{dernier_mail}@{nom_domaine}")
        ######################################################################

        # S'il y a des mails dans la quatrième regex, on regarde s'il y a plusieurs mails
        if len(emails4) != 0:
            if "," in emails4[0]:
                type_mail = 1
                if emails:
                    emails_copy[:] = emails[:]

                emails = []

                emails4_separer = emails4[0].split(",")
                dernier_mail, nom_domaine = emails4_separer[-1].split("@")

                for elt in emails4_separer[:-1]:
                    emails.append(f"{elt.strip()}@{nom_domaine}")

                emails.append(f"{dernier_mail}@{nom_domaine}")
        ######################################################################

        # Soit, le @ a été lu comme un Q et donc on sépare les mails
        if not emails and len(emails5) > 0:
            if "," in emails5[0]:
                type_mail = 1
                if emails:
                    emails_copy[:] = emails[:]

                emails = []

                emails5_separer = emails5[0].split(",")
                dernier_mail, nom_domaine = emails5_separer[-1].split("Q")

                for elt in emails5_separer[:-1]:
                    emails.append(f"{elt.strip()}@{nom_domaine}")

                emails.append(f"{dernier_mail}@{nom_domaine}")
        ######################################################################

        # Contient peut-être des mails avec -\n
        if emails6:
            # Copy de la liste
            emails6_copy = []
            emails6_copy[:] = emails6[:]
            ######################################################################

            # On supprime d'abord les éléments déja connu de la liste
            for mail6 in emails6_copy:
                if mail6 in emails:
                    emails6.remove(mail6)
            ######################################################################

            # Nouvelle copie
            emails6_copy[:] = emails6[:]
            ######################################################################

            # On retire les éléments qui sont bons dans la liste principale
            # Et sinon on modifie les éléments dans la liste principale et qui demande plus d'informations
            # (partie du mail manquant)
            for elt in emails:
                for mail6 in emails6_copy:
                    pos_element = mail6.find(elt)

                    # Si présence d'un mail comme tor-\nres@example.com, on le remplace dans la liste principale
                    if pos_element != -1 and mail6[pos_element - 2: pos_element] == "-\n":
                        index = emails.index(elt)

                        mail = mail6.split(",")[-1].replace("-\n", "")

                        emails[index] = mail
                    ######################################################################
            ######################################################################
        ######################################################################

        # Pour chaque mail, on enlève différents caractères
        for i in range(len(emails)):
            emails[i] = emails[i].replace("\n", "")
            emails[i] = emails[i].replace("(", "").replace(")", "")
            emails[i] = emails[i].replace("{", "").replace("}", "")
            emails[i] = emails[i].strip()
        ######################################################################

        # Si on a des mails trouvés grâce à la première regex, on les rajoute
        for element in emails_copy:
            if element not in emails:
                emails.insert(len(emails) // 2, element)
        ######################################################################

        # Si présence d'un f au début et un g à la fin (problème d'encodeur avec les {}), on les enlève
        if type_mail == 1 and len(emails) > 0:
            nom, domaine = emails[-1].split("@")
            if emails[0][0] == "f" and nom[-1] == "g":
                emails[0] = emails[0][1:]

                emails[-1] = f"{nom[:-1].strip()}@{domaine}"
        ######################################################################

        # Si le mail est trop petit(erreur) -> on l'enlève
        for element in emails:
            if len(element.split("@")[0]) < 2:
                emails.remove(element)
        ######################################################################

        return emails, type_mail
