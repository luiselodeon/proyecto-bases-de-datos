/* ===========================================================
   CONTROL ESCOLAR – MODELO INTEGRAL
   - Gestión de estudiantes y docentes
   - Cursos, planes y grupos
   - Calificaciones, asistencia
   - Finanzas y becas
   - Usuarios y roles
=========================================================== */

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

CREATE SCHEMA IF NOT EXISTS `controlescolar_db`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;
USE `controlescolar_db`;

/* ===========================================================
   1. PERSONAS, USUARIOS Y ROLES
=========================================================== */

CREATE TABLE IF NOT EXISTS persona (
  idpersona           INT AUTO_INCREMENT PRIMARY KEY,
  nombre              VARCHAR(60) NOT NULL,
  apellido_paterno    VARCHAR(60) NOT NULL,
  apellido_materno    VARCHAR(60) NULL DEFAULT NULL,
  genero              ENUM('F','M','O') NULL,
  rfc                 CHAR(13) NULL,
  curp                CHAR(18) NULL,
  dir_pais            VARCHAR(50) NULL,
  dir_estado          VARCHAR(50) NULL,
  dir_municipio       VARCHAR(50) NULL,
  dir_calle_num       VARCHAR(80) NULL,
  dir_codigo_postal   CHAR(5) NULL,
  telefono            VARCHAR(20) NULL,
  correo              VARCHAR(80) NOT NULL,
  UNIQUE KEY uq_persona_correo (correo)
) ENGINE=InnoDB;


-- Autenticacion (auth)
CREATE TABLE IF NOT EXISTS `controlescolar_db`.`usuarios` (
  `idusuario` INT(8) NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(100) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `rol` ENUM(
      'operacion_academica',
      'finanzas_becas',
      'admin'
  ) NOT NULL DEFAULT 'operacion_academica',
  PRIMARY KEY (`idusuario`),
  UNIQUE INDEX `unique_email_idx` (`email` ASC) VISIBLE
) ENGINE = InnoDB;


/* ===========================================================
   2. DEPARTAMENTOS, CARRERAS, PLANES, ASIGNATURAS
=========================================================== */

