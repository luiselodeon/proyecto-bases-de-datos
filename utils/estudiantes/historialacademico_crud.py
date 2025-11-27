import mysql.connector

def list_historial(cursor):
    """List all historial academ

ico records"""
    query = """
    SELECT 
        h.idhistorialacademico,
        h.matricula_alumno,
        h.idasignatura,
        h.idperiodo,
        h.calificacion_final,
        h.estatus_asignatura,
        CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', IFNULL(p.apellido_materno, '')) AS nombre_estudiante,
        a.nombre_asignatura,
        pi.descripcion_periodo
    FROM historialacademico h
    JOIN estudiante e ON h.matricula_alumno = e.matricula_alumno
    JOIN persona p ON e.idpersona = p.idpersona
    JOIN asignatura a ON h.idasignatura = a.idasignatura
    JOIN periodoinscripciones pi ON h.idperiodo = pi.idperiodoinscripciones
    ORDER BY p.apellido_paterno, p.nombre, pi.descripcion_periodo
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_historial(cursor, idhistorial):
    """Get a specific historial record"""
    query = "SELECT * FROM historialacademico WHERE idhistorialacademico = %s"
    cursor.execute(query, (idhistorial,))
    return cursor.fetchone()

def add_historial(cursor, matricula_alumno, idasignatura, idperiodo, calificacion_final, estatus_asignatura):
    """Add new historial academico record"""
    query = """
    INSERT INTO historialacademico (matricula_alumno, idasignatura, idperiodo, calificacion_final, estatus_asignatura)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (matricula_alumno, idasignatura, idperiodo, calificacion_final, estatus_asignatura))
    return cursor.lastrowid

def update_historial(cursor, idhistorial, calificacion_final, estatus_asignatura):
    """Update historial academico record"""
    query = """
    UPDATE historialacademico
    SET calificacion_final = %s, estatus_asignatura = %s
    WHERE idhistorialacademico = %s
    """
    cursor.execute(query, (calificacion_final, estatus_asignatura, idhistorial))

def delete_historial(cursor, idhistorial):
    """Delete historial academico record"""
    query = "DELETE FROM historialacademico WHERE idhistorialacademico = %s"
    cursor.execute(query, (idhistorial,))

def get_estudiantes(cursor):
    """Get list of students for dropdown"""
    query = """
    SELECT e.matricula_alumno,
           CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', IFNULL(p.apellido_materno, '')) AS nombre_completo
    FROM estudiante e
    JOIN persona p ON e.idpersona = p.idpersona
    WHERE e.estatus = 'ACTIVO'
    ORDER BY nombre_completo
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_asignaturas(cursor):
    """Get list of asignaturas for dropdown"""
    query = "SELECT idasignatura, nombre_asignatura FROM asignatura ORDER BY nombre_asignatura"
    cursor.execute(query)
    return cursor.fetchall()

def get_periodos(cursor):
    """Get list of periods for dropdown"""
    query = "SELECT idperiodoinscripciones, descripcion_periodo FROM periodoinscripciones ORDER BY descripcion_periodo DESC"
    cursor.execute(query)
    return cursor.fetchall()

def search_historial(cursor, query_term):
    """Search historial by student name or asignatura"""
    query = """
    SELECT 
        h.idhistorialacademico,
        h.matricula_alumno,
        h.idasignatura,
        h.idperiodo,
        h.calificacion_final,
        h.estatus_asignatura,
        CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', IFNULL(p.apellido_materno, '')) AS nombre_estudiante,
        a.nombre_asignatura,
        pi.descripcion_periodo
    FROM historialacademico h
    JOIN estudiante e ON h.matricula_alumno = e.matricula_alumno
    JOIN persona p ON e.idpersona = p.idpersona
    JOIN asignatura a ON h.idasignatura = a.idasignatura
    JOIN periodoinscripciones pi ON h.idperiodo = pi.idperiodoinscripciones
    WHERE p.nombre LIKE %s 
       OR p.apellido_paterno LIKE %s
       OR a.nombre_asignatura LIKE %s
    ORDER BY p.apellido_paterno, p.nombre
    """
    term = f"%{query_term}%"
    cursor.execute(query, (term, term, term))
    return cursor.fetchall()
