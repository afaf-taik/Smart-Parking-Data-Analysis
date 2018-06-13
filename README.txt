Utilisation: 

prérequis : Python 3.5
/*
*********Base de données ************ 
*/
-installation de datastax-community 3.0.9 selon la version convenable ( 32 bits ou 64 bits)
Vérification de l'installation : ouvrir le CQL shell
si ça n'execute pas, supprimer les fichiers de log et commitlog et redémarrer le service datastax
-execution du fichier queries.py se trouvant dans le dossier data en entrant la commande python queries.py sur tout système d'exploitation ( sur windows il faut installer python d'abord )

-Pour generer les données aléatoirement : 
Utiliser la structure données dans le fichier Generatedata.txt avec un generateur de données json (http://json-generator.com/ ) puis le transformer en csv. 

/*
********* Application ************ 
*/

/!\ L'application ne peut pas tourner si la base de données n'est pas fonctionnelle
Compiler, en étant dans le dossier de l'application :
python full_window.py 

Pour pouvoir manipuler le code il faut avoir installé : 
-PyQt5: module libre qui permet de lier le langage Python avec Qt ( une API orientée objet qui offre des composants d'interface graphique (widgets) et d’autres services). 
-Pandas: bibliothèque open source qui fournit des structures de données et des outils d'analyse de données hautes performances et faciles à utiliser pour Python.
-Matplotlib:est une bibliothèque Python de tracé de courbes 2D qui produit des figures de qualité cross-plateformes.
-Numpy: est le package fondamental pour les manipulations et calculs scientifiques avec Python
-Pdfkit, jinja2 : bibliothèques utilisées pour la génération de fichier pdf.

-Structure du code : 
-----------------------------

-Le fichier gestiondonnees.py donne les differentes fonctionnalités d'analyse de données et de connexion à la BD
-le fichier parkingwindow.py fournit ce qui est interface graphique, il a été créé avec QtDesigner en transformant FenetrePrincipale.ui en un fichier python 
-full_window.py est celui qui contient le main et différentes fonctions liées à l'execution des composants graphiques
-categorie.* sont des fichiers qui servent à garder en note les categories de parking
-les fichiers html et css sont pour la forme des rapports



