import mysql.connector

def list_estados(cursor):
    """List all estados de cuenta with student info"""
    query = """
    SELECT 
        ec.*,
        e.matricula_alumno,
        CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', IFNULL(p.apellido_materno, '')) AS nombre_estudiante
    FROM estadodecuenta ec
    LEFT JOIN estudiante e ON e.idestadodecuenta = ec.idestadodecuenta
    LEFT JOIN persona p ON e.idpersona = p.idpersona
    ORDER BY ec.idestadodecuenta ASC
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_estado(cursor, idestadodecuenta):
    """Get a specific estado de cuenta"""
    query = "SELECT * FROM estadodecuenta WHERE idestadodecuenta = %s"
    cursor.execute(query, (idestadodecuenta,))
    return cursor.fetchone()

def add_estado(cursor, saldo_inicial, limite_credito):
    """Add new estado de cuenta"""
    query = """
    INSERT INTO estadodecuenta (saldo_inicial, saldo_actual, limite_credito)
    VALUES (%s, %s, %s)
    """
    cursor.execute(query, (saldo_inicial, saldo_inicial, limite_credito))
    return cursor.lastrowid

def update_estado(cursor, idestadodecuenta, saldo_actual, limite_credito):
    """Update estado de cuenta"""
    query = """
    UPDATE estadodecuenta
    SET saldo_actual = %s, limite_credito = %s
    WHERE idestadodecuenta = %s
    """
    cursor.execute(query, (saldo_actual, limite_credito, idestadodecuenta))

def delete_estado(cursor, idestadodecuenta):
    """Delete estado de cuenta"""
    query = "DELETE FROM estadodecuenta WHERE idestadodecuenta = %s"
    cursor.execute(query, (idestadodecuenta,))

def search_estados(cursor, query_term):
    """Search estados de cuenta by student name"""
    query = """
    SELECT 
        ec.*,
        e.matricula_alumno,
        CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', IFNULL(p.apellido_materno, '')) AS nombre_estudiante
    FROM estadodecuenta ec
    LEFT JOIN estudiante e ON e.idestadodecuenta = ec.idestadodecuenta
    LEFT JOIN persona p ON e.idpersona = p.idpersona
    WHERE p.nombre LIKE %s OR p.apellido_paterno LIKE %s OR e.matricula_alumno LIKE %s
    ORDER BY ec.idestadodecuenta ASC
    """
    term = f"%{query_term}%"
    cursor.execute(query, (term, term, term))
    return cursor.fetchall()
