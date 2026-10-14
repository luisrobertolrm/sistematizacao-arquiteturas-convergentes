import os
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENTREGA_DIR = os.path.join(BASE_DIR, "entrega")
ZIP_NAME = "Entrega_Sistematizacao_Luis_Roberto_Moraes.zip"
ZIP_PATH = os.path.join(ENTREGA_DIR, ZIP_NAME)

def compactar():
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(ENTREGA_DIR):
            for file in files:
                if file == ZIP_NAME:
                    continue
                file_full = os.path.join(root, file)
                rel_path = os.path.relpath(file_full, ENTREGA_DIR)
                zipf.write(file_full, rel_path)
                print(f"Added to zip: {rel_path}")

    print(f"\nCreated zip archive successfully: {ZIP_PATH}")
    print(f"Size: {os.path.getsize(ZIP_PATH)} bytes ({os.path.getsize(ZIP_PATH) / 1024 / 1024:.2f} MB)")

if __name__ == "__main__":
    compactar()
