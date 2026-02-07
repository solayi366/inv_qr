import sys
import os
from sqlalchemy import text

# Aseguramos que Python encuentre la carpeta 'app'
sys.path.append(os.getcwd())

from app.database import SessionLocal, engine

def reset_fabrica_inteligente():
    db = SessionLocal()
    try:
        print("⏳ Iniciando Protocolo de Limpieza Profunda (V2)...")
        
        # 1. Desactivar TODAS las restricciones (Foreign Keys)
        # Esto es vital para poder borrar sin que SQL Server se queje del orden
        db.execute(text("EXEC sp_msforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT all'"))
        
        # 2. Lista de tablas a reiniciar
        tablas_a_vaciar = [
            "tab_actualizaciones",
            "tab_activotec",      
            "tab_modelo",
            "tab_marca",
            "tab_tipos",
            "tab_area",
            "tab_empleados"
        ]

        for tabla in tablas_a_vaciar:
            print(f"🧹 Borrando datos de: {tabla}")
            # Usamos DELETE en lugar de TRUNCATE para evitar el bloqueo de FK
            db.execute(text(f"DELETE FROM {tabla}"))
            
            print(f"🔄 Reiniciando contador ID a 1 para: {tabla}")
            # Este comando mágico reinicia el "Identity" a 0 (el próximo será 1)
            try:
                db.execute(text(f"DBCC CHECKIDENT ('{tabla}', RESEED, 0)"))
            except Exception:
                # Si la tabla está vacía y nunca tuvo datos, esto podría advertir, pero no importa
                pass

        # 3. Manejo especial de USUARIOS (Para no borrar al Admin)
        print("🛡️  Limpiando usuarios (Protegiendo al Admin)...")
        db.execute(text("DELETE FROM tab_usuarios WHERE username != 'admin'"))
        
        # 4. Reactivar las restricciones de seguridad
        db.execute(text("EXEC sp_msforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT all'"))
        
        db.commit()
        print("\n✅ ¡ÉXITO TOTAL! Base de datos reiniciada.")
        print("   - Se usó DELETE + RESEED para saltar la protección de FK.")
        print("   - El próximo Activo será obligatoriamente el ID: 1")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_fabrica_inteligente()
