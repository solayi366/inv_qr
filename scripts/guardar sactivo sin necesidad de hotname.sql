-- 1. Buscamos el nombre exacto de la restricción del Hostname para borrarla
DECLARE @ConstraintName nvarchar(200)
SELECT @ConstraintName = Name FROM sys.key_constraints
WHERE type = 'UQ' AND parent_object_id = OBJECT_ID('tab_activotec') 
AND unique_index_id IN (SELECT index_id FROM sys.index_columns WHERE object_id = OBJECT_ID('tab_activotec') AND column_id = (SELECT column_id FROM sys.columns WHERE name = 'hostname' AND object_id = OBJECT_ID('tab_activotec')))

-- 2. Borramos la restricción vieja (que no deja meter NULLs)
IF @ConstraintName IS NOT NULL
BEGIN
    EXEC('ALTER TABLE tab_activotec DROP CONSTRAINT ' + @ConstraintName)
    PRINT 'Restricción de Hostname eliminada correctamente.'
END
GO

-- 3. (Opcional) Si quieres que sea único PERO permita muchos nulos, se usa un índice filtrado.
-- Por ahora, para no complicarte, simplemente lo dejamos sin restricción UNIQUE o lo creamos filtrado:
CREATE UNIQUE INDEX IX_Hostname_Unique_NotNull 
ON tab_activotec(hostname) 
WHERE hostname IS NOT NULL;
PRINT 'Nuevo índice inteligente creado: Permite muchos vacíos, pero no hostnames repetidos.'
GO