CREATE TABLE IF NOT EXISTS departamentoacademico (
  iddepartamentoacademico INT AUTO_INCREMENT PRIMARY KEY,
  nombre_departamento     VARCHAR(80) NOT NULL,
  CONSTRAINT uq_departamentoacademico_nombre UNIQUE (nombre_departamento)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS departamentoasignatura (
  iddeptoasignatura       INT AUTO_INCREMENT PRIMARY KEY,
  nombre_deptoasignatura  VARCHAR(100) NOT NULL,
  CONSTRAINT uq_deptoasignatura_nombre UNIQUE (nombre_deptoasignatura)
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS carrera (
  idcarrera               INT AUTO_INCREMENT PRIMARY KEY,
  descripcion_carrera     VARCHAR(80) NOT NULL,
  creditos_carrera        INT NOT NULL,
  iddepartamentoacademico INT NOT NULL,
  costo_inscripcion       DECIMAL(10,2) NOT NULL,
  CONSTRAINT fk_carrera_departamento
    FOREIGN KEY (iddepartamentoacademico) REFERENCES departamentoacademico(iddepartamentoacademico)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Plan de estudios por carrera
CREATE TABLE IF NOT EXISTS planestudio (
  idplanestudio       INT AUTO_INCREMENT PRIMARY KEY,
  nombre_plan         VARCHAR(80) NOT NULL,
  vigencia_inicio     DATE NOT NULL,
  vigencia_fin        DATE NULL,
  idcarrera           INT NOT NULL,
  CONSTRAINT fk_plan_carrera
    FOREIGN KEY (idcarrera) REFERENCES carrera(idcarrera)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS asignatura (
  idasignatura        INT AUTO_INCREMENT PRIMARY KEY,
  nombre_asignatura   VARCHAR(80) NOT NULL,
  creditos_asignatura INT(6) NOT NULL,
  horas_por_sesion    DECIMAL(4,2) NULL,
  clave_asignatura    VARCHAR(20) NOT NULL,
  iddeptoasignatura   INT NOT NULL,
  CONSTRAINT uq_asignatura_clave UNIQUE (clave_asignatura),
  CONSTRAINT fk_asignatura_depto
    FOREIGN KEY (iddeptoasignatura) REFERENCES departamentoasignatura(iddeptoasignatura)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Asignaturas por plan de estudio (semestres, obligatoria/optativa)
CREATE TABLE IF NOT EXISTS plan_asignatura (
  idplanestudio       INT NOT NULL,
  idasignatura        INT NOT NULL,
 semestre            ENUM('1','2','3','4','5','6','7','8','9','10','11','12') NOT NULL,
  tipo                ENUM('OBLIGATORIA','OPTATIVA') NOT NULL DEFAULT 'OBLIGATORIA',
  PRIMARY KEY (idplanestudio, idasignatura),
  CONSTRAINT fk_planasig_plan
    FOREIGN KEY (idplanestudio) REFERENCES planestudio(idplanestudio)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_planasig_asignatura
    FOREIGN KEY (idasignatura) REFERENCES asignatura(idasignatura)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Prerrequisitos entre asignaturas
CREATE TABLE IF NOT EXISTS prerequisito_asignatura (
  idasignatura             INT NOT NULL,
  idasignatura_prereq      INT NOT NULL,
  PRIMARY KEY (idasignatura, idasignatura_prereq),
  CONSTRAINT fk_prerreq_asig
    FOREIGN KEY (idasignatura)        REFERENCES asignatura(idasignatura)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_prerreq_asig_req
    FOREIGN KEY (idasignatura_prereq) REFERENCES asignatura(idasignatura)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

/* ===========================================================
   3. DOCENTES Y CAPACITACIONES / CERTIFICACIONES
=========================================================== */

CREATE TABLE IF NOT EXISTS docente (
  iddocente     INT AUTO_INCREMENT PRIMARY KEY,  
  idpersona     INT NOT NULL,
  fecha_alta    DATE NOT NULL,
  fecha_baja    DATE NULL,
  estatus       ENUM('A','B') NOT NULL DEFAULT 'A', -- Activo / Baja
  CONSTRAINT fk_docente_persona
    FOREIGN KEY (idpersona) REFERENCES persona(idpersona)
    ON DELETE RESTRICT ON UPDATE CASCADE
) 
AUTO_INCREMENT = 100000
ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS certificacion (
  idcertificacion     INT AUTO_INCREMENT PRIMARY KEY,
  descripcion         VARCHAR(100) NOT NULL,
  institucion         VARCHAR(80)  NULL,
  fecha_certificacion DATE NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS capacitacion (
  idcapacitacion  INT AUTO_INCREMENT PRIMARY KEY,
  descripcion     VARCHAR(100) NOT NULL,
  fecha_inicio    DATE NOT NULL,
  fecha_fin       DATE NULL,
  horas_capacitacion DECIMAL(4,2) NULL,
  institucion     VARCHAR(80) NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS docente_certificacion (
  iddocente       INT NOT NULL,
  idcertificacion INT NOT NULL,
  PRIMARY KEY (iddocente, idcertificacion),
  CONSTRAINT fk_docert_docente
    FOREIGN KEY (iddocente) REFERENCES docente(iddocente)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_docert_cert
    FOREIGN KEY (idcertificacion) REFERENCES certificacion(idcertificacion)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS docente_capacitacion (
  iddocente      INT NOT NULL,
  idcapacitacion INT NOT NULL,
  PRIMARY KEY (iddocente, idcapacitacion),
  CONSTRAINT fk_doccap_docente
    FOREIGN KEY (iddocente) REFERENCES docente(iddocente)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_doccap_cap
    FOREIGN KEY (idcapacitacion) REFERENCES capacitacion(idcapacitacion)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

/* ===========================================================
   4. ESTUDIANTES, GRUPOS, HISTORIAL
=========================================================== */

CREATE TABLE IF NOT EXISTS tipo_beca (
  idtipo_beca INT AUTO_INCREMENT PRIMARY KEY,
  nombre_tipo VARCHAR(60) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS beca (
  idbeca          INT AUTO_INCREMENT PRIMARY KEY,
  descripcion_beca VARCHAR(80) NOT NULL,
  porcentaje_beca TINYINT NOT NULL,
  estatus_beca    ENUM('A','I') NOT NULL DEFAULT 'A',
  idtipo_beca     INT NOT NULL,
  CONSTRAINT fk_beca_tipobeca
    FOREIGN KEY (idtipo_beca) REFERENCES tipo_beca(idtipo_beca)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_beca_porcentaje 
  CHECK (porcentaje_beca BETWEEN 0 AND 100)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS estadodecuenta (
  idestadodecuenta INT AUTO_INCREMENT PRIMARY KEY,
  saldo_inicial    DECIMAL(10,2) NOT NULL DEFAULT 0,
  saldo_actual     DECIMAL(10,2) NOT NULL DEFAULT 0,
  limite_credito   DECIMAL(10,2) NULL,
  CONSTRAINT chk_estadodecuenta_saldos
  CHECK (saldo_inicial >= 0 AND saldo_actual >= 0 
  AND (limite_credito IS NULL OR limite_credito >= 0)
  )
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS estudiante (
  matricula_alumno INT AUTO_INCREMENT PRIMARY KEY,
  idpersona        INT NOT NULL,
  idcarrera        INT NOT NULL,
  idplanestudio    INT NOT NULL,
  idbeca           INT NULL,
  idestadodecuenta INT NOT NULL,
  fecha_ingreso    DATE NOT NULL,
  estatus          ENUM('ACTIVO','BAJA','EGRESADO') NOT NULL DEFAULT 'ACTIVO',
  
  CONSTRAINT uq_estudiante_persona UNIQUE (idpersona),
  CONSTRAINT fk_estudiante_persona
    FOREIGN KEY (idpersona) REFERENCES persona(idpersona)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_estudiante_carrera
    FOREIGN KEY (idcarrera) REFERENCES carrera(idcarrera)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_estudiante_plan
    FOREIGN KEY (idplanestudio) REFERENCES planestudio(idplanestudio)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_estudiante_beca
    FOREIGN KEY (idbeca) REFERENCES beca(idbeca)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_estudiante_estadocuenta
    FOREIGN KEY (idestadodecuenta) REFERENCES estadodecuenta(idestadodecuenta)
    ON DELETE RESTRICT ON UPDATE CASCADE
)
AUTO_INCREMENT = 5000000
ENGINE=InnoDB;

/* Historial académico resumido por asignatura y periodo */
CREATE TABLE IF NOT EXISTS historialacademico (
  idhistorialacademico INT AUTO_INCREMENT PRIMARY KEY,
  matricula_alumno     INT NOT NULL,
  idasignatura         INT NOT NULL,
  idperiodo            INT NOT NULL,
  calificacion_final   DECIMAL(4,2) NULL,
  estatus_asignatura   ENUM('APROBADA','REPROBADA','CURSANDO') NOT NULL DEFAULT 'CURSANDO',
  CONSTRAINT fk_hist_estudiante
    FOREIGN KEY (matricula_alumno) REFERENCES estudiante(matricula_alumno)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_hist_asignatura
    FOREIGN KEY (idasignatura) REFERENCES asignatura(idasignatura)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_hist_periodo
    FOREIGN KEY (idperiodo) REFERENCES periodoinscripciones(idperiodoinscripciones)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;


/* ===========================================================
   5. PERIODOS, AULAS, HORARIOS, CLASES PROGRAMADAS
=========================================================== */

CREATE TABLE IF NOT EXISTS periodoinscripciones (
  idperiodoinscripciones INT AUTO_INCREMENT PRIMARY KEY,
  descripcion_periodo    VARCHAR(80) NOT NULL, -- Ej: 2025-1
  fecha_inicio_insc      DATE NOT NULL,
  fecha_fin_insc         DATE NOT NULL,
  estatus                ENUM('ABIERTO','CERRADO') NOT NULL DEFAULT 'ABIERTO',
  costo_por_credito      DECIMAL(10,2) NOT NULL,
  CONSTRAINT chk_periodoinsc_fechas
  CHECK (fecha_fin_insc >= fecha_inicio_insc)
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS calendarioescolar (
  idcalendarioescolar INT AUTO_INCREMENT PRIMARY KEY,
  descripcion         VARCHAR(80) NULL,
  fecha_inicio        DATE NOT NULL,
  fecha_fin           DATE NOT NULL,
  CONSTRAINT chk_calendario_fechas
  CHECK (fecha_fin >= fecha_inicio)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS aula (
  idaula           INT AUTO_INCREMENT PRIMARY KEY,
  descripcion_aula VARCHAR(60) NOT NULL,
  lugar_fisico     VARCHAR(60) NULL,
  capacidad        INT NOT NULL,
  CONSTRAINT chk_aula_capacidad
    CHECK (capacidad >= 1)
) ENGINE=InnoDB;

/* Horario simple: una fila por día y rango de hora */
CREATE TABLE IF NOT EXISTS horario (
  idhorario    INT AUTO_INCREMENT PRIMARY KEY,
  dia_semana   ENUM('LUN','MAR','MIE','JUE','VIE','SAB') NOT NULL,
  hora_inicio  TIME NOT NULL,
  hora_fin     TIME NOT NULL,
  descripcion_horario VARCHAR(80) NULL,
  CONSTRAINT chk_horario_horas
  CHECK (hora_fin > hora_inicio)
) ENGINE=InnoDB;

/* Clase programada = grupo / asignatura / docente / aula / horario / periodo */
CREATE TABLE IF NOT EXISTS claseprogramada (
  idclaseprogramada      INT AUTO_INCREMENT PRIMARY KEY,
  idasignatura           INT NOT NULL,
  modalidad              ENUM('PRESENCIAL','EN_LINEA','HIBRIDA','MULTISEDE') NOT NULL DEFAULT 'PRESENCIAL',
  idhorario              INT NOT NULL,
  iddocente              INT NOT NULL,
  idperiodoinscripciones INT NOT NULL,
  idcalendarioescolar    INT NOT NULL,
  idioma                 ENUM('ESP','ING','FRA') NOT NULL DEFAULT 'ESP',

  CONSTRAINT fk_clase_asignatura
    FOREIGN KEY (idasignatura) REFERENCES asignatura(idasignatura)
    ON DELETE RESTRICT ON UPDATE CASCADE,

  CONSTRAINT fk_clase_horario
    FOREIGN KEY (idhorario) REFERENCES horario(idhorario)
    ON DELETE RESTRICT ON UPDATE CASCADE,

  CONSTRAINT fk_clase_docente
    FOREIGN KEY (iddocente) REFERENCES docente(iddocente)
    ON DELETE RESTRICT ON UPDATE CASCADE,

  CONSTRAINT fk_clase_periodo
    FOREIGN KEY (idperiodoinscripciones) REFERENCES periodoinscripciones(idperiodoinscripciones)
    ON DELETE RESTRICT ON UPDATE CASCADE,

  CONSTRAINT fk_clase_calendario
    FOREIGN KEY (idcalendarioescolar) REFERENCES calendarioescolar(idcalendarioescolar)
    ON DELETE RESTRICT ON UPDATE CASCADE
)
AUTO_INCREMENT = 1000
ENGINE=InnoDB;

/* ===========================================================
   6. INSCRIPCIONES, ASISTENCIA
=========================================================== */

CREATE TABLE IF NOT EXISTS inscripcion (
  idinscripcion      INT AUTO_INCREMENT PRIMARY KEY,
  matricula_alumno   INT NOT NULL,
  idperiodoinscripciones INT NOT NULL,
  fecha_inscripcion  DATE NOT NULL,
  motivo_inscripcion VARCHAR(80) NULL,
  estatus            ENUM('INICIADA','EN_PROCESO','CONCLUIDA','CANCELADA') NOT NULL DEFAULT 'INICIADA',
  CONSTRAINT fk_inscripcion_estudiante
    FOREIGN KEY (matricula_alumno) REFERENCES estudiante(matricula_alumno)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_inscripcion_periodo
    FOREIGN KEY (idperiodoinscripciones) REFERENCES periodoinscripciones(idperiodoinscripciones)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Inscripción a carrera específica
CREATE TABLE IF NOT EXISTS inscripcion_carrera (
  idinscripcion INT NOT NULL,
  idcarrera     INT NOT NULL,
  costo_inscripcion DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (idinscripcion, idcarrera),
  CONSTRAINT fk_inscarrera_inscripcion
    FOREIGN KEY (idinscripcion) REFERENCES inscripcion(idinscripcion)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_inscarrera_carrera
    FOREIGN KEY (idcarrera) REFERENCES carrera(idcarrera)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_inscarrera_costo
    CHECK (costo_inscripcion >= 0)
) ENGINE=InnoDB;

-- Inscripción de estudiante a una clase programada
CREATE TABLE IF NOT EXISTS inscripcion_claseprogramada (
  idinscripcion      INT NOT NULL,
  idclaseprogramada  INT NOT NULL,
  PRIMARY KEY (idinscripcion, idclaseprogramada),
  CONSTRAINT fk_inscclase_inscripcion
    FOREIGN KEY (idinscripcion) REFERENCES inscripcion(idinscripcion)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_inscclase_clase
    FOREIGN KEY (idclaseprogramada) REFERENCES claseprogramada(idclaseprogramada)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

/* Asistencia de estudiantes y docentes */
CREATE TABLE IF NOT EXISTS asistencia (
  idasistencia      INT AUTO_INCREMENT PRIMARY KEY,
  idclaseprogramada INT NOT NULL,
  fecha             DATE NOT NULL,
  tipo              ENUM('ESTUDIANTE','DOCENTE') NOT NULL,
  matricula_alumno  INT NULL,
  iddocente         INT NULL,
  estatus           ENUM('ASISTIO','FALTO','JUSTIFICADO') NOT NULL,
  observaciones     VARCHAR(200) NULL,
  CONSTRAINT fk_asistencia_clase
    FOREIGN KEY (idclaseprogramada) REFERENCES claseprogramada(idclaseprogramada)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_asistencia_estudiante
    FOREIGN KEY (matricula_alumno) REFERENCES estudiante(matricula_alumno)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_asistencia_docente
    FOREIGN KEY (iddocente) REFERENCES docente(iddocente)
    ON DELETE CASCADE ON UPDATE CASCADE

) 

ENGINE=InnoDB;

/* ===========================================================
   7. EVALUACIONES Y CALIFICACIONES
=========================================================== */

-- Actividades (tareas, exámenes, etc.) por clase
CREATE TABLE IF NOT EXISTS evaluacion (
  idevaluacion       INT AUTO_INCREMENT PRIMARY KEY,
  idclaseprogramada  INT NOT NULL,
  tipo_actividad     ENUM('TAREA','EXAMEN','PROYECTO','PARTICIPACION','OTRO') NOT NULL,
  descripcion        VARCHAR(100) NULL,
  fecha_aplicacion   DATE NULL,
  porcentaje         DECIMAL(5,2) NULL,  -- % de la calificación final
  CONSTRAINT fk_eval_clase
    FOREIGN KEY (idclaseprogramada) REFERENCES claseprogramada(idclaseprogramada)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT chk_evaluacion_porcentaje
    CHECK ( porcentaje IS NULL OR (porcentaje >= 0 AND porcentaje <= 100))
) ENGINE=InnoDB;

-- Calificaciones de estudiantes por actividad
CREATE TABLE IF NOT EXISTS calificacion_estudiante (
  idevaluacion      INT NOT NULL,
  idinscripcion     INT NOT NULL,
  calificacion      DECIMAL(4,2) NULL,
  observaciones     VARCHAR(200) NULL,
  PRIMARY KEY (idevaluacion, idinscripcion),
  CONSTRAINT fk_calif_eval
    FOREIGN KEY (idevaluacion) REFERENCES evaluacion(idevaluacion)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_calif_inscripcion
    FOREIGN KEY (idinscripcion) REFERENCES inscripcion(idinscripcion)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT chk_calificacion_rango
    CHECK (calificacion IS NULL OR (calificacion >= 0 AND calificacion <= 10))
) ENGINE=InnoDB;

/* ===========================================================
   8. FINANZAS, PAGOS Y BECAS (ya ligadas arriba)
=========================================================== */

CREATE TABLE IF NOT EXISTS pago (
  idpago            INT AUTO_INCREMENT PRIMARY KEY,
  idestadodecuenta  INT NOT NULL,
  idinscripcion     INT NOT NULL,
  fecha_pago        DATE NOT NULL,
  hora_pago         TIME NULL,
  forma_pago        ENUM('EFECTIVO','TRANSFERENCIA','TARJETA','CHEQUE') NOT NULL,
  tipo_movimiento   ENUM('PAGO','DESCUENTO','BECA','AJUSTE') NOT NULL DEFAULT 'PAGO',
  importe_pago      DECIMAL(10,2) NOT NULL,
  referencia        VARCHAR(80) NULL,
  CONSTRAINT fk_pago_estadocuenta
    FOREIGN KEY (idestadodecuenta) REFERENCES estadodecuenta(idestadodecuenta)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_pago_inscripcion
    FOREIGN KEY (idinscripcion) REFERENCES inscripcion(idinscripcion)
    ON DELETE RESTRICT ON UPDATE CASCADE,
CONSTRAINT chk_pago_importe CHECK (importe_pago > 0)
) ENGINE=InnoDB;

/* ===========================================================
   RESTAURAR MODOS
=========================================================== */

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

