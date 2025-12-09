"""
Versión simplificada del sistema de visión para pruebas rápidas
Sin autenticación y con configuración mínima
"""

import cv2
import requests
import time
from ultralytics import YOLO
import logging

# Configuración simple
IP_WEBCAM = "http://192.168.50.133:8080/video"
BACKEND_URL = "http://localhost:8000/api/v1/vision/actualizar-estado-mesas"
MODELO_MESAS = "Entrenamiendo_mesas/weights/best.pt"
INTERVALO = 5  # segundos

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()


class SistemaSimple:
    def __init__(self):
        logger.info("Cargando modelos...")
        self.model_personas = YOLO('yolov8n.pt')
        self.model_mesas = YOLO(MODELO_MESAS)
        logger.info("Modelos cargados")
        self.ultimo_envio = 0
    
    def detectar(self, frame):
        """Detecta personas y mesas"""
        personas = self.model_personas(frame, classes=[0], verbose=False)[0].boxes
        mesas = self.model_mesas(frame, verbose=False)[0].boxes
        return personas, mesas
    
    def contar_personas_por_mesa(self, personas, mesas):
        """Cuenta cuántas personas hay en cada mesa"""
        resultado = []
        
        for idx, mesa in enumerate(mesas):
            mx1, my1, mx2, my2 = map(int, mesa.xyxy[0])
            count = 0
            
            for persona in personas:
                px1, py1, px2, py2 = map(int, persona.xyxy[0])
                # Centro de la persona
                px_center = (px1 + px2) // 2
                py_center = (py1 + py2) // 2
                
                # ¿Está dentro de la mesa?
                if mx1 <= px_center <= mx2 and my1 <= py_center <= my2:
                    count += 1
            
            resultado.append({
                "id_mesa": idx + 1,
                "personas_detectadas": count,
                "bbox": (mx1, my1, mx2, my2)
            })
        
        return resultado
    
    def dibujar(self, frame, detecciones):
        """Dibuja las detecciones"""
        for det in detecciones:
            x1, y1, x2, y2 = det["bbox"]
            count = det["personas_detectadas"]
            
            # Color según ocupación
            color = (0, 255, 0) if count == 0 else (0, 0, 255)
            
            # Dibujar rectángulo
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
            
            # Texto
            texto = f"Mesa {det['id_mesa']}: {count} personas"
            cv2.putText(frame, texto, (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        return frame
    
    def enviar_backend(self, detecciones):
        """Envía al backend"""
        try:
            payload = {
                "detecciones": [
                    {"id_mesa": d["id_mesa"], "personas_detectadas": d["personas_detectadas"]}
                    for d in detecciones
                ]
            }
            
            response = requests.post(BACKEND_URL, json=payload, timeout=3)
            
            if response.status_code == 200:
                logger.info("✓ Enviado al backend")
                return True
            else:
                logger.error(f"✗ Error: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"✗ Error: {e}")
            return False
    
    def debe_enviar(self):
        """Verifica si debe enviar al backend"""
        ahora = time.time()
        if ahora - self.ultimo_envio >= INTERVALO:
            self.ultimo_envio = ahora
            return True
        return False
    
    def ejecutar(self):
        """Bucle principal"""
        logger.info(f"Conectando a cámara: {IP_WEBCAM}")
        cap = cv2.VideoCapture(IP_WEBCAM)
        
        if not cap.isOpened():
            logger.error("No se pudo conectar a la cámara")
            return
        
        logger.info("✓ Conectado - Presiona 'q' para salir, 's' para envío manual")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Detectar
                personas, mesas = self.detectar(frame)
                detecciones = self.contar_personas_por_mesa(personas, mesas)
                
                # Dibujar
                frame_anotado = self.dibujar(frame, detecciones)
                
                # Enviar si corresponde
                if detecciones and self.debe_enviar():
                    self.enviar_backend(detecciones)
                    
                    # Log simple
                    logger.info("-" * 40)
                    for d in detecciones:
                        estado = "🟢 LIBRE" if d["personas_detectadas"] == 0 else "🔴 OCUPADA"
                        logger.info(f"Mesa {d['id_mesa']}: {estado} ({d['personas_detectadas']} personas)")
                    logger.info("-" * 40)
                
                # Mostrar
                cv2.imshow('Vision System', frame_anotado)
                
                # Teclas
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s') and detecciones:
                    self.enviar_backend(detecciones)
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            logger.info("Sistema cerrado")


if __name__ == "__main__":
    print("""
    ----------------------------------------
      Sistema de Visión - Versión Simple     
     ----------------------------------------
    """)
    
    # Configuración rápida
    usar_webcam = input("¿Usar webcam local? (s/n) [n]: ").lower() == 's'
    
    if usar_webcam:
        IP_WEBCAM = 0
    
    sistema = SistemaSimple()
    sistema.ejecutar()