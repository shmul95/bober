import cv2
import numpy as np
import math

def get_raycasts(
    image: np.ndarray,
    number_ray: int = 11,
    fov: float = 130,
    step_size: float = 1.0,
    threshold: int = 230,
    annotate: bool = True
):
    """
    Calcule la distance jusqu'au premier pixel 'clair' (> threshold) pour chaque rayon
    partant du bas-centre de l'image, et renvoie (distances, annotated_image).

    - On pré-calcul les cos/sin pour chaque rayon.
    - On fait un seuillage en une passe (gris -> mask bool).
    - On vérifie les bornes xi, yi avant de lire mask[yi, xi].
    """

    h, w = image.shape[:2]
    cx, cy = w * 0.5, h - 1.0

    # 1) seuillage binaire (gris > threshold)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mask = gray > threshold

    # 2) préparation des angles
    start_angle = math.radians(90 - fov / 2)
    angle_step  = math.radians(fov / (number_ray - 1))

    # 3) pré-calcul des incréments (dx, dy) pour chaque rayon
    deltas = [
        (math.cos(start_angle + k * angle_step) * step_size,
         math.sin(start_angle + k * angle_step) * step_size)
        for k in range(number_ray)
    ]

    distances = [0] * number_ray
    annotated = image.copy() if annotate else None

    # 4) boucle par rayon
    for k, (dx, dy) in enumerate(deltas):
        x, y = cx, cy
        dist = 0

        while True:
            xi = int(x + 0.5)
            yi = int(y + 0.5)

            # 4a) si on sort du cadre, on arrête et on stocke la distance
            if xi < 0 or xi >= w or yi < 0 or yi >= h:
                distances[k] = dist
                break

            # 4b) si on touche un pixel > threshold, on arrête et on stocke
            if mask[yi, xi]:
                distances[k] = dist
                if annotate:
                    annotated[yi, xi] = (0, 0, 255)
                break

            # 4c) sinon on annot le pixel et on continue d'avancer
            if annotate:
                annotated[yi, xi] = (0, 0, 255)

            x += dx
            y -= dy
            dist += 1

    return distances, annotated

