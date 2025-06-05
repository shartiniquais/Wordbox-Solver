from typing import List, Set, Tuple

def parse_board_chars(chars: str, size: int) -> List[List[str]]:
    """
    Transforme la chaîne plate en grille 2D de chaînes (lettres ou digrammes).
    Les majuscules indiquent le début d'un digramme (ex: 'Qu').
    Retourne une liste de listes de chaînes en majuscules.
    """
    parsed: List[str] = []
    i = 0
    while i < len(chars):
        if chars[i].isupper():
            if i + 1 >= len(chars) or not chars[i + 1].islower():
                raise ValueError(
                    f"Digramme mal formé à la position {i}: "
                    f"une majuscule doit être suivie d'une minuscule."
                )
            parsed.append(chars[i] + chars[i + 1])
            i += 2
        else:
            parsed.append(chars[i])
            i += 1

    if len(parsed) != size * size:
        raise ValueError(
            f"Nombre de tuiles incorrect : "
            f"attendu {size*size}, obtenu {len(parsed)}."
        )

    matrix: List[List[str]] = []
    for row in range(size):
        start = row * size
        matrix.append([parsed[start + col].upper() for col in range(size)])
    return matrix


def load_words(words_file: str,
               min_word_length: int) -> Tuple[Set[str], Set[str]]:
    """
    Lit le fichier de mots, ne garde que ceux de longueur >= min_word_length,
    renvoie deux ensembles :
    - words : tous les mots
    - prefixes : tous les préfixes valides (pour le backtracking)
    """
    words: Set[str] = set()
    prefixes: Set[str] = set()

    with open(words_file, 'r', encoding='utf-8') as f:
        for line in f:
            w = line.strip().upper()
            if len(w) < min_word_length:
                continue
            words.add(w)
            for i in range(1, len(w)):
                prefixes.add(w[:i])

    return words, prefixes


def get_neighbors(x: int, y: int,
                  rows: int, cols: int) -> List[Tuple[int,int]]:
    """Retourne les coordonnées voisines (8 directions) valides."""
    deltas = [(-1,-1),(-1,0),(-1,1),
              ( 0,-1),        ( 0,1),
              ( 1,-1),( 1,0),( 1,1)]
    nbrs: List[Tuple[int,int]] = []
    for dx, dy in deltas:
        nx, ny = x+dx, y+dy
        if 0 <= nx < rows and 0 <= ny < cols:
            nbrs.append((nx, ny))
    return nbrs


def find_all_words(board_chars: str,
                   grid_size: int,
                   min_word_length: int,
                   words_file: str) -> List[Tuple[str, List[Tuple[int, int]]]]:
    """
    Recherche par DFS tous les mots du dictionnaire présents sur la grille.
    Retourne une liste de tuples (mot, chemin) où chemin est la liste des coordonnées.
    """
    board = parse_board_chars(board_chars, grid_size)
    word_set, prefix_set = load_words(words_file, min_word_length)
    found: List[Tuple[str, List[Tuple[int,int]]]] = []
    rows, cols = grid_size, grid_size
    added_words: Set[str] = set()

    def dfs(x: int, y: int,
            current: str,
            path: List[Tuple[int,int]],
            visited: Set[Tuple[int,int]]):
        current += board[x][y]
        path = path + [(x, y)]
        visited = visited | {(x, y)}

        if len(current) >= min_word_length and current in word_set and current not in added_words:
            found.append((current, path))
            added_words.add(current)

        if current not in prefix_set:
            return

        for nx, ny in get_neighbors(x, y, rows, cols):
            if (nx, ny) not in visited:
                dfs(nx, ny, current, path, visited)

    for i in range(rows):
        for j in range(cols):
            dfs(i, j, '', [], set())

    # Trie du mot le plus long au plus court, puis ordre alphabétique
    found.sort(key=lambda w: (-len(w[0]), w[0]))
    return found


if __name__ == "__main__":
    import os

    GRID_SIZE       = int(os.environ.get("GRID_SIZE",       4))
    MIN_WORD_LENGTH = int(os.environ.get("MIN_WORD_LENGTH", 3))
    WORDS_FILE      = f"mots{MIN_WORD_LENGTH}.txt"
    BOARD_CHARS     = os.environ.get("BOARD_CHARS", "")

    words_with_paths = find_all_words(BOARD_CHARS,
                                      GRID_SIZE,
                                      MIN_WORD_LENGTH,
                                      WORDS_FILE)
    print(f"Mots trouvés ({len(words_with_paths)}):")
    for word, path in words_with_paths:
        print(f"{word: <15} {path}")
