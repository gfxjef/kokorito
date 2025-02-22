from flask import Flask, jsonify
import os
import mysql.connector
import json
from ftplib import FTP

app = Flask(__name__)

def generar_y_subir_json():
    """
    Esta función realiza:
    1. Conexión a la BD y extracción de datos.
    2. Conversión a JSON y guardado en archivo.
    3. Conexión al FTP y subida del archivo.
    """
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
        raise Exception(f"Error al conectarse a la base de datos: {e}")
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
        raise Exception(f"Error al crear el archivo JSON: {e}")

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
    except Exception as e:
        raise Exception(f"Error durante la conexión FTP o la subida del archivo: {e}")
    finally:
        if 'ftp' in locals() and ftp is not None:
            ftp.quit()

@app.route("/subir-productos", methods=["GET"])
def subir_productos():
    """
    Endpoint que ejecuta la función generar_y_subir_json()
    y devuelve un mensaje JSON indicando el resultado.
    """
    try:
        generar_y_subir_json()
        return jsonify({"message": "Archivo subido exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Punto de entrada para ejecutar la app de Flask localmente
if __name__ == "__main__":
    # Puedes ajustar el puerto si lo deseas
    app.run(debug=True, host='0.0.0.0', port=5000)
