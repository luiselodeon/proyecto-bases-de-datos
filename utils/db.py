import os
import mysql.connector
from flask import flash
from dotenv import load_dotenv

# --- CONFIGURACIÓN ---
load_dotenv()

# --- Variables de Entorno para MySQL ---
DB_HOST = os.getenv("DB_HOST", "proyecto_bases_mysql_db")
DB_NAME = os.getenv("MYSQL_DATABASE", "controlescolar_db")
DB_USER = os.getenv("MYSQL_USER", "myuser")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "mypassword")

# --- Función para conectar a la base de datos ---
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except mysql.connector.Error as err:
        flash(f"Error al conectar con la base de datos: {err}", "danger")
        return None
