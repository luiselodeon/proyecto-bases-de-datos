import mysql.connector

def list_evaluaciones(cursor):
    """List all evaluaciones with clase information"""
    query = """
    SELECT 
        e.idevaluacion,
        e.idclaseprogramada,
        e.tipo_actividad,
        e.descripcion,
        e.fecha_aplicacion,
        e.porcentaje,
        a.nombre_asignatura,
        pi.descripcion_periodo
    FROM evaluacion e
    JOIN claseprogramada cp ON e.idclaseprogramada = cp.idclaseprogramada
    JOIN asignatura a ON cp.idasignatura = a.idasignatura
    JOIN periodoinscripciones pi ON cp.idperiodoinscripciones = pi.idperiodoinscripciones
    ORDER BY e.fecha_aplicacion DESC
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_evaluacion(cursor, idevaluacion):
    """Get a specific evaluacion"""
    query = "SELECT * FROM evaluacion WHERE idevaluacion = %s"
    cursor.execute(query, (idevaluacion,))
    return cursor.fetchone()

def add_evaluacion(cursor, idclase, tipo, descripcion, fecha, porcentaje):
    """Add new evaluacion"""
    query = """
    INSERT INTO evaluacion (idclaseprogramada, tipo_actividad, descripcion, fecha_aplicacion, porcentaje)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (idclase, tipo, descripcion, fecha, porcentaje))
    return cursor.lastrowid

def update_evaluacion(cursor, idevaluacion, tipo, descripcion, fecha, porcentaje):
    """Update evaluacion"""
    query = """
    UPDATE evaluacion
    SET tipo_actividad = %s, descripcion = %s, fecha_aplicacion = %s, porcentaje = %s
    WHERE idevaluacion = %s
    """
    cursor.execute(query, (tipo, descripcion, fecha, porcentaje, idevaluacion))

def delete_evaluacion(cursor, idevaluacion):
    """Delete evaluacion"""
    query = "DELETE FROM evaluacion WHERE idevaluacion = %s"
    cursor.execute(query, (idevaluacion,))

def get_clases(cursor):
    """Get list of clases programadas for dropdown"""
    query = """
    SELECT cp.idclaseprogramada,
           CONCAT(a.nombre_asignatura, ' - ', pi.descripcion_periodo, ' - ', p.nombre, ' ', p.apellido_paterno, ' (', h.dia_semana, ' ', DATE_FORMAT(h.hora_inicio, '%H:%i'), '-', DATE_FORMAT(h.hora_fin, '%H:%i'), ')') AS descripcion
    FROM claseprogramada cp
    JOIN asignatura a ON cp.idasignatura = a.idasignatura
    JOIN periodoinscripciones pi ON cp.idperiodoinscripciones = pi.idperiodoinscripciones
    JOIN docente d ON cp.iddocente = d.iddocente
    JOIN persona p ON d.idpersona = p.idpersona
    JOIN horario h ON cp.idhorario = h.idhorario
    ORDER BY pi.descripcion_periodo DESC, a.nombre_asignatura
    """
    cursor.execute(query)
    return cursor.fetchall()

def search_evaluaciones(cursor, query_term):
    """Search evaluaciones by asignatura or description"""
    query = """
    SELECT 
        e.idevaluacion,
        e.idclaseprogramada,
        e.tipo_actividad,
        e.descripcion,
        e.fecha_aplicacion,
        e.porcentaje,
        a.nombre_asignatura,
        pi.descripcion_periodo
    FROM evaluacion e
    JOIN claseprogramada cp ON e.idclaseprogramada = cp.idclaseprogramada
    JOIN asignatura a ON cp.idasignatura = a.idasignatura
    JOIN periodoinscripciones pi ON cp.idperiodoinscripciones = pi.idperiodoinscripciones
    WHERE a.nombre_asignatura LIKE %s OR e.descripcion LIKE %s
    ORDER BY e.fecha_aplicacion DESC
    """
    term = f"%{query_term}%"
    cursor.execute(query, (term, term))
    return cursor.fetchall()
