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

#--- carrera

@app.route("/carreras")
def list_carreras():
    conn = get_db_connection()
    if conn is None:
        return render_template("carrera_list.html", carreras=[])

    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.idcarrera, c.descripcion_carrera, c.creditos_carrera,
               c.iddepartamentoacademico, d.nombre_departamento,
               c.costo_inscripcion
        FROM carrera c
        JOIN departamentoacademico d
            ON c.iddepartamentoacademico = d.iddepartamentoacademico
        ORDER BY c.idcarrera;
    """)
    
    carreras = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("carrera_list.html", carreras=carreras)


@app.route("/carreras/add", methods=["GET", "POST"])
def add_carrera():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_carreras"))

    cursor = conn.cursor(dictionary=True)

    # Traer departamentos académicos para el SELECT
    cursor.execute("SELECT * FROM departamentoacademico ORDER BY iddepartamentoacademico;")
    departamentos = cursor.fetchall()

    if request.method == "POST":
        idcarrera = request.form["idcarrera"]
        descripcion = request.form["descripcion_carrera"]
        creditos = request.form["creditos_carrera"]
        iddepto = request.form["iddepartamentoacademico"]
        costo = request.form["costo_inscripcion"]

        try:
            cursor.execute("""
                INSERT INTO carrera
                (idcarrera, descripcion_carrera, creditos_carrera,
                 iddepartamentoacademico, costo_inscripcion)
                VALUES (%s, %s, %s, %s, %s)
            """, (idcarrera, descripcion, creditos, iddepto, costo))
            conn.commit()
            flash("Carrera añadida correctamente.", "success")
            return redirect(url_for("list_carreras"))

        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al añadir carrera: {err}", "danger")

    cursor.close()
    conn.close()
    return render_template("carrera_form.html", carrera=None, departamentos=departamentos)


@app.route("/carreras/edit/<int:idcarrera>", methods=["GET", "POST"])
def edit_carrera(idcarrera):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_carreras"))

    cursor = conn.cursor(dictionary=True)

    # Obtener carrera
    cursor.execute("""
        SELECT * FROM carrera
        WHERE idcarrera = %s;
    """, (idcarrera,))
    carrera = cursor.fetchone()

    if not carrera:
        cursor.close()
        conn.close()
        flash("Carrera no encontrada.", "warning")
        return redirect(url_for("list_carreras"))

    # Traer departamentos académicos para select
    cursor.execute("SELECT * FROM departamentoacademico ORDER BY iddepartamentoacademico;")
    departamentos = cursor.fetchall()

    if request.method == "POST":
        descripcion = request.form["descripcion_carrera"]
        creditos = request.form["creditos_carrera"]
        iddepto = request.form["iddepartamentoacademico"]
        costo = request.form["costo_inscripcion"]

        try:
            cursor.execute("""
                UPDATE carrera
                SET descripcion_carrera = %s,
                    creditos_carrera = %s,
                    iddepartamentoacademico = %s,
                    costo_inscripcion = %s
                WHERE idcarrera = %s
            """, (descripcion, creditos, iddepto, costo, idcarrera))
            conn.commit()
            flash("Carrera actualizada correctamente.", "success")
            return redirect(url_for("list_carreras"))

        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al actualizar carrera: {err}", "danger")

    cursor.close()
    conn.close()
    return render_template("carrera_form.html", carrera=carrera, departamentos=departamentos)


@app.route("/carreras/delete/<int:idcarrera>", methods=["POST"])
def delete_carrera(idcarrera):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_carreras"))

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM carrera WHERE idcarrera = %s;", (idcarrera,))
        conn.commit()
        flash("Carrera eliminada correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar (FK activa): {err}", "danger")

    cursor.close()
    conn.close()
    return redirect(url_for("list_carreras"))
@app.route("/carreras/search")
def search_carreras():
    query_term = request.args.get("query", "")
    if not query_term:
        return redirect(url_for("list_carreras"))

    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_carreras"))

    cursor = conn.cursor(dictionary=True)
    like = f"%{query_term}%"

    cursor.execute("""
        SELECT c.idcarrera, c.descripcion_carrera, c.creditos_carrera,
               c.iddepartamentoacademico, d.nombre_departamento,
               c.costo_inscripcion
        FROM carrera c
        JOIN departamentoacademico d
            ON c.iddepartamentoacademico = d.iddepartamentoacademico
        WHERE c.descripcion_carrera LIKE %s
           OR d.nombre_departamento LIKE %s
           OR c.idcarrera LIKE %s
        ORDER BY c.idcarrera;
    """, (like, like, like))

    carreras = cursor.fetchall()
    cursor.close()
    conn.close()

    flash(f'Mostrando resultados para "{query_term}".', "info")
    return render_template("carrera_list.html", carreras=carreras)

# ---------------------------
# CRUD Asignatura x Carrera
# ---------------------------

@app.route("/asignaturaxcarrera")
def list_asignaturaxcarrera():
    conn = get_db_connection()
    if conn is None:
        return render_template("asignaturaxcarrera_list.html", relaciones=[])

    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT axc.idcarrera,
               c.descripcion_carrera,
               axc.idasignatura,
               a.nombre_asignatura
        FROM asignaturaxcarrera axc
        JOIN carrera c
          ON axc.idcarrera = c.idcarrera
        JOIN asignatura a
          ON axc.idasignatura = a.idasignatura
        ORDER BY c.descripcion_carrera, a.nombre_asignatura;
    """)
    relaciones = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("asignaturaxcarrera_list.html", relaciones=relaciones)


