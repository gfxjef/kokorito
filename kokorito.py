import os
import mysql.connector
import json
from ftplib import FTP

def main():
    # --- Configuración de la base de datos usando variables de entorno ---
    DB_CONFIG = {
        'user': os.environ.get('MYSQL_USER'),
        'password': os.environ.get('MYSQL_PASSWORD'),
        'host': os.environ.get('MYSQL_HOST'),
        'database': os.environ.get('MYSQL_DATABASE'),
        'port': 3306
    }

    # --- Paso 1: Conexión a la base de datos y extracción de datos ---
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM caja_productos")
        registros = cursor.fetchall()
    except Exception as e:
        print(f"Error al conectarse a la base de datos: {e}")
        return
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'db' in locals() and db is not None:
            db.close()

    # --- Paso 2: Conversión de los registros a JSON ---
    nombre_archivo = "productos_caja.json"
    try:
        json_data = json.dumps(registros, default=str, ensure_ascii=False, indent=4)
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write(json_data)
    except Exception as e:
        print(f"Error al crear el archivo JSON: {e}")
        return

    # --- Paso 3: Conexión FTP y subida del archivo ---
    FTP_HOST = 'ns1.to1.fcomet.com'
    FTP_USER = 'atusalud'
    FTP_PASS = '43aQb3sgN3'
    FTP_DIR  = '/public_html/rous/kokrito/caja/'

    try:
        ftp = FTP(FTP_HOST)
        ftp.login(user=FTP_USER, passwd=FTP_PASS)
        ftp.cwd(FTP_DIR)

        with open(nombre_archivo, 'rb') as f:
            ftp.storbinary(f"STOR {nombre_archivo}", f)

        print("Archivo subido exitosamente al FTP.")
    except Exception as e:
        print(f"Error durante la conexión FTP o la subida del archivo: {e}")
    finally:
        if 'ftp' in locals() and ftp is not None:
            ftp.quit()

if __name__ == "__main__":
    main()
