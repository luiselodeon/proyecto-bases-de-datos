import os
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import mysql.connector
from utils.auth import login_required, role_required




# --- Importar CRUDs y conexión DB ---
from utils.db import get_db_connection
from utils.estudiantes import students_crud, historialacademico_crud, inscripcion_crud
from utils.cursos import carreras_crud, asignaturas_crud, periodoinscripciones_crud, prerequisito_crud
from utils.aulas_horarios import departamentos_crud, departamentoasignatura_crud, aula_crud, horario_crud
from utils.docentes import docente_crud, claseprogramada_crud, capacitacion_crud
from utils.calificaciones import calificacion_estudiante_crud, evaluacion_crud
from utils.finanzas_becas import becas_crud, tipobeca_crud, pago_crud, estadodecuenta_crud
from utils.asistencia import asistencia_crud
from utils.admin import usuarios_crud

# --- CONFIGURACIÓN ---
load_dotenv()

# --- App de Flask ---
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "a-super-secret-key")

# Inicializar flask bcrypt
bcrypt = Bcrypt(app)
app.secret_key = "SUPER_CLAVE_SESION"

# --- Rutas para Estudiantes ---

@app.route('/gestion_estudiantes/registro_consulta')
def index():
    """Muestra la lista de todos los estudiantes."""
    conn = get_db_connection()
    if conn is None:
        return render_template('registro_consulta.html', students=[])
    
    cursor = conn.cursor(dictionary=True)
    students = students_crud.list_students(cursor)
    cursor.close()
    conn.close()
    
    return render_template('estudiantes/registro_consulta.html', students=students)

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
    return render_template('estudiantes/registro_consulta.html', students=students)


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


# --- Rutas para Calificación Estudiante ---

@app.route("/calificaciones/calificacion_estudiante")
def list_calificacion_estudiante():
    conn = get_db_connection()
    if conn is None:
        return render_template("calificaciones/calificacion_estudiante_list.html", calificaciones=[])
    
    cursor = conn.cursor(dictionary=True)
    calificaciones = calificacion_estudiante_crud.list_calificaciones(cursor)
    cursor.close()
    conn.close()
    return render_template("calificaciones/calificacion_estudiante_list.html", calificaciones=calificaciones)

@app.route("/calificaciones/calificacion_estudiante/add", methods=["GET", "POST"])
def add_calificacion_estudiante():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_calificacion_estudiante"))
    
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        idevaluacion = request.form["idevaluacion"]
        idinscripcion = request.form["idinscripcion"]
        calificacion = request.form["calificacion"]
        observaciones = request.form["observaciones"]

        try:
            calificacion_estudiante_crud.add_calificacion(cursor, idevaluacion, idinscripcion, calificacion, observaciones)
            conn.commit()
            flash("Calificación añadida correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al añadir calificación: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_calificacion_estudiante"))

    # GET
    evaluaciones = calificacion_estudiante_crud.get_evaluaciones(cursor)
    inscripciones = calificacion_estudiante_crud.get_inscripciones(cursor)
    cursor.close()
    conn.close()
    return render_template("calificaciones/calificacion_estudiante_form.html", calificacion=None, evaluaciones=evaluaciones, inscripciones=inscripciones)

@app.route("/calificaciones/calificacion_estudiante/edit/<int:idevaluacion>/<int:idinscripcion>", methods=["GET", "POST"])
def edit_calificacion_estudiante(idevaluacion, idinscripcion):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_calificacion_estudiante"))
    
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        calificacion = request.form["calificacion"]
        observaciones = request.form["observaciones"]

        try:
            calificacion_estudiante_crud.update_calificacion(cursor, idevaluacion, idinscripcion, calificacion, observaciones)
            conn.commit()
            flash("Calificación actualizada correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al actualizar calificación: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_calificacion_estudiante"))

    # GET
    calificacion = calificacion_estudiante_crud.get_calificacion(cursor, idevaluacion, idinscripcion)
    if not calificacion:
        flash("Calificación no encontrada.", "warning")
        cursor.close()
        conn.close()
        return redirect(url_for("list_calificacion_estudiante"))

    evaluaciones = calificacion_estudiante_crud.get_evaluaciones(cursor)
    inscripciones = calificacion_estudiante_crud.get_inscripciones(cursor)
    cursor.close()
    conn.close()
    return render_template("calificaciones/calificacion_estudiante_form.html", calificacion=calificacion, evaluaciones=evaluaciones, inscripciones=inscripciones)

@app.route("/calificaciones/calificacion_estudiante/delete/<int:idevaluacion>/<int:idinscripcion>", methods=["POST"])
def delete_calificacion_estudiante(idevaluacion, idinscripcion):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_calificacion_estudiante"))
    
    cursor = conn.cursor()
    try:
        calificacion_estudiante_crud.delete_calificacion(cursor, idevaluacion, idinscripcion)
        conn.commit()
        flash("Calificación eliminada correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar la calificación: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_calificacion_estudiante"))

@app.route("/calificaciones/calificacion_estudiante/search")
def search_calificacion_estudiante():
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("list_calificacion_estudiante"))

    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_calificacion_estudiante"))

    cursor = conn.cursor(dictionary=True)
    calificaciones = calificacion_estudiante_crud.search_calificaciones(cursor, query_term)
    cursor.close()
    conn.close()
    flash(f'Mostrando resultados para "{query_term}".', "info")
    return render_template("calificaciones/calificacion_estudiante_list.html", calificaciones=calificaciones)


