import os
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import errorcode

# --- CONFIGURACIÓN ---
load_dotenv()

# --- App de Flask ---
app = Flask(__name__)
# Se necesita una clave secreta para usar mensajes flash (flash messages)
app.secret_key = os.getenv("SECRET_KEY", "a-super-secret-key")

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

# --- Rutas de la Aplicación (CRUD) ---

@app.route('/')
def index():
    """Muestra la lista de todos los estudiantes."""
    conn = get_db_connection()
    if conn is None:
        return render_template('index.html', students=[])
    
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT e.matricula_alumno, p.nombre, p.apellido_paterno, p.apellido_materno, p.correo
    FROM estudiante e
    JOIN persona p ON e.idpersona = p.idpersona
    ORDER BY p.apellido_paterno, p.apellido_materno, p.nombre;
    """
    cursor.execute(query)
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('index.html', students=students)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    """Añade un nuevo estudiante a la base de datos."""
    if request.method == 'POST':
        # Obtener datos del formulario
        matricula = request.form['matricula']
        nombre = request.form['nombre']
        apellido_paterno = request.form['apellido_paterno']
        apellido_materno = request.form['apellido_materno']
        correo = request.form['correo']

        conn = get_db_connection()
        if conn is None:
            return redirect(url_for('index'))
        
        cursor = conn.cursor()
        try:
            # Iniciar transacción
            conn.start_transaction()

            # 1. Obtener el siguiente ID para persona y estado de cuenta
            cursor.execute("SELECT MAX(idpersona) FROM persona")
            next_id_persona = (cursor.fetchone()[0] or 0) + 1
            
            cursor.execute("SELECT MAX(idestadodecuenta) FROM estadodecuenta")
            next_id_estado_cuenta = (cursor.fetchone()[0] or 0) + 1

            # 2. Insertar en `persona`
            sql_persona = "INSERT INTO persona (idpersona, nombre, apellido_paterno, apellido_materno, correo) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql_persona, (next_id_persona, nombre, apellido_paterno, apellido_materno, correo))

            # 3. Insertar en `estadodecuenta` (con valores por defecto)
            sql_estado_cuenta = "INSERT INTO estadodecuenta (idestadodecuenta, cargos, ingresos) VALUES (%s, 0.0, 0.0)"
            cursor.execute(sql_estado_cuenta, (next_id_estado_cuenta,))

            # 4. Insertar en `estudiante`
            sql_estudiante = "INSERT INTO estudiante (matricula_alumno, idpersona, idestadocuenta) VALUES (%s, %s, %s)"
            cursor.execute(sql_estudiante, (matricula, next_id_persona, next_id_estado_cuenta))

            # Confirmar transacción
            conn.commit()
            flash('Estudiante añadido correctamente.', 'success')

        except mysql.connector.Error as err:
            conn.rollback()
            flash(f'Error al añadir estudiante: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('index'))

    return render_template('student_form.html', student=None)

@app.route('/edit/<int:matricula>', methods=['GET', 'POST'])
def edit_student(matricula):
    """Edita la información de un estudiante."""
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('index'))

    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Actualizar datos del estudiante
        nombre = request.form['nombre']
        apellido_paterno = request.form['apellido_paterno']
        apellido_materno = request.form['apellido_materno']
        correo = request.form['correo']
        
        try:
            # Obtenemos el idpersona asociado a la matrícula
            cursor.execute("SELECT idpersona FROM estudiante WHERE matricula_alumno = %s", (matricula,))
            student_data = cursor.fetchone()
            if student_data:
                id_persona = student_data['idpersona']
                # Actualizamos la tabla persona
                sql_update = """
                UPDATE persona 
                SET nombre = %s, apellido_paterno = %s, apellido_materno = %s, correo = %s
                WHERE idpersona = %s
                """
                cursor.execute(sql_update, (nombre, apellido_paterno, apellido_materno, correo, id_persona))
                conn.commit()
                flash('Estudiante actualizado correctamente.', 'success')
            else:
                flash('No se encontró el estudiante.', 'warning')
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f'Error al actualizar: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('index'))

    # Método GET: Mostrar formulario con datos actuales
    query = """
    SELECT p.nombre, p.apellido_paterno, p.apellido_materno, p.correo
    FROM estudiante e
    JOIN persona p ON e.idpersona = p.idpersona
    WHERE e.matricula_alumno = %s
    """
    cursor.execute(query, (matricula,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()

    if student:
        return render_template('student_form.html', student=student)
    else:
        flash('Estudiante no encontrado.', 'warning')
        return redirect(url_for('index'))

@app.route('/delete/<int:matricula>', methods=['POST'])
def delete_student(matricula):
    """Elimina un estudiante de la base de datos."""
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('index'))

    cursor = conn.cursor()
    try:
        conn.start_transaction()

        # 1. Obtener idpersona e idestadocuenta antes de borrar
        cursor.execute("SELECT idpersona, idestadocuenta FROM estudiante WHERE matricula_alumno = %s", (matricula,))
        result = cursor.fetchone()
        if not result:
            flash('Estudiante no encontrado.', 'warning')
            return redirect(url_for('index'))
        
        id_persona, id_estado_cuenta = result

        # 2. Eliminar de `estudiante`
        cursor.execute("DELETE FROM estudiante WHERE matricula_alumno = %s", (matricula,))
        
        # 3. Eliminar de `persona`
        cursor.execute("DELETE FROM persona WHERE idpersona = %s", (id_persona,))

        # 4. Eliminar de `estadodecuenta`
        cursor.execute("DELETE FROM estadodecuenta WHERE idestadodecuenta = %s", (id_estado_cuenta,))

        conn.commit()
        flash('Estudiante eliminado correctamente.', 'success')

    except mysql.connector.Error as err:
        conn.rollback()
        flash(f'Error al eliminar estudiante: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('index'))

@app.route('/search')
def search_student():
    """Busca estudiantes por nombre, matrícula o correo."""
    query_term = request.args.get('query', '')
    if not query_term:
        return redirect(url_for('index'))

    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('index'))

    cursor = conn.cursor(dictionary=True)
    search_pattern = f"%{query_term}%"
    query = """
    SELECT e.matricula_alumno, p.nombre, p.apellido_paterno, p.apellido_materno, p.correo
    FROM estudiante e
    JOIN persona p ON e.idpersona = p.idpersona
    WHERE p.nombre LIKE %s 
       OR p.apellido_paterno LIKE %s 
       OR p.apellido_materno LIKE %s
       OR p.correo LIKE %s
       OR e.matricula_alumno LIKE %s
    ORDER BY p.apellido_paterno, p.apellido_materno, p.nombre;
    """
    cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    flash(f'Mostrando resultados para "{query_term}".', 'info')
    return render_template('index.html', students=students)

# --- Iniciar la Aplicación ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
