# Arquitectura del Sistema con MQTT

## Flujo de Datos Correcto

```
┌─────────────────────┐
│  1. Edge Computing  │
│   (Visión/Cámara)   │
└──────────┬──────────┘
           │ Publica mensajes MQTT
           │ Topic: restaurant/ocupacion
           ▼
┌─────────────────────┐
│  2. Broker MQTT     │
│   (Mosquitto)       │
│   IP: 100.81.10.77  │
└──────────┬──────────┘
           │ Distribuye mensajes
           ▼
┌─────────────────────┐
│  3. Backend         │
│   (FastAPI)         │
│   - Suscrito a MQTT │
│   - Procesa msgs    │
└──────────┬──────────┘
           │ Actualiza
           ▼
┌─────────────────────┐
│  4. Base de Datos   │
│   (PostgreSQL)      │
└─────────────────────┘
           │ Consulta
           ▼
┌─────────────────────┐
│  5. Frontend        │
│   - API REST        │
│   - SSE (eventos)   │
└─────────────────────┘
```

## Componentes

### 1. Sistema de Visión Artificial (Edge Computing)

**Archivo:** `vision-artificial/vision_system.py`

**Responsabilidad:**
- Detectar mesas y personas con YOLO
- **Publicar** detecciones al broker MQTT (NO hacer HTTP requests)

**Configuración MQTT:**
```python
BROKER_HOST = "100.81.10.77"  # IP del broker
BROKER_PORT = 1883
TOPIC_OCUPACION = "restaurant/ocupacion"
DEVICE_ID = "vision_camera_01"
```

**Mensaje publicado:**
```json
{
  "timestamp": "2025-01-15T14:30:00",
  "device_id": "vision_camera_01",
  "detecciones": [
    {
      "id_mesa": 1,
      "personas_detectadas": 2,
      "confianza": 0.95
    }
  ]
}
```

### 2. Broker MQTT (Mosquitto)

**Ubicación:** Raspberry Pi o servidor dedicado
**IP:** `100.81.10.77`
**Puerto:** `1883`

**Topics:**
- `restaurant/ocupacion` - Detecciones del sistema de visión
- `restaurant/dispositivos/+/estado` - Estado de dispositivos (online/offline)

**Instalación:**
```bash
# En Raspberry Pi / Linux
sudo apt update
sudo apt install mosquitto mosquitto-clients

# Iniciar servicio
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```

**Probar conexión:**
```bash
# Suscribirse a mensajes
mosquitto_sub -h 100.81.10.77 -t "restaurant/#" -v

# Publicar mensaje de prueba
mosquitto_pub -h 100.81.10.77 -t "restaurant/ocupacion" -m '{"test": true}'
```

### 3. Backend (FastAPI)

**Archivo:** `back-end/app/services/mqtt_service.py`

**Responsabilidad:**
- **Suscribirse** a topics MQTT del broker
- Procesar mensajes recibidos
- Actualizar base de datos
- Emitir eventos SSE al frontend

**Configuración:**
```python
BROKER_HOST = "100.81.10.77"  # Misma IP que el sistema de visión
BROKER_PORT = 1883
TOPIC_OCUPACION = "restaurant/ocupacion"
```

**Inicio del servicio:**
```python
# En back-end/app/main.py
from app.services.mqtt_service import mqtt_service

@app.on_event("startup")
async def startup_event():
    mqtt_service.start()  # Inicia suscripción MQTT

@app.on_event("shutdown")
async def shutdown_event():
    mqtt_service.stop()
```

### 4. Base de Datos (PostgreSQL)

El backend actualiza la BD cuando recibe mensajes MQTT:

```python
def actualizar_estado_mesas(self, detecciones: list):
    # Lógica para actualizar mesas en la BD
    # Respeta reservas activas
    # Emite eventos SSE a clientes conectados
```

### 5. Frontend

**Conexión con Backend:**
- **API REST:** Consultas normales (GET/POST/PUT/DELETE)
- **SSE (Server-Sent Events):** Recibe actualizaciones en tiempo real cuando cambia el estado de las mesas

## Configuración Paso a Paso

### Paso 1: Configurar Broker MQTT (Raspberry Pi)

```bash
# SSH a Raspberry Pi
ssh pi@100.81.10.77

# Instalar Mosquitto
sudo apt update
sudo apt install mosquitto mosquitto-clients

# Configurar para permitir conexiones remotas
sudo nano /etc/mosquitto/mosquitto.conf

# Agregar:
listener 1883
allow_anonymous true

# Reiniciar
sudo systemctl restart mosquitto
```

### Paso 2: Configurar Sistema de Visión

```bash
cd vision-artificial

# Editar config.py
# Cambiar BROKER_HOST a la IP correcta
BROKER_HOST = "100.81.10.77"

# Instalar dependencias
pip install paho-mqtt opencv-python ultralytics

# Ejecutar
python vision_system.py
```

### Paso 3: Configurar Backend

```bash
cd back-end

# Editar app/services/mqtt_service.py
# Cambiar BROKER_HOST
BROKER_HOST = "100.81.10.77"

# Iniciar backend
uvicorn app.main:app --reload
```

### Paso 4: Verificar Funcionamiento

1. **Iniciar broker MQTT** (Raspberry Pi)
2. **Iniciar backend** (se suscribe automáticamente)
3. **Iniciar sistema de visión** (publica detecciones)
4. **Verificar logs:**
   - Backend debería mostrar: `[OK] Backend conectado al broker MQTT`
   - Visión debería mostrar: `✓ Conectado al broker MQTT`
   - Cuando hay detecciones: `✓ Detecciones publicadas al broker MQTT`

## Debugging

### Ver mensajes MQTT en tiempo real:

```bash
# En cualquier máquina en la misma red
mosquitto_sub -h 100.81.10.77 -t "restaurant/#" -v
```

### Verificar que el broker está corriendo:

```bash
# En Raspberry Pi
sudo systemctl status mosquitto

# Verificar puerto abierto
netstat -tuln | grep 1883
```

### Logs del backend:

El backend imprime logs cuando:
- Se conecta al broker: `[OK] Backend conectado al broker MQTT`
- Recibe un mensaje: `[MENSAJE] Mensaje recibido`
- Actualiza una mesa: `[OK] X mesa(s) actualizada(s)`

## Ventajas de Esta Arquitectura

1. **Desacoplamiento:** El sistema de visión no necesita saber dónde está el backend
2. **Escalabilidad:** Puedes tener múltiples suscriptores (backend, dashboard, analytics)
3. **Resiliencia:** Si el backend cae, los mensajes se pueden guardar (con QoS y retain)
4. **Edge Computing:** La visión procesa localmente, solo envía resultados finales
5. **Asíncrono:** No bloquea el sistema de visión esperando respuestas HTTP

## Solución de Problemas Comunes

### Error: "No conectado al broker MQTT"
- Verificar que Mosquitto esté corriendo: `sudo systemctl status mosquitto`
- Verificar IP correcta en `config.py`
- Verificar firewall: `sudo ufw allow 1883`

### El backend no recibe mensajes
- Verificar que el backend se suscribió correctamente (ver logs de startup)
- Verificar que ambos usan la misma IP de broker
- Probar con `mosquitto_sub` para verificar que los mensajes llegan

### El sistema de visión no puede publicar
- Verificar conexión de red
- Verificar que `paho-mqtt` está instalado: `pip install paho-mqtt`
- Ver logs del sistema de visión para errores de conexión
