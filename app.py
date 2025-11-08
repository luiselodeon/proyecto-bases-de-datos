import os
import requests
from flask import Flask, render_template_string, request, redirect, url_for
from dotenv import load_dotenv

# --- PASO 1: INSTALACIÓN ---
# Antes de ejecutar, instala las librerías necesarias:
# pip install Flask python-dotenv requests mysql-connector-python

import mysql.connector
from mysql.connector import errorcode

# --- PASO 2: CONFIGURACIÓN ---
load_dotenv()

# --- Variables de Entorno para MySQL ---
DB_HOST = os.getenv("DB_HOST", "proyecto_bases_mysql_db")
DB_NAME = os.getenv("MYSQL_DATABASE", "controlescolar_db")
DB_USER = os.getenv("MYSQL_USER", "myuser")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "mypassword")

# --- App de Flask ---
app = Flask(__name__)

# --- Función para conectar a la base de datos ---
def get_db_connection():
    try:
        print("--- Intentando conectar a la base de datos con: ---")
        print(f"Host: {DB_HOST}")
        print(f"Database: {DB_NAME}")
        print(f"User: {DB_USER}")
        print("-------------------------------------------------")
        conn = mysql.connector.connect(host=DB_HOST,
                                       database=DB_NAME,
                                       user=DB_USER,
                                       password=DB_PASSWORD)
        print("¡Conexión exitosa!")
        return conn
    except mysql.connector.Error as err:
        print("--- ERROR DE CONEXIÓN A LA BASE DE DATOS ---")
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Acceso denegado. Revisa el usuario o la contraseña.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"Error: La base de datos '{DB_NAME}' no existe.")
        else:
            print(f"Error inesperado: {err}")
        print("-------------------------------------------")
        return None

# --- Plantillas HTML con Bootstrap ---
INDEX_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Directorio de Estudiantes</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1 class="mb-4">Directorio de Estudiantes</h1>

        <!-- Tabla de Estudiantes -->
        <div class="card">
            <div class="card-header">Lista de Estudiantes</div>
            <div class="card-body">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Matrícula</th>
                            <th>Nombre Completo</th>
                            <th>Correo</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for student in students %}
                        <tr>
                            <td>{{ student.matricula_alumno }}</td>
                            <td>{{ student.nombre }} {{ student.apellido_paterno }} {{ student.apellido_materno }}</td>
                            <td>{{ student.correo }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# --- Rutas de la Aplicación ---

@app.route('/')
def index():
    conn = get_db_connection()
    if conn is None:
        return "Error en la conexión a la base de datos", 500
        
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT e.matricula_alumno, p.nombre, p.apellido_paterno, p.apellido_materno, p.correo
    FROM estudiante e
    JOIN persona p ON e.idpersona = p.idpersona;
    """
    
    cursor.execute(query)
    students = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template_string(INDEX_HTML, students=students)

# --- Iniciar la Aplicación ---

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))