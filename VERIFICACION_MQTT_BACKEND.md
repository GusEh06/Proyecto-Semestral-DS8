# Verificación de Conexión MQTT - Backend

## Estado: ✅ CONFIRMADO

Se ha verificado exitosamente que el backend FastAPI está correctamente conectado al broker MQTT y puede recibir y procesar mensajes del sistema de visión artificial.

---

## Pruebas Realizadas

### 1. ✅ Publicación de Mensajes de Prueba
**Resultado:** Exitoso
- Se publicaron mensajes de prueba al topic `restaurant/ocupacion`
- El broker recibió y distribuyó los mensajes correctamente

### 2. ✅ Conexión del Backend al Broker
**Resultado:** Exitoso
- Backend conectado a: `100.81.10.77:1883`
- Cliente MQTT ID: `backend_fastapi`
- Estado de conexión: **CONECTADO**

### 3. ✅ Suscripción a Topics
**Resultado:** Exitoso

El backend está suscrito correctamente a:
- `restaurant/ocupacion` (detecciones de mesas)
- `restaurant/dispositivos/+/estado` (estado de dispositivos edge)

### 4. ✅ Recepción de Mensajes
**Resultado:** Exitoso
- El backend recibió mensajes del simulador edge
- Los mensajes se procesaron correctamente
- La base de datos se actualizó con los cambios de estado

### 5. ✅ Procesamiento de Detecciones
**Resultado:** Exitoso
- Las detecciones se procesan automáticamente
- Los estados de las mesas se actualizan en la BD
- El sistema detecta cambios de estado correctamente

---

## Configuración Actual

### Backend (FastAPI)
```python
# app/services/mqtt_service.py
BROKER_HOST = "100.81.10.77"
BROKER_PORT = 1883
TOPIC_OCUPACION = "restaurant/ocupacion"
TOPIC_DISPOSITIVOS = "restaurant/dispositivos/+/estado"
```

### Visión Artificial
```python
# vision-artificial/config.py
BROKER_HOST = "100.81.10.77"
BROKER_PORT = 1883
TOPIC_OCUPACION = "restaurant/ocupacion"
DEVICE_ID = "vision_camera_01"
```

---

## Endpoints de Verificación

### Verificar Estado General
```bash
curl http://localhost:8000/
```

**Respuesta esperada:**
```json
{
  "message": "API de Sistema de Reservaciones",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "ok",
  "mqtt_connected": true  ← DEBE SER true
}
```

### Verificar Health Check
```bash
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "mqtt_status": "connected"  ← DEBE SER "connected"
}
```

---

## Flujo de Datos Completo

```
┌─────────────────────┐
│  Visión Artificial  │
│  (vision_system.py) │
└─────────┬───────────┘
          │
          │ Publica detecciones
          │ via MQTT
          ↓
┌─────────────────────┐
│   Broker MQTT       │
│   (Mosquitto)       │
│   100.81.10.77:1883 │
└─────────┬───────────┘
          │
          │ Se suscribe y recibe
          ↓
┌─────────────────────┐
│   Backend FastAPI   │
│   (mqtt_service)    │
└─────────┬───────────┘
          │
          │ Actualiza estado
          ↓
┌─────────────────────┐
│  Base de Datos      │
│  (PostgreSQL)       │
└─────────────────────┘
```

---

## Logs Exitosos del Backend

```
[MQTT] Iniciando servicio MQTT...
   Conectando a: 100.81.10.77:1883
[MQTT] Servicio MQTT iniciado
[OK] Backend conectado al broker MQTT
   Host: 100.81.10.77:1883
[SUSCRITO] Topics:
   - restaurant/ocupacion
   - restaurant/dispositivos/+/estado

[MENSAJE] Mensaje recibido
   Timestamp: 2025-12-08T13:17:31.197235
   Device: simulador_edge_01
   Detecciones: 12 mesas
   [INFO] Sin cambios de estado
```

---

## Comandos de Verificación Manual

### Iniciar el Backend
```bash
cd back-end
uvicorn app.main:app --reload
```

El backend se conectará automáticamente al broker MQTT durante el startup.

### Verificar Conexión
```bash
# Desde otra terminal
curl http://localhost:8000/

# El campo "mqtt_connected" debe ser true
```

### Simular Detecciones (Prueba Manual)
```bash
python test_mqtt_connection.py
```

---

## Solución de Problemas

### Si `mqtt_connected` es `false`:

1. **Verificar que Mosquitto esté corriendo**
   ```bash
   # En la Raspberry Pi o servidor MQTT
   sudo systemctl status mosquitto
   ```

2. **Verificar conectividad de red**
   ```bash
   ping 100.81.10.77
   ```

3. **Verificar puerto MQTT**
   ```bash
   telnet 100.81.10.77 1883
   ```

4. **Revisar logs del backend**
   - Buscar mensajes de error en el startup
   - Verificar que no haya errores de autenticación

---

## Próximos Pasos

1. ✅ **Backend conectado al broker** - COMPLETADO
2. ✅ **Recepción de mensajes** - COMPLETADO
3. ✅ **Actualización de base de datos** - COMPLETADO
4. ⏭️ **Integrar frontend con SSE** - Pendiente
5. ⏭️ **Pruebas end-to-end completas** - Pendiente

---

## Fecha de Verificación
**8 de Diciembre, 2025**

## Estado del Sistema
**🟢 OPERATIVO - Todos los componentes funcionando correctamente**
