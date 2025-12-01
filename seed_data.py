#!/usr/bin/env python3
"""
Database Seeding Script
Populates the database with realistic test data
"""

import os
import mysql.connector
from faker import Faker
import random
from datetime import datetime, timedelta
from decimal import Decimal
from werkzeug.security import generate_password_hash

# Initialize Faker
fake = Faker('es_MX')  # Mexican Spanish locale

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'rootpassword'),
        database=os.getenv('DB_NAME', 'universidad_db')
    )

def clear_database(cursor):
    """Clear all tables in reverse dependency order"""
    print("🗑️  Clearing existing data...")
    
    tables = [
        'pago', 'calificacion_estudiante', 'evaluacion', 'asistencia',
        'inscripcion', 'historialacademico', 'docente_capacitacion',
        'docente_certificacion', 'estudiante', 'docente',
        'claseprogramada', 'prerequisito_asignatura', 'plan_asignatura',
        'horario', 'aula', 'calendarioescolar', 'periodoinscripciones',
        'asignatura', 'planestudio', 'carrera', 'capacitacion',
        'certificacion', 'beca', 'tipo_beca', 'departamentoasignatura',
        'departamentoacademico', 'estadodecuenta', 'persona', 'usuarios'
    ]
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in tables:
        try:
            cursor.execute(f"TRUNCATE TABLE {table}")
        except Exception as e:
            print(f"Could not truncate {table}: {e}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    print("Database cleared\n")

def seed_personas(cursor, count=100):
    """Generate persona records"""
    print(f"Creating {count} personas...")
    personas = []
    
    for i in range(count):
        nombre = fake.first_name()
        apellido_paterno = fake.last_name()
        apellido_materno = fake.last_name()
        correo = f"{nombre.lower()}.{apellido_paterno.lower()}@{fake.domain_name()}"
        
        cursor.execute("""
            INSERT INTO persona (nombre, apellido_paterno, apellido_materno, correo)
            VALUES (%s, %s, %s, %s)
        """, (nombre, apellido_paterno, apellido_materno, correo))
        
        personas.append(cursor.lastrowid)
    
    print(f"Created {len(personas)} personas\n")
    return personas

def seed_departamentos_academicos(cursor, count=5):
    """Generate departamento academico records"""
    print(f"Creating {count} departamentos académicos...")
    
    departamentos = [
        "Ingeniería y Tecnología",
        "Ciencias Sociales y Humanidades",
        "Ciencias de la Salud",
        "Ciencias Exactas y Naturales",
        "Artes y Diseño"
    ]
    
    ids = []
    for depto in departamentos[:count]:
        cursor.execute("""
            INSERT INTO departamentoacademico (nombre_departamento)
            VALUES (%s)
        """, (depto,))
        ids.append(cursor.lastrowid)
    
    print(f"Created {len(ids)} departamentos académicos\n")
    return ids

def seed_departamentos_asignatura(cursor, count=5):
    """Generate departamento asignatura records"""
    print(f"Creating {count} departamentos de asignatura...")
    
    deptos = [
        "Matemáticas y Física",
        "Programación y Desarrollo",
        "Humanidades y Letras",
        "Administración y Negocios",
        "Diseño y Comunicación"
    ]
    
    ids = []
    for depto in deptos[:count]:
        cursor.execute("""
            INSERT INTO departamentoasignatura (nombre_deptoasignatura)
            VALUES (%s)
        """, (depto,))
        ids.append(cursor.lastrowid)
    
    print(f"Created {len(ids)} departamentos de asignatura\n")
    return ids

def seed_tipos_beca(cursor, count=5):
    """Generate tipo_beca records"""
    print(f"Creating {count} tipos de beca...")
    
    tipos = [
        "Beca Académica",
        "Beca Deportiva",
        "Beca Cultural",
        "Beca Socioeconómica",
        "Beca de Excelencia"
    ]
    
    ids = []
    for tipo in tipos[:count]:
        cursor.execute("""
            INSERT INTO tipo_beca (nombre_tipo)
            VALUES (%s)
        """, (tipo,))
        ids.append(cursor.lastrowid)
    
    print(f"Created {len(ids)} tipos de beca\n")
    return ids

def seed_becas(cursor, tipos_beca, count=10):
    """Generate beca records"""
    print(f"Creating {count} becas...")
    
    ids = []
    for i in range(count):
        descripcion = f"Beca {fake.word().capitalize()} {fake.year()}"
        porcentaje = random.choice([10, 20, 25, 30, 40, 50, 75, 100])
        estatus = random.choice(['A', 'A', 'A', 'B'])  # Mostly active
        idtipo_beca = random.choice(tipos_beca)
        
        cursor.execute("""
            INSERT INTO beca (descripcion_beca, porcentaje_beca, estatus_beca, idtipo_beca)
            VALUES (%s, %s, %s, %s)
        """, (descripcion, porcentaje, estatus, idtipo_beca))
        ids.append(cursor.lastrowid)
    
    print(f"Created {len(ids)} becas\n")
    return ids

def seed_carreras(cursor, deptos_academicos, count=8):
    """Generate carrera records"""
    print(f"Creating {count} carreras...")
    
    carreras_data = [
        ("Ingeniería en Sistemas Computacionales", 240, random.choice(deptos_academicos), 15000.00),
        ("Licenciatura en Administración", 220, random.choice(deptos_academicos), 12000.00),
        ("Ingeniería Industrial", 230, random.choice(deptos_academicos), 14000.00),
        ("Licenciatura en Diseño Gráfico", 200, random.choice(deptos_academicos), 13000.00),
        ("Licenciatura en Psicología", 210, random.choice(deptos_academicos), 11000.00),
        ("Ingeniería Civil", 250, random.choice(deptos_academicos), 16000.00),
        ("Licenciatura en Comunicación", 200, random.choice(deptos_academicos), 10000.00),
        ("Licenciatura en Derecho", 240, random.choice(deptos_academicos), 14500.00),
    ]
    
    ids = []
    for carrera_data in carreras_data[:count]:
        cursor.execute("""
            INSERT INTO carrera (descripcion_carrera, creditos_carrera, iddepartamentoacademico, costo_inscripcion)
            VALUES (%s, %s, %s, %s)
        """, carrera_data)
        ids.append(cursor.lastrowid)
    
    print(f"Created {len(ids)} carreras\n")
    return ids

def seed_planes_estudio(cursor, carreras):
    """Generate plan estudio for each carrera"""
    print(f"Creating planes de estudio...")
    
    ids = []
    for idcarrera in carreras:
        nombre_plan = f"Plan {random.choice([2020, 2021, 2022, 2023])}"
        vigencia_inicio = fake.date_between(start_date='-3y', end_date='today')
        vigencia_fin = None if random.random() > 0.3 else fake.date_between(start_date='today', end_date='+2y')
        
        cursor.execute("""
            INSERT INTO planestudio (nombre_plan, vigencia_inicio, vigencia_fin, idcarrera)
            VALUES (%s, %s, %s, %s)
        """, (nombre_plan, vigencia_inicio, vigencia_fin, idcarrera))
        ids.append(cursor.lastrowid)
    
    print(f"Created {len(ids)} planes de estudio\n")
    return ids

def seed_asignaturas(cursor, deptos_asignatura, count=40):
    """Generate asignatura records"""
    print(f"Creating {count} asignaturas...")
    
    materias = [
        "Cálculo Diferencial", "Álgebra Lineal", "Física", "Química",
        "Programación I", "Programación II", "Estructuras de Datos",
        "Base de Datos", "Redes de Computadoras", "Sistemas Operativos",
        "Administración", "Contabilidad", "Marketing", "Finanzas",
        "Psicología General", "Psicología Social", "Estadística",
        "Metodología de la Investigación", "Ética Profesional",
        "Desarrollo Web", "Inteligencia Artificial", "Ciberseguridad",
        "Diseño Digital", "Animación", "Comunicación Organizacional",
        "Derecho Civil", "Derecho Penal", "Inglés I", "Inglés II",
        "Mecánica de Materiales", "Termodinámica", "Electromagnetismo",
        "Análisis Numérico", "Ecuaciones Diferenciales", "Probabilidad",
        "Machine Learning", "Cloud Computing", "DevOps", "UX/UI Design",
        "Gestión de Proyectos"
    ]
    
    ids = []
    for i in range(min(count, len(materias))):
        nombre = materias[i]
        clave = f"{fake.random_uppercase_letter()}{fake.random_uppercase_letter()}{random.randint(100, 999)}"
        creditos_asignatura = random.choice([4, 5, 6, 8])
        horas_por_sesion = Decimal(random.choice([1.5, 2.0, 2.5, 3.0, 3.5, 4.0]))
        iddeptoasignatura = random.choice(deptos_asignatura)
        
        cursor.execute("""
            INSERT INTO asignatura (clave_asignatura, nombre_asignatura, creditos_asignatura, horas_por_sesion, iddeptoasignatura)
            VALUES (%s, %s, %s, %s, %s)
        """, (clave, nombre, creditos_asignatura, horas_por_sesion, iddeptoasignatura))
        ids.append(cursor.lastrowid)
    
    print(f"Created {len(ids)} asignaturas\n")
    return ids

def seed_plan_asignatura(cursor, planes, asignaturas):
    """Link planes with asignaturas"""
    print(f"Linking planes de estudio with asignaturas...")
    
    count = 0
    for idplan in planes:
        # Each plan has 20-30 asignaturas
        num_asignaturas = random.randint(20, min(30, len(asignaturas)))
        selected_asignaturas = random.sample(asignaturas, num_asignaturas)
        
        for semestre, idasignatura in enumerate(selected_asignaturas, start=1):
            semestre_num = ((semestre - 1) // 5) + 1  # 5 materias per semester
            
            cursor.execute("""
                INSERT INTO plan_asignatura (idplanestudio, idasignatura, semestre)
                VALUES (%s, %s, %s)
            """, (idplan, idasignatura, semestre_num))
            count += 1
    
    print(f"Created {count} plan-asignatura relationships\n")

def seed_capacitaciones(cursor, count=10):
    """Generate capacitacion records"""
    print(f"Creating {count} capacitaciones...")
    
    tipos = ["Curso de", "Taller de", "Diplomado en", "Seminario de", "Certificación en"]
    temas = ["Pedagogía", "Tecnología Educativa", "Liderazgo", "Innovación", 
             "Investigación", "Competencias Digitales", "Evaluación"]
    
    ids = []
    for i in range(count):
        descripcion = f"{random.choice(tipos)} {random.choice(temas)}"
        fecha_inicio = fake.date_between(start_date='-1y', end_date='+6m')
        fecha_fin = fecha_inicio + timedelta(days=random.randint(30, 180))
        horas = Decimal(random.choice([20, 30, 40, 60, 80, 100, 120]))
        institucion = fake.company()
        
        cursor.execute("""
            INSERT INTO capacitacion (descripcion, fecha_inicio, fecha_fin, horas_capacitacion, institucion)
            VALUES (%s, %s, %s, %s, %s)
        """, (descripcion, fecha_inicio, fecha_fin, horas, institucion))
        ids.append(cursor.lastrowid)
    
    print(f"Created {len(ids)} capacitaciones\n")
    return ids

def seed_certificaciones(cursor, count=10):
    """Generate certificacion records"""
    print(f"Creating {count} certificaciones...")
    
    certs = [
        "Certificación en Competencias Docentes",
        "Certificación en Tecnología Educativa",
        "Certificación Internacional en Inglés",
        "Certificación en Evaluación Educativa",
        "Certificación en Investigación",
        "Certificación en Gestión Académica",
        "Certificación en Innovación Pedagógica",
        "Certificación en Educación Digital",
        "Certificación en Didáctica",
        "Certificación en Tutorías Académicas"
    ]
    
    ids = []
    for i in range(min(count, len(certs))):
        nombre = certs[i]
        institucion_emisora = fake.company()
        fecha_cert = fake.date_between(start_date='-2y', end_date='today')
        
        cursor.execute("""
            INSERT INTO certificacion (descripcion, institucion, fecha_certificacion)
            VALUES (%s, %s, %s)
        """, (nombre, institucion_emisora, fecha_cert))
        ids.append(cursor.lastrowid)
    
    print(f"Created {len(ids)} certificaciones\n")
    return ids

def seed_aulas(cursor, count=15):
    """Generate aula records"""
    print(f"Creating {count} aulas...")
    
    edificios = ['A', 'B', 'C', 'D', 'E']
    ids = []
    
    for i in range(count):
        edificio = random.choice(edificios)
        numero = random.randint(101, 505)
        descripcion = f"Aula {edificio}-{numero}"
        lugar_fisico = f"Edificio {edificio}, Piso {numero // 100}"
        capacidad = random.choice([20, 25, 30, 35, 40, 50])
        
        cursor.execute("""
            INSERT INTO aula (descripcion_aula, lugar_fisico, capacidad)
            VALUES (%s, %s, %s)
        """, (descripcion, lugar_fisico, capacidad))
        ids.append(cursor.lastrowid)
    
    print(f"Created {len(ids)} aulas\n")
    return ids

def seed_horarios(cursor, count=20):
    """Generate horario records"""
    print(f"Creating {count} horarios...")
    
    dias = ['LUN', 'MAR', 'MIE', 'JUE', 'VIE', 'SAB']
    horas_inicio = ['07:00:00', '08:00:00', '09:00:00', '10:00:00', '11:00:00', 
                    '12:00:00', '13:00:00', '14:00:00', '15:00:00', '16:00:00',
                    '17:00:00', '18:00:00', '19:00:00']
    
    ids = []
    for i in range(count):
        dia_semana = random.choice(dias)
        hora_inicio = random.choice(horas_inicio)
        h, m, s = map(int, hora_inicio.split(':'))
        duracion = random.choice([1, 2, 3])  # hours
        hora_fin = f"{(h + duracion) % 24:02d}:{m:02d}:{s:02d}"
        descripcion = f"{dia_semana} {hora_inicio}-{hora_fin}"
        
        cursor.execute("""
            INSERT INTO horario (dia_semana, hora_inicio, hora_fin, descripcion_horario)
            VALUES (%s, %s, %s, %s)
        """, (dia_semana, hora_inicio, hora_fin, descripcion))
        ids.append(cursor.lastrowid)
    
    print(f"Created {len(ids)} horarios\n")
    return ids

def seed_periodos_inscripciones(cursor, count=5):
    """Generate periodo inscripciones records"""
    print(f"Creating {count} periodos de inscripciones...")
    
    ids = []
    start_year = 2022
    
    for i in range(count):
        year = start_year + (i // 2)
        periodo = "Ene-Jun" if i % 2 == 0 else "Ago-Dic"
        descripcion = f"{periodo} {year}"
        estatus = random.choice(['ABIERTO', 'ABIERTO', 'CERRADO'])
        costo_credito = Decimal(random.choice([500.00, 550.00, 600.00, 650.00]))
        
        if i % 2 == 0:  # Ene-Jun
            fecha_inicio = datetime(year, 1, 15).date()
            fecha_fin = datetime(year, 6, 30).date()
        else:  # Ago-Dic
            fecha_inicio = datetime(year, 8, 15).date()
            fecha_fin = datetime(year, 12, 20).date()
        
        cursor.execute("""
            INSERT INTO periodoinscripciones (descripcion_periodo, fecha_inicio_insc, fecha_fin_insc, estatus, costo_por_credito)
            VALUES (%s, %s, %s, %s, %s)
        """, (descripcion, fecha_inicio, fecha_fin, estatus, costo_credito))
        ids.append(cursor.lastrowid)
    
    print(f"Created {len(ids)} periodos de inscripciones\n")
    return ids

def seed_calendario_escolar(cursor, periodos, count=5):
    """Generate calendario escolar records"""
    print(f"Creating {count} calendarios escolares...")
    
    ids = []
    for i, idperiodo in enumerate(periodos[:count]):
        descripcion = f"Calendario Escolar {2022 + i}"
        
        # Get periodo dates to base calendar on
        cursor.execute("SELECT fecha_inicio_insc, fecha_fin_insc FROM periodoinscripciones WHERE idperiodoinscripciones = %s", (idperiodo,))
        result = cursor.fetchone()
        if result:
            fecha_inicio = result[0]
            fecha_fin = result[1]
            
            cursor.execute("""
                INSERT INTO calendarioescolar (descripcion, fecha_inicio, fecha_fin)
                VALUES (%s, %s, %s)
            """, (descripcion, fecha_inicio, fecha_fin))
            ids.append(cursor.lastrowid)
    
    print(f"Created {len(ids)} calendarios escolares\n")
    return ids

def seed_estudiantes(cursor, personas, carreras, planes, becas, count=30):
    """Generate estudiante records with estadodecuenta"""
    print(f"Creating {count} estudiantes...")
    
    # Use first 'count' personas for students
    estudiante_personas = personas[:count]
    ids = []
    
    for idpersona in estudiante_personas:
        # Create estadodecuenta first
        idcarrera = random.choice(carreras)
        
        # Get costo_inscripcion from carrera
        cursor.execute("SELECT costo_inscripcion FROM carrera WHERE idcarrera = %s", (idcarrera,))
        costo = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO estadodecuenta (saldo_inicial, saldo_actual, limite_credito)
            VALUES (%s, %s, NULL)
        """, (costo, costo))
        idestadodecuenta = cursor.lastrowid
        
        # Create estudiante (matricula_alumno is AUTO_INCREMENT)
        fecha_ingreso = fake.date_between(start_date='-4y', end_date='today')
        idplanestudio = random.choice([p for p in planes])  # Get matching plan
        idbeca = random.choice(becas + [None, None, None])  # 25% have scholarship
        estatus = random.choice(['ACTIVO', 'ACTIVO', 'ACTIVO', 'BAJA'])  # Mostly active
        
        cursor.execute("""
            INSERT INTO estudiante (idpersona, idcarrera, idplanestudio, idbeca, idestadodecuenta, fecha_ingreso, estatus)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (idpersona, idcarrera, idplanestudio, idbeca, idestadodecuenta, fecha_ingreso, estatus))
        ids.append(cursor.lastrowid)
    
    print(f"Created {len(ids)} estudiantes\n")
    return ids

def seed_docentes(cursor, personas, count=30):
    """Generate docente records"""
    print(f"Creating {count} docentes...")
    
    # Use next 'count' personas for teachers
    docente_personas = personas[30:30+count]
    ids = []
    
    for idpersona in docente_personas:
        fecha_alta = fake.date_between(start_date='-10y', end_date='-1y')
        fecha_baja = None if random.random() > 0.1 else fake.date_between(start_date=fecha_alta, end_date='today')
        estatus = 'B' if fecha_baja else 'A'
        
        cursor.execute("""
            INSERT INTO docente (idpersona, fecha_alta, fecha_baja, estatus)
            VALUES (%s, %s, %s, %s)
        """, (idpersona, fecha_alta, fecha_baja, estatus))
        ids.append(cursor.lastrowid)
    
    print(f"Created {len(ids)} docentes\n")
    return ids

def seed_clases_programadas(cursor, asignaturas, docentes, periodos, aulas, horarios, count=30):
    """Generate claseprogramada records"""
    print(f"Creating {count} clases programadas...")
    
    # Need to get calendario IDs first
    cursor.execute("SELECT idcalendarioescolar FROM calendarioescolar LIMIT 30")
    calendarios = [row[0] for row in cursor.fetchall()]
    if not calendarios:
        print("Warning: No calendarios found, skipping clases\n")
        return []
    
    ids = []
    for i in range(count):
        idasignatura = random.choice(asignaturas)
        iddocente = random.choice(docentes)
        idperiodo = random.choice(periodos)
        idaula = random.choice(aulas)
        idhorario = random.choice(horarios)
        idcalendario = random.choice(calendarios)
        modalidad = random.choice(['PRESENCIAL', 'PRESENCIAL', 'EN_LINEA', 'HIBRIDA'])
        idioma = random.choice(['ESP', 'ESP', 'ESP', 'ING'])  # Mostly Spanish
        
        try:
            cursor.execute("""
                INSERT INTO claseprogramada (idasignatura, modalidad, idhorario, iddocente, 
                                            idperiodoinscripciones, idcalendarioescolar, idaula, idioma)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (idasignatura, modalidad, idhorario, iddocente, idperiodo, idcalendario, idaula, idioma))
            ids.append(cursor.lastrowid)
        except Exception as e:
            print(f"  Warning: Error creating clase {i+1}: {e}")
    
    print(f"Created {len(ids)} clases programadas\n")
    return ids

def seed_inscripciones(cursor, estudiantes, clases, count=50):
    """Generate inscripcion records"""
    print(f"Creating {count} inscripciones...")
    
    ids = []
    for i in range(count):
        matricula = random.choice(estudiantes)  # estudiantes are already matricula_alumno IDs
        idclase = random.choice(clases)
        fecha_inscripcion = fake.date_between(start_date='-6m', end_date='today')
        motivo = random.choice([None, None, "Inscripción regular", "Cambio de grupo"])
        estatus = random.choice(['INICIADA', 'EN_PROCESO', 'EN_PROCESO', 'CONCLUIDA'])
        
        try:
            cursor.execute("""
                INSERT INTO inscripcion (matricula_alumno, idclaseprogramada, fecha_inscripcion, motivo_inscripcion, estatus)
                VALUES (%s, %s, %s, %s, %s)
            """, (matricula, idclase, fecha_inscripcion, motivo, estatus))
            ids.append(cursor.lastrowid)
        except Exception as e:
            # Skip duplicates or errors
            pass
    
    print(f"Created {len(ids)} inscripciones\n")
    return ids


def seed_docente_capacitaciones(cursor, docentes, capacitaciones):
    """Assign docentes to capacitaciones"""
    print(f"Assigning docentes to capacitaciones...")
    
    count = 0
    for  iddocente in docentes[:15]:  # First 15 docentes
        # Each docente has 1-3 capacitaciones
        num_caps = random.randint(1, 3)
        selected_caps = random.sample(capacitaciones, min(num_caps, len(capacitaciones)))
        
        for idcapacitacion in selected_caps:
            try:
                cursor.execute("""
                    INSERT INTO docente_capacitacion (iddocente, idcapacitacion)
                    VALUES (%s, %s)
                """, (iddocente, idcapacitacion))
                count += 1
            except:
                pass
    
    print(f"Created {count} docente-capacitacion assignments\n")

def seed_docente_certificaciones(cursor, docentes, certificaciones):
    """Assign docentes to certificaciones"""
    print(f"Assigning docentes to certificaciones...")
    
    count = 0
    for iddocente in docentes[:15]:  # First 15 docentes
        # Each docente has 1-2 certificaciones
        num_certs = random.randint(1, 2)
        selected_certs = random.sample(certificaciones, min(num_certs, len(certificaciones)))
        
        for idcertificacion in selected_certs:
            try:
                cursor.execute("""
                    INSERT INTO docente_certificacion (iddocente, idcertificacion)
                    VALUES (%s, %s)
                """, (iddocente, idcertificacion))
                count += 1
            except:
                pass
    
    print(f"Created {count} docente-certificacion assignments\n")

def seed_pagos(cursor, estudiantes, count=20):
    """Generate pago records for some students"""
    print(f"Creating {count} pagos...")
    
    formas_pago = ['EFECTIVO', 'TRANSFERENCIA', 'TARJETA', 'CHEQUE']
    tipos_movimiento = ['PAGO', 'PAGO', 'PAGO', 'DESCUENTO', 'BECA']  # Mostly payments
    
    ids = []
    for i in range(count):
        matricula = random.choice(estudiantes)  # estudiantes are matricula_alumno IDs
        
        # Get estadodecuenta for this student
        cursor.execute("""
            SELECT e.idestadodecuenta, ec.saldo_actual 
            FROM estudiante e 
            JOIN estadodecuenta ec ON e.idestadodecuenta = ec.idestadodecuenta 
            WHERE e.matricula_alumno = %s
        """, (matricula,))
        result = cursor.fetchone()
        if not result:
            continue
        idestadodecuenta, saldo_actual = result[0], result[1]
        
        fecha_pago = fake.date_between(start_date='-6m', end_date='today')
        hora_pago = fake.time()
        forma_pago = random.choice(formas_pago)
        tipo_movimiento = random.choice(tipos_movimiento)
        # Make sure importe doesn't exceed current balance
        max_importe = float(saldo_actual) if saldo_actual > 0 else 1000
        importe = Decimal(random.choice([500, 1000, 1500, 2000, 2500, min(3000, max_importe)]))
        referencia = f"REF-{fake.random_number(digits=10)}" if random.random() > 0.5 else None
        
        try:
            cursor.execute("""
                INSERT INTO pago (idestadodecuenta, fecha_pago, hora_pago, forma_pago, 
                                 tipo_movimiento, importe_pago, referencia)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (idestadodecuenta, fecha_pago, hora_pago, forma_pago, tipo_movimiento, importe, referencia))
        
            # Update balance
            cursor.execute("""
                UPDATE estadodecuenta 
                SET saldo_actual = GREATEST(0, saldo_actual - %s)
                WHERE idestadodecuenta = %s
            """, (importe, idestadodecuenta))
            
            ids.append(cursor.lastrowid)
        except Exception as e:
            # Skip errors
            pass
    
    print(f"Created {len(ids)} pagos\n")
    return ids

def seed_prerequisitos(cursor, asignaturas):
    """Generate prerequisite relationships between subjects"""
    print(f"Assigning prerequisites to asignaturas...")
    
    count = 0
    # Only assign prerequisites to some subjects (e.g., later semesters)
    for idasignatura in asignaturas[10:]: 
        if random.random() > 0.7:  # 30% chance of having a prerequisite
            # Pick a potential prerequisite from earlier subjects
            pos = asignaturas.index(idasignatura)
            potential_prereqs = asignaturas[:pos]
            if potential_prereqs:
                idprereq = random.choice(potential_prereqs)
                try:
                    cursor.execute("""
                        INSERT INTO prerequisito_asignatura (idasignatura, idasignatura_prereq)
                        VALUES (%s, %s)
                    """, (idasignatura, idprereq))
                    count += 1
                except:
                    pass
    
    print(f"Created {count} prerequisite relationships\n")

def seed_historial_academico(cursor, estudiantes, asignaturas, periodos):
    """Generate academic history for students"""
    print(f"Generating academic history...")
    
    count = 0
    for matricula in estudiantes:
        # Generate 2-5 past courses per student
        num_courses = random.randint(2, 5)
        selected_asigs = random.sample(asignaturas, min(num_courses, len(asignaturas)))
        
        for idasignatura in selected_asigs:
            idperiodo = random.choice(periodos)
            calificacion = Decimal(random.uniform(6.0, 10.0)).quantize(Decimal('0.01'))
            estatus = 'APROBADA' if calificacion >= 7.0 else 'REPROBADA'
            
            try:
                cursor.execute("""
                    INSERT INTO historialacademico (matricula_alumno, idasignatura, idperiodo, 
                                                   calificacion_final, estatus_asignatura)
                    VALUES (%s, %s, %s, %s, %s)
                """, (matricula, idasignatura, idperiodo, calificacion, estatus))
                count += 1
            except:
                pass
                
    print(f"Created {count} academic history records\n")

def seed_evaluaciones(cursor, clases):
    """Generate evaluations for classes"""
    print(f"Generating evaluations for classes...")
    
    evaluaciones = []
    tipos = ['TAREA', 'EXAMEN', 'PROYECTO', 'PARTICIPACION', 'OTRO']
    
    for idclase in clases:
        # Create 2-4 evaluations per class
        num_evals = random.randint(2, 4)
        
        for i in range(num_evals):
            tipo = random.choice(tipos)
            descripcion = f"{tipo.capitalize()} {i+1}"
            fecha = fake.date_between(start_date='-4m', end_date='today')
            porcentaje = Decimal(100 / num_evals).quantize(Decimal('0.01'))
            
            try:
                cursor.execute("""
                    INSERT INTO evaluacion (idclaseprogramada, tipo_actividad, descripcion, 
                                           fecha_aplicacion, porcentaje)
                    VALUES (%s, %s, %s, %s, %s)
                """, (idclase, tipo, descripcion, fecha, porcentaje))
                evaluaciones.append(cursor.lastrowid)
            except:
                pass
                
    print(f"Created {len(evaluaciones)} evaluations\n")
    return evaluaciones

def seed_calificaciones(cursor, inscripciones, evaluaciones):
    """Generate grades for student enrollments"""
    print(f"Generating student grades...")
    
    count = 0
    # Map evaluations to their class to know which students to grade
    cursor.execute("SELECT idevaluacion, idclaseprogramada FROM evaluacion")
    eval_map = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Map enrollments: class -> list of inscripcion_ids
    class_enrollments = {}
    cursor.execute("SELECT idinscripcion, idclaseprogramada FROM inscripcion")
    for row in cursor.fetchall():
        if row[1] not in class_enrollments:
            class_enrollments[row[1]] = []
        class_enrollments[row[1]].append(row[0])
        
    for idevaluacion in evaluaciones:
        if idevaluacion not in eval_map: continue
        
        idclase = eval_map[idevaluacion]
        if idclase in class_enrollments:
            for idinscripcion in class_enrollments[idclase]:
                calificacion = Decimal(random.uniform(5.0, 10.0)).quantize(Decimal('0.01'))
                observaciones = random.choice([None, None, "Buen trabajo", "Faltó detalle", "Excelente"])
                
                try:
                    cursor.execute("""
                        INSERT INTO calificacion_estudiante (idevaluacion, idinscripcion, calificacion, observaciones)
                        VALUES (%s, %s, %s, %s)
                    """, (idevaluacion, idinscripcion, calificacion, observaciones))
                    count += 1
                except:
                    pass

    print(f"Created {count} student grades\n")

def seed_asistencia(cursor, clases, inscripciones):
    """Generate attendance records"""
    print(f"Generating attendance records...")
    
    count = 0
    # Map enrollments: class -> list of (idinscripcion, matricula_alumno)
    class_students = {}
    cursor.execute("SELECT idclaseprogramada, matricula_alumno FROM inscripcion")
    for row in cursor.fetchall():
        if row[0] not in class_students:
            class_students[row[0]] = []
        class_students[row[0]].append(row[1])
        
    for idclase in clases:
        # Generate 5 sessions per class
        for _ in range(5):
            fecha = fake.date_between(start_date='-1m', end_date='today')
            
            # Student attendance
            if idclase in class_students:
                for matricula in class_students[idclase]:
                    estatus = random.choice(['ASISTIO', 'ASISTIO', 'ASISTIO', 'FALTO', 'JUSTIFICADO'])
                    try:
                        cursor.execute("""
                            INSERT INTO asistencia (idclaseprogramada, fecha, tipo, matricula_alumno, estatus)
                            VALUES (%s, %s, 'ESTUDIANTE', %s, %s)
                        """, (idclase, fecha, matricula, estatus))
                        count += 1
                    except:
                        pass
            
            # Teacher attendance (fetch teacher for class first)
            cursor.execute("SELECT iddocente FROM claseprogramada WHERE idclaseprogramada = %s", (idclase,))
            result = cursor.fetchone()
            if result:
                iddocente = result[0]
                estatus = random.choice(['ASISTIO', 'ASISTIO', 'ASISTIO', 'FALTO'])
                try:
                    cursor.execute("""
                        INSERT INTO asistencia (idclaseprogramada, fecha, tipo, iddocente, estatus)
                        VALUES (%s, %s, 'DOCENTE', %s, %s)
                    """, (idclase, fecha, iddocente, estatus))
                    count += 1
                except:
                    pass

    print(f"Created {count} attendance records\n")

def seed_usuarios(cursor):
    """Create admin user"""
    print(f"Creating admin user...")
    
    password = 'admin123'
    hashed_password = generate_password_hash(password)
    
    cursor.execute("""
        INSERT INTO usuarios (email, password, rol)
        VALUES ('admin@universidad.edu', %s, 'admin')
    """, (hashed_password,))
    
    print(f"Created admin user (email: admin@universidad.edu, password: {password})\n")

def main():
    """Main seeding function"""
    print("\n" + "="*60)
    print("🌱 DATABASE SEEDING SCRIPT")
    print("="*60 + "\n")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Clear existing data
        clear_database(cursor)
        
        # Seed base tables
        personas = seed_personas(cursor, 100)
        deptos_academicos = seed_departamentos_academicos(cursor, 5)
        deptos_asignatura = seed_departamentos_asignatura(cursor, 5)
        tipos_beca = seed_tipos_beca(cursor, 5)
        becas = seed_becas(cursor, tipos_beca, 10)
        
        # Seed first-level dependencies
        carreras = seed_carreras(cursor, deptos_academicos, 8)
        planes = seed_planes_estudio(cursor, carreras)
        asignaturas = seed_asignaturas(cursor, deptos_asignatura, 40)
        seed_plan_asignatura(cursor, planes, asignaturas)
        capacitaciones = seed_capacitaciones(cursor, 10)
        certificaciones = seed_certificaciones(cursor, 10)
        aulas = seed_aulas(cursor, 15)
        horarios = seed_horarios(cursor, 20)
        periodos = seed_periodos_inscripciones(cursor, 5)
        seed_calendario_escolar(cursor, periodos, 5)
        
        # Seed CRITICAL tables (30 records each)
        estudiantes = seed_estudiantes(cursor, personas, carreras, planes, becas, 30)
        docentes = seed_docentes(cursor, personas, 30)
        clases = seed_clases_programadas(cursor, asignaturas, docentes, periodos, aulas, horarios, 30)
        
        # Seed relationship tables
        inscripciones = seed_inscripciones(cursor, estudiantes, clases, 50)
        seed_docente_capacitaciones(cursor, docentes, capacitaciones)
        seed_docente_certificaciones(cursor, docentes, certificaciones)
        seed_pagos(cursor, estudiantes, 20)
        
        # Seed new modules
        seed_prerequisitos(cursor, asignaturas)
        seed_historial_academico(cursor, estudiantes, asignaturas, periodos)
        evaluaciones = seed_evaluaciones(cursor, clases)
        seed_calificaciones(cursor, inscripciones, evaluaciones)
        seed_asistencia(cursor, clases, inscripciones)
        
        seed_usuarios(cursor)
        
        # Commit all changes
        conn.commit()
        
        print("\n" + "="*60)
        print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("="*60 + "\n")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

