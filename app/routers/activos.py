from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import uuid, json
from .. import models, database, utils

router = APIRouter(tags=["Activos"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
def pagina_principal(request: Request, page: int = 1, size: int = 20, db: Session = Depends(database.get_db)):
    # Filtramos para mostrar solo equipos principales (no accesorios)
    query = db.query(models.ActivoTec).filter(models.ActivoTec.id_padre_activo == None)
    
    # Calculamos el total y las páginas
    total_count = query.count()
    total_pages = (total_count + size - 1) // size
    
    if page < 1: page = 1
    if total_pages > 0 and page > total_pages: page = total_pages

    # Consultamos solo el bloque de la página actual
    activos = query.order_by(models.ActivoTec.id_activo.desc())\
                   .offset((page - 1) * size)\
                   .limit(size).all()
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "activos": activos, 
        "user": request.session.get("usuario"),
        "page": page,
        "total_pages": total_pages,
        "total_count": total_count,
        "size": size
    })

@router.get("/ver/{id}")
def ver_hoja_vida(request: Request, id: int, db: Session = Depends(database.get_db)):
    activo = db.query(models.ActivoTec).get(id)
    if not activo: raise HTTPException(404)
    return templates.TemplateResponse("ficha.html", {"request": request, "activo": activo, "user": request.session.get("usuario")})

@router.get("/crear")
def form_crear(request: Request, db: Session = Depends(database.get_db)):
    if not request.session.get("usuario"): return RedirectResponse("/login")
    return templates.TemplateResponse("crear.html", {
        "request": request, 
        "tipos": db.query(models.TipoEquipo).all(), 
        "marcas": db.query(models.Marca).all(), 
        "modelos": db.query(models.Modelo).all(), 
        "areas": db.query(models.Area).all(),
        "posibles_padres": db.query(models.ActivoTec).filter(models.ActivoTec.id_padre_activo == None).all()
    })

@router.post("/crear")
def procesar_crear(request: Request, serial: str = Form(...), id_tipoequi: int = Form(...), id_marca: int = Form(...), estado: str = Form(...), 
                   referencia: str = Form(None), hostname: str = Form(None), ip_equipo: str = Form(None), mac_activo: str = Form(None), 
                   id_modelo: int = Form(None), id_padre_activo: int = Form(None), cod_responsable: str = Form(None), 
                   nom_nuevo_empleado: str = Form(None), id_area_nuevo: int = Form(None), 
                   accesorios_json_final: str = Form(None),
                   db: Session = Depends(database.get_db)):
    usuario_actual = request.session.get("usuario")
    if not usuario_actual: return RedirectResponse("/login")
    
    try:
        responsable_final = None
        if cod_responsable and cod_responsable.strip():
            emp = db.query(models.Empleado).filter(models.Empleado.cod_nom == cod_responsable.strip()).first()
            if emp: responsable_final = emp.cod_nom
            elif nom_nuevo_empleado:
                # Lógica para crear empleado si no existe
                nuevo_id = cod_responsable.strip() if any(char.isdigit() for char in cod_responsable) else "T-" + str(uuid.uuid4().hex[:4]).upper()
                area_id = id_area_nuevo if id_area_nuevo else db.query(models.Area).first().id_area
                nuevo_emp = models.Empleado(cod_nom=nuevo_id, nom_emple=(nom_nuevo_empleado or cod_responsable).upper(), id_area=area_id, activo=True)
                db.add(nuevo_emp); db.commit(); responsable_final = nuevo_emp.cod_nom

        mac_final = utils.limpiar_mac(mac_activo)
        nuevo = models.ActivoTec(
            serial=serial, referencia=referencia, hostname=hostname, ip_equipo=ip_equipo, mac_activo=mac_final,
            id_tipoequi=id_tipoequi, id_marca=id_marca, id_modelo=id_modelo if id_modelo and id_modelo>0 else None,
            estado=estado, id_padre_activo=id_padre_activo, cod_nom_responsable=responsable_final, codigo_qr=str(uuid.uuid4())
        )
        db.add(nuevo); db.commit(); db.refresh(nuevo)
        
        # Generar código QR final
        url_real = str(request.url_for('ver_hoja_vida', id=nuevo.id_activo))
        nuevo.codigo_qr = f"ACT-{nuevo.id_activo:04d}"
        utils.generar_codigo_qr(nuevo.codigo_qr, url_real)
        
        utils.registrar_historia(db, nuevo.id_activo, "CREACION", f"Activo creado. Resp: {responsable_final or 'Bodega'}", usuario_actual)
        db.commit()

        # Procesar accesorios si vienen en el JSON
        if accesorios_json_final:
            try:
                lista_acc = json.loads(accesorios_json_final)
                for acc in lista_acc:
                    t_h = utils.buscar_o_crear(db, models.TipoEquipo, nom_tipo=acc['tipo'])
                    m_h = utils.buscar_o_crear(db, models.Marca, nom_marca=acc['marca'])
                    hijo = models.ActivoTec(
                        serial=acc['serial'], referencia=acc.get('referencia'), 
                        id_tipoequi=t_h.id_tipoequi, id_marca=m_h.id_marca, 
                        estado="Bueno", id_padre_activo=nuevo.id_activo, codigo_qr=str(uuid.uuid4())
                    )
                    db.add(hijo); db.commit(); db.refresh(hijo)
                    hijo.codigo_qr = f"ACC-{hijo.id_activo:04d}"
                    utils.generar_codigo_qr(hijo.codigo_qr, str(request.url_for('ver_hoja_vida', id=hijo.id_activo)))
                    utils.registrar_historia(db, hijo.id_activo, "CREACION", f"Accesorio vinculado a {nuevo.codigo_qr}", usuario_actual)
                db.commit()
            except: pass

        return RedirectResponse(f"/ver/{nuevo.id_activo}?msg=Activo Creado&tipo=success", status_code=303)
    except Exception as e: return RedirectResponse(f"/?msg=Error: {str(e)}&tipo=danger", status_code=303)