# --- Rutas para Docente (Administración Personal) ---

@app.route("/docentes")
def list_docentes():
    conn = get_db_connection()
    if conn is None:
        return render_template("docentes/docente_list.html", docentes=[])
    cursor = conn.cursor(dictionary=True)
    docentes = docente_crud.list_docentes(cursor)
    cursor.close()
    conn.close()
    return render_template("docentes/docente_list.html", docentes=docentes)

@app.route("/docentes/add", methods=["GET", "POST"])
def add_docente():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_docentes"))
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        idpersona = request.form["idpersona"]
        fecha_alta = request.form["fecha_alta"]
        estatus = request.form.get("estatus", "A")
        try:
            docente_crud.add_docente(cursor, idpersona, fecha_alta, estatus)
            conn.commit()
            flash("Docente añadido correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al añadir docente: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_docentes"))

    personas = docente_crud.get_personas_sin_docente(cursor)
    cursor.close()
    conn.close()
    return render_template("docentes/docente_form.html", docente=None, personas=personas)

@app.route("/docentes/edit/<int:iddocente>", methods=["GET", "POST"])
def edit_docente(iddocente):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_docentes"))
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        fecha_alta = request.form["fecha_alta"]
        fecha_baja = request.form.get("fecha_baja") or None
        estatus = request.form["estatus"]
        try:
            docente_crud.update_docente(cursor, iddocente, fecha_alta, fecha_baja, estatus)
            conn.commit()
            flash("Docente actualizado correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al actualizar docente: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_docentes"))

    docente = docente_crud.get_docente(cursor, iddocente)
    if not docente:
        flash("Docente no encontrado.", "warning")
        cursor.close()
        conn.close()
        return redirect(url_for("list_docentes"))
    
    personas = []
    cursor.close()
    conn.close()
    return render_template("docentes/docente_form.html", docente=docente, personas=personas)

@app.route("/docentes/delete/<int:iddocente>", methods=["POST"])
def delete_docente(iddocente):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_docentes"))
    cursor = conn.cursor()
    try:
        docente_crud.delete_docente(cursor, iddocente)
        conn.commit()
        flash("Docente eliminado correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_docentes"))

@app.route("/docentes/search")
def search_docentes():
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("list_docentes"))
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_docentes"))
    cursor = conn.cursor(dictionary=True)
    docentes = docente_crud.search_docentes(cursor, query_term)
    cursor.close()
    conn.close()
    flash(f'Resultados para "{query_term}".', "info")
    return render_template("docentes/docente_list.html", docentes=docentes)


# --- Rutas para Historial Académico ---

@app.route("/historial")
def list_historial():
    conn = get_db_connection()
    if conn is None:
        return render_template("estudiantes/historialacademico_list.html", historiales=[])
    cursor = conn.cursor(dictionary=True)
    historiales = historialacademico_crud.list_historial(cursor)
    cursor.close()
    conn.close()
    return render_template("estudiantes/historialacademico_list.html", historiales=historiales)

@app.route("/historial/add", methods=["GET", "POST"])
def add_historial():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_historial"))
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        matricula = request.form["matricula_alumno"]
        idasignatura = request.form["idasignatura"]
        idperiodo = request.form["idperiodo"]
        calificacion = request.form.get("calificacion_final") or None
        estatus = request.form["estatus_asignatura"]
        try:
            historialacademico_crud.add_historial(cursor, matricula, idasignatura, idperiodo, calificacion, estatus)
            conn.commit()
            flash("Registro añadido correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_historial"))

    estudiantes = historialacademico_crud.get_estudiantes(cursor)
    asignaturas = historialacademico_crud.get_asignaturas(cursor)
    periodos = historialacademico_crud.get_periodos(cursor)
    cursor.close()
    conn.close()
    return render_template("estudiantes/historialacademico_form.html", historial=None, estudiantes=estudiantes, asignaturas=asignaturas, periodos=periodos)

@app.route("/historial/edit/<int:idhistorial>", methods=["GET", "POST"])
def edit_historial(idhistorial):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_historial"))
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        calificacion = request.form.get("calificacion_final") or None
        estatus = request.form["estatus_asignatura"]
        try:
            historialacademico_crud.update_historial(cursor, idhistorial, calificacion, estatus)
            conn.commit()
            flash("Registro actualizado correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_historial"))

    historial = historialacademico_crud.get_historial(cursor, idhistorial)
    if not historial:
        flash("Registro no encontrado.", "warning")
        cursor.close()
        conn.close()
        return redirect(url_for("list_historial"))
    
    estudiantes = historialacademico_crud.get_estudiantes(cursor)
    asignaturas = historialacademico_crud.get_asignaturas(cursor)
    periodos = historialacademico_crud.get_periodos(cursor)
    cursor.close()
    conn.close()
    return render_template("estudiantes/historialacademico_form.html", historial=historial, estudiantes=estudiantes, asignaturas=asignaturas, periodos=periodos)

@app.route("/historial/delete/<int:idhistorial>", methods=["POST"])
def delete_historial(idhistorial):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_historial"))
    cursor = conn.cursor()
    try:
        historialacademico_crud.delete_historial(cursor, idhistorial)
        conn.commit()
        flash("Registro eliminado correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_historial"))

@app.route("/historial/search")
def search_historial():
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("list_historial"))
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_historial"))
    cursor = conn.cursor(dictionary=True)
    historiales = historialacademico_crud.search_historial(cursor, query_term)
    cursor.close()
    conn.close()
    flash(f'Resultados para "{query_term}".', "info")
    return render_template("estudiantes/historialacademico_list.html", historiales=historiales)


