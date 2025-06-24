import cv2
import numpy as np
import math

def get_raycasts(image, number_ray=11, fov=130, step_size=1, annotate=True):
    height, width = image.shape[:2]
    distances = []

    cx = width / 2.0
    cy = height - 1

    angle_offset = math.radians(fov / (number_ray - 1))
    base_angle = math.radians(90)

    annotated = image.copy()

    for k in range(number_ray):
        angle = base_angle - fov * math.pi / 360 + k * angle_offset
        x, y = cx, cy
        hit = False
        hit_dist = 0

        while 0 <= x < width and 0 <= y < height:
            xi = int(round(x))
            yi = int(round(y))

            if 0 <= xi < width and 0 <= yi < height:
                pixel = image[yi, xi]

                if pixel[0] > 230 and pixel[1] > 230 and pixel[2] > 230:
                    distances.append(hit_dist)
                    hit = True
                    break
                
                if annotate:
                    annotated[yi, xi] = [255, 0, 0]
            else:
                break
            
            x += step_size * math.cos(angle)
            y -= step_size * math.sin(angle)
            hit_dist += 1

        if not hit:
            distances.append(hit_dist)

    return distances, annotated

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    image = cv2.imread("prediction_mask.png")
    distances, annotated = get_raycasts(image, number_ray=11, fov=130)

    print("Distances raycasts :", distances)

    plt.figure(figsize=(10, 6))
    plt.imshow(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB))
    plt.title("Raycast")
    plt.axis("off")
    plt.show()
