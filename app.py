import os
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import mysql.connector
from utils.auth import login_required, role_required




# --- Importar CRUDs y conexión DB ---
from utils.db import get_db_connection
from utils.estudiantes import students_crud
from utils.cursos import carreras_crud, asignaturas_crud, asignaturaxcarrera_crud
from utils.aulas_horarios import departamentos_crud, departamentoasignatura_crud
from utils.finanzas_becas import becas_crud, tipobeca_crud

# --- CONFIGURACIÓN ---
load_dotenv()

# --- App de Flask ---
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "a-super-secret-key")

# Inicializar flask bcrypt
bcrypt = Bcrypt(app)
app.secret_key = "SUPER_CLAVE_SESION"

# --- Rutas para Estudiantes ---

@app.route('/')
def index():
    """Muestra la lista de todos los estudiantes."""
    conn = get_db_connection()
    if conn is None:
        return render_template('index.html', students=[])
    
    cursor = conn.cursor(dictionary=True)
    students = students_crud.list_students(cursor)
    cursor.close()
    conn.close()
    
    return render_template('estudiantes/index.html', students=students)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    """Añade un nuevo estudiante."""
    if request.method == 'POST':
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
            conn.start_transaction()
            students_crud.add_student(cursor, matricula, nombre, apellido_paterno, apellido_materno, correo)
            conn.commit()
            flash('Estudiante añadido correctamente.', 'success')
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f'Error al añadir estudiante: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('index'))

    return render_template('estudiantes/student_form.html', student=None)

@app.route('/edit/<int:matricula>', methods=['GET', 'POST'])
def edit_student(matricula):
    """Edita la información de un estudiante."""
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('index'))

    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido_paterno = request.form['apellido_paterno']
        apellido_materno = request.form['apellido_materno']
        correo = request.form['correo']
        
        try:
            if students_crud.update_student(cursor, matricula, nombre, apellido_paterno, apellido_materno, correo):
                conn.commit()
                flash('Estudiante actualizado correctamente.', 'success')
            else:
                flash('No se encontró el estudiante para actualizar.', 'warning')
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f'Error al actualizar: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('index'))

    # GET
    student = students_crud.get_student(cursor, matricula)
    cursor.close()
    conn.close()

    if student:
        student_dict = dict(zip(cursor.column_names, student)) if not isinstance(student, dict) else student
        return render_template('estudiantes/student_form.html', student=student_dict, matricula=matricula)
    else:
        flash('Estudiante no encontrado.', 'warning')
        return redirect(url_for('index'))


@app.route('/delete/<int:matricula>', methods=['POST'])
def delete_student(matricula):
    """Elimina un estudiante."""
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('index'))

    cursor = conn.cursor()
    try:
        conn.start_transaction()
        if students_crud.delete_student(cursor, matricula):
            conn.commit()
            flash('Estudiante eliminado correctamente.', 'success')
        else:
            flash('Estudiante no encontrado para eliminar.', 'warning')
            conn.rollback()
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f'Error al eliminar estudiante: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('index'))

@app.route('/search')
def search_student():
    """Busca estudiantes."""
    query_term = request.args.get('query', '')
    if not query_term:
        return redirect(url_for('index'))

    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('index'))

    cursor = conn.cursor(dictionary=True)
    students = students_crud.search_student(cursor, query_term)
    cursor.close()
    conn.close()

    flash(f'Mostrando resultados para "{query_term}".', 'info')
    return render_template('estudiantes/index.html', students=students)


@app.route('/placeholder/<section>')
def placeholder(section):
    """Ruta para secciones en construcción."""
    return render_template('placeholder.html', section_name=section.replace('_', ' ').title())


# --- Rutas para Carreras ---

@app.route("/cursos_planes/carreras")
def list_carreras():
    conn = get_db_connection()
    if conn is None:
        return render_template("carrera_list.html", carreras=[])

    cursor = conn.cursor(dictionary=True)
    carreras = carreras_crud.list_carreras(cursor)
    cursor.close()
    conn.close()
    return render_template("cursos/carrera_list.html", carreras=carreras)

@app.route("/cursos_planes/carreras/add", methods=["GET", "POST"])
def add_carrera():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_carreras"))
    
    cursor = conn.cursor(dictionary=True)
    
    if request.method == "POST":
        idcarrera = request.form["idcarrera"]
        descripcion = request.form["descripcion_carrera"]
        creditos = request.form["creditos_carrera"]
        iddepto = request.form["iddepartamentoacademico"]
        costo = request.form["costo_inscripcion"]

        try:
            carreras_crud.add_carrera(cursor, idcarrera, descripcion, creditos, iddepto, costo)
            conn.commit()
            flash("Carrera añadida correctamente.", "success")
            return redirect(url_for("list_carreras"))
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al añadir carrera: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
    
    # GET
    departamentos = carreras_crud.get_departamentos(cursor)
    cursor.close()
    conn.close()
    return render_template("cursos/carrera_form.html", carrera=None, departamentos=departamentos)