@app.route("/asignaturaxcarrera/add", methods=["GET", "POST"])
def add_asignaturaxcarrera():
    conn = get_db_connection()
    if conn is None:
        flash("No se pudo conectar a la base de datos.", "danger")
        return redirect(url_for("list_asignaturaxcarrera"))

    cursor = conn.cursor(dictionary=True)

    # Catálogos para los SELECT
    cursor.execute("""
        SELECT idcarrera, descripcion_carrera
        FROM carrera
        ORDER BY idcarrera;
    """)
    carreras = cursor.fetchall()

    cursor.execute("""
        SELECT idasignatura, nombre_asignatura
        FROM asignatura
        ORDER BY idasignatura;
    """)
    asignaturas = cursor.fetchall()

    if request.method == "POST":
        idcarrera = request.form.get("idcarrera")
        idasignatura = request.form.get("idasignatura")

        try:
            cursor2 = conn.cursor()
            cursor2.execute("""
                INSERT INTO asignaturaxcarrera (idcarrera, idasignatura)
                VALUES (%s, %s)
            """, (idcarrera, idasignatura))
            conn.commit()
            cursor2.close()
            flash("Asignatura asociada a la carrera correctamente.", "success")
            return redirect(url_for("list_asignaturaxcarrera"))
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al guardar la relación: {err}", "danger")

    cursor.close()
    conn.close()

    return render_template(
        "asignaturaxcarrera_form.html",
        carreras=carreras,
        asignaturas=asignaturas,
        relacion=None
    )


@app.route("/asignaturaxcarrera/delete/<int:idcarrera>/<int:idasignatura>", methods=["POST"])
def delete_asignaturaxcarrera(idcarrera, idasignatura):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_asignaturaxcarrera"))

    cursor = conn.cursor()
    try:
        cursor.execute("""
            DELETE FROM asignaturaxcarrera
            WHERE idcarrera = %s AND idasignatura = %s
        """, (idcarrera, idasignatura))
        conn.commit()
        flash("Relación eliminada correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar la relación: {err}", "danger")

    cursor.close()
    conn.close()
    return redirect(url_for("list_asignaturaxcarrera"))


@app.route("/asignaturaxcarrera/search")
def search_asignaturaxcarrera():
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("list_asignaturaxcarrera"))

    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_asignaturaxcarrera"))

    cursor = conn.cursor(dictionary=True)
    pattern = f"%{query_term}%"

    cursor.execute("""
        SELECT axc.idcarrera,
               c.descripcion_carrera,
               axc.idasignatura,
               a.nombre_asignatura
        FROM asignaturaxcarrera axc
        JOIN carrera c
          ON axc.idcarrera = c.idcarrera
        JOIN asignatura a
          ON axc.idasignatura = a.idasignatura
        WHERE c.descripcion_carrera LIKE %s
           OR a.nombre_asignatura LIKE %s
           OR axc.idcarrera LIKE %s
           OR axc.idasignatura LIKE %s
        ORDER BY c.descripcion_carrera, a.nombre_asignatura;
    """, (pattern, pattern, pattern, pattern))

    relaciones = cursor.fetchall()
    cursor.close()
    conn.close()

    flash(f'Mostrando resultados para "{query_term}".', "info")
    return render_template("asignaturaxcarrera_list.html", relaciones=relaciones)



