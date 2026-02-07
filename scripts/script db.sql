-- Tabla de Marcas 
CREATE TABLE tab_marca(
    id_marca INT IDENTITY(1,1) PRIMARY KEY, 
    nom_marca VARCHAR(100) NOT NULL UNIQUE 
);

-- Tabla tipos de equipos (Tablet, PC, Lector)
CREATE TABLE tab_tipos(
    id_tipoequi INT IDENTITY(1,1) PRIMARY KEY,
    nom_tipo varchar(100) NOT NULL UNIQUE
);

-- Tabla de Areas (Tecnología, Operaciones)
CREATE TABLE tab_area(
    id_area INT IDENTITY(1,1) PRIMARY KEY,
    nom_area VARCHAR(50) NOT NULL UNIQUE
);


-- Tabla de modelo dependiendo de la marca 
CREATE TABLE tab_modelo(
    id_modelo INT IDENTITY(1,1) PRIMARY KEY, 
    nom_modelo VARCHAR(100) NOT NULL,
    id_marca INT NOT NULL, 
    CONSTRAINT FK_Modelo_Marca FOREIGN KEY (id_marca) REFERENCES tab_marca(id_marca)
);

-- Tabla de empleados 
CREATE TABLE tab_empleados(
    cod_nom VARCHAR(6) NOT NULL PRIMARY KEY, 
    nom_emple VARCHAR(100) NOT NULL,
    id_area INT NOT NULL,
    activo BIT DEFAULT 1, 

    CONSTRAINT FK_Empleado_Area FOREIGN KEY (id_area) REFERENCES tab_area(id_area)
);


-- Tabla principal del dispositivo (Activo tecnologico)
CREATE TABLE tab_activotec(
    id_activo INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Datos de Identificación
    serial VARCHAR(100) UNIQUE, 
    codigo_qr VARCHAR(50) UNIQUE, 
    hostname varchar(100) UNIQUE,
    referencia VARCHAR(100), 
    mac_activo VARCHAR(17),
    
    -- Datos de Red
    ip_equipo VARCHAR(15), 
    
    -- Llaves Foráneas 
    id_tipoequi INT NOT NULL,
    id_marca INT NOT NULL,
    id_modelo INT NULL, 
    
    -- Estado y Responsable
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('Bueno', 'Malo', 'En Reparación', 'Baja')), 
    cod_nom_responsable VARCHAR(6) NULL, 
    id_padre_activo INT NULL, 

    CONSTRAINT FK_Activo_Tipo FOREIGN KEY (id_tipoequi) REFERENCES tab_tipos(id_tipoequi),
    CONSTRAINT FK_Activo_Marca FOREIGN KEY (id_marca) REFERENCES tab_marca(id_marca),
    CONSTRAINT FK_Activo_Modelo FOREIGN KEY (id_modelo) REFERENCES tab_modelo(id_modelo),
    CONSTRAINT FK_Activo_Empleado FOREIGN KEY (cod_nom_responsable) REFERENCES tab_empleados(cod_nom),
    
    -- La relación jerárquica 
    CONSTRAINT FK_Activo_Padre FOREIGN KEY (id_padre_activo) REFERENCES tab_activotec(id_activo)

);


-- Tabla de actualizaciones / Historial de eventos
CREATE TABLE tab_actualizaciones(
    id_evento INT IDENTITY(1,1) PRIMARY KEY,
    fecha datetime DEFAULT GETDATE(), 
    id_activo INT NOT NULL,
    tipo_evento VARCHAR(50) NOT NULL, 
    desc_evento TEXT NOT NULL,
    usuario_sistema VARCHAR(50), 

    CONSTRAINT FK_Historial_Activo FOREIGN KEY (id_activo) REFERENCES tab_activotec(id_activo) 
);

-- Tabla de usuarios 
CREATE TABLE tab_usuarios(
    id_usuario INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE, -- Falta el nombre de usuario
    contraseña VARCHAR(255) NOT NULL, -- Usa al menos 255 chars para hashes seguros
);