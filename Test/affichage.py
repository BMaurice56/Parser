from colorama import Fore, Style

def selectcouleur(pourcentage : float):
    """

    :param pourcentage:
    :return: la couleur relié au pourcentage
    """
    if pourcentage >= 90 :
        return Fore.GREEN
    elif pourcentage >=70:
        return Fore.LIGHTYELLOW_EX
    elif pourcentage >= 50:
        return Fore.LIGHTMAGENTA_EX
    else:
        return Fore.RED


def afficher_barre_pourcentage(pourcentages: dict) -> None:
    """
    Affiche la barre de pourcentage dans le terminal

    :param pourcentages: list des pourcentages à afficher
    :return: None
    """
    total = 0
    max_longueur_nom = 10

    for el, p in pourcentages.items():
        # Assurez-vous que le pourcentage est dans la plage [0, 100]
        if p < 0 or p > 100:
            raise ValueError("Pourcentage impossible")
        total += p
    total /= len(pourcentages)

    print("Pourcentage par élément:")
    for element, pourcentage in pourcentages.items():
        couleur = selectcouleur(pourcentage)
        barre = '■' * int(pourcentage / 5)  # Ajuste la division pour une meilleure échelle
        espace = ' ' * (max_longueur_nom - len(element))  # Ajoute l'espace pour aligner les barres
        print(f"{element}:{espace}\t {couleur}{barre}  {pourcentage}%{Style.RESET_ALL}")

    print()
    # Convertis le pourcentage en un nombre entier pour l'affichage de la barre
    pourcentage_entier = int(total)

    # Choisi la couleur en fonction du pourcentage
    couleur = selectcouleur(total)

    # Créer et affiche la barre de pourcentage avec le caractère carré coloré
    barre_texte = "Pourcentage de ressemblance avec le résultat attendu: "
    barre_texte += f'{round(total, 2)}% \n |{"■" * pourcentage_entier}{"_" * (100 - pourcentage_entier)}|'
    print(f"{couleur}{barre_texte} {Style.RESET_ALL}")