# ---------------------------
# CRUD Departamento Académico
# ---------------------------

@app.route("/departamentos")
def list_departamentos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM departamentoacademico ORDER BY iddepartamentoacademico;")
    departamentos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("departamento_list.html", departamentos=departamentos)

@app.route("/departamentos/search")
def search_departamentos():
    """Busca departamentos académicos por ID o por nombre."""
    query_term = request.args.get("query", "").strip()

    # Si no escribieron nada, regresamos a la lista normal
    if not query_term:
        return redirect(url_for("list_departamentos"))

    conn = get_db_connection()
    if conn is None:
        flash("No se pudo conectar a la base de datos.", "danger")
        return redirect(url_for("list_departamentos"))

    cursor = conn.cursor(dictionary=True)

    # Buscamos por nombre o por ID convertido a texto
    search_pattern = f"%{query_term}%"
    cursor.execute("""
        SELECT *
        FROM departamentoacademico
        WHERE nombre_departamento LIKE %s
           OR CAST(iddepartamentoacademico AS CHAR) LIKE %s
        ORDER BY iddepartamentoacademico;
    """, (search_pattern, search_pattern))

    departamentos = cursor.fetchall()
    cursor.close()
    conn.close()

    flash(f'Mostrando resultados para "{query_term}".', "info")
    return render_template("departamento_list.html", departamentos=departamentos)

@app.route("/departamentos/add", methods=["GET", "POST"])
def add_departamento():
    if request.method == "POST":
        iddep = request.form["iddepartamentoacademico"]
        nombre = request.form["nombre_departamento"]

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO departamentoacademico (iddepartamentoacademico, nombre_departamento)
                VALUES (%s, %s)
            """, (iddep, nombre))

            conn.commit()
            flash("Departamento añadido correctamente.", "success")
            return redirect(url_for("list_departamentos"))

        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al añadir departamento: {err}", "danger")

        cursor.close()
        conn.close()

    return render_template("departamento_form.html", departamento=None)


@app.route("/departamentos/edit/<int:iddep>", methods=["GET", "POST"])
def edit_departamento(iddep):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM departamentoacademico WHERE iddepartamentoacademico = %s;",
        (iddep,)
    )
    departamento = cursor.fetchone()

    if not departamento:
        flash("Departamento no encontrado.", "warning")
        cursor.close()
        conn.close()
        return redirect(url_for("list_departamentos"))

    if request.method == "POST":
        nombre = request.form["nombre_departamento"]

        try:
            cursor.execute("""
                UPDATE departamentoacademico
                SET nombre_departamento = %s
                WHERE iddepartamentoacademico = %s
            """, (nombre, iddep))

            conn.commit()
            flash("Departamento actualizado correctamente.", "success")
            return redirect(url_for("list_departamentos"))

        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al actualizar departamento: {err}", "danger")

    cursor.close()
    conn.close()

    return render_template("departamento_form.html", departamento=departamento)


@app.route("/departamentos/delete/<int:iddep>", methods=["POST"])
def delete_departamento(iddep):
    """Elimina un departamento académico.

    Si está siendo usado como FK en otra tabla (por ejemplo, carrera),
    MySQL lanzará un error y mostramos un mensaje amable.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM departamentoacademico WHERE iddepartamentoacademico = %s",
            (iddep,)
        )
        conn.commit()
        flash("Departamento eliminado correctamente.", "success")

    except mysql.connector.Error as err:
        conn.rollback()

        # Si es por Foreign Key, mostramos un mensaje más entendible
        if err.errno == errorcode.ER_ROW_IS_REFERENCED_2:
            flash(
                "No se puede eliminar el departamento porque está siendo usado "
                "en otras tablas (por ejemplo, alguna carrera).",
                "danger"
            )
        else:
            flash(f"No se pudo eliminar: {err}", "danger")

    cursor.close()
    conn.close()
    return redirect(url_for("list_departamentos"))


