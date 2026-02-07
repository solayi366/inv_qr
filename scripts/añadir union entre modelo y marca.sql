
-- 1. Asegurarnos de que la columna existe (si no, la crea)
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'tab_modelo') AND name = 'id_tipoequi')
BEGIN
    ALTER TABLE tab_modelo ADD id_tipoequi INT;
    ALTER TABLE tab_modelo ADD CONSTRAINT FK_Modelo_Tipo FOREIGN KEY (id_tipoequi) REFERENCES tab_tipos(id_tipoequi);
    PRINT 'Columna id_tipoequi agregada.';
END
GO

-- 2. ACTUALIZAR LOS DATOS (Quitar los NULLs)
-- Asigna el Tipo 'TABLET' (ID 1) a los modelos Samsung
UPDATE tab_modelo SET id_tipoequi = 3 WHERE nom_modelo LIKE '%SYMBOL%';

-- Asigna el Tipo 'PORTATIL' (ID 2) a los modelos Dell o HP
UPDATE tab_modelo SET id_tipoequi = 2 WHERE nom_modelo LIKE '%Latitude%' OR nom_modelo LIKE '%Vostro%';

-- Asigna el Tipo 'LECTOR' (ID 3) a los lectores
UPDATE tab_modelo SET id_tipoequi = 3 WHERE nom_modelo LIKE '%Symbol%' OR nom_modelo LIKE '%Honeywell%';

-- Verificamos cómo quedó
SELECT * FROM tab_modelo;
GO