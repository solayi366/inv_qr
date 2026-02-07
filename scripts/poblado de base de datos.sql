-- Insertar Marcas
INSERT INTO tab_marca (nom_marca) VALUES ('SAMSUNG'), ('DELL'), ('SYMBOL'), ('GENIUS');

-- Insertar Tipos
INSERT INTO tab_tipos (nom_tipo) VALUES ('TABLET'), ('PORTATIL'), ('LECTOR'), ('MOUSE');

-- Insertar Areas
INSERT INTO tab_area (nom_area) VALUES ('TECNOLOGIA'), ('OPERACIONES');

-- Insertar Empleado (Víctor)
INSERT INTO tab_empleados (cod_nom, nom_emple, id_area, activo) 
VALUES ('123456', 'VICTOR', 2, 1); -- Asumiendo que 2 es Operaciones