# --- Rutas para Periodo de Inscripciones ---

@app.route("/periodos")
def list_periodos():
    conn = get_db_connection()
    if conn is None:
        return render_template("cursos/periodoinscripciones_list.html", periodos=[])
    cursor = conn.cursor(dictionary=True)
    periodos = periodoinscripciones_crud.list_periodos(cursor)
    cursor.close()
    conn.close()
    return render_template("cursos/periodoinscripciones_list.html", periodos=periodos)

@app.route("/periodos/add", methods=["GET", "POST"])
def add_periodo():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_periodos"))
    cursor = conn.cursor()

    if request.method == "POST":
        descripcion = request.form["descripcion_periodo"]
        fecha_inicio = request.form["fecha_inicio_insc"]
        fecha_fin = request.form["fecha_fin_insc"]
        costo_credito = request.form["costo_por_credito"]
        estatus = request.form.get("estatus", "ABIERTO")
        try:
            periodoinscripciones_crud.add_periodo(cursor, descripcion, fecha_inicio, fecha_fin, costo_credito, estatus)
            conn.commit()
            flash("Periodo añadido correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_periodos"))

    cursor.close()
    conn.close()
    return render_template("cursos/periodoinscripciones_form.html", periodo=None)

@app.route("/periodos/edit/<int:idperiodo>", methods=["GET", "POST"])
def edit_periodo(idperiodo):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_periodos"))
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        descripcion = request.form["descripcion_periodo"]
        fecha_inicio = request.form["fecha_inicio_insc"]
        fecha_fin = request.form["fecha_fin_insc"]
        costo_credito = request.form["costo_por_credito"]
        estatus = request.form["estatus"]
        try:
            periodoinscripciones_crud.update_periodo(cursor, idperiodo, descripcion, fecha_inicio, fecha_fin, costo_credito, estatus)
            conn.commit()
            flash("Periodo actualizado correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_periodos"))

    periodo = periodoinscripciones_crud.get_periodo(cursor, idperiodo)
    if not periodo:
        flash("Periodo no encontrado.", "warning")
        cursor.close()
        conn.close()
        return redirect(url_for("list_periodos"))
    
    cursor.close()
    conn.close()
    return render_template("cursos/periodoinscripciones_form.html", periodo=periodo)

@app.route("/periodos/delete/<int:idperiodo>", methods=["POST"])
def delete_periodo(idperiodo):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_periodos"))
    cursor = conn.cursor()
    try:
        periodoinscripciones_crud.delete_periodo(cursor, idperiodo)
        conn.commit()
        flash("Periodo eliminado correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_periodos"))

@app.route("/periodos/search")
def search_periodos():
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("list_periodos"))
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_periodos"))
    cursor = conn.cursor(dictionary=True)
    periodos = periodoinscripciones_crud.search_periodos(cursor, query_term)
    cursor.close()
    conn.close()
    flash(f'Resultados para "{query_term}".', "info")
    return render_template("cursos/periodoinscripciones_list.html", periodos=periodos)


# --- Rutas para Inscripciones ---

@app.route("/inscripciones")
def list_inscripciones():
    conn = get_db_connection()
    if conn is None:
        return render_template("estudiantes/inscripcion_list.html", inscripciones=[])
    cursor = conn.cursor(dictionary=True)
    inscripciones = inscripcion_crud.list_inscripciones(cursor)
    cursor.close()
    conn.close()
    return render_template("estudiantes/inscripcion_list.html", inscripciones=inscripciones)

@app.route("/inscripciones/add", methods=["GET", "POST"])
def add_inscripcion():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_inscripciones"))
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        matricula = request.form["matricula_alumno"]
        idperiodo = request.form["idperiodo"]
        fecha = request.form["fecha_inscripcion"]
        motivo = request.form.get("motivo_inscripcion") or None
        estatus = request.form.get("estatus", "INICIADA")
        try:
            inscripcion_crud.add_inscripcion(cursor, matricula, idperiodo, fecha, motivo, estatus)
            conn.commit()
            flash("Inscripción añadida correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_inscripciones"))

    estudiantes = inscripcion_crud.get_estudiantes(cursor)
    periodos = inscripcion_crud.get_periodos(cursor)
    cursor.close()
    conn.close()
    return render_template("estudiantes/inscripcion_form.html", inscripcion=None, estudiantes=estudiantes, periodos=periodos)

@app.route("/inscripciones/edit/<int:idinscripcion>", methods=["GET", "POST"])
def edit_inscripcion(idinscripcion):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_inscripciones"))
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        fecha = request.form["fecha_inscripcion"]
        motivo = request.form.get("motivo_inscripcion") or None
        estatus = request.form["estatus"]
        try:
            inscripcion_crud.update_inscripcion(cursor, idinscripcion, fecha, motivo, estatus)
            conn.commit()
            flash("Inscripción actualizada correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_inscripciones"))

    inscripcion = inscripcion_crud.get_inscripcion(cursor, idinscripcion)
    if not inscripcion:
        flash("Inscripción no encontrada.", "warning")
        cursor.close()
        conn.close()
        return redirect(url_for("list_inscripciones"))
    
    estudiantes = inscripcion_crud.get_estudiantes(cursor)
    periodos = inscripcion_crud.get_periodos(cursor)
    cursor.close()
    conn.close()
    return render_template("estudiantes/inscripcion_form.html", inscripcion=inscripcion, estudiantes=estudiantes, periodos=periodos)