@app.route("/cursos_planes/carreras/edit/<int:idcarrera>", methods=["GET", "POST"])
def edit_carrera(idcarrera):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_carreras"))

    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        descripcion = request.form["descripcion_carrera"]
        creditos = request.form["creditos_carrera"]
        iddepto = request.form["iddepartamentoacademico"]
        costo = request.form["costo_inscripcion"]

        try:
            carreras_crud.update_carrera(cursor, idcarrera, descripcion, creditos, iddepto, costo)
            conn.commit()
            flash("Carrera actualizada correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al actualizar carrera: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_carreras"))

    # GET
    carrera = carreras_crud.get_carrera(cursor, idcarrera)
    if not carrera:
        flash("Carrera no encontrada.", "warning")
        cursor.close()
        conn.close()
        return redirect(url_for("list_carreras"))
    
    departamentos = carreras_crud.get_departamentos(cursor)
    cursor.close()
    conn.close()
    return render_template("cursos/carrera_form.html", carrera=carrera, departamentos=departamentos)

@app.route("/cursos_planes/carreras/delete/<int:idcarrera>", methods=["POST"])
def delete_carrera(idcarrera):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_carreras"))

    cursor = conn.cursor()
    try:
        carreras_crud.delete_carrera(cursor, idcarrera)
        conn.commit()
        flash("Carrera eliminada correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar (FK activa): {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_carreras"))

@app.route("/cursos_planes/carreras/search")
def search_carreras():
    query_term = request.args.get("query", "")
    if not query_term:
        return redirect(url_for("list_carreras"))

    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_carreras"))

    cursor = conn.cursor(dictionary=True)
    carreras = carreras_crud.search_carreras(cursor, query_term)
    cursor.close()
    conn.close()

    flash(f'Mostrando resultados para "{query_term}".', "info")
    return render_template("cursos/carrera_list.html", carreras=carreras)


# --- Rutas para Asignatura x Carrera ---

@app.route("/cursos_planes/asignaturaxcarrera")
def list_asignaturaxcarrera():
    conn = get_db_connection()
    if conn is None:
        return render_template("asignaturaxcarrera_list.html", relaciones=[])

    cursor = conn.cursor(dictionary=True)
    relaciones = asignaturaxcarrera_crud.list_asignaturaxcarrera(cursor)
    cursor.close()
    conn.close()
    return render_template("cursos/asignaturaxcarrera_list.html", relaciones=relaciones)

@app.route("/cursos_planes/asignaturaxcarrera/add", methods=["GET", "POST"])
def add_asignaturaxcarrera():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_asignaturaxcarrera"))

    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        idcarrera = request.form.get("idcarrera")
        idasignatura = request.form.get("idasignatura")

        try:
            asignaturaxcarrera_crud.add_asignaturaxcarrera(cursor, idcarrera, idasignatura)
            conn.commit()
            flash("Asignatura asociada a la carrera correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al guardar la relación: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_asignaturaxcarrera"))

    # GET
    carreras = asignaturaxcarrera_crud.get_carreras(cursor)
    asignaturas = asignaturaxcarrera_crud.get_asignaturas(cursor)
    cursor.close()
    conn.close()
    return render_template("cursos/asignaturaxcarrera_form.html", carreras=carreras, asignaturas=asignaturas, relacion=None)

@app.route("/cursos_planes/asignaturaxcarrera/delete/<int:idcarrera>/<int:idasignatura>", methods=["POST"])
def delete_asignaturaxcarrera(idcarrera, idasignatura):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_asignaturaxcarrera"))

    cursor = conn.cursor()
    try:
        asignaturaxcarrera_crud.delete_asignaturaxcarrera(cursor, idcarrera, idasignatura)
        conn.commit()
        flash("Relación eliminada correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar la relación: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_asignaturaxcarrera"))

@app.route("/cursos_planes/asignaturaxcarrera/search")
def search_asignaturaxcarrera():
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("list_asignaturaxcarrera"))

    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_asignaturaxcarrera"))

    cursor = conn.cursor(dictionary=True)
    relaciones = asignaturaxcarrera_crud.search_asignaturaxcarrera(cursor, query_term)
    cursor.close()
    conn.close()
    flash(f'Mostrando resultados para "{query_term}".', "info")
    return render_template("cursos/asignaturaxcarrera_list.html", relaciones=relaciones)


