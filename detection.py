import os
import cv2
import numpy as np
from PIL import ImageGrab
import pytesseract
from typing import Tuple, List


# ================== CONFIGURATION ==================
MIN_CONTOUR_AREA   = 500
CIRCULARITY_THRESH = 0.6
UPSCALE            = 2
DARK_THRESHOLDS    = [150, 120, 100]
FALLBACK_THRESH    = [80, 60, 40]
DEBUG_DETECT_OUT   = "debug_detect.png"
DEBUG_PROC_OUT     = "debug_processed.png"
# ====================================================


def capture_screenshot(bbox: Tuple[int, int, int, int]) -> np.ndarray:
    img = ImageGrab.grab(bbox=bbox)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def detect_cell_contours(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask_w = cv2.inRange(hsv, np.array([0, 0, 200]), np.array([180, 30, 255]))
    mask_c = cv2.inRange(hsv, np.array([80, 50, 50]), np.array([100, 255, 255]))
    mask = cv2.bitwise_or(mask_w, mask_c)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    centers, boxes = [], []
    for cnt in cnts:
        area = cv2.contourArea(cnt)
        if area < MIN_CONTOUR_AREA:
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        rad = (w + h) / 4
        circ = area / (np.pi * rad * rad)
        if circ < CIRCULARITY_THRESH:
            continue
        centers.append((x + w // 2, y + h // 2))
        boxes.append((x, y, w, h))
    return centers, boxes


def ocr_cell(cell):
    h, w = cell.shape[:2]
    cell_big = cv2.resize(cell, (w * UPSCALE, h * UPSCALE), interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(cell_big, cv2.COLOR_BGR2GRAY)

    _, mask_dark = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    mask_disk = np.zeros_like(mask_dark)
    cy, cx = mask_dark.shape[0] // 2, mask_dark.shape[1] // 2
    radius = int(min(cx, cy) * 0.9)
    cv2.circle(mask_disk, (cx, cy), radius, 255, -1)
    processed = cv2.bitwise_and(mask_dark, mask_disk)
    processed = cv2.medianBlur(processed, 3)

    def ocr_psm(psm):
        config = f"-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ --psm {psm}"
        txt = pytesseract.image_to_string(processed, config=config).strip().upper()
        return txt

    text_10 = ocr_psm(10)
    text_13 = ocr_psm(13)

    print(f"[DEBUG] OCR 10: '{text_10}'")
    print(f"[DEBUG] OCR 13: '{text_13}'")

    # Heuristiques spécifiques
    if text_10 == "D" and text_13 == "P" or text_10 == "" and text_13 == "PP":
        final = "P"
    elif len(text_13) == 2 and text_13[0].isupper() and text_13[1].islower():
        final = text_13
    elif len(text_10) == 1 and text_10.isalpha():
        final = text_10
    elif len(text_13) == 1 and text_13.isalpha():
        final = text_13
    elif text_10 == "QU" or text_13 == "QU":
        final = "Qu"
    elif text_10 == "TH" or text_13 == "TH":
        final = "Th"
    elif text_10 == "IN" or text_13 == "IN":
        final = "In"
    elif text_10 == "HE" or text_13 == "HE":
        final = "He"
    else:
        final = "?"

    return final, processed


def read_board(grid_size: int, bbox: Tuple[int, int, int, int]) -> Tuple[
        List[List[str]], List[List[Tuple[int, int]]]]:
    img = capture_screenshot(bbox)
    centers, boxes = detect_cell_contours(img)
    if len(centers) != grid_size ** 2:
        raise RuntimeError(f"Trouvé {len(centers)} cases, attendu {grid_size ** 2}.")

    # Sauvegarde image debug avec rectangles
    dbg = img.copy()
    for (x, y, w, h) in boxes:
        cv2.rectangle(dbg, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imwrite(DEBUG_DETECT_OUT, dbg)
    print(f"[DEBUG] détection saved to {DEBUG_DETECT_OUT}")

    # Tri des centres par lignes puis colonnes
    centers = sorted(centers, key=lambda c: c[1])
    center_grid = []
    for i in range(grid_size):
        row = sorted(centers[i * grid_size:(i + 1) * grid_size], key=lambda c: c[0])
        center_grid.append(row)

    # Découpe & OCR
    ws = [w for (_, _, w, _) in boxes]
    hs = [h for (_, _, _, h) in boxes]
    cw, ch = int(np.mean(ws)), int(np.mean(hs))
    hw, hh = cw // 2, ch // 2

    letters = []
    procs = []
    for row in center_grid:
        for (cx, cy) in row:
            crop = img[cy - hh:cy + hh, cx - hw:cx + hw]
            letter, proc = ocr_cell(crop)
            letters.append(letter)
            procs.append(proc)

    print(f"[DEBUG] letters: {letters}")

    # Sauvegarde debug OCR
    ph, pw = procs[0].shape
    mosaic = np.zeros((ph * grid_size, pw * grid_size), dtype=np.uint8)
    for idx, proc in enumerate(procs):
        r, c = divmod(idx, grid_size)
        mosaic[r * ph:(r + 1) * ph, c * pw:(c + 1) * pw] = proc
    cv2.imwrite(DEBUG_PROC_OUT, mosaic)
    print(f"[DEBUG] processed masks saved to {DEBUG_PROC_OUT}")

    # Format grille finale
    board = [letters[i * grid_size:(i + 1) * grid_size] for i in range(grid_size)]

    return board, center_grid


if __name__ == "__main__":
    GRID_SIZE = int(os.environ.get("GRID_SIZE", 5))
    BBOX = tuple(map(int, os.environ.get("BBOX", "781,455,1198,870").split(",")))

    board, center_grid = read_board(GRID_SIZE, BBOX)
    flat = ''.join((c.lower() if len(c) == 1 else c) for r in board for c in r)
    print(f"BOARD_CHARS = '{flat}'")
    print("Board:")
    for row in board:
        print(' '.join(row))
