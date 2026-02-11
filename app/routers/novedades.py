from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import uuid, shutil, os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .. import models, database, utils

router = APIRouter(tags=["Novedades y Soporte"])
templates = Jinja2Templates(directory="templates")

# Configuración de Correo (Mantenida de tu main.py)
SMTP_USER = "solayitapias1@gmail.com" 
SMTP_PASSWORD = "rrvz xzmd ngaw mxch" 
EMAIL_DESTINO = "solayitapias1@gmail.com"
BASE_URL = "https://enviabuca.ddns.net/"

def enviar_alerta_email(asunto, mensaje_html):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = EMAIL_DESTINO
        msg['Subject'] = asunto
        msg.attach(MIMEText(mensaje_html, 'html'))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, EMAIL_DESTINO, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error correo: {e}")
        return False

# --- PORTAL DE USUARIOS ---
@router.get("/portal-reportes", response_class=templates.TemplateResponse)
def vista_portal_reportes(request: Request):
    return templates.TemplateResponse("portal_reportes.html", {"request": request})

@router.get("/api/mis-activos/{cedula}")
def buscar_mis_activos(cedula: str, db: Session = Depends(database.get_db)):
    activos = db.query(models.ActivoTec).filter(
        models.ActivoTec.cod_nom_responsable == cedula,
        models.ActivoTec.estado != "Baja"
    ).all()
    if not activos:
        return {"encontrado": False, "mensaje": "No se encontraron activos asignados."}
    nombre = activos[0].responsable.nom_emple if activos[0].responsable else "Usuario"
    lista = [{"id": a.id_activo, "tipo": a.tipo.nom_tipo, "marca": a.marca.nom_marca, 
              "modelo": a.modelo.nom_modelo if a.modelo else "Genérico", 
              "serial": a.serial, "foto_qr": f"/static/qrcodes/{a.codigo_qr}.png"} for a in activos]
    return {"encontrado": True, "empleado": nombre, "activos": lista}

@router.post("/crear-ticket")
async def crear_ticket_novedad(request: Request, cedula: str = Form(...), id_activo: int = Form(...), 
                               tipo_dano: str = Form(...), descripcion: str = Form(...), 
                               foto: UploadFile = File(None), db: Session = Depends(database.get_db)):
    try:
        ruta_foto = ""
        if foto and foto.filename:
            ext = foto.filename.split(".")[-1]
            fname = f"ticket_{id_activo}_{uuid.uuid4().hex[:6]}.{ext}"
            os.makedirs("static/uploads", exist_ok=True)
            with open(f"static/uploads/{fname}", "wb") as buffer:
                shutil.copyfileobj(foto.file, buffer)
            ruta_foto = f"{BASE_URL}static/uploads/{fname}"

        activo = db.query(models.ActivoTec).get(id_activo)
        nombre_reportante = activo.responsable.nom_emple if activo.responsable else "Anónimo"
        
        nuevo = models.Novedad(cedula_reportante=cedula, nombre_reportante=nombre_reportante, 
                               id_activo=id_activo, tipo_daño=tipo_dano, descripcion=descripcion, evidencia_foto=ruta_foto)
        db.add(nuevo)
        activo.estado = "Malo"
        utils.registrar_historia(db, id_activo, "REPORTE_USUARIO", f"Falla: {descripcion}", "PORTAL_WEB")
        db.commit()

        # Envío de correo
        html = f"<h2>Nuevo Reporte de Falla</h2><p>Activo: {activo.serial}</p><p>Daño: {tipo_dano}</p>"
        enviar_alerta_email(f"🚨 TICKET #{nuevo.id_novedad}", html)
        
        return templates.TemplateResponse("portal_exito.html", {"request": request, "id_ticket": nuevo.id_novedad})
    except Exception as e:
        return RedirectResponse("/portal-reportes?error=true", status_code=303)

# --- GESTIÓN ADMIN ---
@router.get("/gestion-novedades", response_class=templates.TemplateResponse)
def panel_novedades(request: Request, db: Session = Depends(database.get_db)):
    if not request.session.get("usuario"): return RedirectResponse("/login")
    tickets = db.query(models.Novedad).filter(models.Novedad.estado_ticket != "Cerrado").order_by(models.Novedad.fecha_reporte.desc()).all()
    return templates.TemplateResponse("lista_novedades.html", {"request": request, "tickets": tickets})

@router.post("/novedad/resolver/{id}")
def resolver_novedad(request: Request, id: int, solucion: str = Form(...), db: Session = Depends(database.get_db)):
    if not request.session.get("usuario"): return RedirectResponse("/login")
    t = db.query(models.Novedad).get(id)
    t.estado_ticket = "Cerrado"
    utils.registrar_historia(db, t.id_activo, "MANTENIMIENTO_CORRECTIVO", f"Ticket #{id} resuelto: {solucion}", request.session.get("usuario"))
    db.commit()
    return RedirectResponse("/gestion-novedades?msg=Ticket resuelto exitosamente&tipo=success", status_code=303)
