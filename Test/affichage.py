from colorama import Fore, Style


def afficher_barre_pourcentage(pourcentage):
    # Assurez-vous que le pourcentage est dans la plage [0, 100]
    pourcentage = max(0, min(100, pourcentage))

    # Convertissez le pourcentage en un nombre entier pour l'affichage de la barre
    pourcentage_entier = int(pourcentage)

    # Choisissez la couleur en fonction du pourcentage
    if pourcentage >= 95:
        couleur = Fore.GREEN
    elif pourcentage >= 85:
        couleur = Fore.LIGHTYELLOW_EX
    elif pourcentage >= 70:
        couleur = Fore.YELLOW
    else:
        couleur = Fore.RED

    # Créez et affichez la barre de pourcentage avec le caractère carré coloré
    barre_texte = f'Pourcentage de ressemblance avec le resultat attendu: {round(pourcentage,2)}% \n |{"■" * pourcentage_entier}{"_" * (100 - pourcentage_entier)}|'
    print(f'{couleur}{barre_texte} {Style.RESET_ALL}')
