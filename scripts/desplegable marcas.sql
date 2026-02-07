DECLARE @IdMarcaSamsung INT;
DECLARE @IdTipoTablet INT;

-- 1. BUSCAMOS LOS IDs CORRECTOS (Para no adivinar si es el 1, el 2 o el 5)
-- Asegúrate de que en tu base de datos la marca se llame 'SAMSUNG' y el tipo 'TABLET'
SELECT @IdMarcaSamsung = id_marca FROM tab_marca WHERE nom_marca = 'SAMSUNG';
SELECT @IdTipoTablet = id_tipoequi FROM tab_tipos WHERE nom_tipo = 'TABLET';

-- Verificamos si encontramos los IDs
IF @IdMarcaSamsung IS NULL
BEGIN
    PRINT '❌ ERROR: No encontré la marca SAMSUNG. ¿Está escrita diferente en tu tabla tab_marca?';
END
ELSE IF @IdTipoTablet IS NULL
BEGIN
    PRINT '❌ ERROR: No encontré el tipo TABLET. ¿Está escrito diferente en tu tabla tab_tipos?';
END
ELSE
BEGIN
    -- 2. INSERTAMOS LOS MODELOS (Si no existen ya)
    
    -- Galaxy Tab A7 Lite
    IF NOT EXISTS (SELECT 1 FROM tab_modelo WHERE nom_modelo = 'Galaxy Tab A7 Lite')
    BEGIN
        INSERT INTO tab_modelo (nom_modelo, id_marca, id_tipoequi) 
        VALUES ('Galaxy Tab A7 Lite', @IdMarcaSamsung, @IdTipoTablet);
    END

    -- Galaxy Tab A8
    IF NOT EXISTS (SELECT 1 FROM tab_modelo WHERE nom_modelo = 'Galaxy Tab A8')
    BEGIN
        INSERT INTO tab_modelo (nom_modelo, id_marca, id_tipoequi) 
        VALUES ('Galaxy Tab A8', @IdMarcaSamsung, @IdTipoTablet);
    END

    -- Galaxy Tab A9
    IF NOT EXISTS (SELECT 1 FROM tab_modelo WHERE nom_modelo = 'Galaxy Tab A9')
    BEGIN
        INSERT INTO tab_modelo (nom_modelo, id_marca, id_tipoequi) 
        VALUES ('Galaxy Tab A9', @IdMarcaSamsung, @IdTipoTablet);
    END

    -- Galaxy Tab A11
    IF NOT EXISTS (SELECT 1 FROM tab_modelo WHERE nom_modelo = 'Galaxy Tab A11')
    BEGIN
        INSERT INTO tab_modelo (nom_modelo, id_marca, id_tipoequi) 
        VALUES ('Galaxy Tab A11', @IdMarcaSamsung, @IdTipoTablet);
    END

    PRINT '✅ ¡Modelos de Tablets Samsung insertados correctamente!';
    
    -- Mostramos cómo quedó la tabla
    SELECT T.nom_tipo, M.nom_marca, Mod.nom_modelo 
    FROM tab_modelo Mod
    JOIN tab_marca M ON Mod.id_marca = M.id_marca
    JOIN tab_tipos T ON Mod.id_tipoequi = T.id_tipoequi
    WHERE T.nom_tipo = 'TABLET';
END
GO