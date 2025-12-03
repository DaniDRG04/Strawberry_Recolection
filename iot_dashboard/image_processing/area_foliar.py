import os
import glob
from datetime import datetime

import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

IMAGE_DIR = "C:\\Users\\dregg\\Downloads\\drj\\captures\\all_images"
IMAGE_PATTERN = "img_*.jpg"
OUTPUT_CSV = "area_foliar_timeseries.csv"
OUTPUT_FIG = "area_foliar_timeseries.png"
SHOW_DEBUG = True

def parse_timestamp_from_name(filename: str) -> datetime:
    """
    Espera nombres tipo: img_YYYYMMDD_HHMMSS.ext
    Ejemplo: img_20251103_145704.jpg
    """
    base = os.path.basename(filename)
    name, _ = os.path.splitext(base)

    try:
        _, date_part, time_part = name.split("_")
        dt = datetime.strptime(date_part + time_part, "%Y%m%d%H%M%S")
    except ValueError:
        # Si falla el parseo, simplemente usa el orden alfabético
        dt = None
    return dt


def compute_leaf_area_mask(image_bgr: np.ndarray) -> np.ndarray:
    """
    Crea una máscara binaria aproximando el área de planta.
    Estrategia simple:
      1. Convertir a gris.
      2. Umbralización de Otsu (separa zonas más brillantes).
      3. Operaciones morfológicas para limpiar ruido.
    Devuelve máscara de 0 / 255.
    """

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # Otsu threshold: separa fondo oscuro de zonas iluminadas
    _, mask = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Morfología: abrir para quitar ruido pequeño, cerrar para rellenar huecos
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    return mask

def main():
    pattern = os.path.join(IMAGE_DIR, IMAGE_PATTERN)
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"No se encontraron imágenes con patrón: {pattern}")
        return

    records = []

    for i, f in enumerate(files, start=1):
        print(f"[{i}/{len(files)}] Procesando {f} ...")
        img = cv2.imread(f)
        if img is None:
            print(f"  ¡Advertencia! No se pudo leer {f}")
            continue

        mask = compute_leaf_area_mask(img)

        total_pixels = mask.size
        leaf_pixels = np.count_nonzero(mask == 255)
        leaf_fraction = leaf_pixels / total_pixels

        timestamp = parse_timestamp_from_name(f)

        records.append(
            {
                "file": os.path.basename(f),
                "timestamp": timestamp,
                "leaf_pixels": leaf_pixels,
                "total_pixels": total_pixels,
                "leaf_fraction": leaf_fraction,
            }
        )

        # Muestra de depuración opcional
        if SHOW_DEBUG and i % 20 == 0:  # por ejemplo, cada 20 imágenes
            cv2.imshow("Imagen", img)
            cv2.imshow("Mascara", mask)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    # Crear DataFrame
    df = pd.DataFrame(records)

    # Ordenar por timestamp si existe (si no, por nombre)
    if df["timestamp"].notna().all():
        df = df.sort_values("timestamp")
    else:
        df = df.sort_values("file")

    # Guardar CSV
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nCSV guardado en: {OUTPUT_CSV}")

    # Imprimir resumen simple
    print("\nResumen:")
    print(df[["file", "timestamp", "leaf_pixels", "leaf_fraction"]].head())
    print("...")
    print(df[["file", "timestamp", "leaf_pixels", "leaf_fraction"]].tail())

    # Graficar serie de tiempo (usando fracción para que sea independiente del tamaño)
    if df["timestamp"].notna().all():
        x = df["timestamp"]
        x_label = "Tiempo"
    else:
        x = range(len(df))
        x_label = "Índice de imagen"

    plt.figure(figsize=(10, 5))
    plt.plot(x, df["leaf_fraction"], marker="o")
    plt.xlabel(x_label)
    plt.ylabel("Fracción de área de planta (0–1)")
    plt.title("Evolución del área foliar (proyección en la imagen)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUTPUT_FIG, dpi=150)
    print(f"Gráfica guardada en: {OUTPUT_FIG}")
    plt.show()


if __name__ == "__main__":
    main()
