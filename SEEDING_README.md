# Database Seeding Script

## Descripción

Script de Python para poblar la base de datos con datos de prueba realistas al iniciar los contenedores de Docker.

## Características

- **Datos Realistas**: Usa Faker con localización mexicana
- **100 Personas** base para reutilizar
- **Mínimo 5 registros** por tabla
- **30 registros** para tablas críticas:
  - Estudiantes
  - Docentes  
  - Clases Programadas
- Respeta todas las dependencias de foreign keys
- Genera datos relacionales consistentes

## Requisitos

```bash
pip install mysql-connector-python Faker
```

## Uso

### Ejecución Manual

```bash
# Configurar variables de entorno
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=rootpassword
export DB_NAME=universidad_db

# Ejecutar el script
python3 seed_data.py
```

### Ejecución con Docker

El script detecta automáticamente las variables de entorno de Docker.

```bash
docker exec -it proyecto_bases_web python /app/seed_data.py
```

## Datos Generados

| Tabla | Cantidad |
|-------|----------|
| Personas | 100 |
| Estudiantes | 30 |
| Docentes | 30 |
| Clases Programadas | 30 |
| Asignaturas | 40 |
| Carreras | 8 |
| Becas | 10 |
| Aulas | 15 |
| Horarios | 20 |
| Periodos | 5 |
| Inscripciones | 50 |
| Pagos | 20 |
| Demás tablas | 5+ |

## Usuario Admin Generado

```
Email: admin@universidad.edu
Password: admin123
Rol: admin
```

## Estructura del Script

1. `clear_database()` - Limpia datos existentes
2. Tablas base (personas, departamentos, tipos)
3. Dependencias de primer nivel (carreras, planes, asignaturas)
4. Tablas críticas (estudiantes, docentes, clases)
5. Tablas de relaciones (inscripciones, asignaciones)
6. Commit de transacción

## Notas

- El script usa transacciones - si falla, hace rollback
- Las matrículas se generan aleatoriamente
- Los saldos de estudiantes se inicializan con el costo de inscripción
- Los pagos se restan de los saldos automáticamente
