import cv2
import numpy as np
from pynput import mouse
from PIL import ImageGrab

print("Clique 2 fois pour définir la zone de capture (coin haut-gauche, puis bas-droit).")

clicks = []

def on_click(x, y, button, pressed):
    if pressed:
        clicks.append((x, y))
        print(f"Clic #{len(clicks)} à ({x}, {y})")
        if len(clicks) == 2:
            # Stop listener
            return False

# Affiche l'écran pour aider à viser
screen = np.array(ImageGrab.grab())
screen_bgr = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
cv2.imshow("Cliquez sur la zone", screen_bgr)
cv2.waitKey(1)

# Attend 2 clics
with mouse.Listener(on_click=on_click) as listener:
    listener.join()

cv2.destroyAllWindows()

# Ordonner les coordonnées
(x1, y1), (x2, y2) = clicks
x_min, x_max = sorted([x1, x2])
y_min, y_max = sorted([y1, y2])

print(f"\nCoordonnées bbox : ({x_min}, {y_min}, {x_max}, {y_max})")
print(f"Largeur : {x_max - x_min} px")
print(f"Hauteur : {y_max - y_min} px")

# Tu peux copier ça dans ton detection.py :
print(f"\n# Pour ton script :")
print(f"BBOX = ({x_min}, {y_min}, {x_max}, {y_max})")
