import mysql.connector

def get_top_students(cursor, limit=20):
    """
    Obtiene los estudiantes con mejor promedio general basado en historial académico.
    """
    query = """
    SELECT 
        e.matricula_alumno,
        CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', IFNULL(p.apellido_materno, '')) AS nombre_completo,
        c.descripcion_carrera,
        ROUND(AVG(h.calificacion_final), 2) as promedio_general
    FROM historialacademico h
    JOIN estudiante e ON h.matricula_alumno = e.matricula_alumno
    JOIN persona p ON e.idpersona = p.idpersona
    JOIN carrera c ON e.idcarrera = c.idcarrera
    GROUP BY e.matricula_alumno, nombre_completo, c.descripcion_carrera
    ORDER BY promedio_general DESC
    LIMIT %s
    """
    cursor.execute(query, (limit,))
    return cursor.fetchall()

def get_popular_subjects(cursor, limit=20):
    """
    Obtiene las materias con más inscripciones.
    """
    query = """
    SELECT 
        a.idasignatura,
        a.nombre_asignatura,
        COUNT(i.idinscripcion) as total_inscritos
    FROM inscripcion i
    JOIN claseprogramada cp ON i.idclaseprogramada = cp.idclaseprogramada
    JOIN asignatura a ON cp.idasignatura = a.idasignatura
    GROUP BY a.idasignatura, a.nombre_asignatura
    ORDER BY total_inscritos DESC
    LIMIT %s
    """
    cursor.execute(query, (limit,))
    return cursor.fetchall()

def get_busy_schedules(cursor, limit=20):
    """
    Obtiene los horarios con más clases programadas.
    """
    query = """
    SELECT 
        h.idhorario,
        h.dia_semana,
        DATE_FORMAT(h.hora_inicio, '%H:%i') as hora_inicio,
        DATE_FORMAT(h.hora_fin, '%H:%i') as hora_fin,
        COUNT(cp.idclaseprogramada) as total_clases
    FROM claseprogramada cp
    JOIN horario h ON cp.idhorario = h.idhorario
    GROUP BY h.idhorario, h.dia_semana, h.hora_inicio, h.hora_fin
    ORDER BY total_clases DESC
    LIMIT %s
    """
    cursor.execute(query, (limit,))
    return cursor.fetchall()
