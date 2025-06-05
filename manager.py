# manager.py
from detection import read_board
from finder import find_all_words
from player import play
import time

# ================== CONFIGURATION ==================
GRID_SIZE = 4
MIN_WORD_LENGTH = 4
BBOX = (704, 314, 1318, 914)
WORDS_FILE = f"mots{MIN_WORD_LENGTH}.txt"
# ===================================================

def main():
    print("[INFO] Lecture du plateau en cours...")
    board, centers = read_board(GRID_SIZE, BBOX)

    flat = "".join(c.lower() if len(c) == 1 else c for row in board for c in row)
    print(f"\nBOARD_CHARS = '{flat}'")
    print("Board:")
    for row in board:
        print(" ".join(row))

    print("\n[INFO] Recherche des mots...")
    results = find_all_words(flat, GRID_SIZE, MIN_WORD_LENGTH, WORDS_FILE)
    print(f"[INFO] {len(results)} mots trouvés.")
    for word, _ in results:
        print(word)

    input("\nAppuie sur [Entrée] pour commencer à jouer automatiquement...")
    play(results, centers, dry_run=False,  bbox=BBOX[:2])

if __name__ == "__main__":
    main()
