import os
import time
import base64
import datetime
import pathlib
import cv2
import mysql.connector
from mysql.connector import errorcode  # por si lo ocupas despu�s

TIME_OFFSET = datetime.timedelta(hours=8)

# MySQL
DB_CFG = {
    "host": "10.25.15.228",
    "user": "strawberry",
    "password": "1234567890",
    "database": "strawberries",
    "autocommit": True,
}

TABLE_NAME = "plant_images"

SAVE_DIR = str(pathlib.Path.home() / "captures")

PARAMETROS = {
    "width": 1280,
    "height": 720,
}

# ---- SQL m�nimas ----
def get_db_connection():
    return mysql.connector.connect(**DB_CFG)

def insert_capture(conn, ts_str, img_b64):
    ins = f"INSERT INTO `{TABLE_NAME}` (date_time, image_base64) VALUES (%s, %s)"
    cur = conn.cursor()
    cur.execute(ins, (ts_str, img_b64))
    cur.close()
# ---------------------

def ensure_outdir(base_dir):
    day = datetime.date.today().strftime("%Y-%m-%d")
    outdir = os.path.join(base_dir, day)
    os.makedirs(outdir, exist_ok=True)
    return outdir

def timestamp_name(prefix="img"):
    now = datetime.datetime.now()
    return f"{prefix}_{now.strftime('%Y%m%d_%H%M%S')}.jpg"

def take_photo_usb(width, height, out_path):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("No se pudo abrir la c�mara")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    time.sleep(0.25)  # estabilizar
    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        raise Exception("No se pudo capturar la imagen")
    if not cv2.imwrite(out_path, frame):
        raise Exception("No se pudo guardar la imagen")

def main():
    os.makedirs(SAVE_DIR, exist_ok=True)

    while True:
        try:
            t0 = time.time()

            # 1) Tomar la foto
            outdir = ensure_outdir(SAVE_DIR)
            img_path = os.path.join(outdir, timestamp_name("img"))
            take_photo_usb(PARAMETROS["width"], PARAMETROS["height"], img_path)

            # 2) Convertir a base64 leyendo el .jpg
            with open(img_path, "rb") as f:
                img_bytes = f.read()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")

            # 3) Guardar .txt con el base64
            txt_path = img_path.rsplit(".", 1)[0] + ".txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(img_b64)

            # 4) Insertar en MySQL
            ts_str = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
            conn = get_db_connection()
            try:
                insert_capture(conn, ts_str, img_b64)
            finally:
                conn.close()

        except Exception as e:
            print(f"[ERROR] {e}")

        # Dormir hasta la siguiente hora exacta
        time.sleep(3600)

if __name__ == "__main__":
    main()