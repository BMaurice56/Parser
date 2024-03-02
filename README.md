# PDF Parser

Ce logiciel a pour but d'analyser des documents scientifiques de type pdf 
et d'en extraire les différentes informations de celui-ci comme :
- Titre
- Auteurs
- Abstract
- Paragraphes
- Bibliographies
- etc...

# Lancement
Pour lancer ce logiciel sur un pdf ou sur un dossier, effectuer la commande suivante :
```
$ pip install --upgrade PyPDF2==3.0.1
$ pip install --upgrade python-Levenshtein==0.25.0
$ pip install --upgrade PyTermGUI==7.7.1
```

Et enfin réaliser la commande suivante :
```
$ python3 main.py -outputfile [/path/to/the/file.pdf, /path/to/the/dir/]
- outputfile : -t text
               -x xml
```
