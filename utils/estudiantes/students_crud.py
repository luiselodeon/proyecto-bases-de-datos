import mysql.connector
from datetime import date

def get_carreras(cursor):
    """Obtiene la lista de carreras disponibles"""
    cursor.execute("SELECT idcarrera, descripcion_carrera FROM carrera ORDER BY descripcion_carrera")
    return cursor.fetchall()

def get_becas(cursor):
    """Obtiene la lista de becas disponibles"""
    cursor.execute("""
        SELECT b.idbeca, b.descripcion_beca, b.porcentaje_beca, tb.nombre_tipo 
        FROM beca b 
        JOIN tipo_beca tb ON b.idtipo_beca = tb.idtipo_beca 
        WHERE b.estatus_beca = 'A' 
        ORDER BY b.descripcion_beca
    """)
    return cursor.fetchall()

def list_students(cursor):
    query = """
    SELECT e.matricula_alumno, p.nombre, p.apellido_paterno, p.apellido_materno, p.correo, c.descripcion_carrera, e.estatus, b.porcentaje_beca, tb.nombre_tipo
    FROM estudiante e
    JOIN persona p ON e.idpersona = p.idpersona
    LEFT JOIN carrera c ON e.idcarrera = c.idcarrera
    LEFT JOIN beca b ON e.idbeca = b.idbeca
    LEFT JOIN tipo_beca tb ON b.idtipo_beca = tb.idtipo_beca
    ORDER BY p.apellido_paterno, p.apellido_materno, p.nombre;
    """
    cursor.execute(query)
    return cursor.fetchall()

def add_student(cursor, nombre, apellido_paterno, apellido_materno, correo, idcarrera, idbeca=None):
    # 1. Obtener el siguiente ID para persona y estado de cuenta
    cursor.execute("SELECT MAX(idpersona) FROM persona")
    result = cursor.fetchone()
    next_id_persona = (result['MAX(idpersona)'] or 0) + 1 if result else 1
    
    cursor.execute("SELECT MAX(idestadodecuenta) FROM estadodecuenta")
    result = cursor.fetchone()
    next_id_estado_cuenta = (result['MAX(idestadodecuenta)'] or 0) + 1 if result else 1

    # 2. Obtener el primer plan de estudios de la carrera (asumiendo que hay al menos uno)
    cursor.execute("SELECT idplanestudio FROM planestudio WHERE idcarrera = %s LIMIT 1", (idcarrera,))
    plan_result = cursor.fetchone()
    if not plan_result:
        # Si no hay plan, usar un valor por defecto o lanzar error
        idplanestudio = 1  # Valor por defecto, ajustar según necesidad
    else:
        idplanestudio = plan_result['idplanestudio']

    # 3. Insertar en `persona`
    sql_persona = "INSERT INTO persona (idpersona, nombre, apellido_paterno, apellido_materno, correo) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql_persona, (next_id_persona, nombre, apellido_paterno, apellido_materno, correo))

    # 4. Insertar en `estadodecuenta` (con valores por defecto)
    sql_estado_cuenta = "INSERT INTO estadodecuenta (idestadodecuenta, saldo_inicial, saldo_actual) VALUES (%s, 0.0, 0.0)"
    cursor.execute(sql_estado_cuenta, (next_id_estado_cuenta,))

    # 5. Insertar en `estudiante`
    fecha_hoy = date.today()
    sql_estudiante = """INSERT INTO estudiante 
                        (idpersona, idcarrera, idplanestudio, idestadodecuenta, fecha_ingreso, idbeca) 
                        VALUES (%s, %s, %s, %s, %s, %s)"""
    cursor.execute(sql_estudiante, (next_id_persona, idcarrera, idplanestudio, next_id_estado_cuenta, fecha_hoy, idbeca))

def get_student(cursor, matricula):
    query = """
    SELECT p.nombre, p.apellido_paterno, p.apellido_materno, p.correo, e.idcarrera, e.idbeca, e.estatus
    FROM estudiante e
    JOIN persona p ON e.idpersona = p.idpersona
    WHERE e.matricula_alumno = %s
    """
    cursor.execute(query, (matricula,))
    return cursor.fetchone()

def update_student(cursor, matricula, nombre, apellido_paterno, apellido_materno, correo, idcarrera, estatus, idbeca=None):
    # Obtenemos el idpersona asociado a la matrícula
    cursor.execute("SELECT idpersona FROM estudiante WHERE matricula_alumno = %s", (matricula,))
    student_data = cursor.fetchone()
    if student_data:
        id_persona = student_data['idpersona']
        # Actualizamos la tabla persona
        sql_update = """
        UPDATE persona 
        SET nombre = %s, apellido_paterno = %s, apellido_materno = %s, correo = %s
        WHERE idpersona = %s
        """
        cursor.execute(sql_update, (nombre, apellido_paterno, apellido_materno, correo, id_persona))
        
        # Actualizamos la beca, carrera y estatus en la tabla estudiante
        sql_update_estudiante = "UPDATE estudiante SET idbeca = %s, idcarrera = %s, estatus = %s WHERE matricula_alumno = %s"
        cursor.execute(sql_update_estudiante, (idbeca, idcarrera, estatus, matricula))
        
        return True
    return False

def delete_student(cursor, matricula):
    # 1. Obtener idpersona e idestadodecuenta antes de borrar
    cursor.execute("SELECT idpersona, idestadodecuenta FROM estudiante WHERE matricula_alumno = %s", (matricula,))
    result = cursor.fetchone()
    if not result:
        return False
    
    id_persona, id_estado_cuenta = result

    # 2. Eliminar de `estudiante`
    cursor.execute("DELETE FROM estudiante WHERE matricula_alumno = %s", (matricula,))
    
    # 3. Eliminar de `persona`
    cursor.execute("DELETE FROM persona WHERE idpersona = %s", (id_persona,))

    # 4. Eliminar de `estadodecuenta`
    cursor.execute("DELETE FROM estadodecuenta WHERE idestadodecuenta = %s", (id_estado_cuenta,))
    return True

def search_student(cursor, query_term):
    search_pattern = f"%{query_term}%"
    query = """
    SELECT e.matricula_alumno, p.nombre, p.apellido_paterno, p.apellido_materno, p.correo, c.descripcion_carrera, e.estatus, b.porcentaje_beca, tb.nombre_tipo
    FROM estudiante e
    JOIN persona p ON e.idpersona = p.idpersona
    LEFT JOIN carrera c ON e.idcarrera = c.idcarrera
    LEFT JOIN beca b ON e.idbeca = b.idbeca
    LEFT JOIN tipo_beca tb ON b.idtipo_beca = tb.idtipo_beca
    WHERE p.nombre LIKE %s 
       OR p.apellido_paterno LIKE %s 
       OR p.apellido_materno LIKE %s
       OR p.correo LIKE %s
       OR e.matricula_alumno LIKE %s
       OR tb.nombre_tipo LIKE %s
       OR CAST(b.porcentaje_beca AS CHAR) LIKE %s
    ORDER BY p.apellido_paterno, p.apellido_materno, p.nombre;
    """
    cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
    return cursor.fetchall()