# ---------------------------
# CRUD Asignatura
# ---------------------------

@app.route("/asignaturas")
def list_asignaturas():
    conn = get_db_connection()
    if conn is None:
        return render_template("asignatura_list.html", asignaturas=[])

    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            a.idasignatura,
            a.nombre_asignatura,
            a.creditos_asignatura,
            a.horas_por_sesion,
            d.nombre_deptoasignatura,   -- 👈 mismo nombre que usas en el template
            a.clave_asignatura          -- 👈 la clave que generas en add/edit
        FROM asignatura a
        LEFT JOIN departamentoasignatura d
          ON a.iddeptoasignatura = d.iddeptoasignatura
        ORDER BY a.idasignatura;
    """)
    asignaturas = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("asignatura_list.html", asignaturas=asignaturas)


@app.route("/asignaturas/add", methods=["GET", "POST"])
def add_asignatura():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_asignaturas"))

    cursor = conn.cursor(dictionary=True)

    # Cargar departamentos de asignatura para el select
    cursor.execute("""
        SELECT iddeptoasignatura, nombre_deptoasignatura
        FROM departamentoasignatura
        ORDER BY iddeptoasignatura;
    """)
    departamentos = cursor.fetchall()

    if request.method == "POST":
        idasignatura = request.form["idasignatura"]
        nombre = request.form["nombre_asignatura"]
        creditos = request.form["creditos_asignatura"]
        horas = request.form.get("horas_por_sesion") or None
        iddepto = request.form.get("iddeptoasignatura") or None

        # Generar clave_asignatura
        prefijo = "DEPT"
        if iddepto:
            cursor.execute("""
                SELECT nombre_deptoasignatura
                FROM departamentoasignatura
                WHERE iddeptoasignatura = %s
            """, (iddepto,))
            row = cursor.fetchone()
            if row and row["nombre_deptoasignatura"]:
                prefijo = row["nombre_deptoasignatura"][:4].upper()

        codigo = str(idasignatura)[:3]
        clave = f"{prefijo}{codigo}"

        try:
            cursor2 = conn.cursor()
            cursor2.execute("""
                INSERT INTO asignatura
                    (idasignatura, nombre_asignatura, creditos_asignatura,
                     horas_por_sesion, iddeptoasignatura, clave_asignatura)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (idasignatura, nombre, creditos, horas, iddepto, clave))
            conn.commit()
            cursor2.close()
            flash("Asignatura añadida correctamente.", "success")
            return redirect(url_for("list_asignaturas"))
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al añadir asignatura: {err}", "danger")

    cursor.close()
    conn.close()
    return render_template("asignatura_form.html",
                           asignatura=None,
                           departamentos=departamentos)


@app.route("/asignaturas/edit/<int:idasignatura>", methods=["GET", "POST"])
def edit_asignatura(idasignatura):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_asignaturas"))

    cursor = conn.cursor(dictionary=True)

    # Traer asignatura
    cursor.execute("""
        SELECT a.idasignatura,
               a.nombre_asignatura,
               a.creditos_asignatura,
               a.horas_por_sesion,
               a.iddeptoasignatura,
               a.clave_asignatura
        FROM asignatura a
        WHERE a.idasignatura = %s;
    """, (idasignatura,))
    asignatura = cursor.fetchone()

    if not asignatura:
        cursor.close()
        conn.close()
        flash("Asignatura no encontrada.", "warning")
        return redirect(url_for("list_asignaturas"))

    # Cargar departamentos
    cursor.execute("""
        SELECT iddeptoasignatura, nombre_deptoasignatura
        FROM departamentoasignatura
        ORDER BY iddeptoasignatura;
    """)
    departamentos = cursor.fetchall()

    if request.method == "POST":
        nombre = request.form["nombre_asignatura"]
        creditos = request.form["creditos_asignatura"]
        horas = request.form.get("horas_por_sesion") or None
        iddepto = request.form.get("iddeptoasignatura") or None

        # Recalcular clave por si cambió el departamento
        prefijo = "DEPT"
        if iddepto:
            cursor.execute("""
                SELECT nombre_deptoasignatura
                FROM departamentoasignatura
                WHERE iddeptoasignatura = %s
            """, (iddepto,))
            row = cursor.fetchone()
            if row and row["nombre_deptoasignatura"]:
                prefijo = row["nombre_deptoasignatura"][:4].upper()

        codigo = str(idasignatura)[:3]
        clave = f"{prefijo}{codigo}"

        try:
            cursor2 = conn.cursor()
            cursor2.execute("""
                UPDATE asignatura
                SET nombre_asignatura   = %s,
                    creditos_asignatura = %s,
                    horas_por_sesion    = %s,
                    iddeptoasignatura   = %s,
                    clave_asignatura    = %s
                WHERE idasignatura = %s
            """, (nombre, creditos, horas, iddepto, clave, idasignatura))
            conn.commit()
            cursor2.close()
            flash("Asignatura actualizada correctamente.", "success")
            return redirect(url_for("list_asignaturas"))
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al actualizar asignatura: {err}", "danger")

    cursor.close()
    conn.close()
    return render_template("asignatura_form.html",
                           asignatura=asignatura,
                           departamentos=departamentos)


