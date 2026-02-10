import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# --- CONFIGURACIÓN DE CONEXIÓN ---
SERVER = os.getenv("DB_SERVER", "invqr.chii2mgga6uz.us-east-2.rds.amazonaws.com")
DATABASE = os.getenv("DB_NAME", "invqr")
USER = os.getenv("DB_USER", "admin")
PASSWORD = os.getenv("DB_PASSWORD", "3nviaBuca")

DATABASE_URL = f"mssql+pyodbc://{USER}:{PASSWORD}@{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server"

def limpiar_activos():
    print("🧹 INICIANDO BORRADO DE ACTIVOS...")
    
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 1. Quitar seguros (Constraints) para evitar errores
        session.execute(text("EXEC sp_msforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT all'"))
        
        # 2. Borrar Activos y sus dependencias (Novedades y Actualizaciones)
        # Es necesario borrar las novedades porque apuntan a los activos viejos.
        tablas = ["tab_novedades", "tab_actualizaciones", "tab_activotec"]
        
        for tabla in tablas:
            try:
                session.execute(text(f"DELETE FROM {tabla}"))
                session.execute(text(f"DBCC CHECKIDENT ('{tabla}', RESEED, 0)")) # Reiniciar ID a 0
                print(f"   ✅ {tabla} vaciada y reiniciada.")
            except Exception as e:
                print(f"   ⚠️ {tabla}: {e}")

        session.commit()
        
        # 3. Poner seguros de nuevo
        session.execute(text("EXEC sp_msforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT all'"))
        
        print("\n🚀 ¡LISTO! La tabla tab_activotec está vacía (ID 0).")
        print("   Ya puedes ejecutar 'python cargar_todo.py' para llenar los nuevos datos.")

    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    limpiar_activos()
