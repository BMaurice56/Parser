from colorama import Fore, Style


def afficher_barre_pourcentage(pourcentage: float) -> None:
    """
    Affiche la barre de pourcentage dans le terminal

    :param pourcentage: valeur
    :return: None
    """

    # Assurez-vous que le pourcentage est dans la plage [0, 100]
    if pourcentage < 0 or pourcentage > 100:
        raise ValueError("Pourcentage impossible")

    pourcentage = max(0, min(100, int(pourcentage)))

    # Convertis le pourcentage en un nombre entier pour l'affichage de la barre
    pourcentage_entier = int(pourcentage)

    # Choisi la couleur en fonction du pourcentage
    if pourcentage >= 95:
        couleur = Fore.GREEN
    elif pourcentage >= 85:
        couleur = Fore.LIGHTYELLOW_EX
    elif pourcentage >= 70:
        couleur = Fore.YELLOW
    else:
        couleur = Fore.RED

    # Créer et affiche la barre de pourcentage avec le caractère carré coloré
    barre_texte = "Pourcentage de ressemblance avec le résultat attendu: "
    barre_texte += f'{round(pourcentage, 2)}% \n |{"■" * pourcentage_entier}{"_" * (100 - pourcentage_entier)}|'
    print(f"{couleur}{barre_texte} {Style.RESET_ALL}")