@app.route("/asignaturas/delete/<int:idasignatura>", methods=["POST"])
def delete_asignatura(idasignatura):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_asignaturas"))

    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM asignatura WHERE idasignatura = %s;",
            (idasignatura,)
        )
        conn.commit()
        flash("Asignatura eliminada correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar la asignatura: {err}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("list_asignaturas"))


# ---------------------------
# CRUD Tipo de Beca
# ---------------------------

@app.route("/tipobeca")
def list_tipobeca():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT idtipo_beca, nombre_tipo
        FROM tipo_beca
        ORDER BY idtipo_beca;
    """)
    tipos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("tipobeca_list.html", tipos=tipos)


@app.route("/tipobeca/add", methods=["GET", "POST"])
def add_tipobeca():
    if request.method == "POST":
        idtipo = request.form["idtipo_beca"]
        nombre = request.form["nombre_tipo"]

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO tipo_beca (idtipo_beca, nombre_tipo)
                VALUES (%s, %s)
            """, (idtipo, nombre))

            conn.commit()
            flash("Tipo de beca añadido correctamente.", "success")
            return redirect(url_for("list_tipobeca"))

        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al añadir tipo de beca: {err}", "danger")

        cursor.close()
        conn.close()

    return render_template("tipobeca_form.html", tipo=None)


@app.route("/tipobeca/edit/<int:idtipo>", methods=["GET", "POST"])
def edit_tipobeca(idtipo):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tipo_beca WHERE idtipo_beca = %s", (idtipo,))
    tipo = cursor.fetchone()

    if not tipo:
        flash("Tipo de beca no encontrado.", "warning")
        return redirect(url_for("list_tipobeca"))

    if request.method == "POST":
        nombre = request.form["nombre_tipo"]

        try:
            cursor.execute("""
                UPDATE tipo_beca
                SET nombre_tipo = %s
                WHERE idtipo_beca = %s
            """, (nombre, idtipo))

            conn.commit()
            flash("Tipo de beca actualizado correctamente.", "success")
            return redirect(url_for("list_tipobeca"))

        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al actualizar tipo de beca: {err}", "danger")

    cursor.close()
    conn.close()

    return render_template("tipobeca_form.html", tipo=tipo)


@app.route("/tipobeca/delete/<int:idtipo>", methods=["POST"])
def delete_tipobeca(idtipo):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM tipo_beca WHERE idtipo_beca = %s", (idtipo,))
        conn.commit()
        flash("Tipo de beca eliminado correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar: {err}", "danger")

    cursor.close()
    conn.close()

    return redirect(url_for("list_tipobeca"))


