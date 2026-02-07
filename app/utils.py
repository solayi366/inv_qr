import qrcode
import os

def generar_codigo_qr(nombre_archivo: str, datos_para_el_qr: str):
    """
    Genera un QR que contiene 'datos_para_el_qr' (la URL)
    pero se guarda en el disco como 'nombre_archivo.png'
    """
    # 1. Crear la carpeta si no existe
    ruta_carpeta = "static/qrcodes"
    if not os.path.exists(ruta_carpeta):
        os.makedirs(ruta_carpeta)
    
    # 2. Configurar el QR (Tamaño y corrección de errores)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # 3. Meter los datos 
    qr.add_data(datos_para_el_qr)
    qr.make(fit=True)

    # 4. Crear la imagen
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 5. Guardar el archivo con el nombre bonito (ACT-0001.png)
    ruta_completa = os.path.join(ruta_carpeta, f"{nombre_archivo}.png")
    img.save(ruta_completa)
    
    print(f"✅ QR Generado: {ruta_completa} -> Apunta a: {datos_para_el_qr}")

def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        session.refresh(instance)
        return instance