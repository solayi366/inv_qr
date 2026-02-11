from fastapi import APIRouter, Depends, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from .. import models, database, utils

router = APIRouter(tags=["Autenticación"])
templates = Jinja2Templates(directory="templates")

@router.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.username == username).first()
    if not user or not utils.verify_password(password, user.contraseña):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Credenciales inválidas"})
    request.session["usuario"] = user.username
    return RedirectResponse(url="/?msg=Bienvenido al Sistema&tipo=success", status_code=303)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login?msg=Sesión cerrada&tipo=info", status_code=303)
