import mysql.connector
from datetime import date

def list_inscripciones(cursor):
    """List all inscripciones"""
    query = """
    SELECT 
        i.idinscripcion,
        i.matricula_alumno,
        i.idclaseprogramada,
        i.fecha_inscripcion,
        i.motivo_inscripcion,
        i.estatus,
        CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', IFNULL(p.apellido_materno, '')) AS nombre_estudiante,
        a.nombre_asignatura,
        pi.descripcion_periodo,
        h.dia_semana,
        h.hora_inicio,
        h.hora_fin,
        au.descripcion_aula,
        CONCAT(pd.nombre, ' ', pd.apellido_paterno) AS nombre_docente
    FROM inscripcion i
    JOIN estudiante e ON i.matricula_alumno = e.matricula_alumno
    JOIN persona p ON e.idpersona = p.idpersona
    JOIN claseprogramada cp ON i.idclaseprogramada = cp.idclaseprogramada
    JOIN asignatura a ON cp.idasignatura = a.idasignatura
    JOIN periodoinscripciones pi ON cp.idperiodoinscripciones = pi.idperiodoinscripciones
    JOIN horario h ON cp.idhorario = h.idhorario
    JOIN aula au ON cp.idaula = au.idaula
    JOIN docente d ON cp.iddocente = d.iddocente
    JOIN persona pd ON d.idpersona = pd.idpersona
    ORDER BY i.fecha_inscripcion DESC
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_inscripcion(cursor, idinscripcion):
    """Get a specific inscripcion"""
    query = "SELECT * FROM inscripcion WHERE idinscripcion = %s"
    cursor.execute(query, (idinscripcion,))
    return cursor.fetchone()

def check_classroom_capacity(cursor, idclaseprogramada):
    """Check if classroom has available capacity for new enrollment"""
    # Get classroom capacity
    query_capacity = """
    SELECT au.capacidad
    FROM claseprogramada cp
    JOIN aula au ON cp.idaula = au.idaula
    WHERE cp.idclaseprogramada = %s
    """
    cursor.execute(query_capacity, (idclaseprogramada,))
    result = cursor.fetchone()
    
    if not result:
        return False, "Clase programada no encontrada"
    
    capacidad = result['capacidad']
    
    # Count current enrollments
    query_count = """
    SELECT COUNT(*) as total
    FROM inscripcion
    WHERE idclaseprogramada = %s AND estatus != 'CANCELADA'
    """
    cursor.execute(query_count, (idclaseprogramada,))
    count_result = cursor.fetchone()
    current_enrollments = count_result['total']
    
    if current_enrollments >= capacidad:
        return False, f"El aula está llena ({current_enrollments}/{capacidad})"
    
    return True, None

def add_inscripcion(cursor, matricula_alumno, idclaseprogramada, motivo_inscripcion, estatus='INICIADA'):
    """Add new inscripcion with capacity validation"""
    # Check capacity first
    can_enroll, error = check_classroom_capacity(cursor, idclaseprogramada)
    if not can_enroll:
        raise Exception(error)
    
    fecha_inscripcion = date.today()
    query = """
    INSERT INTO inscripcion (matricula_alumno, idclaseprogramada, fecha_inscripcion, motivo_inscripcion, estatus)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (matricula_alumno, idclaseprogramada, fecha_inscripcion, motivo_inscripcion, estatus))
    return cursor.lastrowid

def update_inscripcion(cursor, idinscripcion, idclaseprogramada, motivo_inscripcion, estatus):
    """Update inscripcion"""
    # Get current enrollment info
    current = get_inscripcion(cursor, idinscripcion)
    
    # If changing to a different class, check new class capacity
    if current and current['idclaseprogramada'] != idclaseprogramada:
        can_enroll, error = check_classroom_capacity(cursor, idclaseprogramada)
        if not can_enroll:
            raise Exception(error)
    
    fecha_inscripcion = date.today()
    query = """
    UPDATE inscripcion
    SET idclaseprogramada = %s, fecha_inscripcion = %s, motivo_inscripcion = %s, estatus = %s
    WHERE idinscripcion = %s
    """
    cursor.execute(query, (idclaseprogramada, fecha_inscripcion, motivo_inscripcion, estatus, idinscripcion))

