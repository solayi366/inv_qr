import qrcode
from PIL import Image, ImageDraw

# 1. Configuración de rutas y URL
url = "https://inventario.envia06.com/portal-reportes"
logo_path = "static/logo_e.png"  # Asegúrate de que esta imagen exista
output_path = "static/qr_envia_integrado.png"

# 2. Crear QR con corrección de errores ALTA (H)
# Esto es vital para que el QR funcione aunque el logo "tape" parte de los datos
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

# Crear imagen base en blanco y negro, luego pasar a RGBA
img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGBA')
width, height = img_qr.size

# 3. Procesar el Logo
try:
    logo = Image.open(logo_path).convert('RGBA')
    
    # El logo ocupará el 25% del QR para que no deje de ser escaneable
    logo_size = width // 4 
    logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
    
    # 4. CREAR EL "ESPACIO INTEGRADO" (Círculo o Cuadrado blanco de fondo)
    # Esto hace que el logo no choque con los cuadritos negros
    pos_x = (width - logo.size[0]) // 2
    pos_y = (height - logo.size[1]) // 2
    
    # Creamos una máscara blanca un poco más grande que el logo para el borde
    padding = 10 
    white_space = Image.new('RGBA', (logo.size[0] + padding, logo.size[1] + padding), (255, 255, 255, 255))
    
    # Pegamos el fondo blanco en el centro del QR
    img_qr.paste(white_space, (pos_x - padding//2, pos_y - padding//2), white_space)
    
    # Pegamos el logo sobre ese espacio blanco
    img_qr.paste(logo, (pos_x, pos_y), logo)
    
    print("🚀 QR con logo integrado generado con éxito.")
except Exception as e:
    print(f"❌ Error integrando el logo: {e}")

# 5. Guardar
img_qr.save(output_path)
