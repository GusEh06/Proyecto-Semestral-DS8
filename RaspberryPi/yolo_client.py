from ultralytics import YOLO
import cv2
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

# Configuración MQTT
BROKER = "IP_DE_LA_PI"
TOPIC = "restaurante/mesas"
RECONNECT_DELAY = 5

# Configuración del modelo
model = YOLO("yolov8n.pt")  # o tu modelo entrenado

# Variables de estado
is_connected = False

def on_connect(client, userdata, flags, rc):
    global is_connected
    if rc == 0:
        print("✓ Conectado al broker MQTT")
        is_connected = True
    else:
        print(f"✗ Error de conexión: {rc}")
        is_connected = False

def on_disconnect(client, userdata, rc):
    global is_connected
    is_connected = False
    print("✗ Desconectado del broker")
    if rc != 0:
        print(f"Reconectando en {RECONNECT_DELAY} segundos...")

# Configurar cliente MQTT con reconexión automática
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect

try:
    client.connect(BROKER, 1883, 60)
except Exception as e:
    print(f"Error inicial de conexión: {e}")

client.loop_start()

# Captura de video
cap = cv2.VideoCapture(0)

# Configuración de detección
CONFIDENCE_THRESHOLD = 0.5
MESA_ID = 1  # Cambiar según la mesa que esta cámara monitorea

# Estado anterior para evitar spam
estado_anterior = None
ultimo_envio = 0
INTERVALO_MINIMO = 3  # segundos entre envíos del mismo estado

print("Iniciando detección de personas...")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error al capturar frame")
        break
    
    # Realizar detección
    results = model(frame)
    
    # Contar personas detectadas en la mesa
    personas = sum(1 for r in results[0].boxes 
                  if r.cls == 0 and r.conf > CONFIDENCE_THRESHOLD)
    
    # Determinar estado
    estado = "ocupada" if personas > 0 else "disponible"
    
    # Enviar solo si hay cambio o ha pasado suficiente tiempo
    tiempo_actual = time.time()
    if estado != estado_anterior or (tiempo_actual - ultimo_envio) > 60:
        if is_connected:
            mensaje = {
                "mesa_id": MESA_ID,
                "estado": estado,
                "personas_detectadas": personas,
                "timestamp": datetime.now().isoformat(),
                "confianza": float(max([r.conf for r in results[0].boxes], default=0))
            }
            
            try:
                result = client.publish(TOPIC, json.dumps(mensaje), qos=1)
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"✓ Enviado: Mesa {MESA_ID} → {estado} ({personas} personas)")
                    estado_anterior = estado
                    ultimo_envio = tiempo_actual
                else:
                    print(f"✗ Error al publicar: {result.rc}")
            except Exception as e:
                print(f"✗ Error: {e}")
        else:
            print("⚠ Esperando conexión al broker...")
    
    # Mostrar resultados (opcional)
    annotated_frame = results[0].plot()
    cv2.putText(annotated_frame, f"Estado: {estado}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Detección", annotated_frame)
    
    if cv2.waitKey(1) == 27:  # ESC para salir
        break

cap.release()
cv2.destroyAllWindows()
client.loop_stop()
client.disconnect()
