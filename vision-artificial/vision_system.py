"""
Sistema de Visión Artificial para Gestión de Mesas de Restaurante
=================================================================

Este módulo detecta personas y mesas en tiempo real, calcula el estado
de cada mesa y actualiza automáticamente el backend FastAPI.

Autor: Sistema de Reservaciones
Fecha: 2025
"""

import cv2
import requests
import time
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

#CONFIGURACIÓN

# URLs y rutas
IP_WEBCAM = "http://192.168.50.133:8080/video"  # Cambiar según tu IP
BACKEND_URL = "http://localhost:8000/api/v1/vision/actualizar-estado-mesas"
RUTA_MODELO_MESAS = "Entrenamiendo_mesas/weights/best.pt"

# Parámetros de actualización
INTERVALO_ACTUALIZACION = 5  # Segundos entre envíos al backend
CONFIDENCE_THRESHOLD = 0.5   # Umbral de confianza para detecciones

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# CLASES DE DATOS 

@dataclass
class BoundingBox:
    """Representa un cuadro delimitador (bounding box)"""
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float
    label: str
    
    @property
    def center(self) -> Tuple[int, int]:
        """Retorna el centro del bounding box"""
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)
    
    @property
    def area(self) -> int:
        """Retorna el área del bounding box"""
        return (self.x2 - self.x1) * (self.y2 - self.y1)
    
    def contains_point(self, x: int, y: int) -> bool:
        """Verifica si un punto está dentro del bounding box"""
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2
    
    def overlaps_with(self, other: 'BoundingBox') -> bool:
        """Verifica si hay solapamiento con otro bounding box"""
        return not (self.x2 < other.x1 or self.x1 > other.x2 or
                   self.y2 < other.y1 or self.y1 > other.y2)
    
    def overlap_area(self, other: 'BoundingBox') -> int:
        """Calcula el área de solapamiento con otro bounding box"""
        if not self.overlaps_with(other):
            return 0
        
        x_overlap = max(0, min(self.x2, other.x2) - max(self.x1, other.x1))
        y_overlap = max(0, min(self.y2, other.y2) - max(self.y1, other.y1))
        return x_overlap * y_overlap


@dataclass
class DeteccionMesa:
    """Representa una mesa detectada con personas"""
    id_mesa: int
    bbox: BoundingBox
    personas_detectadas: int
    personas_bbox: List[BoundingBox]
    
    def __repr__(self):
        return f"Mesa {self.id_mesa}: {self.personas_detectadas} personas"


# ======================== CLASE PRINCIPAL ========================

