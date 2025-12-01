import mysql.connector

def list_calificaciones(cursor):
    query = """
    SELECT 
        ce.idevaluacion,
        ce.idinscripcion,
        ce.calificacion,
        ce.observaciones,
        e.descripcion AS evaluacion_descripcion,
        p.nombre,
        p.apellido_paterno,
        p.apellido_materno
    FROM calificacion_estudiante ce
    JOIN evaluacion e ON ce.idevaluacion = e.idevaluacion
    JOIN inscripcion i ON ce.idinscripcion = i.idinscripcion
    JOIN estudiante est ON i.matricula_alumno = est.matricula_alumno
    JOIN persona p ON est.idpersona = p.idpersona
    ORDER BY p.apellido_paterno, p.nombre
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_calificacion(cursor, idevaluacion, idinscripcion):
    query = """
    SELECT * FROM calificacion_estudiante 
    WHERE idevaluacion = %s AND idinscripcion = %s
    """
    cursor.execute(query, (idevaluacion, idinscripcion))
    return cursor.fetchone()

def add_calificacion(cursor, idevaluacion, idinscripcion, calificacion, observaciones):
    query = """
    INSERT INTO calificacion_estudiante (idevaluacion, idinscripcion, calificacion, observaciones)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (idevaluacion, idinscripcion, calificacion, observaciones))

def update_calificacion(cursor, idevaluacion, idinscripcion, calificacion, observaciones):
    query = """
    UPDATE calificacion_estudiante
    SET calificacion = %s, observaciones = %s
    WHERE idevaluacion = %s AND idinscripcion = %s
    """
    cursor.execute(query, (calificacion, observaciones, idevaluacion, idinscripcion))

def delete_calificacion(cursor, idevaluacion, idinscripcion):
    query = "DELETE FROM calificacion_estudiante WHERE idevaluacion = %s AND idinscripcion = %s"
    cursor.execute(query, (idevaluacion, idinscripcion))

def get_evaluaciones(cursor):
    cursor.execute("SELECT idevaluacion, descripcion FROM evaluacion")
    return cursor.fetchall()

def get_inscripciones(cursor):
    query = """
    SELECT 
        i.idinscripcion,
        CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', IFNULL(p.apellido_materno, '')) AS nombre_completo
    FROM inscripcion i
    JOIN estudiante est ON i.matricula_alumno = est.matricula_alumno
    JOIN persona p ON est.idpersona = p.idpersona
    ORDER BY nombre_completo
    """
    cursor.execute(query)
    return cursor.fetchall()

def search_calificaciones(cursor, query_term):
    query = """
    SELECT 
        ce.idevaluacion,
        ce.idinscripcion,
        ce.calificacion,
        ce.observaciones,
        e.descripcion AS evaluacion_descripcion,
        p.nombre,
        p.apellido_paterno,
        p.apellido_materno
    FROM calificacion_estudiante ce
    JOIN evaluacion e ON ce.idevaluacion = e.idevaluacion
    JOIN inscripcion i ON ce.idinscripcion = i.idinscripcion
    JOIN estudiante est ON i.matricula_alumno = est.matricula_alumno
    JOIN persona p ON est.idpersona = p.idpersona
    WHERE p.nombre LIKE %s OR p.apellido_paterno LIKE %s OR e.descripcion LIKE %s
    ORDER BY p.apellido_paterno, p.nombre
    """
    term = f"%{query_term}%"
    cursor.execute(query, (term, term, term))
    return cursor.fetchall()