@router.get("/editar/{id}")
def form_editar(request: Request, id: int, db: Session = Depends(database.get_db)):
    if not request.session.get("usuario"): return RedirectResponse("/login")
    activo = db.query(models.ActivoTec).get(id)
    return templates.TemplateResponse("editar.html", {
        "request": request, "activo": activo, 
        "tipos": db.query(models.TipoEquipo).all(), 
        "marcas": db.query(models.Marca).all(), 
        "modelos": db.query(models.Modelo).all(), 
        "areas": db.query(models.Area).all(),
        "posibles_padres": db.query(models.ActivoTec).filter(models.ActivoTec.id_activo != id, models.ActivoTec.id_padre_activo == None).all()
    })

@router.post("/editar/{id}")
def procesar_editar(request: Request, id: int, serial: str = Form(...), id_tipoequi: int = Form(...), id_marca: int = Form(...), 
                    estado: str = Form(...), referencia: str = Form(None), ip_equipo: str = Form(None), mac_activo: str = Form(None), 
                    id_modelo: int = Form(None), id_padre_activo: int = Form(None), cod_responsable: str = Form(None), db: Session = Depends(database.get_db)):
    usuario = request.session.get("usuario")
    if not usuario: return RedirectResponse("/login")
    
    a = db.query(models.ActivoTec).get(id)
    # Registrar auditoría básica
    utils.registrar_historia(db, a.id_activo, "EDICION", "Actualización de ficha técnica", usuario)
    
    a.serial = serial; a.referencia = referencia; a.ip_equipo = ip_equipo; a.mac_activo = mac_activo
    a.id_tipoequi = id_tipoequi; a.id_marca = id_marca; a.estado = estado; a.id_padre_activo = id_padre_activo
    a.id_modelo = id_modelo if id_modelo and id_modelo > 0 else None
    a.cod_nom_responsable = cod_responsable
    
    db.commit()
    return RedirectResponse(f"/ver/{id}?msg=Guardado&tipo=success", status_code=303)

@router.get("/eliminar/{id}")
def eliminar_activo(request: Request, id: int, db: Session = Depends(database.get_db)):
    if not request.session.get("usuario"): return RedirectResponse("/login")
    a = db.query(models.ActivoTec).get(id)
    if not a: return RedirectResponse("/?msg=No encontrado", status_code=303)
    
    # Eliminar historial asociado
    db.query(models.Actualizacion).filter(models.Actualizacion.id_activo == id).delete()
    db.delete(a)
    db.commit()
    return RedirectResponse("/?msg=Eliminado correctamente&tipo=success", status_code=303)


@router.get("/imprimir/{id}", response_class=templates.TemplateResponse)
def imprimir_etiqueta(request: Request, id: int, db: Session = Depends(database.get_db)):
    if not request.session.get("usuario"): return RedirectResponse("/login", status_code=303)
    activo = db.query(models.ActivoTec).filter(models.ActivoTec.id_activo == id).first()
    if not activo: raise HTTPException(status_code=404)
    return templates.TemplateResponse("imprimir.html", {"request": request, "activo": activo})

@router.get("/historial/{id}")
def ver_historial_activo(request: Request, id: int, db: Session = Depends(database.get_db)):
    if not request.session.get("usuario"): return RedirectResponse("/login", status_code=303)
    
    activo = db.query(models.ActivoTec).filter(models.ActivoTec.id_activo == id).first()
    if not activo: raise HTTPException(status_code=404)
    
    historial = db.query(models.Actualizacion).filter(
        models.Actualizacion.id_activo == id
    ).order_by(models.Actualizacion.fecha.desc()).all()
    
    return templates.TemplateResponse("historial.html", {
        "request": request, 
        "activo": activo,
        "historial": historial
    })