# --- Rutas para Departamento Académico ---

@app.route("/aulas_horarios/departamentos")
def list_departamentos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    departamentos = departamentos_crud.list_departamentos(cursor)
    cursor.close()
    conn.close()
    return render_template("aulas_horarios/departamento_list.html", departamentos=departamentos)

@app.route("/aulas_horarios/departamentos/add", methods=["GET", "POST"])
def add_departamento():
    if request.method == "POST":
        iddep = request.form["iddepartamentoacademico"]
        nombre = request.form["nombre_departamento"]

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            departamentos_crud.add_departamento(cursor, iddep, nombre)
            conn.commit()
            flash("Departamento añadido correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al añadir departamento: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_departamentos"))

    return render_template("aulas_horarios/departamento_form.html", departamento=None)

@app.route("/aulas_horarios/departamentos/edit/<int:iddep>", methods=["GET", "POST"])
def edit_departamento(iddep):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        nombre = request.form["nombre_departamento"]
        try:
            departamentos_crud.update_departamento(cursor, iddep, nombre)
            conn.commit()
            flash("Departamento actualizado correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al actualizar departamento: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_departamentos"))

    # GET
    departamento = departamentos_crud.get_departamento(cursor, iddep)
    cursor.close()
    conn.close()
    if not departamento:
        flash("Departamento no encontrado.", "warning")
        return redirect(url_for("list_departamentos"))
    return render_template("aulas_horarios/departamento_form.html", departamento=departamento)

@app.route("/aulas_horarios/departamentos/delete/<int:iddep>", methods=["POST"])
def delete_departamento(iddep):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        departamentos_crud.delete_departamento(cursor, iddep)
        conn.commit()
        flash("Departamento eliminado correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_departamentos"))

@app.route("/aulas_horarios/departamentos/search")
def search_departamentos():
    query_term = request.args.get("query", "")
    if not query_term:
        return redirect(url_for("list_departamentos"))

    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_departamentos"))

    cursor = conn.cursor(dictionary=True)
    departamentos = departamentos_crud.search_departamentos(cursor, query_term)
    cursor.close()
    conn.close()
    flash(f'Mostrando resultados para "{query_term}".', "info")
    return render_template("aulas_horarios/departamento_list.html", departamentos=departamentos)


# --- Rutas para Asignatura ---

@app.route("/cursos_planes/asignaturas")
def list_asignaturas():
    conn = get_db_connection()
    if conn is None:
        return render_template("asignatura_list.html", asignaturas=[])

    cursor = conn.cursor(dictionary=True)
    asignaturas = asignaturas_crud.list_asignaturas(cursor)
    cursor.close()
    conn.close()
    return render_template("cursos/asignatura_list.html", asignaturas=asignaturas)

@app.route("/cursos_planes/asignaturas/add", methods=["GET", "POST"])
def add_asignatura():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_asignaturas"))
    
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        idasignatura = request.form["idasignatura"]
        nombre = request.form["nombre_asignatura"]
        creditos = request.form["creditos_asignatura"]
        horas = request.form.get("horas_por_sesion") or None
        iddepto = request.form.get("iddeptoasignatura") or None

        try:
            asignaturas_crud.add_asignatura(cursor, idasignatura, nombre, creditos, horas, iddepto)
            conn.commit()
            flash("Asignatura añadida correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al añadir asignatura: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_asignaturas"))

    # GET
    departamentos = asignaturas_crud.get_departamentos_asignatura(cursor)
    cursor.close()
    conn.close()
    return render_template("cursos/asignatura_form.html", asignatura=None, departamentos=departamentos)


@app.route("/cursos_planes/asignaturas/edit/<int:idasignatura>", methods=["GET", "POST"])
def edit_asignatura(idasignatura):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_asignaturas"))

    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        nombre = request.form["nombre_asignatura"]
        creditos = request.form["creditos_asignatura"]
        horas = request.form.get("horas_por_sesion") or None
        iddepto = request.form.get("iddeptoasignatura") or None

        try:
            asignaturas_crud.update_asignatura(cursor, idasignatura, nombre, creditos, horas, iddepto)
            conn.commit()
            flash("Asignatura actualizada correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al actualizar asignatura: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_asignaturas"))

    # GET
    asignatura = asignaturas_crud.get_asignatura(cursor, idasignatura)
    if not asignatura:
        flash("Asignatura no encontrada.", "warning")
        cursor.close()
        conn.close()
        return redirect(url_for("list_asignaturas"))
    
    departamentos = asignaturas_crud.get_departamentos_asignatura(cursor)
    cursor.close()
    conn.close()
    return render_template("cursos/asignatura_form.html", asignatura=asignatura, departamentos=departamentos)