@app.route("/inscripciones/delete/<int:idinscripcion>", methods=["POST"])
def delete_inscripcion(idinscripcion):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_inscripciones"))
    cursor = conn.cursor()
    try:
        inscripcion_crud.delete_inscripcion(cursor, idinscripcion)
        conn.commit()
        flash("Inscripción eliminada correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_inscripciones"))

@app.route("/inscripciones/search")
def search_inscripciones():
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("list_inscripciones"))
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_inscripciones"))
    cursor = conn.cursor(dictionary=True)
    inscripciones = inscripcion_crud.search_inscripciones(cursor, query_term)
    cursor.close()
    conn.close()
    flash(f'Resultados para "{query_term}".', "info")
    return render_template("estudiantes/inscripcion_list.html", inscripciones=inscripciones)


# --- Rutas para Clases Programadas (Asignación a Cursos) ---

@app.route("/clases")
def list_clases():
    conn = get_db_connection()
    if conn is None:
        return render_template("docentes/claseprogramada_list.html", clases=[])
    cursor = conn.cursor(dictionary=True)
    clases = claseprogramada_crud.list_clases(cursor)
    cursor.close()
    conn.close()
    return render_template("docentes/claseprogramada_list.html", clases=clases)

@app.route("/clases/add", methods=["GET", "POST"])
def add_clase():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_clases"))
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        idasignatura = request.form["idasignatura"]
        modalidad = request.form["modalidad"]
        idhorario = request.form["idhorario"]
        iddocente = request.form["iddocente"]
        idperiodo = request.form["idperiodo"]
        idcalendario = request.form["idcalendario"]
        idioma = request.form.get("idioma", "ESP")
        try:
            claseprogramada_crud.add_clase(cursor, idasignatura, modalidad, idhorario, iddocente, idperiodo, idcalendario, idioma)
            conn.commit()
            flash("Clase añadida correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_clases"))

    asignaturas = claseprogramada_crud.get_asignaturas(cursor)
    docentes = claseprogramada_crud.get_docentes(cursor)
    horarios = claseprogramada_crud.get_horarios(cursor)
    periodos = claseprogramada_crud.get_periodos(cursor)
    calendarios = claseprogramada_crud.get_calendarios(cursor)
    cursor.close()
    conn.close()
    return render_template("docentes/claseprogramada_form.html", clase=None, asignaturas=asignaturas, docentes=docentes, horarios=horarios, periodos=periodos, calendarios=calendarios)

@app.route("/clases/edit/<int:idclase>", methods=["GET", "POST"])
def edit_clase(idclase):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_clases"))
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        idasignatura = request.form["idasignatura"]
        modalidad = request.form["modalidad"]
        idhorario = request.form["idhorario"]
        iddocente = request.form["iddocente"]
        idperiodo = request.form["idperiodo"]
        idcalendario = request.form["idcalendario"]
        idioma = request.form["idioma"]
        try:
            claseprogramada_crud.update_clase(cursor, idclase, idasignatura, modalidad, idhorario, iddocente, idperiodo, idcalendario, idioma)
            conn.commit()
            flash("Clase actualizada correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_clases"))

    clase = claseprogramada_crud.get_clase(cursor, idclase)
    if not clase:
        flash("Clase no encontrada.", "warning")
        cursor.close()
        conn.close()
        return redirect(url_for("list_clases"))
    
    asignaturas = claseprogramada_crud.get_asignaturas(cursor)
    docentes = claseprogramada_crud.get_docentes(cursor)
    horarios = claseprogramada_crud.get_horarios(cursor)
    periodos = claseprogramada_crud.get_periodos(cursor)
    calendarios = claseprogramada_crud.get_calendarios(cursor)
    cursor.close()
    conn.close()
    return render_template("docentes/claseprogramada_form.html", clase=clase, asignaturas=asignaturas, docentes=docentes, horarios=horarios, periodos=periodos, calendarios=calendarios)

@app.route("/clases/delete/<int:idclase>", methods=["POST"])
def delete_clase(idclase):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_clases"))
    cursor = conn.cursor()
    try:
        claseprogramada_crud.delete_clase(cursor, idclase)
        conn.commit()
        flash("Clase eliminada correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_clases"))

@app.route("/clases/search")
def search_clases():
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("list_clases"))
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_clases"))
    cursor = conn.cursor(dictionary=True)
    clases = claseprogramada_crud.search_clases(cursor, query_term)
    cursor.close()
    conn.close()
    flash(f'Resultados para "{query_term}".', "info")
    return render_template("docentes/claseprogramada_list.html", clases=clases)


# --- Rutas para Capacitación ---

@app.route("/capacitaciones")
def list_capacitaciones():
    conn = get_db_connection()
    if conn is None:
        return render_template("docentes/capacitacion_list.html", capacitaciones=[])
    cursor = conn.cursor(dictionary=True)
    capacitaciones = capacitacion_crud.list_capacitaciones(cursor)
    cursor.close()
    conn.close()
    return render_template("docentes/capacitacion_list.html", capacitaciones=capacitaciones)

