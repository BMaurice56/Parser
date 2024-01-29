# PDF Parser

Ce logiciel a pour but d'analyser des documents scientific de type pdf 
et d'en extraire les différentes informations de celui-ci comme :
- Titre
- Auteurs
- Paragraphes
- Bibliographies

Option utile pour pdftotext : 
- -raw pour garder la structure dans l'ordre du contenue



Pdf2txt:
  -Pdf lecture vertical commande : pdf2txt -V fichierPdf.pdf fichierTxt.txt
  -Pdf lecture normal commande : pdf2txt -A fichierPdf.pdf fichierTxt.txt
  
Pdf2txt va affciher chaque schéma à la fin de la page de la page où est le schéma (après le numéro de la page)

Pdftotxt va afficher le schéma à l'endroit où il est dans le pdf
