from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .. import models, database

router = APIRouter(tags=["Parámetros"])
templates = Jinja2Templates(directory="templates")

@router.get("/parametros")
def gestionar_parametros(request: Request, db: Session = Depends(database.get_db)):
    if not request.session.get("usuario"): return RedirectResponse("/login")
    return templates.TemplateResponse("parametros.html", {
        "request": request, 
        "marcas": db.query(models.Marca).all(), 
        "modelos": db.query(models.Modelo).all(),
        "tipos": db.query(models.TipoEquipo).all(), 
        "areas": db.query(models.Area).all(), 
        "empleados": db.query(models.Empleado).all()
    })

@router.post("/{tipo}/crear")
def crear_parametro_generico(request: Request, tipo: str, db: Session = Depends(database.get_db),
                             nom_marca: str = Form(None), nom_tipo: str = Form(None), nom_area: str = Form(None),
                             nom_modelo: str = Form(None), id_marca: int = Form(None), id_tipoequi: int = Form(None),
                             cod_nom: str = Form(None), nom_emple: str = Form(None), id_area: int = Form(None)):
    if not request.session.get("usuario"): return RedirectResponse("/login")
    try:
        if tipo == "marca": db.add(models.Marca(nom_marca=nom_marca.upper()))
        elif tipo == "tipo": db.add(models.TipoEquipo(nom_tipo=nom_tipo.upper()))
        elif tipo == "area": db.add(models.Area(nom_area=nom_area))
        elif tipo == "modelo": db.add(models.Modelo(nom_modelo=nom_modelo, id_marca=id_marca, id_tipoequi=id_tipoequi))
        elif tipo == "empleado": db.add(models.Empleado(cod_nom=cod_nom, nom_emple=nom_emple.upper(), id_area=id_area, activo=True))
        db.commit()
        return RedirectResponse("/parametros?msg=Creado correctamente&tipo=success", status_code=303)
    except Exception as e: return RedirectResponse(f"/parametros?msg=Error: {e}&tipo=danger", status_code=303)

@router.get("/editar_parametro/{tipo}/{id}")
def vista_editar_parametro(request: Request, tipo: str, id: str, db: Session = Depends(database.get_db)):
    if not request.session.get("usuario"): return RedirectResponse("/login")
    item = None
    if tipo == "marca": item = db.query(models.Marca).get(int(id))
    elif tipo == "modelo": item = db.query(models.Modelo).get(int(id))
    elif tipo == "tipo": item = db.query(models.TipoEquipo).get(int(id))
    elif tipo == "area": item = db.query(models.Area).get(int(id))
    elif tipo == "empleado": item = db.query(models.Empleado).get(id)
    return templates.TemplateResponse("editar_parametro.html", {
        "request": request, "item": item, "tipo": tipo, 
        "marcas": db.query(models.Marca).all(), 
        "tipos": db.query(models.TipoEquipo).all(), 
        "areas": db.query(models.Area).all()
    })

@router.post("/editar_parametro/{tipo}/{id}")
def procesar_editar_parametro(request: Request, tipo: str, id: str, nombre: str = Form(...), 
                              nuevo_codigo: str = Form(None), id_marca: int = Form(None), 
                              id_tipoequi: int = Form(None), id_area: int = Form(None), 
                              db: Session = Depends(database.get_db)):
    if not request.session.get("usuario"): return RedirectResponse("/login")
    try:
        if tipo == "marca": db.query(models.Marca).filter(models.Marca.id_marca == int(id)).update({"nom_marca": nombre.upper()})
        elif tipo == "tipo": db.query(models.TipoEquipo).filter(models.TipoEquipo.id_tipoequi == int(id)).update({"nom_tipo": nombre.upper()})
        elif tipo == "area": db.query(models.Area).filter(models.Area.id_area == int(id)).update({"nom_area": nombre})
        elif tipo == "modelo": db.query(models.Modelo).filter(models.Modelo.id_modelo == int(id)).update({"nom_modelo": nombre, "id_marca": id_marca, "id_tipoequi": id_tipoequi})
        elif tipo == "empleado":
            db.query(models.Empleado).filter(models.Empleado.cod_nom == id).update({"nom_emple": nombre.upper(), "id_area": id_area})
        db.commit()
        return RedirectResponse("/parametros?msg=Editado correctamente&tipo=success", status_code=303)
    except Exception as e:
        db.rollback()
        return RedirectResponse(f"/parametros?msg=Error: {e}&tipo=danger", status_code=303)

@router.get("/{tipo}/eliminar/{id}")
def eliminar_parametro(request: Request, tipo: str, id: str, db: Session = Depends(database.get_db)):
    if not request.session.get("usuario"): return RedirectResponse("/login")
    try:
        item = None
        if tipo == "marca": item = db.query(models.Marca).get(int(id))
        elif tipo == "tipo": item = db.query(models.TipoEquipo).get(int(id))
        elif tipo == "area": item = db.query(models.Area).get(int(id))
        elif tipo == "modelo": item = db.query(models.Modelo).get(int(id))
        elif tipo == "empleado": item = db.query(models.Empleado).get(id)
        if item:
            db.delete(item)
            db.commit()
        return RedirectResponse("/parametros?msg=Eliminado correctamente&tipo=success", status_code=303)
    except IntegrityError:
        return RedirectResponse("/parametros?msg=Error: El registro está en uso&tipo=danger", status_code=303)