class SistemaVisionMesas:
    """
    Sistema completo de visión artificial para gestión de mesas.
    
    Funcionalidades:
    - Detecta mesas y personas en tiempo real
    - Calcula cuántas personas hay en cada mesa
    - Determina el estado de cada mesa (disponible/ocupada/reservada)
    - Envía actualizaciones al backend automáticamente
    """
    
    def __init__(self, 
                 ip_webcam: str = IP_WEBCAM,
                 backend_url: str = BACKEND_URL,
                 modelo_mesas_path: str = RUTA_MODELO_MESAS,
                 intervalo_actualizacion: int = INTERVALO_ACTUALIZACION):
        """
        Inicializa el sistema de visión.
        
        Args:
            ip_webcam: URL de la cámara IP o índice de webcam
            backend_url: URL del endpoint del backend
            modelo_mesas_path: Ruta al modelo YOLO de mesas
            intervalo_actualizacion: Segundos entre envíos al backend
        """
        logger.info("Inicializando Sistema de Visión de Mesas...")
        
        self.ip_webcam = ip_webcam
        self.backend_url = backend_url
        self.intervalo_actualizacion = intervalo_actualizacion
        
        # Cargar modelos YOLO
        logger.info("Cargando modelo YOLO para personas...")
        self.model_personas = YOLO('yolov8n.pt')  # Modelo COCO preentrenado
        
        logger.info("Cargando modelo YOLO para mesas...")
        self.model_mesas = YOLO(modelo_mesas_path)
        
        # Variables de control
        self.ultimo_envio = 0
        self.mesas_registradas: Dict[int, DeteccionMesa] = {}
        self.contador_frames = 0
        
        # Estadísticas
        self.total_envios = 0
        self.envios_exitosos = 0
        self.envios_fallidos = 0
        
        logger.info("✓ Sistema inicializado correctamente")
    
    # ==================== DETECCIÓN ====================
    
    def detectar_personas(self, frame: np.ndarray) -> List[BoundingBox]:
        """
        Detecta personas en el frame.
        
        Args:
            frame: Frame de video (numpy array)
        
        Returns:
            Lista de BoundingBox con personas detectadas
        """
        # Ejecutar modelo YOLO - clase 0 es 'person' en COCO
        results = self.model_personas(frame, classes=[0], verbose=False)
        
        personas = []
        for box in results[0].boxes:
            if float(box.conf[0]) >= CONFIDENCE_THRESHOLD:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                personas.append(BoundingBox(
                    x1=x1, y1=y1, x2=x2, y2=y2,
                    confidence=float(box.conf[0]),
                    label="Persona"
                ))
        
        return personas
    
    def detectar_mesas(self, frame: np.ndarray) -> List[BoundingBox]:
        """
        Detecta mesas en el frame.
        
        Args:
            frame: Frame de video (numpy array)
        
        Returns:
            Lista de BoundingBox con mesas detectadas
        """
        # Ejecutar modelo YOLO personalizado
        results = self.model_mesas(frame, verbose=False)
        
        mesas = []
        for idx, box in enumerate(results[0].boxes):
            if float(box.conf[0]) >= CONFIDENCE_THRESHOLD:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                mesas.append(BoundingBox(
                    x1=x1, y1=y1, x2=x2, y2=y2,
                    confidence=float(box.conf[0]),
                    label=f"Mesa {idx + 1}"
                ))
        
        return mesas
    
    # ==================== CRUCE DE DETECCIONES ====================
    
    def asignar_personas_a_mesas(self, 
                                 mesas: List[BoundingBox], 
                                 personas: List[BoundingBox]) -> List[DeteccionMesa]:
        """
        Determina qué personas están en qué mesas.
        
        Usa dos métodos:
        1. Verifica si el centro de la persona está dentro de la mesa
        2. Verifica el porcentaje de solapamiento entre bounding boxes
        
        Args:
            mesas: Lista de bounding boxes de mesas
            personas: Lista de bounding boxes de personas
        
        Returns:
            Lista de DeteccionMesa con personas asignadas
        """
        detecciones = []
        
        for idx, mesa in enumerate(mesas):
            personas_en_mesa = []
            
            for persona in personas:
                # Método 1: Centro de persona dentro de mesa
                px, py = persona.center
                esta_dentro = mesa.contains_point(px, py)
                
                # Método 2: Solapamiento significativo (>30% del área de la persona)
                if not esta_dentro:
                    overlap = mesa.overlap_area(persona)
                    porcentaje_overlap = (overlap / persona.area) * 100
                    esta_dentro = porcentaje_overlap > 30
                
                if esta_dentro:
                    personas_en_mesa.append(persona)
            
            detecciones.append(DeteccionMesa(
                id_mesa=idx + 1,
                bbox=mesa,
                personas_detectadas=len(personas_en_mesa),
                personas_bbox=personas_en_mesa
            ))
        
        return detecciones
    
    #  VISUALIZACIÓN 
    
    def dibujar_detecciones(self, 
                           frame: np.ndarray, 
                           detecciones: List[DeteccionMesa]) -> np.ndarray:
        """
        Dibuja las detecciones en el frame.
        
        Args:
            frame: Frame de video
            detecciones: Lista de detecciones de mesas
        
        Returns:
            Frame anotado
        """
        frame_anotado = frame.copy()
        
        for det in detecciones:
            # Determinar color según cantidad de personas
            if det.personas_detectadas == 0:
                color = (0, 255, 0)  # Verde - disponible
                estado = "DISPONIBLE"
            elif det.personas_detectadas <= 2:
                color = (0, 255, 255)  # Amarillo - poco ocupada
                estado = "OCUPADA"
            else:
                color = (0, 0, 255)  # Rojo - muy ocupada
                estado = "OCUPADA"
            
            # Dibujar mesa
            bbox = det.bbox
            cv2.rectangle(frame_anotado, 
                         (bbox.x1, bbox.y1), 
                         (bbox.x2, bbox.y2), 
                         color, 3)
            
            # Etiqueta de mesa
            label = f"MESA {det.id_mesa} - {estado}"
            personas_text = f"{det.personas_detectadas} persona{'s' if det.personas_detectadas != 1 else ''}"
            
            # Fondo para el texto
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(frame_anotado,
                         (bbox.x1, bbox.y1 - 50),
                         (bbox.x1 + max(label_size[0], 200), bbox.y1),
                         color, -1)
            
            # Texto
            cv2.putText(frame_anotado, label,
                       (bbox.x1 + 5, bbox.y1 - 28),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame_anotado, personas_text,
                       (bbox.x1 + 5, bbox.y1 - 8),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Dibujar personas en esta mesa
            for persona_bbox in det.personas_bbox:
                cv2.rectangle(frame_anotado,
                             (persona_bbox.x1, persona_bbox.y1),
                             (persona_bbox.x2, persona_bbox.y2),
                             (255, 0, 0), 2)  # Azul para personas
        
        # Información general en la esquina
        info_y = 30
        cv2.putText(frame_anotado, f"Mesas detectadas: {len(detecciones)}",
                   (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        total_personas = sum(d.personas_detectadas for d in detecciones)
        cv2.putText(frame_anotado, f"Personas totales: {total_personas}",
                   (10, info_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame_anotado
    
    # COMUNICACIÓN CON BACKEND 
    
    def enviar_actualizacion_backend(self, detecciones: List[DeteccionMesa]) -> bool:
        """
        Envía las detecciones al backend.
        
        Args:
            detecciones: Lista de detecciones de mesas
        
        Returns:
            True si el envío fue exitoso, False en caso contrario
        """
        try:
            # Preparar datos
            payload = {
                "detecciones": [
                    {
                        "id_mesa": det.id_mesa,
                        "personas_detectadas": det.personas_detectadas
                    }
                    for det in detecciones
                ]
            }
            
            # Enviar POST al backend
            logger.info(f"Enviando actualización al backend...")
            response = requests.post(
                self.backend_url,
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"Actualización enviada exitosamente")
                self.envios_exitosos += 1
                
                # Mostrar respuesta del servidor
                data = response.json()
                for resultado in data.get('resultados', []):
                    if resultado['success']:
                        logger.info(f"  Mesa {resultado['id_mesa']}: "
                                  f"{resultado['estado_anterior']} → {resultado['estado_nuevo']} "
                                  f"({resultado['personas_detectadas']} personas)")
                
                return True
            else:
                logger.error(f"✗ Error del servidor: {response.status_code}")
                logger.error(f"  Respuesta: {response.text}")
                self.envios_fallidos += 1
                return False
                
        except requests.exceptions.Timeout:
            logger.error("✗ Timeout al conectar con el backend")
            self.envios_fallidos += 1
            return False
        except requests.exceptions.ConnectionError:
            logger.error("✗ No se pudo conectar con el backend. ¿Está corriendo?")
            self.envios_fallidos += 1
            return False
        except Exception as e:
            logger.error(f"✗ Error inesperado: {e}")
            self.envios_fallidos += 1
            return False
    
    def debe_actualizar_backend(self) -> bool:
        """
        Verifica si es momento de enviar actualización al backend.
        
        Returns:
            True si debe actualizar, False en caso contrario
        """
        tiempo_actual = time.time()
        if tiempo_actual - self.ultimo_envio >= self.intervalo_actualizacion:
            self.ultimo_envio = tiempo_actual
            return True
        return False
    
    # ==================== LOGS Y ESTADÍSTICAS ====================
    
    def mostrar_estadisticas_consola(self, detecciones: List[DeteccionMesa]):
        """Muestra estadísticas en consola de forma clara"""
        logger.info("=" * 60)
        logger.info(f"Frame #{self.contador_frames}")
        logger.info(f"Tiempo: {datetime.now().strftime('%H:%M:%S')}")
        logger.info("-" * 60)
        
        for det in detecciones:
            if det.personas_detectadas == 0:
                estado_emoji = "🟢"
                estado = "DISPONIBLE"
            else:
                estado_emoji = "🔴"
                estado = "OCUPADA"
            
            logger.info(f"{estado_emoji} Mesa {det.id_mesa} → {estado} "
                       f"({det.personas_detectadas} persona{'s' if det.personas_detectadas != 1 else ''})")
        
        logger.info("-" * 60)
        logger.info(f"Total de mesas: {len(detecciones)}")
        total_personas = sum(d.personas_detectadas for d in detecciones)
        logger.info(f"Total de personas: {total_personas}")
        logger.info(f"Envíos exitosos/fallidos: {self.envios_exitosos}/{self.envios_fallidos}")
        logger.info("=" * 60)
    
    # ==================== BUCLE PRINCIPAL ====================
    
    def ejecutar(self, usar_webcam: bool = False, webcam_index: int = 0):
        """
        Ejecuta el sistema de visión en tiempo real.
        
        Args:
            usar_webcam: Si True, usa webcam local en lugar de IP
            webcam_index: Índice de la webcam (0 para la predeterminada)
        """
        logger.info(" Iniciando sistema de visión...")
        
        # Conectar a cámara
        if usar_webcam:
            logger.info(f"Conectando a webcam {webcam_index}...")
            cap = cv2.VideoCapture(webcam_index)
        else:
            logger.info(f"Conectando a cámara IP: {self.ip_webcam}...")
            cap = cv2.VideoCapture(self.ip_webcam)
        
        if not cap.isOpened():
            logger.error(" No se pudo conectar a la cámara")
            logger.error("Verifica:")
            logger.error("  1. La IP está correcta")
            logger.error("  2. Estás en la misma red")
            logger.error("  3. La aplicación IP Webcam está corriendo")
            return
        
        logger.info("Conectado a la cámara")
        logger.info(f"Enviando actualizaciones cada {self.intervalo_actualizacion} segundos")
        logger.info("Presiona 'q' para salir | 's' para envío manual | 'e' para estadísticas")
        logger.info("")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    logger.error("Conexión con cámara perdida")
                    break
                
                self.contador_frames += 1
                
                # 1. Detectar personas y mesas
                personas = self.detectar_personas(frame)
                mesas = self.detectar_mesas(frame)
                
                # 2. Asignar personas a mesas
                detecciones = self.asignar_personas_a_mesas(mesas, personas)
                
                # 3. Dibujar visualización
                frame_anotado = self.dibujar_detecciones(frame, detecciones)
                
                # 4. Actualizar backend automáticamente
                if detecciones and self.debe_actualizar_backend():
                    self.total_envios += 1
                    self.enviar_actualizacion_backend(detecciones)
                    self.mostrar_estadisticas_consola(detecciones)
                
                # 5. Mostrar frame
                cv2.imshow('Sistema de Visión - Mesas del Restaurante', frame_anotado)
                
                # 6. Manejar teclas
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    logger.info("Saliendo...")
                    break
                elif key == ord('s') and detecciones:
                    logger.info("Envío manual solicitado...")
                    self.total_envios += 1
                    self.enviar_actualizacion_backend(detecciones)
                    self.mostrar_estadisticas_consola(detecciones)
                elif key == ord('e'):
                    if detecciones:
                        self.mostrar_estadisticas_consola(detecciones)
                    else:
                        logger.info("No hay detecciones para mostrar")
        
        except KeyboardInterrupt:
            logger.info("\nInterrumpido por el usuario")
        except Exception as e:
            logger.error(f"\n Error inesperado: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Limpieza
            cap.release()
            cv2.destroyAllWindows()
            
            # Estadísticas finales
            logger.info("\n" + "=" * 60)
            logger.info("ESTADÍSTICAS FINALES")
            logger.info("=" * 60)
            logger.info(f"Frames procesados: {self.contador_frames}")
            logger.info(f"Total de envíos: {self.total_envios}")
            logger.info(f"Envíos exitosos: {self.envios_exitosos}")
            logger.info(f"Envíos fallidos: {self.envios_fallidos}")
            if self.total_envios > 0:
                tasa_exito = (self.envios_exitosos / self.total_envios) * 100
                logger.info(f"Tasa de éxito: {tasa_exito:.1f}%")
            logger.info("=" * 60)
            logger.info("✓ Sistema finalizado correctamente")


# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal para ejecutar el sistema"""
    print("""

     Sistema de Visión Artificial para Gestión de Mesas       
            Restaurante - Sistema de Reservaciones     
          -----------------------------------------------             
    """)
    
    #  VARIABLES LOCALES (NO TOCAN LAS GLOBALES)
    ip_webcam_local = IP_WEBCAM
    backend_url_local = BACKEND_URL
    intervalo_local = INTERVALO_ACTUALIZACION
    
    print("\n🔧 CONFIGURACIÓN")
    print("-" * 60)
    
    opcion = input("¿Usar webcam local? (s/n) [n]: ").strip().lower()
    usar_webcam = opcion == 's'
    
    if usar_webcam:
        webcam_index = input("Índice de webcam [0]: ").strip()
        webcam_index = int(webcam_index) if webcam_index else 0
    else:
        ip = input(f"IP de cámara [{IP_WEBCAM}]: ").strip()
        if ip:
            ip_webcam_local = ip
        webcam_index = 0
    
    backend = input(f"URL del backend [{BACKEND_URL}]: ").strip()
    if backend:
        backend_url_local = backend
    
    intervalo = input(f"Intervalo de actualización en segundos [{INTERVALO_ACTUALIZACION}]: ").strip()
    if intervalo:
        intervalo_local = int(intervalo)
    
    print("\n✓ Configuración completada\n")
    
    #  INICIALIZACIÓN CORRECTA (SIN VARIABLES GLOBALES)
    sistema = SistemaVisionMesas(
        ip_webcam=webcam_index if usar_webcam else ip_webcam_local,
        backend_url=backend_url_local,
        intervalo_actualizacion=intervalo_local
    )
    
    sistema.ejecutar(usar_webcam=usar_webcam, webcam_index=webcam_index)



if __name__ == "__main__":
    main()