@app.route("/capacitaciones/add", methods=["GET", "POST"])
def add_capacitacion():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_capacitaciones"))
    cursor = conn.cursor()
    if request.method == "POST":
        desc = request.form["descripcion"]
        inst = request.form.get("institucion") or None
        inicio = request.form["fecha_inicio"]
        fin = request.form.get("fecha_fin") or None
        horas = request.form.get("horas") or None
        try:
            capacitacion_crud.add_capacitacion(cursor, desc, inicio, fin, horas, inst)
            conn.commit()
            flash("Capacitación añadida correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_capacitaciones"))
    cursor.close()
    conn.close()
    return render_template("docentes/capacitacion_form.html", capacitacion=None)

@app.route("/capacitaciones/edit/<int:idcapacitacion>", methods=["GET", "POST"])
def edit_capacitacion(idcapacitacion):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_capacitaciones"))
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        desc = request.form["descripcion"]
        inst = request.form.get("institucion") or None
        inicio = request.form["fecha_inicio"]
        fin = request.form.get("fecha_fin") or None
        horas = request.form.get("horas") or None
        try:
            capacitacion_crud.update_capacitacion(cursor, idcapacitacion, desc, inicio, fin, horas, inst)
            conn.commit()
            flash("Capacitación actualizada correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_capacitaciones"))
    capacitacion = capacitacion_crud.get_capacitacion(cursor, idcapacitacion)
    cursor.close()
    conn.close()
    if not capacitacion:
        flash("Capacitación no encontrada.", "warning")
        return redirect(url_for("list_capacitaciones"))
    return render_template("docentes/capacitacion_form.html", capacitacion=capacitacion)

@app.route("/capacitaciones/delete/<int:idcapacitacion>", methods=["POST"])
def delete_capacitacion(idcapacitacion):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_capacitaciones"))
    cursor = conn.cursor()
    try:
        capacitacion_crud.delete_capacitacion(cursor, idcapacitacion)
        conn.commit()
        flash("Capacitación eliminada correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Error: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_capacitaciones"))

@app.route("/capacitaciones/search")
def search_capacitaciones():
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("list_capacitaciones"))
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_capacitaciones"))
    cursor = conn.cursor(dictionary=True)
    capacitaciones = capacitacion_crud.search_capacitaciones(cursor, query_term)
    cursor.close()
    conn.close()
    flash(f'Resultados para "{query_term}".', "info")
    return render_template("docentes/capacitacion_list.html", capacitaciones=capacitaciones)


# --- Rutas para Prerequisitos ---

@app.route("/prerequisitos")
def list_prerequisitos():
    conn = get_db_connection()
    if conn is None:
        return render_template("cursos/prerequisito_list.html", prerequisitos=[])
    cursor = conn.cursor(dictionary=True)
    prerequisitos = prerequisito_crud.list_prerequisitos(cursor)
    cursor.close()
    conn.close()
    return render_template("cursos/prerequisito_list.html", prerequisitos=prerequisitos)

@app.route("/prerequisitos/add", methods=["GET", "POST"])
def add_prerequisito():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_prerequisitos"))
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        idasignatura = request.form["idasignatura"]
        idasignatura_prereq = request.form["idasignatura_prereq"]
        try:
            prerequisito_crud.add_prerequisito(cursor, idasignatura, idasignatura_prereq)
            conn.commit()
            flash("Prerequisito añadido correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_prerequisitos"))
    asignaturas = prerequisito_crud.get_asignaturas(cursor)
    cursor.close()
    conn.close()
    return render_template("cursos/prerequisito_form.html", asignaturas=asignaturas)

@app.route("/prerequisitos/delete/<int:idasignatura>/<int:idasignatura_prereq>", methods=["POST"])
def delete_prerequisito(idasignatura, idasignatura_prereq):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_prerequisitos"))
    cursor = conn.cursor()
    try:
        prerequisito_crud.delete_prerequisito(cursor, idasignatura, idasignatura_prereq)
        conn.commit()
        flash("Prerequisito eliminado correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Error: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_prerequisitos"))

@app.route("/prerequisitos/search")
def search_prerequisitos():
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("list_prerequisitos"))
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_prerequisitos"))
    cursor = conn.cursor(dictionary=True)
    prerequisitos = prerequisito_crud.search_prerequisitos(cursor, query_term)
    cursor.close()
    conn.close()
    flash(f'Resultados para "{query_term}".', "info")
    return render_template("cursos/prerequisito_list.html", prerequisitos=prerequisitos)


# --- Rutas para Evaluaciones ---

@app.route("/evaluaciones")
def list_evaluaciones():
    conn = get_db_connection()
    if conn is None:
        return render_template("calificaciones/evaluacion_list.html", evaluaciones=[])
    cursor = conn.cursor(dictionary=True)
    evaluaciones = evaluacion_crud.list_evaluaciones(cursor)
    cursor.close()
    conn.close()
    return render_template("calificaciones/evaluacion_list.html", evaluaciones=evaluaciones)

@app.route("/evaluaciones/add", methods=["GET", "POST"])
def add_evaluacion():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_evaluaciones"))
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        idclase = request.form["idclase"]
        tipo = request.form["tipo"]
        desc = request.form.get("descripcion") or None
        fecha = request.form.get("fecha") or None
        porc = request.form.get("porcentaje") or None
        try:
            evaluacion_crud.add_evaluacion(cursor, idclase, tipo, desc, fecha, porc)
            conn.commit()
            flash("Evaluación añadida correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_evaluaciones"))
    clases = evaluacion_crud.get_clases(cursor)
    cursor.close()
    conn.close()
    return render_template("calificaciones/evaluacion_form.html", evaluacion=None, clases=clases)

