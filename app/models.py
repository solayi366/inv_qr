from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime  # Importación correcta

class Marca(Base):
    __tablename__ = "tab_marca"
    id_marca = Column(Integer, primary_key=True, index=True)
    nom_marca = Column(String(100), unique=True, nullable=False)
    
    modelos = relationship("Modelo", back_populates="marca")
    activos = relationship("ActivoTec", back_populates="marca")

class TipoEquipo(Base):
    __tablename__ = "tab_tipos"
    id_tipoequi = Column(Integer, primary_key=True, index=True)
    nom_tipo = Column(String(100), unique=True, nullable=False)

    activos = relationship("ActivoTec", back_populates="tipo")

class Area(Base):
    __tablename__ = "tab_area"
    id_area = Column(Integer, primary_key=True, index=True)
    nom_area = Column(String(50), unique=True, nullable=False)

    empleados = relationship("Empleado", back_populates="area")

class Modelo(Base):
    __tablename__ = "tab_modelo"
    id_modelo = Column(Integer, primary_key=True, index=True)
    nom_modelo = Column(String(100), nullable=False)
    id_marca = Column(Integer, ForeignKey("tab_marca.id_marca"), nullable=False)
    
    id_tipoequi = Column(Integer, ForeignKey("tab_tipos.id_tipoequi"), nullable=True) 

    marca = relationship("Marca", back_populates="modelos")
    activos = relationship("ActivoTec", back_populates="modelo")

class Empleado(Base):
    __tablename__ = "tab_empleados"
    cod_nom = Column(String(6), primary_key=True, index=True) 
    nom_emple = Column(String(100), nullable=False)
    id_area = Column(Integer, ForeignKey("tab_area.id_area"), nullable=False)
    activo = Column(Boolean, default=True)

    area = relationship("Area", back_populates="empleados")
    activos_asignados = relationship("ActivoTec", back_populates="responsable")

class ActivoTec(Base):
    __tablename__ = "tab_activotec"
    
    id_activo = Column(Integer, primary_key=True, index=True)
    serial = Column(String(100), unique=True)
    codigo_qr = Column(String(50), unique=True)
    hostname = Column(String(100), nullable=True)
    referencia = Column(String(100))
    mac_activo = Column(String(17))
    ip_equipo = Column(String(15))
    
    id_tipoequi = Column(Integer, ForeignKey("tab_tipos.id_tipoequi"), nullable=False)
    id_marca = Column(Integer, ForeignKey("tab_marca.id_marca"), nullable=False)
    id_modelo = Column(Integer, ForeignKey("tab_modelo.id_modelo"), nullable=True)
    
    estado = Column(String(20), nullable=False)
    cod_nom_responsable = Column(String(6), ForeignKey("tab_empleados.cod_nom"), nullable=True)
    
    id_padre_activo = Column(Integer, ForeignKey("tab_activotec.id_activo"), nullable=True)

    tipo = relationship("TipoEquipo", back_populates="activos")
    marca = relationship("Marca", back_populates="activos")
    modelo = relationship("Modelo", back_populates="activos")
    responsable = relationship("Empleado", back_populates="activos_asignados")
    
    padre = relationship("ActivoTec", remote_side=[id_activo], back_populates="hijos")
    hijos = relationship("ActivoTec", back_populates="padre")
    
    historial = relationship("Actualizacion", back_populates="activo_rel")
    
    # Relación con la nueva tabla de novedades
    novedades = relationship("Novedad", back_populates="activo")

class Actualizacion(Base):
    __tablename__ = "tab_actualizaciones"
    id_evento = Column(Integer, primary_key=True, index=True)
    # CORRECCIÓN AQUÍ: Se usa datetime.utcnow directamente, no datetime.datetime.utcnow
    fecha = Column(DateTime, default=datetime.utcnow)
    id_activo = Column(Integer, ForeignKey("tab_activotec.id_activo"), nullable=False)
    tipo_evento = Column(String(50), nullable=False)
    desc_evento = Column(Text, nullable=False)
    usuario_sistema = Column(String(50))

    activo_rel = relationship("ActivoTec", back_populates="historial")

class Usuario(Base):
    __tablename__ = "tab_usuarios"
    id_usuario = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    contraseña = Column(String(255), nullable=False)

# --- NUEVA TABLA PARA EL MÓDULO DE REPORTES ---
class Novedad(Base):
    __tablename__ = "tab_novedades"

    id_novedad = Column(Integer, primary_key=True, index=True)
    fecha_reporte = Column(DateTime, default=datetime.now)
    
    # Quién reporta
    cedula_reportante = Column(String(50)) 
    nombre_reportante = Column(String(100))
    
    # Sobre qué activo
    id_activo = Column(Integer, ForeignKey("tab_activotec.id_activo"))
    
    # Detalle
    tipo_daño = Column(String(50)) 
    descripcion = Column(String(500))
    evidencia_foto = Column(String(255)) # Ruta del archivo
    
    # Estado del ticket
    estado_ticket = Column(String(20), default="Pendiente") 

    # Relación
    activo = relationship("ActivoTec", back_populates="novedades")