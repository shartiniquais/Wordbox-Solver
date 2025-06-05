# player.py
import time
import pyautogui
from typing import List, Tuple

def play(paths: List[Tuple[str, List[Tuple[int, int]]]],
         centers: List[List[Tuple[int, int]]],
         pause: float = 0.05,
         wait_between_words: float = 0.09,
         dry_run: bool = True,
         bbox: Tuple[int, int] = (0, 0)):
    """
    paths   : liste de (mot, chemin)
    centers : grille des centres (dans l'image)
    dry_run : ne clique pas, déplace seulement la souris
    bbox    : offset (x, y) à appliquer pour convertir vers l'écran
    """
    offset_x, offset_y = bbox
    pyautogui.FAILSAFE = True

    print("[INFO] Simulation des mouvements (dry_run=True)..." if dry_run else "[INFO] Début de la saisie automatique...")
    time.sleep(1)

    for word, path in paths:
        if not path:
            continue

        print(f"[JOUER] {word} ({len(path)} lettres)")

        # Aller à la première lettre
        x0, y0 = centers[path[0][0]][path[0][1]]
        pyautogui.moveTo(x0 + offset_x, y0 + offset_y)
        if not dry_run:
            pyautogui.mouseDown()
        time.sleep(pause)

        # Glisser vers les autres lettres
        for i, j in path[1:]:
            xi, yi = centers[i][j]
            pyautogui.moveTo(xi + offset_x, yi + offset_y, duration=pause)

        if not dry_run:
            pyautogui.mouseUp()
        time.sleep(wait_between_words)

    print("[INFO] Tous les mots ont été joués." if not dry_run else "[INFO] Simulation terminée (aucun clic effectué).")