def delete_inscripcion(cursor, idinscripcion):
    """Delete inscripcion"""
    query = "DELETE FROM inscripcion WHERE idinscripcion = %s"
    cursor.execute(query, (idinscripcion,))

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

def get_clases_programadas(cursor):
    """Get list of scheduled classes with enrollment info for dropdown"""
    query = """
    SELECT 
        cp.idclaseprogramada,
        a.nombre_asignatura,
        pi.descripcion_periodo,
        CONCAT(h.dia_semana, ' ', h.hora_inicio, '-', h.hora_fin) AS horario,
        CONCAT(pd.nombre, ' ', pd.apellido_paterno) AS nombre_docente,
        au.descripcion_aula,
        au.capacidad,
        COUNT(i.idinscripcion) AS inscritos
    FROM claseprogramada cp
    JOIN asignatura a ON cp.idasignatura = a.idasignatura
    JOIN periodoinscripciones pi ON cp.idperiodoinscripciones = pi.idperiodoinscripciones
    JOIN horario h ON cp.idhorario = h.idhorario
    JOIN aula au ON cp.idaula = au.idaula
    JOIN docente d ON cp.iddocente = d.iddocente
    JOIN persona pd ON d.idpersona = pd.idpersona
    LEFT JOIN inscripcion i ON cp.idclaseprogramada = i.idclaseprogramada AND i.estatus != 'CANCELADA'
    WHERE pi.estatus = 'ABIERTO'
    GROUP BY cp.idclaseprogramada, a.nombre_asignatura, pi.descripcion_periodo, 
             h.dia_semana, h.hora_inicio, h.hora_fin, pd.nombre, pd.apellido_paterno,
             au.descripcion_aula, au.capacidad
    ORDER BY pi.descripcion_periodo DESC, a.nombre_asignatura
    """
    cursor.execute(query)
    return cursor.fetchall()

def search_inscripciones(cursor, query_term):
    """Search inscripciones by student name, subject, or period"""
    query = """
    SELECT 
        i.idinscripcion,
        i.matricula_alumno,
        i.idclaseprogramada,
        i.fecha_inscripcion,
        i.motivo_inscripcion,
        i.estatus,
        CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', IFNULL(p.apellido_materno, '')) AS nombre_estudiante,
        a.nombre_asignatura,
        pi.descripcion_periodo,
        h.dia_semana,
        h.hora_inicio,
        h.hora_fin,
        au.descripcion_aula,
        CONCAT(pd.nombre, ' ', pd.apellido_paterno) AS nombre_docente
    FROM inscripcion i
    JOIN estudiante e ON i.matricula_alumno = e.matricula_alumno
    JOIN persona p ON e.idpersona = p.idpersona
    JOIN claseprogramada cp ON i.idclaseprogramada = cp.idclaseprogramada
    JOIN asignatura a ON cp.idasignatura = a.idasignatura
    JOIN periodoinscripciones pi ON cp.idperiodoinscripciones = pi.idperiodoinscripciones
    JOIN horario h ON cp.idhorario = h.idhorario
    JOIN aula au ON cp.idaula = au.idaula
    JOIN docente d ON cp.iddocente = d.iddocente
    JOIN persona pd ON d.idpersona = pd.idpersona
    WHERE p.nombre LIKE %s 
       OR p.apellido_paterno LIKE %s
       OR a.nombre_asignatura LIKE %s
       OR pi.descripcion_periodo LIKE %s
    ORDER BY i.fecha_inscripcion DESC
    """
    term = f"%{query_term}%"
    cursor.execute(query, (term, term, term, term))
    return cursor.fetchall()
