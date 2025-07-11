import cv2
import argparse
from raycast import get_raycasts  # adapte l’import selon où ta fonction est définie

def main():
    parser = argparse.ArgumentParser(description="Test du raycast sur une image fixe")
    parser.add_argument("image_path", help="Chemin vers l'image à tester")
    parser.add_argument(
        "--save", "-s",
        action="store_true",
        help="Enregistrer l'image annotée sous annotated.jpg"
    )
    args = parser.parse_args()

    # 1) Lecture
    img = cv2.imread(args.image_path)
    if img is None:
        print(f"[ERROR] Impossible de charger {args.image_path}")
        return

    # 2) Appel du raycast
    distances, annotated = get_raycasts(
        image=img,
        number_ray=11,
        fov=130,
        step_size=1.0,
        threshold=230,
        annotate=True
    )

    # 3) Affichage des distances
    print("Distances raycast :", distances)

    # 4) Affichage de l'image annotée
    cv2.imshow("Annotated", annotated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 5) Optionnel : sauvegarde du résultat
    if args.save:
        out_path = "annotated.jpg"
        cv2.imwrite(out_path, annotated)
        print(f"[INFO] Image annotée enregistrée sous {out_path}")

if __name__ == "__main__":
    main()
