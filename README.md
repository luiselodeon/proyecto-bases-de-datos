# Sistema de Gestión Universitaria - Documentación Técnica

Este repositorio contiene el código fuente de una aplicación web integral para la gestión de una universidad. El sistema permite administrar estudiantes, docentes, cursos, inscripciones, calificaciones, finanzas y más, a través de una interfaz web intuitiva.

## 🛠️ Stack Tecnológico

El proyecto está construido utilizando las siguientes tecnologías:

*   **Lenguaje de Programación:** [Python 3.9](https://www.python.org/)
*   **Framework Web:** [Flask](https://flask.palletsprojects.com/) - Microframework ligero y flexible.
*   **Base de Datos:** [MySQL 8.0](https://www.mysql.com/) - Sistema de gestión de bases de datos relacional.
*   **Conector de Base de Datos:** `mysql-connector-python` - Driver oficial de MySQL para Python.
*   **Frontend:** HTML5, CSS3, Bootstrap 5 (para estilos y componentes responsivos).
*   **Contenerización:** [Docker](https://www.docker.com/) y Docker Compose.

## 📂 Estructura del Proyecto

El proyecto sigue una estructura modular para facilitar el mantenimiento y la escalabilidad. A continuación se describen los componentes principales:

### 1. `app.py`
Es el punto de entrada principal de la aplicación.
*   Inicializa la aplicación Flask.
*   Configura la conexión a la base de datos.
*   Define todas las rutas (endpoints) del sistema.
*   Gestiona la lógica de las vistas y renderiza las plantillas HTML.
*   Maneja el manejo de errores global y las notificaciones (flash messages).

### 2. `utils/`
Este directorio contiene la lógica de negocio y las operaciones CRUD (Create, Read, Update, Delete) separadas por módulos funcionales. Esto mantiene `app.py` limpio y organizado.

*   **`estudiantes/`**: Gestión de alumnos, inscripciones, historial académico.
*   **`docentes/`**: Gestión de profesores, capacitaciones, certificaciones.
*   **`cursos/`**: Gestión de asignaturas, planes de estudio, horarios, prerequisitos.
*   **`aulas_horarios/`**: Administración de espacios físicos y tiempos.
*   **`finanzas_becas/`**: Control de pagos, becas y estados de cuenta.
*   **`calificaciones/`**: Registro y consulta de evaluaciones.
*   **`asistencia/`**: Control de asistencia de alumnos y docentes.
*   **`auth.py`**: Funciones auxiliares para autenticación y seguridad.
*   **`db.py`**: Utilidades de conexión a base de datos.

### 3. `templates/`
Contiene los archivos HTML (plantillas Jinja2) que conforman la interfaz de usuario. La estructura de carpetas refleja la de `utils/` para una fácil navegación.

*   **`base.html`**: Plantilla maestra que define la estructura común (header, footer, navegación) que heredan las demás páginas.
*   **`estudiantes/`, `docentes/`, `cursos/`, etc.**: Subcarpetas con formularios y listas para cada módulo.

### 4. `seed_data.py`
Script de "sembrado" de datos (seeding).
*   Utiliza la librería `Faker` para generar datos de prueba realistas y masivos.
*   Puebla la base de datos con estudiantes, profesores, cursos, inscripciones, pagos, etc.
*   **Nota:** Configurado para generar fechas estrictamente entre **2015 y 2035** y evitar duplicidad en correos y periodos.

## 🐳 Dockerización

El proyecto está completamente contenerizado para garantizar un entorno de desarrollo consistente y fácil despliegue.

### `Dockerfile`
Define la imagen de Docker para la aplicación web.
*   Basa la imagen en `python:3.9-slim`.
*   Instala las dependencias del sistema necesarias (como el cliente MySQL).
*   Copia los archivos del proyecto al contenedor.
*   Instala las librerías de Python listadas en `requirements.txt`.
*   Expone el puerto 5000.

### `docker-compose.yml`
Orquesta los servicios necesarios para levantar la aplicación completa.
*   **`web`**: El servicio de la aplicación Flask (construido desde el `Dockerfile`).
*   **`db`**: El servicio de base de datos MySQL 8.0.
*   Configura las redes, volúmenes (para persistencia de datos) y variables de entorno.

### `docker-entrypoint.sh`
Script de entrada que se ejecuta al iniciar el contenedor `web`.
*   Espera a que la base de datos MySQL esté lista antes de iniciar la aplicación (evita errores de conexión al inicio).
*   Ejecuta el script `seed_data.py` si la base de datos está vacía o si se indica explícitamente.
*   Inicia el servidor de desarrollo de Flask.

## 🚀 Cómo Iniciar

Para ejecutar el proyecto localmente, asegúrate de tener Docker y Docker Compose instalados.

1.  **Clonar el repositorio:**
    ```bash
    git clone <url-del-repositorio>
    cd proyecto-bases-de-datos
    ```

2.  **Construir y levantar los contenedores:**
    ```bash
    docker compose up --build
    ```

3.  **Acceder a la aplicación:**
    Abre tu navegador y visita: `http://localhost:5000`

La primera vez que se ejecute, el sistema tardará unos minutos en generar los datos de prueba (seeding). Verás el progreso en la terminal.
