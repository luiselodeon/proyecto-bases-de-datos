
# --- Rutas para Plan de Estudio ---

@app.route("/cursos_planes/planestudios")
def list_planestudios():
    conn = get_db_connection()
    if conn is None:
        return render_template("cursos/planestudio_list.html", planes=[])
    
    cursor = conn.cursor(dictionary=True)
    planes = planestudio_crud.list_planestudios(cursor)
    cursor.close()
    conn.close()
    return render_template("cursos/planestudio_list.html", planes=planes)

@app.route("/cursos_planes/planestudios/add", methods=["GET", "POST"])
def add_planestudio():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_planestudios"))
    
    cursor = conn.cursor(dictionary=True)
    
    if request.method == "POST":
        nombre_plan = request.form["nombre_plan"]
        vigencia_inicio = request.form["vigencia_inicio"]
        vigencia_fin = request.form.get("vigencia_fin") or None
        idcarrera = request.form["idcarrera"]
        
        try:
            planestudio_crud.add_planestudio(cursor, nombre_plan, vigencia_inicio, vigencia_fin, idcarrera)
            conn.commit()
            flash("Plan de estudio añadido correctamente.", "success")
            return redirect(url_for("list_planestudios"))
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al añadir plan de estudio: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
    
    # GET - Obtener carreras para el dropdown
    carreras = planestudio_crud.get_carreras(cursor)
    cursor.close()
    conn.close()
    return render_template("cursos/planestudio_form.html", plan=None, carreras=carreras)

@app.route("/cursos_planes/planestudios/edit/<int:idplanestudio>", methods=["GET", "POST"])
def edit_planestudio(idplanestudio):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_planestudios"))
    
    cursor = conn.cursor(dictionary=True)
    
    if request.method == "POST":
        nombre_plan = request.form["nombre_plan"]
        vigencia_inicio = request.form["vigencia_inicio"]
        vigencia_fin = request.form.get("vigencia_fin") or None
        idcarrera = request.form["idcarrera"]
        
        try:
            planestudio_crud.update_planestudio(cursor, idplanestudio, nombre_plan, vigencia_inicio, vigencia_fin, idcarrera)
            conn.commit()
            flash("Plan de estudio actualizado correctamente.", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al actualizar plan de estudio: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("list_planestudios"))
    
    # GET
    plan = planestudio_crud.get_planestudio(cursor, idplanestudio)
    if not plan:
        flash("Plan de estudio no encontrado.", "warning")
        cursor.close()
        conn.close()
        return redirect(url_for("list_planestudios"))
    
    carreras = planestudio_crud.get_carreras(cursor)
    cursor.close()
    conn.close()
    return render_template("cursos/planestudio_form.html", plan=plan, carreras=carreras)

@app.route("/cursos_planes/planestudios/delete/<int:idplanestudio>", methods=["POST"])
def delete_planestudio(idplanestudio):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_planestudios"))
    
    cursor = conn.cursor()
    try:
        planestudio_crud.delete_planestudio(cursor, idplanestudio)
        conn.commit()
        flash("Plan de estudio eliminado correctamente.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"No se pudo eliminar el plan de estudio: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("list_planestudios"))

@app.route("/cursos_planes/planestudios/search")
def search_planestudios():
    query_term = request.args.get("query", "")
    if not query_term:
        return redirect(url_for("list_planestudios"))
    
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("list_planestudios"))
    
    cursor = conn.cursor(dictionary=True)
    planes = planestudio_crud.search_planestudio(cursor, query_term)
    cursor.close()
    conn.close()
    
    flash(f'Mostrando resultados para "{query_term}".', "info")
    return render_template("cursos/planestudio_list.html", planes=planes)

