import mysql.connector

def list_asistencias(cursor):
    query = """
    SELECT 
        asi.idasistencia,
        CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', IFNULL(p.apellido_materno, '')) AS nombre_estudiante,
        a.nombre_asignatura AS nombre_clase,
        asi.fecha AS fecha_asistencia,
        asi.estatus AS estado_asistencia
    FROM asistencia asi
    JOIN claseprogramada cp ON asi.idclaseprogramada = cp.idclaseprogramada
    JOIN asignatura a ON cp.idasignatura = a.idasignatura
    LEFT JOIN estudiante e ON asi.matricula_alumno = e.matricula_alumno
    LEFT JOIN persona p ON e.idpersona = p.idpersona
    ORDER BY asi.fecha DESC
    """
    cursor.execute(query)
    return cursor.fetchall()


def get_asistencia(cursor, idasistencia):
    """Get a specific asistencia"""
    query = "SELECT * FROM asistencia WHERE idasistencia = %s"
    cursor.execute(query, (idasistencia,))
    return cursor.fetchone()

def add_asistencia(cursor, idclase, fecha, tipo, matricula, iddocente, estatus, observaciones):
    """Add new asistencia"""
    query = """
    INSERT INTO asistencia (idclaseprogramada, fecha, tipo, matricula_alumno, iddocente, estatus, observaciones)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (idclase, fecha, tipo, matricula, iddocente, estatus, observaciones))
    return cursor.lastrowid

def update_asistencia(cursor, idasistencia, estatus, observaciones):
    """Update asistencia"""
    query = """
    UPDATE asistencia
    SET estatus = %s, observaciones = %s
    WHERE idasistencia = %s
    """
    cursor.execute(query, (estatus, observaciones, idasistencia))

def delete_asistencia(cursor, idasistencia):
    """Delete asistencia"""
    query = "DELETE FROM asistencia WHERE idasistencia = %s"
    cursor.execute(query, (idasistencia,))

def get_clases(cursor):
    """Get list of clases programadas for dropdown"""
    query = """
    SELECT cp.idclaseprogramada,
           CONCAT(a.nombre_asignatura, ' - ', pi.descripcion_periodo) AS descripcion
    FROM claseprogramada cp
    JOIN asignatura a ON cp.idasignatura = a.idasignatura
    JOIN periodoinscripciones pi ON cp.idperiodoinscripciones = pi.idperiodoinscripciones
    ORDER BY pi.descripcion_periodo DESC, a.nombre_asignatura
    """
    cursor.execute(query)
    return cursor.fetchall()

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

def get_docentes(cursor):
    """Get list of docentes for dropdown"""
    query = """
    SELECT d.iddocente,
           CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', IFNULL(p.apellido_materno, '')) AS nombre_completo
    FROM docente d
    JOIN persona p ON d.idpersona = p.idpersona
    WHERE d.estatus = 'A'
    ORDER BY nombre_completo
    """
    cursor.execute(query)
    return cursor.fetchall()

def search_asistencias(cursor, query_term):
    """Search asistencias by asignatura or persona name"""
    query = """
    SELECT 
        asi.idasistencia,
        asi.idclaseprogramada,
        asi.fecha,
        asi.tipo,
        asi.matricula_alumno,
        asi.iddocente,
        asi.estatus,
        asi.observaciones,
        a.nombre_asignatura,
        CASE 
            WHEN asi.tipo = 'ESTUDIANTE' THEN CONCAT(p.nombre, ' ', p.apellido_paterno)
            WHEN asi.tipo = 'DOCENTE' THEN CONCAT(pd.nombre, ' ', pd.apellido_paterno)
        END AS persona_nombre
    FROM asistencia asi
    JOIN claseprogramada cp ON asi.idclaseprogramada = cp.idclaseprogramada
    JOIN asignatura a ON cp.idasignatura = a.idasignatura
    LEFT JOIN estudiante e ON asi.matricula_alumno = e.matricula_alumno
    LEFT JOIN persona p ON e.idpersona = p.idpersona
    LEFT JOIN docente d ON asi.iddocente = d.iddocente
    LEFT JOIN persona pd ON d.idpersona = pd.idpersona
    WHERE a.nombre_asignatura LIKE %s OR p.nombre LIKE %s OR pd.nombre LIKE %s
    ORDER BY asi.fecha DESC
    """
    term = f"%{query_term}%"
    cursor.execute(query, (term, term, term))
    return cursor.fetchall()
