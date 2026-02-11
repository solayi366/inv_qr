from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, database, utils
from .routers import auth, activos, novedades, parametros, excel

app = FastAPI(title="Sistema Inventario QR")

# Configuración básica
app.add_middleware(SessionMiddleware, secret_key="SUPXROSEVREUOIC4MBIPME")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Crear tablas
models.Base.metadata.create_all(bind=database.engine)

# Inyectar routers (IMPORTANTE: El orden importa)
app.include_router(auth.router)
app.include_router(activos.router)
app.include_router(novedades.router)
app.include_router(parametros.router)
app.include_router(excel.router)

@app.get("/dashboard")
def dashboard_view(request: Request):
    if not request.session.get("usuario"): return RedirectResponse("/login")
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/stats")
def api_estadisticas(request: Request, db: Session = Depends(database.get_db)):
    if not request.session.get("usuario"): raise HTTPException(401)
    total = db.query(models.ActivoTec).count()
    pendientes = db.query(models.Novedad).filter(models.Novedad.estado_ticket != "Cerrado").count()
    por_estado = db.query(models.ActivoTec.estado, func.count(models.ActivoTec.id_activo)).group_by(models.ActivoTec.estado).all()
    por_marca = db.query(models.Marca.nom_marca, func.count(models.ActivoTec.id_activo)).join(models.Marca).group_by(models.Marca.nom_marca).limit(5).all()
    
    return {
        "total": total, "pendientes": pendientes,
        "estados": [{"label": e[0], "count": e[1]} for e in por_estado],
        "marcas": [{"label": m[0], "count": m[1]} for m in por_marca]
    }

@app.on_event("startup")
def startup_event():
    db = database.SessionLocal()
    user = db.query(models.Usuario).filter(models.Usuario.username == "admin").first()
    if not user:
        db.add(models.Usuario(username="admin", contraseña=utils.get_password_hash("admin123")))
        db.commit()
    db.close()
