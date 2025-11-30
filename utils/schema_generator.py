# utils/schema_generator.py

def generate_schema_from_table(cursor, table_name):
    cursor.execute(f"DESCRIBE {table_name}")
    columns = cursor.fetchall()

    schema = {}

    for col in columns:
        name = col["Field"]
        type_info = col["Type"]
        required = col["Null"] == "NO"

        # Ignorar columnas que no se deben validar
        if name in ("id", "idusuario", "created_at", "updated_at", "iddepartamentoacademico", "idpersona", "idusuario",
                     "iddeptoasignatura", "idcarrera", "idplanestudio", "idasignatura", "iddocente", "idcertificacion",
                       "idcapacitacion", "idtipo_beca", "idbeca", "idestadodecuenta", "matricula_alumno", "idhistorialacademico",
                         "idperiodoinscripciones", "idcalendarioescolar", "idaula", "idhorario", "idclaseprogramada", "idinscripcion",
                           "idasistencia", "idevaluacion", "idpago", "fecha_ingreso", "estatus", "vigencia_fin"):
            continue

        # VARCHAR
        if "varchar" in type_info:
            max_len = int(type_info.split("(")[1].split(")")[0])
            schema[name] = {"type": "string", "max": max_len, "required": required}

        # INT
        elif type_info.startswith("int"):
            schema[name] = {"type": "int", "required": required}

        # DECIMAL, FLOAT
        elif type_info.startswith(("decimal", "float", "double")):
            schema[name] = {"type": "float", "required": required}

        # DATE
        elif type_info.startswith("date"):
            schema[name] = {"type": "date", "required": required}

        # ENUM
        elif type_info.startswith("enum"):
            values = type_info.replace("enum(", "").replace(")", "")
            values = [v.strip("'") for v in values.split(",")]
            schema[name] = {"type": "enum", "values": values, "required": required}

        # DEFAULT fallback
        else:
            schema[name] = {"type": "string", "required": required}

    return schema
