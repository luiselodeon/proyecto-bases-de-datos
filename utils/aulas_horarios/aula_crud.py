import mysql.connector

def list_aulas(cursor):
    """List all aulas"""
    query = "SELECT * FROM aula ORDER BY descripcion_aula"
    cursor.execute(query)
    return cursor.fetchall()

def get_aula(cursor, idaula):
    """Get a specific aula"""
    query = "SELECT * FROM aula WHERE idaula = %s"
    cursor.execute(query, (idaula,))
    return cursor.fetchone()

def check_aula_capacity_reduction(cursor, idaula, new_capacity):
    """
    Check if reducing aula capacity would violate current enrollments.
    Returns (can_update, error_message)
    """
    # Get maximum enrollment count for any class using this aula
    query = """
    SELECT 
        cp.idclaseprogramada,
        a.nombre_asignatura,
        pi.descripcion_periodo,
        COUNT(i.idinscripcion) as inscritos
    FROM claseprogramada cp
    JOIN asignatura a ON cp.idasignatura = a.idasignatura
    JOIN periodoinscripciones pi ON cp.idperiodoinscripciones = pi.idperiodoinscripciones
    LEFT JOIN inscripcion i ON cp.idclaseprogramada = i.idclaseprogramada 
        AND i.estatus != 'CANCELADA'
    WHERE cp.idaula = %s
    GROUP BY cp.idclaseprogramada, a.nombre_asignatura, pi.descripcion_periodo
    HAVING COUNT(i.idinscripcion) > %s
    ORDER BY inscritos DESC
    LIMIT 1
    """
    cursor.execute(query, (idaula, new_capacity))
    result = cursor.fetchone()
    
    if result:
        return False, f"No se puede reducir la capacidad a {new_capacity}. La clase '{result['nombre_asignatura']}' ({result['descripcion_periodo']}) tiene {result['inscritos']} estudiantes inscritos."
    
    return True, None

def add_aula(cursor, descripcion, lugar, capacidad):
    """Add new aula"""
    query = """
    INSERT INTO aula (descripcion_aula, lugar_fisico, capacidad)
    VALUES (%s, %s, %s)
    """
    cursor.execute(query, (descripcion, lugar, capacidad))
    return cursor.lastrowid

def update_aula(cursor, idaula, descripcion, lugar, capacidad):
    """Update aula with capacity validation"""
    # Convert capacidad to int if it's a string
    capacidad = int(capacidad)
    
    # Get current capacity
    current_aula = get_aula(cursor, idaula)
    if not current_aula:
        raise Exception("Aula no encontrada")
    
    current_capacity = current_aula['capacidad']
    
    # If reducing capacity, check if it's valid
    if capacidad < current_capacity:
        can_update, error = check_aula_capacity_reduction(cursor, idaula, capacidad)
        if not can_update:
            raise Exception(error)
    
    query = """
    UPDATE aula
    SET descripcion_aula = %s, lugar_fisico = %s, capacidad = %s
    WHERE idaula = %s
    """
    cursor.execute(query, (descripcion, lugar, capacidad, idaula))

def delete_aula(cursor, idaula):
    """Delete aula"""
    query = "DELETE FROM aula WHERE idaula = %s"
    cursor.execute(query, (idaula,))

def search_aulas(cursor, query_term):
    """Search aulas by description or place"""
    query = "SELECT * FROM aula WHERE descripcion_aula LIKE %s OR lugar_fisico LIKE %s ORDER BY descripcion_aula"
    term = f"%{query_term}%"
    cursor.execute(query, (term, term))
    return cursor.fetchall()