@app.route("/tipobeca/search")
def search_tipobeca():
    query_term = request.args.get("query", "")
    if not query_term:
        return redirect(url_for("list_tipobeca"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    patron = f"%{query_term}%"

    cursor.execute("""
        SELECT idtipo_beca, nombre_tipo
        FROM tipo_beca
        WHERE nombre_tipo LIKE %s
           OR idtipo_beca LIKE %s
        ORDER BY idtipo_beca;
    """, (patron, patron))

    tipos = cursor.fetchall()

    cursor.close()
    conn.close()

    flash(f'Resultados para "{query_term}".', "info")
    return render_template("tipobeca_list.html", tipos=tipos)

# ---------------------------
# CRUD Beca
# ---------------------------

@app.route("/becas")
def list_becas():
    conn = get_db_connection()
    if conn is None:
        return render_template("beca_list.html", becas=[])

    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.idbeca,
               b.descripcion_beca,
               b.porcentaje_beca,
               b.estatus_beca,
               b.idtipo_beca,
               t.nombre_tipo
        FROM beca b
        LEFT JOIN tipo_beca t
          ON b.idtipo_beca = t.idtipo_beca
        ORDER BY b.idbeca;
    """)
    becas = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("beca_list.html", becas=becas)


@app.route("/becas/add", methods=["GET", "POST"])
def add_beca():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_becas"))

    cursor = conn.cursor(dictionary=True)

    # Cargar tipos de beca para el combo
    cursor.execute("SELECT idtipo_beca, nombre_tipo FROM tipo_beca ORDER BY idtipo_beca;")
    tipos = cursor.fetchall()

    if request.method == "POST":
        idbeca = request.form["idbeca"]
        descripcion = request.form["descripcion_beca"]
        porcentaje = request.form.get("porcentaje_beca") or None
        estatus = request.form.get("estatus_beca") or None
        idtipo_beca = request.form.get("idtipo_beca") or None

        try:
            cursor2 = conn.cursor()
            cursor2.execute("""
                INSERT INTO beca
                (idbeca, descripcion_beca, porcentaje_beca, estatus_beca, idtipo_beca)
                VALUES (%s, %s, %s, %s, %s)
            """, (idbeca, descripcion, porcentaje, estatus, idtipo_beca))
            conn.commit()
            cursor2.close()
            flash("Beca añadida correctamente.", "success")
            return redirect(url_for("list_becas"))
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al añadir beca: {err}", "danger")

    cursor.close()
    conn.close()
    return render_template("beca_form.html", beca=None, tipos_beca=tipos)


@app.route("/becas/edit/<int:idbeca>", methods=["GET", "POST"])
def edit_beca(idbeca):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_becas"))

    cursor = conn.cursor(dictionary=True)

    # Traer beca
    cursor.execute("""
        SELECT b.idbeca, b.descripcion_beca, b.porcentaje_beca,
               b.estatus_beca, b.idtipo_beca
        FROM beca b
        WHERE b.idbeca = %s;
    """, (idbeca,))
    beca = cursor.fetchone()

    if not beca:
        flash("Beca no encontrada.", "warning")
        cursor.close()
        conn.close()
        return redirect(url_for("list_becas"))

    # Cargar tipos de beca
    cursor.execute("SELECT idtipo_beca, nombre_tipo FROM tipo_beca ORDER BY idtipo_beca;")
    tipos = cursor.fetchall()

    if request.method == "POST":
        descripcion = request.form["descripcion_beca"]
        porcentaje = request.form.get("porcentaje_beca") or None
        estatus = request.form.get("estatus_beca") or None
        idtipo_beca = request.form.get("idtipo_beca") or None

        try:
            cursor2 = conn.cursor()
            cursor2.execute("""
                UPDATE beca
                SET descripcion_beca = %s,
                    porcentaje_beca = %s,
                    estatus_beca = %s,
                    idtipo_beca = %s
                WHERE idbeca = %s
            """, (descripcion, porcentaje, estatus, idtipo_beca, idbeca))
            conn.commit()
            cursor2.close()
            flash("Beca actualizada correctamente.", "success")
            return redirect(url_for("list_becas"))
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al actualizar beca: {err}", "danger")

    cursor.close()
    conn.close()
    return render_template("beca_form.html", beca=beca, tipos_beca=tipos)



@app.route("/becas/delete/<int:idbeca>", methods=["POST"])
def delete_beca(idbeca):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_becas"))

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM beca WHERE idbeca = %s;", (idbeca,))
        conn.commit()
        flash("Beca eliminada correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar la beca: {err}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("list_becas"))


@app.route("/becas/search")
def search_becas():
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("list_becas"))

    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_becas"))

    cursor = conn.cursor(dictionary=True)
    patron = f"%{query_term}%"

    cursor.execute("""
        SELECT b.idbeca,
               b.descripcion_beca,
               b.porcentaje_beca,
               b.estatus_beca,
               b.idtipo_beca,
               t.nombre_tipo
        FROM beca b
        LEFT JOIN tipo_beca t ON b.idtipo_beca = t.idtipo_beca
        WHERE b.descripcion_beca LIKE %s
           OR b.estatus_beca LIKE %s
           OR t.nombre_tipo LIKE %s
        ORDER BY b.idbeca;
    """, (patron, patron, patron))

    becas = cursor.fetchall()
    cursor.close()
    conn.close()

    flash(f'Mostrando resultados para "{query_term}".', "info")
    return render_template("beca_list.html", becas=becas)

# ---------------------------
# CRUD Departamento de Asignatura
# ---------------------------

@app.route("/departamentos_asignatura")
def list_departamentos_asignatura():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT iddeptoasignatura, nombre_deptoasignatura
        FROM departamentoasignatura
        ORDER BY iddeptoasignatura;
    """)
    departamentos = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("departamentoasignatura_list.html", departamentos=departamentos)


@app.route("/departamentos_asignatura/add", methods=["GET", "POST"])
def add_departamento_asignatura():
    if request.method == "POST":
        iddep = request.form["iddeptoasignatura"]
        nombre = request.form["nombre_deptoasignatura"]

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO departamentoasignatura
                (iddeptoasignatura, nombre_deptoasignatura)
                VALUES (%s, %s)
            """, (iddep, nombre))

            conn.commit()
            flash("Departamento de asignatura añadido correctamente.", "success")
            return redirect(url_for("list_departamentos_asignatura"))
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al añadir: {err}", "danger")

        cursor.close()
        conn.close()

    return render_template("departamentoasignatura_form.html", departamento=None)


@app.route("/departamentos_asignatura/edit/<int:iddep>", methods=["GET", "POST"])
def edit_departamento_asignatura(iddep):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM departamentoasignatura
        WHERE iddeptoasignatura = %s;
    """, (iddep,))
    departamento = cursor.fetchone()

    if not departamento:
        flash("Departamento no encontrado.", "warning")
        return redirect(url_for("list_departamentos_asignatura"))

    if request.method == "POST":
        nombre = request.form["nombre_deptoasignatura"]

        try:
            cursor2 = conn.cursor()
            cursor2.execute("""
                UPDATE departamentoasignatura
                SET nombre_deptoasignatura = %s
                WHERE iddeptoasignatura = %s
            """, (nombre, iddep))
            conn.commit()
            flash("Departamento de asignatura actualizado correctamente.", "success")
            return redirect(url_for("list_departamentos_asignatura"))
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al actualizar: {err}", "danger")

    cursor.close()
    conn.close()
    return render_template("departamentoasignatura_form.html", departamento=departamento)


@app.route("/departamentos_asignatura/delete/<int:iddep>", methods=["POST"])
def delete_departamento_asignatura(iddep):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM departamentoasignatura
            WHERE iddeptoasignatura = %s
        """, (iddep,))
        conn.commit()
        flash("Departamento de asignatura eliminado.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar: {err}", "danger")

    cursor.close()
    conn.close()
    return redirect(url_for("list_departamentos_asignatura"))


# ---------------------------
# BUSCAR DEPARTAMENTO
# ---------------------------

@app.route("/departamentos_asignatura/search")
def search_departamentos_asignatura():
    term = request.args.get("query", "")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM departamentoasignatura
        WHERE nombre_deptoasignatura LIKE %s
           OR iddeptoasignatura LIKE %s
        ORDER BY iddeptoasignatura;
    """, (f"%{term}%", f"%{term}%"))

    resultados = cursor.fetchall()
    cursor.close()
    conn.close()

    flash(f'Resultados para "{term}"', "info")
    return render_template("departamentoasignatura_list.html", departamentos=resultados)





# --- Iniciar la Aplicación ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
