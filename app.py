import os
import requests
from flask import Flask, render_template_string, request, redirect, url_for
from dotenv import load_dotenv

# --- PASO 1: INSTALACIÓN ---
# Antes de ejecutar, instala las librerías necesarias:
# pip install Flask python-dotenv requests

import psycopg2
from psycopg2 import extras

# --- PASO 2: CONFIGURACIÓN ---
load_dotenv()

# --- Variables de Entorno para PostgreSQL ---
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "mydatabase")
DB_USER = os.getenv("POSTGRES_USER", "myuser")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "mypassword")

# --- App de Flask ---
app = Flask(__name__)

# --- Función para conectar a la base de datos ---
def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST,
                            database=DB_NAME,
                            user=DB_USER,
                            password=DB_PASSWORD)
    return conn

# --- Inicializar la base de datos (crear tabla si no existe) ---
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS directorio (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            correo VARCHAR(255),
            telefono VARCHAR(20)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Llamar a init_db al inicio de la aplicación
with app.app_context():
    init_db()

# --- Funciones de Ayuda para la Base de Datos ---
def db_get_entries():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM directorio ORDER BY id DESC")
    entries = cur.fetchall()
    cur.close()
    conn.close()
    return entries

def db_search_entries(query):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM directorio WHERE nombre ILIKE %s ORDER BY id DESC", ('%{}'.format(query),))
    entries = cur.fetchall()
    cur.close()
    conn.close()
    return entries

def db_add_entry(nombre, correo, telefono):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO directorio (nombre, correo, telefono) VALUES (%s, %s, %s)",
                (nombre, correo, telefono))
    conn.commit()
    cur.close()
    conn.close()

def db_get_entry(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM directorio WHERE id = %s", (id,))
    entry = cur.fetchone()
    cur.close()
    conn.close()
    return entry

def db_update_entry(id, nombre, correo, telefono):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE directorio SET nombre = %s, correo = %s, telefono = %s WHERE id = %s",
                (nombre, correo, telefono, id))
    conn.commit()
    cur.close()
    conn.close()

def db_delete_entry(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM directorio WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()

# --- Plantillas HTML con Bootstrap ---
INDEX_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Directorio con Flask y Supabase</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1 class="mb-4">Directorio de Contactos</h1>

        <!-- Formulario de Búsqueda -->
        <div class="card mb-4">
            <div class="card-header">Buscar Contacto</div>
            <div class="card-body">
                <form action="{{ url_for('index') }}" method="get" class="d-flex">
                    <input type="text" name="query" class="form-control me-2" placeholder="Buscar por nombre..." value="{{ request.args.get('query', '') }}">
                    <button type="submit" class="btn btn-primary">Buscar</button>
                </form>
            </div>
        </div>

        <!-- Formulario para Añadir -->
        <div class="card mb-4">
            <div class="card-header">Añadir Nuevo Contacto</div>
            <div class="card-body">
                <form action="{{ url_for('add') }}" method="post">
                    <div class="mb-3">
                        <input type="text" name="nombre" class="form-control" placeholder="Nombre" required>
                    </div>
                    <div class="mb-3">
                        <input type="email" name="correo" class="form-control" placeholder="Correo electrónico">
                    </div>
                    <div class="mb-3">
                        <input type="text" name="telefono" class="form-control" placeholder="Teléfono">
                    </div>
                    <button type="submit" class="btn btn-success">Añadir</button>
                </form>
            </div>
        </div>

        <!-- Tabla de Contactos -->
        <div class="card">
            <div class="card-header">Lista de Contactos</div>
            <div class="card-body">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Nombre</th>
                            <th>Correo</th>
                            <th>Teléfono</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for entry in entries %}
                        <tr>
                            <td>{{ entry.nombre }}</td>
                            <td>{{ entry.correo }}</td>
                            <td>{{ entry.telefono }}</td>
                            <td>
                                <a href="{{ url_for('edit', id=entry.id) }}" class="btn btn-warning btn-sm">Editar</a>
                                <a href="{{ url_for('delete', id=entry.id) }}" class="btn btn-danger btn-sm">Eliminar</a>
                            </td>
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

EDIT_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Editar Contacto</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="card">
            <div class="card-header">
                <h1>Editar Contacto</h1>
            </div>
            <div class="card-body">
                <form action="{{ url_for('update', id=entry.id) }}" method="post">
                    <div class="mb-3">
                        <label for="nombre" class="form-label">Nombre</label>
                        <input type="text" id="nombre" name="nombre" class="form-control" value="{{ entry.nombre }}" required>
                    </div>
                    <div class="mb-3">
                        <label for="correo" class="form-label">Correo</label>
                        <input type="email" id="correo" name="correo" class="form-control" value="{{ entry.correo }}">
                    </div>
                    <div class="mb-3">
                        <label for="telefono" class="form-label">Teléfono</label>
                        <input type="text" id="telefono" name="telefono" class="form-control" value="{{ entry.telefono }}">
                    </div>
                    <button type="submit" class="btn btn-primary">Actualizar</button>
                    <a href="{{ url_for('index') }}" class="btn btn-secondary">Cancelar</a>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
'''

# --- Rutas de la Aplicación ---

@app.route('/')
def index():
    query = request.args.get('query')
    if query:
        entries = db_search_entries(query)
    else:
        entries = db_get_entries()
    return render_template_string(INDEX_HTML, entries=entries)

@app.route('/add', methods=['POST'])
def add():
    nombre = request.form['nombre']
    correo = request.form['correo']
    telefono = request.form['telefono']
    db_add_entry(nombre, correo, telefono)
    return redirect(url_for('index'))

@app.route('/edit/<int:id>')
def edit(id):
    entry = db_get_entry(id)
    return render_template_string(EDIT_HTML, entry=entry)

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    nombre = request.form['nombre']
    correo = request.form['correo']
    telefono = request.form['telefono']
    db_update_entry(id, nombre, correo, telefono)
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    db_delete_entry(id)
    return redirect(url_for('index'))

# --- Iniciar la Aplicación ---

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))