@app.route("/evaluaciones/edit/<int:idevaluacion>", methods=["GET", "POST"])
def edit_evaluacion(idevaluacion):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_evaluaciones"))
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        tipo = request.form["tipo"]
        desc = request.form.get("descripcion") or None
        fecha = request.form.get("fecha") or None
        porc = request.form.get("porcentaje") or None
        try:
            evaluacion_crud.update_evaluacion(cursor, idevaluacion, tipo, desc, fecha, porc)
            conn.commit()
            flash("Evaluación actualizada correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_evaluaciones"))
    evaluacion = evaluacion_crud.get_evaluacion(cursor, idevaluacion)
    if not evaluacion:
        flash("Evaluación no encontrada.", "warning")
        cursor.close()
        conn.close()
        return redirect(url_for("list_evaluaciones"))
    clases = evaluacion_crud.get_clases(cursor)
    cursor.close()
    conn.close()
    return render_template("calificaciones/evaluacion_form.html", evaluacion=evaluacion, clases=clases)

@app.route("/evaluaciones/delete/<int:idevaluacion>", methods=["POST"])
def delete_evaluacion(idevaluacion):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_evaluaciones"))
    cursor = conn.cursor()
    try:
        evaluacion_crud.delete_evaluacion(cursor, idevaluacion)
        conn.commit()
        flash("Evaluación eliminada correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Error: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_evaluaciones"))

@app.route("/evaluaciones/search")
def search_evaluaciones():
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("list_evaluaciones"))
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_evaluaciones"))
    cursor = conn.cursor(dictionary=True)
    evaluaciones = evaluacion_crud.search_evaluaciones(cursor, query_term)
    cursor.close()
    conn.close()
    flash(f'Resultados para "{query_term}".', "info")
    return render_template("calificaciones/evaluacion_list.html", evaluaciones=evaluaciones)


# --- Rutas para Asistencia ---

@app.route("/asistencias")
def list_asistencias():
    conn = get_db_connection()
    if conn is None:
        return render_template("asistencia/asistencia_list.html", asistencias=[])
    cursor = conn.cursor(dictionary=True)
    asistencias = asistencia_crud.list_asistencias(cursor)
    cursor.close()
    conn.close()
    return render_template("asistencia/asistencia_list.html", asistencias=asistencias)

@app.route("/asistencias/add", methods=["GET", "POST"])
def add_asistencia():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_asistencias"))
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        idclase = request.form["idclase"]
        fecha = request.form["fecha"]
        tipo = request.form["tipo"]
        matricula = request.form.get("matricula") or None
        iddocente = request.form.get("iddocente") or None
        estatus = request.form["estatus"]
        observaciones = request.form.get("observaciones") or None
        try:
            asistencia_crud.add_asistencia(cursor, idclase, fecha, tipo, matricula, iddocente, estatus, observaciones)
            conn.commit()
            flash("Asistencia añadida correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_asistencias"))
    clases = asistencia_crud.get_clases(cursor)
    estudiantes = asistencia_crud.get_estudiantes(cursor)
    docentes = asistencia_crud.get_docentes(cursor)
    cursor.close()
    conn.close()
    return render_template("asistencia/asistencia_form.html", asistencia=None, clases=clases, estudiantes=estudiantes, docentes=docentes)

@app.route("/asistencias/edit/<int:idasistencia>", methods=["GET", "POST"])
def edit_asistencia(idasistencia):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_asistencias"))
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        estatus = request.form["estatus"]
        observaciones = request.form.get("observaciones") or None
        try:
            asistencia_crud.update_asistencia(cursor, idasistencia, estatus, observaciones)
            conn.commit()
            flash("Asistencia actualizada correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_asistencias"))
    asistencia = asistencia_crud.get_asistencia(cursor, idasistencia)
    if not asistencia:
        flash("Asistencia no encontrada.", "warning")
        cursor.close()
        conn.close()
        return redirect(url_for("list_asistencias"))
    clases = asistencia_crud.get_clases(cursor)
    estudiantes = asistencia_crud.get_estudiantes(cursor)
    docentes = asistencia_crud.get_docentes(cursor)
    cursor.close()
    conn.close()
    return render_template("asistencia/asistencia_form.html", asistencia=asistencia, clases=clases, estudiantes=estudiantes, docentes=docentes)

@app.route("/asistencias/delete/<int:idasistencia>", methods=["POST"])
def delete_asistencia(idasistencia):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_asistencias"))
    cursor = conn.cursor()
    try:
        asistencia_crud.delete_asistencia(cursor, idasistencia)
        conn.commit()
        flash("Asistencia eliminada correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Error: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_asistencias"))

@app.route("/asistencias/search")
def search_asistencias():
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("list_asistencias"))
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_asistencias"))
    cursor = conn.cursor(dictionary=True)
    asistencias = asistencia_crud.search_asistencias(cursor, query_term)
    cursor.close()
    conn.close()
    flash(f'Resultados para "{query_term}".', "info")
    return render_template("asistencia/asistencia_list.html", asistencias=asistencias)


# --- Rutas para Aulas ---

@app.route("/aulas")
def list_aulas():
    conn = get_db_connection()
    if conn is None:
        return render_template("aulas_horarios/aula_list.html", aulas=[])
    cursor = conn.cursor(dictionary=True)
    aulas = aula_crud.list_aulas(cursor)
    cursor.close()
    conn.close()
    return render_template("aulas_horarios/aula_list.html", aulas=aulas)

