"""
Archivo de configuración para el Sistema de Visión Artificial
"""

# CONFIGURACIÓN DE CÁMARA

# Cámara IP (IP Webcam app)
IP_WEBCAM = "http://192.168.1.125:8080/video"  # Cambiar según tu IP

# Webcam local (alternativa)
USAR_WEBCAM_LOCAL = False
WEBCAM_INDEX = 0  # 0 para cámara predeterminada

#CONFIGURACIÓN DE BACKEND 

# URL del backend FastAPI
BACKEND_URL = "http://localhost:8000/api/v1/vision/actualizar-estado-mesas"

# Token de autenticación
ADMIN_TOKEN = None 

#  CONFIGURACIÓN DE MODELOS 

# Ruta al modelo YOLO de mesas (entrenado)
RUTA_MODELO_MESAS = "Entrenamiendo_mesas/weights/best.pt"

# Modelo YOLO para personas (COCO preentrenado)
MODELO_PERSONAS = "yolov8n.pt" 

# CONFIGURACIÓN DE DETECCIÓN

# Umbral de confianza para las detecciones
CONFIDENCE_THRESHOLD = 0.5

# Porcentaje mínimo de solapamiento para considerar persona en mesa (%)
OVERLAP_THRESHOLD = 30

#  CONFIGURACIÓN DE ACTUALIZACIÓN

# Intervalo de envío al backend (segundos)
INTERVALO_ACTUALIZACION = 5

# Enviar solo si hay cambios en el estado
ENVIAR_SOLO_CAMBIOS = False

# CONFIGURACIÓN DE VISUALIZACIÓN

# Mostrar ventana de visualización
MOSTRAR_VENTANA = True

# Tamaño de la ventana de visualización
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Colores para las visualizaciones (BGR)
COLOR_MESA_DISPONIBLE = (0, 255, 0)    # Verde
COLOR_MESA_OCUPADA = (0, 0, 255)       # Rojo
COLOR_MESA_RESERVADA = (0, 255, 255)   # Amarillo
COLOR_PERSONA = (255, 0, 0)            # Azul

# CONFIGURACIÓN DE LOGGING

# Nivel de logging
LOG_LEVEL = "INFO"

# Mostrar estadísticas cada N frames
MOSTRAR_STATS_CADA = 30

# Guardar logs en archivo
GUARDAR_LOGS = True
LOG_FILE = "vision_system.log"

# ==================== CONFIGURACIÓN 

# Timeout para requests al backend (segundos)
REQUEST_TIMEOUT = 5

# Reintentos en caso de fallo
MAX_REINTENTOS = 3

# FPS objetivo para procesamiento
TARGET_FPS = 30

# Guardar frames con detecciones
GUARDAR_FRAMES = False
FRAMES_DIR = "frames_guardados"