@app.route("/cursos_planes/asignaturas/delete/<int:idasignatura>", methods=["POST"])
def delete_asignatura(idasignatura):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_asignaturas"))

    cursor = conn.cursor()
    try:
        asignaturas_crud.delete_asignatura(cursor, idasignatura)
        conn.commit()
        flash("Asignatura eliminada correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar la asignatura: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_asignaturas"))


# --- Rutas para Tipo de Beca ---

@app.route("/finanzas_becas/tipobeca")
def list_tipobeca():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    tipos = tipobeca_crud.list_tipobeca(cursor)
    cursor.close()
    conn.close()
    return render_template("finanzas_becas/tipobeca_list.html", tipos=tipos)

@app.route("/finanzas_becas/tipobeca/add", methods=["GET", "POST"])
def add_tipobeca():
    if request.method == "POST":
        idtipo = request.form["idtipo_beca"]
        nombre = request.form["nombre_tipo"]
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            tipobeca_crud.add_tipobeca(cursor, idtipo, nombre)
            conn.commit()
            flash("Tipo de beca añadido correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al añadir tipo de beca: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_tipobeca"))
    return render_template("finanzas_becas/tipobeca_form.html", tipo=None)

@app.route("/finanzas_becas/tipobeca/edit/<int:idtipo>", methods=["GET", "POST"])
def edit_tipobeca(idtipo):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        nombre = request.form["nombre_tipo"]
        try:
            tipobeca_crud.update_tipobeca(cursor, idtipo, nombre)
            conn.commit()
            flash("Tipo de beca actualizado correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al actualizar tipo de beca: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_tipobeca"))

    # GET
    tipo = tipobeca_crud.get_tipobeca(cursor, idtipo)
    cursor.close()
    conn.close()
    if not tipo:
        flash("Tipo de beca no encontrado.", "warning")
        return redirect(url_for("list_tipobeca"))
    return render_template("finanzas_becas/tipobeca_form.html", tipo=tipo)

@app.route("/finanzas_becas/tipobeca/delete/<int:idtipo>", methods=["POST"])
def delete_tipobeca(idtipo):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        tipobeca_crud.delete_tipobeca(cursor, idtipo)
        conn.commit()
        flash("Tipo de beca eliminado correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_tipobeca"))

@app.route("/finanzas_becas/tipobeca/search")
def search_tipobeca():
    query_term = request.args.get("query", "")
    if not query_term:
        return redirect(url_for("list_tipobeca"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    tipos = tipobeca_crud.search_tipobeca(cursor, query_term)
    cursor.close()
    conn.close()
    flash(f'Resultados para "{query_term}".', "info")
    return render_template("finanzas_becas/tipobeca_list.html", tipos=tipos)


# --- Rutas para Beca ---

@app.route("/finanzas_becas/becas")
@role_required("finanzas_becas")
def list_becas():
    conn = get_db_connection()
    if conn is None:
        return render_template("beca_list.html", becas=[])
    cursor = conn.cursor(dictionary=True)
    becas = becas_crud.list_becas(cursor)
    cursor.close()
    conn.close()
    return render_template("finanzas_becas/beca_list.html", becas=becas)

@app.route("/finanzas_becas/becas/add", methods=["GET", "POST"])
def add_beca():
    conn = get_db_connection()
    if conn is None: return redirect(url_for("list_becas"))
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        idbeca = request.form["idbeca"]
        descripcion = request.form["descripcion_beca"]
        porcentaje = request.form.get("porcentaje_beca") or None
        estatus = request.form.get("estatus_beca") or None
        idtipo_beca = request.form.get("idtipo_beca") or None

        try:
            becas_crud.add_beca(cursor, idbeca, descripcion, porcentaje, estatus, idtipo_beca)
            conn.commit()
            flash("Beca añadida correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al añadir beca: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_becas"))

    # GET
    tipos_beca = becas_crud.get_tipos_beca(cursor)
    cursor.close()
    conn.close()
    return render_template("finanzas_becas/beca_form.html", beca=None, tipos_beca=tipos_beca)


@app.route("/finanzas_becas/becas/edit/<int:idbeca>", methods=["GET", "POST"])
def edit_beca(idbeca):
    conn = get_db_connection()
    if conn is None: return redirect(url_for("list_becas"))
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        descripcion = request.form["descripcion_beca"]
        porcentaje = request.form.get("porcentaje_beca") or None
        estatus = request.form.get("estatus_beca") or None
        idtipo_beca = request.form.get("idtipo_beca") or None

        try:
            becas_crud.update_beca(cursor, idbeca, descripcion, porcentaje, estatus, idtipo_beca)
            conn.commit()
            flash("Beca actualizada correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al actualizar beca: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_becas"))

    # GET
    beca = becas_crud.get_beca(cursor, idbeca)
    if not beca:
        flash("Beca no encontrada.", "warning")
        cursor.close()
        conn.close()
        return redirect(url_for("list_becas"))
    
    tipos_beca = becas_crud.get_tipos_beca(cursor)
    cursor.close()
    conn.close()
    return render_template("finanzas_becas/beca_form.html", beca=beca, tipos_beca=tipos_beca)