@app.route("/aulas/add", methods=["GET", "POST"])
def add_aula():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_aulas"))
    cursor = conn.cursor()
    if request.method == "POST":
        desc = request.form["descripcion"]
        lugar = request.form.get("lugar") or None
        capacidad = request.form["capacidad"]
        try:
            aula_crud.add_aula(cursor, desc, lugar, capacidad)
            conn.commit()
            flash("Aula añadida correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_aulas"))
    cursor.close()
    conn.close()
    return render_template("aulas_horarios/aula_form.html", aula=None)

@app.route("/aulas/edit/<int:idaula>", methods=["GET", "POST"])
def edit_aula(idaula):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_aulas"))
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        desc = request.form["descripcion"]
        lugar = request.form.get("lugar") or None
        capacidad = request.form["capacidad"]
        try:
            aula_crud.update_aula(cursor, idaula, desc, lugar, capacidad)
            conn.commit()
            flash("Aula actualizada correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_aulas"))
    aula = aula_crud.get_aula(cursor, idaula)
    cursor.close()
    conn.close()
    if not aula:
        flash("Aula no encontrada.", "warning")
        return redirect(url_for("list_aulas"))
    return render_template("aulas_horarios/aula_form.html", aula=aula)

@app.route("/aulas/delete/<int:idaula>", methods=["POST"])
def delete_aula(idaula):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_aulas"))
    cursor = conn.cursor()
    try:
        aula_crud.delete_aula(cursor, idaula)
        conn.commit()
        flash("Aula eliminada correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Error: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_aulas"))

@app.route("/aulas/search")
def search_aulas():
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("list_aulas"))
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_aulas"))
    cursor = conn.cursor(dictionary=True)
    aulas = aula_crud.search_aulas(cursor, query_term)
    cursor.close()
    conn.close()
    flash(f'Resultados para "{query_term}".', "info")
    return render_template("aulas_horarios/aula_list.html", aulas=aulas)


# --- Rutas para Horarios ---

@app.route("/horarios")
def list_horarios():
    conn = get_db_connection()
    if conn is None:
        return render_template("aulas_horarios/horario_list.html", horarios=[])
    cursor = conn.cursor(dictionary=True)
    horarios = horario_crud.list_horarios(cursor)
    cursor.close()
    conn.close()
    return render_template("aulas_horarios/horario_list.html", horarios=horarios)

@app.route("/horarios/add", methods=["GET", "POST"])
def add_horario():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_horarios"))
    cursor = conn.cursor()
    if request.method == "POST":
        dia = request.form["dia_semana"]
        inicio = request.form["hora_inicio"]
        fin = request.form["hora_fin"]
        desc = request.form.get("descripcion") or None
        try:
            horario_crud.add_horario(cursor, dia, inicio, fin, desc)
            conn.commit()
            flash("Horario añadido correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_horarios"))
    cursor.close()
    conn.close()
    return render_template("aulas_horarios/horario_form.html", horario=None)

@app.route("/horarios/edit/<int:idhorario>", methods=["GET", "POST"])
def edit_horario(idhorario):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_horarios"))
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        dia = request.form["dia_semana"]
        inicio = request.form["hora_inicio"]
        fin = request.form["hora_fin"]
        desc = request.form.get("descripcion") or None
        try:
            horario_crud.update_horario(cursor, idhorario, dia, inicio, fin, desc)
            conn.commit()
            flash("Horario actualizado correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_horarios"))
    horario = horario_crud.get_horario(cursor, idhorario)
    cursor.close()
    conn.close()
    if not horario:
        flash("Horario no encontrado.", "warning")
        return redirect(url_for("list_horarios"))
    return render_template("aulas_horarios/horario_form.html", horario=horario)

@app.route("/horarios/delete/<int:idhorario>", methods=["POST"])
def delete_horario(idhorario):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_horarios"))
    cursor = conn.cursor()
    try:
        horario_crud.delete_horario(cursor, idhorario)
        conn.commit()
        flash("Horario eliminado correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Error: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_horarios"))

@app.route("/horarios/search")
def search_horarios():
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("list_horarios"))
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_horarios"))
    cursor = conn.cursor(dictionary=True)
    horarios = horario_crud.search_horarios(cursor, query_term)
    cursor.close()
    conn.close()
    flash(f'Resultados para "{query_term}".', "info")
    return render_template("aulas_horarios/horario_list.html", horarios=horarios)


# --- Rutas para Pagos ---

@app.route("/pagos")
def list_pagos():
    conn = get_db_connection()
    if conn is None:
        return render_template("finanzas_becas/pago_list.html", pagos=[])
    cursor = conn.cursor(dictionary=True)
    pagos = pago_crud.list_pagos(cursor)
    cursor.close()
    conn.close()
    return render_template("finanzas_becas/pago_list.html", pagos=pagos)

@app.route("/pagos/add", methods=["GET", "POST"])
def add_pago():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_pagos"))
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        idestado = request.form["idestadodecuenta"]
        monto = request.form["monto"]
        try:
            pago_crud.registrar_pago(cursor, idestado, monto)
            conn.commit()
            flash("Pago registrado correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_pagos"))
    estudiantes = pago_crud.get_estudiantes_con_saldo(cursor)
    cursor.close()
    conn.close()
    return render_template("finanzas_becas/pago_form.html", estudiantes=estudiantes)


# --- Rutas para Estados de Cuenta ---

