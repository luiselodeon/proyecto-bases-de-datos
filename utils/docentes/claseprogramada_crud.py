import mysql.connector

def list_clases(cursor):
    """List all clases programadas"""
    query = """
    SELECT 
        cp.idclaseprogramada,
        cp.idasignatura,
        cp.modalidad,
        cp.idhorario,
        cp.iddocente,
        cp.idperiodoinscripciones,
        cp.idcalendarioescolar,
        cp.idioma,
        a.nombre_asignatura,
        CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', IFNULL(p.apellido_materno, '')) AS nombre_docente,
        pi.descripcion_periodo,
        h.dia_semana,
        h.hora_inicio,
        h.hora_fin
    FROM claseprogramada cp
    JOIN asignatura a ON cp.idasignatura = a.idasignatura
    JOIN docente d ON cp.iddocente = d.iddocente
    JOIN persona p ON d.idpersona = p.idpersona
    JOIN periodoinscripciones pi ON cp.idperiodoinscripciones = pi.idperiodoinscripciones
    JOIN horario h ON cp.idhorario = h.idhorario
    ORDER BY pi.descripcion_periodo DESC, a.nombre_asignatura
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_clase(cursor, idclase):
    """Get a specific clase programada"""
    query = "SELECT * FROM claseprogramada WHERE idclaseprogramada = %s"
    cursor.execute(query, (idclase,))
    return cursor.fetchone()

def add_clase(cursor, idasignatura, modalidad, idihorario, iddocente, idperiodo, idcalendario, idioma='ESP'):
    """Add new clase programada"""
    query = """
    INSERT INTO claseprogramada (idasignatura, modalidad, idhorario, iddocente, idperiodoinscripciones, idcalendarioescolar, idioma)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (idasignatura, modalidad, idhorario, iddocente, idperiodo, idcalendario, idioma))
    return cursor.lastrowid

def update_clase(cursor, idclase, idasignatura, modalidad, idhorario, iddocente, idperiodo, idcalendario, idioma):
    """Update clase programada"""
    query = """
    UPDATE claseprogramada
    SET idasignatura = %s, modalidad = %s, idhorario = %s, iddocente = %s, 
        idperiodoinscripciones = %s, idcalendarioescolar = %s, idioma = %s
    WHERE idclaseprogramada = %s
    """
    cursor.execute(query, (idasignatura, modalidad, idhorario, iddocente, idperiodo, idcalendario, idioma, idclase))

def delete_clase(cursor, idclase):
    """Delete clase programada"""
    query = "DELETE FROM claseprogramada WHERE idclaseprogramada = %s"
    cursor.execute(query, (idclase,))

def get_asignaturas(cursor):
    """Get list of asignaturas for dropdown"""
    query = "SELECT idasignatura, nombre_asignatura FROM asignatura ORDER BY nombre_asignatura"
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

def get_horarios(cursor):
    """Get list of horarios for dropdown"""
    query = """
    SELECT idhorario, 
           CONCAT(dia_semana, ' ', TIME_FORMAT(hora_inicio, '%H:%i'), '-', TIME_FORMAT(hora_fin, '%H:%i')) AS descripcion
    FROM horario
    ORDER BY dia_semana, hora_inicio
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_periodos(cursor):
    """Get list of periods for dropdown"""
    query = "SELECT idperiodoinscripciones, descripcion_periodo FROM periodoinscripciones ORDER BY descripcion_periodo DESC"
    cursor.execute(query)
    return cursor.fetchall()

def get_calendarios(cursor):
    """Get list of calendarios escolares for dropdown"""
    query = "SELECT idcalendarioescolar, descripcion FROM calendarioescolar ORDER BY fecha_inicio DESC"
    cursor.execute(query)
    return cursor.fetchall()

def search_clases(cursor, query_term):
    """Search clases by asignatura or docente name"""
    query = """
    SELECT 
        cp.idclaseprogramada,
        cp.idasignatura,
        cp.modalidad,
        cp.idhorario,
        cp.iddocente,
        cp.idperiodoinscripciones,
        cp.idcalendarioescolar,
        cp.idioma,
        a.nombre_asignatura,
        CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', IFNULL(p.apellido_materno, '')) AS nombre_docente,
        pi.descripcion_periodo,
        h.dia_semana,
        h.hora_inicio,
        h.hora_fin
    FROM claseprogramada cp
    JOIN asignatura a ON cp.idasignatura = a.idasignatura
    JOIN docente d ON cp.iddocente = d.iddocente
    JOIN persona p ON d.idpersona = p.idpersona
    JOIN periodoinscripciones pi ON cp.idperiodoinscripciones = pi.idperiodoinscripciones
    JOIN horario h ON cp.idhorario = h.idhorario
    WHERE a.nombre_asignatura LIKE %s 
       OR p.nombre LIKE %s
       OR p.apellido_paterno LIKE %s
    ORDER BY pi.descripcion_periodo DESC
    """
    term = f"%{query_term}%"
    cursor.execute(query, (term, term, term))
    return cursor.fetchall()
