import os
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import mysql.connector
from utils.auth import login_required, role_required




# --- Importar CRUDs y conexión DB ---
from utils.db import get_db_connection
from utils.estudiantes import students_crud, historialacademico_crud, inscripcion_crud
from utils.cursos import carreras_crud, asignaturas_crud, periodoinscripciones_crud
from utils.aulas_horarios import departamentos_crud, departamentoasignatura_crud
from utils.docentes import docente_crud, claseprogramada_crud
from utils.calificaciones import calificacion_estudiante_crud
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

