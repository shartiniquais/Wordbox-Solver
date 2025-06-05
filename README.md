# Wordbox-Solver
Wordbox Solver est un programme permettant de jouer automatiquement au jeu WordBox de Plato.

⚠️ Ne fonctionne que sur ordinateur

J'utilise google play jeux sur windows 11, mais ça devrait marcher sur n'importe quel émulateur.

# Comment utiliser

## Configuration
Lancer le fichier bbox.py pour récupérer les coordonnées de la boite de jeu. 

C'est l'endroit ou le programme regardera, il ne faudra donc plus bouger la fenêtre pendant le jeu.

Modifier les valeurs dans manager.py : 

`GRID_SIZE = 4` -> Taille de la grille (seulement 4x4 et 5x5 sont supportés)

`MIN_WORD_LENGTH = 4` -> Longueur minimale des mots recherchés, WordBox ne supporte que 3 ou 4 mais mots2.txt est fourni en cas de besoin donc mettre "2" est techniquement possible

`BBOX = (704, 314, 1318, 914)` -> Coordonnées bbox données par bbox.py

## Jeu
* Lancer une partie et dès que les lettres sont visibles, lancer le manager.py puis rapidement revenir sur le jeu pour qu'il prenne une capture d'écran.
* Une fois la capture faite, le code va chercher les lettres puis les mots disponibles. (pendant ce temps la, vous pouvez toujours jouer)
* Une fois que la recherche est terminée, la console vous demandera d'appuier sur "entrée". Faite "entrée" dans la console et revenez rapidement dans le jeu.
* Votre souris sera controlée automatiquement pour jouer les mots trouvés, des plus gros aux plus petits.
### ⚠️En cas de problème, (ou si la manche est terminée mais que la souris continue) aller en haut a gauche de l'écran vite avec la souris stoppera le script⚠️
* Relancer le script (manager.py) a chaque nouvelle manche
