import qrcode
import os
from passlib.context import CryptContext
from datetime import datetime
from . import models
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generar_codigo_qr(nombre, url):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    os.makedirs("static/qrcodes", exist_ok=True)
    img.save(f"static/qrcodes/{nombre}.png")

def limpiar_serial(valor):
    if not valor: return None
    s = str(valor).strip().upper()
    BLACKLIST = ["N.A", "NA", "NONE", "SERIAL", "SERIE", "MARCA", "MODELO", "REFERENCIA", "GENERICO", "", "MOUSE", "TECLADO", "NULL"]
    if s in BLACKLIST or len(s) < 3: return None
    return s.split('/')[0].strip()

def limpiar_mac(valor):
    if not valor: return None
    s = str(valor).strip().upper().replace(" ", "")
    return s[:17]

def get_password_hash(password): return pwd_context.hash(password)
def verify_password(plain, hashed): return pwd_context.verify(plain, hashed)

def registrar_historia(db: Session, id_activo: int, tipo: str, descripcion: str, usuario: str):
    try:
        nuevo = models.Actualizacion(
            id_activo=id_activo,
            tipo_evento=tipo,
            desc_evento=descripcion[:250], 
            usuario_sistema=usuario,
            fecha=datetime.now()
        )
        db.add(nuevo)
    except Exception as e:
        print(f"Error guardando historial: {e}")

def buscar_o_crear(db: Session, modelo, **filtros):
    instancia = db.query(modelo).filter_by(**filtros).first()
    if instancia: return instancia
    else:
        nueva_instancia = modelo(**filtros)
        db.add(nueva_instancia); db.commit(); db.refresh(nueva_instancia)
        return nueva_instancia
