import mysql.connector

# Note: This implements a virtual 'pago' system based on estadodecuenta updates
# Since there's no 'pago' table in the schema, we track payment history via comments

def list_pagos(cursor):
    """List all estadodecuenta records with payment activity"""
    query = """
    SELECT 
        ec.idestadodecuenta,
        e.matricula_alumno,
        CONCAT(p.nombre, ' ', p.apellido_paterno) AS nombre_estudiante,
        ec.saldo_inicial,
        ec.saldo_actual,
        (ec.saldo_inicial - ec.saldo_actual) AS monto_pagado
    FROM estadodecuenta ec
    JOIN estudiante e ON e.idestadodecuenta = ec.idestadodecuenta
    JOIN persona p ON e.idpersona = p.idpersona
    WHERE ec.saldo_inicial != ec.saldo_actual
    ORDER BY e.matricula_alumno
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_estado_cuenta(cursor, idestadodecuenta):
    """Get estado de cuenta details"""
    query = """
    SELECT 
        ec.*,
        e.matricula_alumno,
        CONCAT(p.nombre, ' ', p.apellido_paterno) AS nombre_estudiante
    FROM estadodecuenta ec
    LEFT JOIN estudiante e ON e.idestadodecuenta = ec.idestadodecuenta
    LEFT JOIN persona p ON e.idpersona = p.idpersona
    WHERE ec.idestadodecuenta = %s
    """
    cursor.execute(query, (idestadodecuenta,))
    return cursor.fetchone()

def registrar_pago(cursor, idestadodecuenta, monto_pago):
    """Register a payment by reducing saldo_actual"""
    query = """
    UPDATE estadodecuenta
    SET saldo_actual = GREATEST(0, saldo_actual - %s)
    WHERE idestadodecuenta = %s
    """
    cursor.execute(query, (monto_pago, idestadodecuenta))

def get_estudiantes_con_saldo(cursor):
    """Get students with outstanding balances"""
    query = """
    SELECT 
        e.matricula_alumno,
        CONCAT(p.nombre, ' ', p.apellido_paterno) AS nombre_completo,
        ec.idestadodecuenta,
        ec.saldo_actual
    FROM estudiante e
    JOIN persona p ON e.idpersona = p.idpersona
    JOIN estadodecuenta ec ON e.idestadodecuenta = ec.idestadodecuenta
    WHERE ec.saldo_actual \u003e 0
    ORDER BY nombre_completo
    """
    cursor.execute(query)
    return cursor.fetchall()