@app.route("/finanzas_becas/becas/delete/<int:idbeca>", methods=["POST"])
def delete_beca(idbeca):
    conn = get_db_connection()
    if conn is None: return redirect(url_for("list_becas"))
    cursor = conn.cursor()
    try:
        becas_crud.delete_beca(cursor, idbeca)
        conn.commit()
        flash("Beca eliminada correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar la beca: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_becas"))

@app.route("/finanzas_becas/becas/search")
def search_becas():
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("list_becas"))

    conn = get_db_connection()
    if conn is None: return redirect(url_for("list_becas"))

    cursor = conn.cursor(dictionary=True)
    becas = becas_crud.search_becas(cursor, query_term)
    cursor.close()
    conn.close()
    flash(f'Mostrando resultados para "{query_term}".', "info")
    return render_template("finanzas_becas/beca_list.html", becas=becas)


# --- Rutas para Departamento de Asignatura ---

@app.route("/aulas_horarios/departamentos_asignatura")
def list_departamentos_asignatura():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    departamentos = departamentoasignatura_crud.list_departamentos_asignatura(cursor)
    cursor.close()
    conn.close()
    return render_template("aulas_horarios/departamentoasignatura_list.html", departamentos=departamentos)

@app.route("/aulas_horarios/departamentos_asignatura/add", methods=["GET", "POST"])
def add_departamento_asignatura():
    if request.method == "POST":
        iddep = request.form["iddeptoasignatura"]
        nombre = request.form["nombre_deptoasignatura"]
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            departamentoasignatura_crud.add_departamento_asignatura(cursor, iddep, nombre)
            conn.commit()
            flash("Departamento de asignatura añadido correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al añadir: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_departamentos_asignatura"))
    return render_template("aulas_horarios/departamentoasignatura_form.html", departamento=None)

@app.route("/aulas_horarios/departamentos_asignatura/edit/<int:iddep>", methods=["GET", "POST"])
def edit_departamento_asignatura(iddep):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        nombre = request.form["nombre_deptoasignatura"]
        try:
            departamentoasignatura_crud.update_departamento_asignatura(cursor, iddep, nombre)
            conn.commit()
            flash("Departamento de asignatura actualizado correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al actualizar: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_departamentos_asignatura"))

    # GET
    departamento = departamentoasignatura_crud.get_departamento_asignatura(cursor, iddep)
    cursor.close()
    conn.close()
    if not departamento:
        flash("Departamento no encontrado.", "warning")
        return redirect(url_for("list_departamentos_asignatura"))
    return render_template("departamentoasignatura_form.html", departamento=departamento)

@app.route("/aulas_horarios/departamentos_asignatura/delete/<int:iddep>", methods=["POST"])
def delete_departamento_asignatura(iddep):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        departamentoasignatura_crud.delete_departamento_asignatura(cursor, iddep)
        conn.commit()
        flash("Departamento de asignatura eliminado.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_departamentos_asignatura"))

@app.route("/aulas_horarios/departamentos_asignatura/search")
def search_departamentos_asignatura():
    term = request.args.get("query", "")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    resultados = departamentoasignatura_crud.search_departamentos_asignatura(cursor, term)
    cursor.close()
    conn.close()
    flash(f'Resultados para "{term}"', "info")
    return render_template("departamentoasignatura_list.html", departamentos=resultados)


# --- Iniciar la Aplicación ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)


# ruta de login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password_form = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
        user = cursor.fetchone()
        print("Usuario obtenido:", user)

        if user and user["password"] == password_form:
            # Si estás usando bcrypt, cambiar por:
            # if bcrypt.check_password_hash(user["password"], password_form):

            session["user_id"] = user["idusuario"]
            session["user_email"] = user["email"]
            session["user_rol"] = user["rol"]

            return redirect(url_for("index"))
        else:
            flash("Credenciales incorrectas", "danger")

    return render_template("login.html")



# ruta de logout
@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("login"))