@app.route("/estados")
def list_estados():
    conn = get_db_connection()
    if conn is None:
        return render_template("finanzas_becas/estadodecuenta_list.html", estados=[])
    cursor = conn.cursor(dictionary=True)
    estados = estadodecuenta_crud.list_estados(cursor)
    cursor.close()
    conn.close()
    return render_template("finanzas_becas/estadodecuenta_list.html", estados=estados)

@app.route("/estados/add", methods=["GET", "POST"])
def add_estado():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_estados"))
    cursor = conn.cursor()
    if request.method == "POST":
        saldo_inicial = request.form["saldo_inicial"]
        limite = request.form.get("limite_credito") or None
        try:
            estadodecuenta_crud.add_estado(cursor, saldo_inicial, limite)
            conn.commit()
            flash("Estado de cuenta creado correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_estados"))
    cursor.close()
    conn.close()
    return render_template("finanzas_becas/estadodecuenta_form.html", estado=None)

@app.route("/estados/edit/<int:idestado>", methods=["GET", "POST"])
def edit_estado(idestado):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_estados"))
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        saldo_actual = request.form["saldo_actual"]
        limite = request.form.get("limite_credito") or None
        try:
            estadodecuenta_crud.update_estado(cursor, idestado, saldo_actual, limite)
            conn.commit()
            flash("Estado de cuenta actualizado correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_estados"))
    estado = estadodecuenta_crud.get_estado(cursor, idestado)
    cursor.close()
    conn.close()
    if not estado:
        flash("Estado de cuenta no encontrado.", "warning")
        return redirect(url_for("list_estados"))
    return render_template("finanzas_becas/estadodecuenta_form.html", estado=estado)

@app.route("/estados/delete/<int:idestado>", methods=["POST"])
def delete_estado(idestado):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_estados"))
    cursor = conn.cursor()
    try:
        estadodecuenta_crud.delete_estado(cursor, idestado)
        conn.commit()
        flash("Estado de cuenta eliminado correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Error: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_estados"))

@app.route("/estados/search")
def search_estados():
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("list_estados"))
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_estados"))
    cursor = conn.cursor(dictionary=True)
    estados = estadodecuenta_crud.search_estados(cursor, query_term)
    cursor.close()
    conn.close()
    flash(f'Resultados para "{query_term}".', "info")
    return render_template("finanzas_becas/estadodecuenta_list.html", estados=estados)


# --- Rutas para Usuarios ---

@app.route("/usuarios")
def list_usuarios():
    conn = get_db_connection()
    if conn is None:
        return render_template("admin/usuarios_list.html", usuarios=[])
    cursor = conn.cursor(dictionary=True)
    usuarios = usuarios_crud.list_usuarios(cursor)
    cursor.close()
    conn.close()
    return render_template("admin/usuarios_list.html", usuarios=usuarios)

@app.route("/usuarios/add", methods=["GET", "POST"])
def add_usuario():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_usuarios"))
    cursor = conn.cursor()
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        rol = request.form["rol"]
        try:
            usuarios_crud.add_usuario(cursor, email, password, rol)
            conn.commit()
            flash("Usuario añadido correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_usuarios"))
    cursor.close()
    conn.close()
    return render_template("admin/usuarios_form.html", usuario=None)

@app.route("/usuarios/edit/<int:idusuario>", methods=["GET", "POST"])
def edit_usuario(idusuario):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_usuarios"))
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        email = request.form["email"]
        rol = request.form["rol"]
        password = request.form.get("password") or None
        try:
            usuarios_crud.update_usuario(cursor, idusuario, email, rol, password)
            conn.commit()
            flash("Usuario actualizado correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_usuarios"))
    usuario = usuarios_crud.get_usuario(cursor, idusuario)
    cursor.close()
    conn.close()
    if not usuario:
        flash("Usuario no encontrado.", "warning")
        return redirect(url_for("list_usuarios"))
    return render_template("admin/usuarios_form.html", usuario=usuario)

@app.route("/usuarios/delete/<int:idusuario>", methods=["POST"])
def delete_usuario(idusuario):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_usuarios"))
    cursor = conn.cursor()
    try:
        usuarios_crud.delete_usuario(cursor, idusuario)
        conn.commit()
        flash("Usuario eliminado correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Error: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_usuarios"))

@app.route("/usuarios/search")
def search_usuarios():
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("list_usuarios"))
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_usuarios"))
    cursor = conn.cursor(dictionary=True)
    usuarios = usuarios_crud.search_usuarios(cursor, query_term)
    cursor.close()
    conn.close()
    flash(f'Resultados para "{query_term}".', "info")
    return render_template("admin/usuarios_list.html", usuarios=usuarios)


# --- Iniciar la Aplicación ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)


# ruta de login
@app.route("/", methods=["GET", "POST"])
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

#ruta del registro

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["username"].strip()
        password = request.form["password"]

        role = "operacion_academica"   # rol por default

        if not email or not password:
            flash("Rellena todos los campos", "warning")
            return redirect(url_for("register"))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # validar si ya existe el email
        cursor.execute(
            "SELECT idusuario FROM usuarios WHERE email=%s",
            (email,)
        )
        exists = cursor.fetchone()

        if exists:
            flash("Ya existe un usuario con ese correo.", "warning")
            cursor.close()
            conn.close()
            return redirect(url_for("register"))

        # insertar usuario sin hashing
        cursor.execute(
            "INSERT INTO usuarios (email, password, rol) VALUES (%s, %s, %s)",
            (email, password, role)
        )
        conn.commit()

        cursor.close()
        conn.close()

        flash("Usuario registrado. Inicia sesión.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

