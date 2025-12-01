import mysql.connector

# Note: This implements a virtual 'pago' system based on estadodecuenta updates
# Since there's no 'pago' table in the schema, we track payment history via comments

def list_pagos(cursor):
    """List all payments with student details"""
    query = """
    SELECT 
        p.idpago,
        p.idestadodecuenta,
        p.fecha_pago,
        p.hora_pago,
        p.forma_pago,
        p.tipo_movimiento,
        p.importe_pago,
        p.referencia,
        e.matricula_alumno,
        CONCAT(per.nombre, ' ', per.apellido_paterno) AS nombre_estudiante,
        ec.saldo_actual
    FROM pago p
    JOIN estadodecuenta ec ON p.idestadodecuenta = ec.idestadodecuenta
    JOIN estudiante e ON e.idestadodecuenta = ec.idestadodecuenta
    JOIN persona per ON e.idpersona = per.idpersona
    ORDER BY p.fecha_pago DESC, p.hora_pago DESC
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_pago(cursor, idpago):
    """Get a single payment by ID"""
    query = """
    SELECT * FROM pago WHERE idpago = %s
    """
    cursor.execute(query, (idpago,))
    return cursor.fetchone()

def add_pago(cursor, idestadodecuenta, forma_pago, tipo_movimiento, importe_pago, referencia=None):
    """Register a new payment and update balance"""
    # 1. Insert into pago (Date/Time auto-set by NOW())
    query_insert = """
    INSERT INTO pago (idestadodecuenta, fecha_pago, hora_pago, forma_pago, tipo_movimiento, importe_pago, referencia)
    VALUES (%s, CURDATE(), CURTIME(), %s, %s, %s, %s)
    """
    cursor.execute(query_insert, (idestadodecuenta, forma_pago, tipo_movimiento, importe_pago, referencia))
    
    # 2. Update estadodecuenta (Subtract amount from balance)
    # Use GREATEST to ensure saldo_actual never goes below 0 (constraint requirement)
    query_update = """
    UPDATE estadodecuenta
    SET saldo_actual = GREATEST(0, saldo_actual - %s)
    WHERE idestadodecuenta = %s
    """
    cursor.execute(query_update, (importe_pago, idestadodecuenta))




def update_pago(cursor, idpago, forma_pago, tipo_movimiento, new_importe, referencia=None):
    """Update payment details and adjust balance"""
    # 1. Get old amount and idestadodecuenta
    cursor.execute("SELECT importe_pago, idestadodecuenta FROM pago WHERE idpago = %s", (idpago,))
    old_data = cursor.fetchone()
    if not old_data:
        return False
    
    old_importe = old_data['importe_pago']
    idestadodecuenta = old_data['idestadodecuenta']

    # 2. Update pago record (Keep original date/time)
    query_update_pago = """
    UPDATE pago 
    SET forma_pago = %s, tipo_movimiento = %s, importe_pago = %s, referencia = %s
    WHERE idpago = %s
    """
    cursor.execute(query_update_pago, (forma_pago, tipo_movimiento, new_importe, referencia, idpago))

    # 3. Adjust balance: Add back old amount, subtract new amount
    # Net change = old_importe - new_importe (added to balance)
    # Use GREATEST to ensure saldo_actual never goes below 0 (constraint requirement)
    query_adjust_balance = """
    UPDATE estadodecuenta
    SET saldo_actual = GREATEST(0, saldo_actual + %s - %s)
    WHERE idestadodecuenta = %s
    """
    cursor.execute(query_adjust_balance, (old_importe, new_importe, idestadodecuenta))
    return True

def delete_pago(cursor, idpago):
    """Delete payment and revert balance"""
    # 1. Get amount and idestadodecuenta
    cursor.execute("SELECT importe_pago, idestadodecuenta FROM pago WHERE idpago = %s", (idpago,))
    data = cursor.fetchone()
    if not data:
        return False
    
    importe = data['importe_pago']
    idestadodecuenta = data['idestadodecuenta']

    # 2. Delete pago
    cursor.execute("DELETE FROM pago WHERE idpago = %s", (idpago,))

    # 3. Revert balance (Add amount back)
    cursor.execute("UPDATE estadodecuenta SET saldo_actual = saldo_actual + %s WHERE idestadodecuenta = %s", (importe, idestadodecuenta))
    return True

def get_estudiantes_para_pago(cursor):
    """Get all students for payment selection"""
    query = """
    SELECT 
        e.matricula_alumno,
        CONCAT(p.nombre, ' ', p.apellido_paterno) AS nombre_completo,
        ec.idestadodecuenta,
        ec.saldo_actual
    FROM estudiante e
    JOIN persona p ON e.idpersona = p.idpersona
    JOIN estadodecuenta ec ON e.idestadodecuenta = ec.idestadodecuenta
    ORDER BY nombre_completo
    """
    cursor.execute(query)
    return cursor.fetchall()
