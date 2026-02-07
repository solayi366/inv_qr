import pandas as pd
import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy.exc import DataError, IntegrityError, ProgrammingError

# --- CONFIGURACIÓN DE COLUMNAS (ARCHIVO COMPLETO) ---
ARCHIVO_DATOS = "datos.txt"

# 1. Datos Generales
COL_AREA = "Nom_Ubicacion"
COL_RESPONSABLE = "Usuario"

# 2. Grupos de Hardware a procesar
GRUPOS = [
    { "nombre": "COMPUTO", "col_tipo": "Nom_TipoEquipo", "col_marca": "Marca_CPU", "col_modelo": "Ref_CPU" },
    { "nombre": "MONITOR", "tipo_fijo": "MONITOR", "col_marca": "Marca_Monitor", "col_modelo": "Ref_Monitor" },
    { "nombre": "IMPRESORA", "tipo_fijo": "IMPRESORA", "col_marca": "Marca_Impresora", "col_modelo": "Ref_Impresora" },
    { "nombre": "LECTOR USB", "tipo_fijo": "LECTOR", "col_marca": "Marca_LectorUSB", "col_modelo": "Ref_LectorUSB" },
    { "nombre": "LECTOR INALAMBRICO", "tipo_fijo": "LECTOR", "col_marca": "Marca_LectorIn", "col_modelo": "Ref_LectorIn" },
    { "nombre": "ESCANER", "tipo_fijo": "ESCANER", "col_marca": "Marca_Escaner", "col_modelo": "Ref_Escaner" },
    { "nombre": "TELEFONO", "tipo_fijo": "TELEFONO", "col_marca": "Marca_Tel", "col_modelo": "Ref_Tel" },
    { "nombre": "UPS", "tipo_fijo": "UPS", "col_marca": "Marca_UPS", "col_modelo": "Ref_UPS" }
]

# ---------------------------------------------------------------
sys.path.append(os.getcwd())
try:
    from app import models, database
except ImportError:
    sys.exit("❌ Error: Ejecuta desde la raíz del proyecto.")

def limpiar(texto):
    if pd.isna(texto) or str(texto).strip() in ["", "nan", "N.A", "n.a", "0"]:
        return None
    return str(texto).strip().upper()

def es_persona(texto):
    if not texto: return False
    texto = str(texto).strip()
    if any(char.isdigit() for char in texto): return False
    return True

def get_or_create(db, model, **kwargs):
    """
    Intenta obtener o crear un registro.
    Si falla (por texto muy largo u otro error), OMITE el registro y sigue vivo.
    """
    # 1. Primero intentamos buscar (lectura segura)
    try:
        instance = db.query(model).filter_by(**kwargs).first()
        if instance: return instance
    except Exception:
        db.rollback() # Por si acaso

    # 2. Si no existe, intentamos crear (escritura riesgosa)
    try:
        instance = model(**kwargs)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance
    except (DataError, IntegrityError, ProgrammingError, Exception) as e:
        db.rollback() # IMPORTANTE: Limpiar la sesión para que el siguiente no falle
        valor = list(kwargs.values())[0]
        print(f"   ⚠️ OMITIDO (Error DB): {valor} -> Posiblemente muy largo.")
        return None

def procesar_completo():
    if not os.path.exists(ARCHIVO_DATOS):
        print(f"❌ Falta el archivo '{ARCHIVO_DATOS}'"); return

    print("🔄 Leyendo TODOS los parámetros del archivo...")
    try:
        df = pd.read_csv(ARCHIVO_DATOS, sep='\t')
        if "Marca_CPU" not in df.columns: df = pd.read_csv(ARCHIVO_DATOS)
    except:
        print("❌ Error leyendo archivo."); return

    db = database.SessionLocal()
    cache = {"area": {}, "tipo": {}, "marca": {}}
    stats = {"marcas": 0, "modelos": 0, "tipos": 0}

    try:
        for index, row in df.iterrows():
            
            # --- 1. ÁREA y EMPLEADO ---
            area = limpiar(row.get(COL_AREA))
            if area and area not in cache["area"]:
                # Intentamos crear
                obj = get_or_create(db, models.Area, nom_area=area)
                if obj: # Solo si se creó exitosamente guardamos en caché
                    cache["area"][area] = obj.id_area

            resp = row.get(COL_RESPONSABLE)
            nombre = limpiar(resp)
            # Solo procesamos empleado si el área existe (o se pudo crear)
            if nombre and es_persona(resp) and area in cache["area"]:
                cedula_fake = ("E" + nombre.replace(" ", ""))[:6]
                if not db.query(models.Empleado).filter_by(nom_emple=nombre).first():
                    # Aquí también usamos try interno por si el nombre es muy largo
                    try:
                        nuevo = models.Empleado(cod_nom=cedula_fake, nom_emple=nombre, id_area=cache["area"][area], activo=True)
                        db.add(nuevo); db.commit()
                    except:
                        db.rollback()
                        print(f"   ⚠️ Empleado omitido: {nombre}")

            # --- 2. BARRIDO DE EQUIPOS ---
            for grupo in GRUPOS:
                if "col_tipo" in grupo:
                    nom_tipo = limpiar(row.get(grupo["col_tipo"]))
                else:
                    nom_tipo = grupo["tipo_fijo"]

                nom_marca = limpiar(row.get(grupo["col_marca"]))
                nom_modelo = str(row.get(grupo["col_modelo"])).strip()
                if nom_modelo in ["nan", "N.A", "0", ""]: nom_modelo = None

                if nom_tipo and nom_marca:
                    # TIPO
                    if nom_tipo not in cache["tipo"]:
                        obj = get_or_create(db, models.TipoEquipo, nom_tipo=nom_tipo)
                        if obj:
                            cache["tipo"][nom_tipo] = obj.id_tipoequi
                            stats["tipos"] += 1
                    
                    # MARCA
                    if nom_marca not in cache["marca"]:
                        obj = get_or_create(db, models.Marca, nom_marca=nom_marca)
                        if obj:
                            cache["marca"][nom_marca] = obj.id_marca
                            stats["marcas"] += 1

                    # MODELO (Solo si tenemos Marca y Tipo válidos)
                    if nom_modelo and nom_marca in cache["marca"] and nom_tipo in cache["tipo"]:
                        id_marca = cache["marca"][nom_marca]
                        id_tipo = cache["tipo"][nom_tipo]
                        
                        # Verificamos existencia
                        existe = db.query(models.Modelo).filter_by(nom_modelo=nom_modelo).first()
                        if not existe:
                            try:
                                nuevo_mod = models.Modelo(nom_modelo=nom_modelo, id_marca=id_marca, id_tipoequi=id_tipo)
                                db.add(nuevo_mod); db.commit()
                                stats["modelos"] += 1
                            except:
                                db.rollback()
                                print(f"   ⚠️ Modelo omitido: {nom_modelo}")

        print("\n✅ ¡PROCESO TERMINADO!")
        print(f"   - Tipos nuevos: {stats['tipos']}")
        print(f"   - Marcas nuevas: {stats['marcas']}")
        print(f"   - Modelos nuevos: {stats['modelos']}")

    except Exception as e:
        print(f"❌ Error general inesperado: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    procesar_completo()
