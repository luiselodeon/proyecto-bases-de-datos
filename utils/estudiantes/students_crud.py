import mysql.connector

def list_students(cursor):
    query = """
    SELECT e.matricula_alumno, p.nombre, p.apellido_paterno, p.apellido_materno, p.correo
    FROM estudiante e
    JOIN persona p ON e.idpersona = p.idpersona
    ORDER BY p.apellido_paterno, p.apellido_materno, p.nombre;
    """
    cursor.execute(query)
    return cursor.fetchall()

def add_student(cursor, matricula, nombre, apellido_paterno, apellido_materno, correo):
    # 1. Obtener el siguiente ID para persona y estado de cuenta
    cursor.execute("SELECT MAX(idpersona) FROM persona")
    next_id_persona = (cursor.fetchone()[0] or 0) + 1
    
    cursor.execute("SELECT MAX(idestadodecuenta) FROM estadodecuenta")
    next_id_estado_cuenta = (cursor.fetchone()[0] or 0) + 1

    # 2. Insertar en `persona`
    sql_persona = "INSERT INTO persona (idpersona, nombre, apellido_paterno, apellido_materno, correo) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql_persona, (next_id_persona, nombre, apellido_paterno, apellido_materno, correo))

    # 3. Insertar en `estadodecuenta` (con valores por defecto)
    sql_estado_cuenta = "INSERT INTO estadodecuenta (idestadodecuenta, cargos, ingresos) VALUES (%s, 0.0, 0.0)"
    cursor.execute(sql_estado_cuenta, (next_id_estado_cuenta,))

    # 4. Insertar en `estudiante`
    sql_estudiante = "INSERT INTO estudiante (matricula_alumno, idpersona, idestadocuenta) VALUES (%s, %s, %s)"
    cursor.execute(sql_estudiante, (matricula, next_id_persona, next_id_estado_cuenta))

def get_student(cursor, matricula):
    query = """
    SELECT p.nombre, p.apellido_paterno, p.apellido_materno, p.correo
    FROM estudiante e
    JOIN persona p ON e.idpersona = p.idpersona
    WHERE e.matricula_alumno = %s
    """
    cursor.execute(query, (matricula,))
    return cursor.fetchone()

def update_student(cursor, matricula, nombre, apellido_paterno, apellido_materno, correo):
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
        return True
    return False

def delete_student(cursor, matricula):
    # 1. Obtener idpersona e idestadocuenta antes de borrar
    cursor.execute("SELECT idpersona, idestadocuenta FROM estudiante WHERE matricula_alumno = %s", (matricula,))
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
    SELECT e.matricula_alumno, p.nombre, p.apellido_paterno, p.apellido_materno, p.correo
    FROM estudiante e
    JOIN persona p ON e.idpersona = p.idpersona
    WHERE p.nombre LIKE %s 
       OR p.apellido_paterno LIKE %s 
       OR p.apellido_materno LIKE %s
       OR p.correo LIKE %s
       OR e.matricula_alumno LIKE %s
    ORDER BY p.apellido_paterno, p.apellido_materno, p.nombre;
    """
    cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
    return cursor.fetchall()
