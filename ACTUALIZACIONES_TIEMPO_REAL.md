# 📡 Sistema de Actualizaciones en Tiempo Real

Este documento explica cómo funciona el sistema de actualizaciones automáticas de mesas usando **Server-Sent Events (SSE)**.

## 🎯 ¿Qué hace?

Antes tenías que hacer clic en el botón "Actualizar" para ver cambios en las mesas. Ahora:
- ✅ Las mesas se actualizan **automáticamente** cuando cambian
- ✅ No necesitas hacer clic en nada
- ✅ Múltiples usuarios ven los cambios **al instante**

---

## 🔄 Flujo de Datos

```
┌─────────────────┐         ┌──────────────┐         ┌─────────────┐
│  Raspberry Pi   │  MQTT   │   Backend    │   SSE   │  Frontend   │
│  (Edge Device)  │────────>│  (FastAPI)   │────────>│  (React)    │
└─────────────────┘         └──────────────┘         └─────────────┘
      Sensores                  Python                   Browser
```

### Paso a paso:

1. **Raspberry Pi detecta personas** → Envía mensaje MQTT
2. **Backend recibe MQTT** → Actualiza base de datos
3. **Backend emite evento SSE** → Envía a todos los clientes conectados
4. **Frontend recibe evento** → Actualiza UI automáticamente

---

## 🛠️ Componentes del Sistema

### 1️⃣ Backend: Endpoint SSE (`back-end/app/routers/mesas.py`)

**Ubicación:** Líneas 15-136

#### ¿Qué hace?
Crea un endpoint que mantiene una conexión abierta con cada cliente:

```python
@router.get("/stream")
async def stream_mesas(request: Request):
    """
    Endpoint que transmite actualizaciones en tiempo real.
    URL: GET /api/v1/mesas/stream
    """
    return StreamingResponse(event_generator(request), ...)
```

#### Componentes clave:

- **`event_queues`**: Lista global de colas. Cada cliente conectado tiene su propia cola.
- **`event_generator()`**: Generador asíncrono que envía eventos al cliente.
- **`broadcast_mesa_update()`**: Función que envía eventos a TODOS los clientes.

#### ¿Cómo funciona la cola?
```python
# Cada cliente obtiene su propia cola
queue = asyncio.Queue()
event_queues.append(queue)

# El cliente espera eventos de su cola
event = await queue.get()

# Enviar al cliente en formato SSE
yield f"data: {json.dumps(event)}\n\n"
```

---

### 2️⃣ Backend: Servicio MQTT (`back-end/app/services/mqtt_service.py`)

**Ubicación:** Líneas 178-218

#### ¿Qué hace?
Cuando MQTT actualiza las mesas, emite un evento SSE:

```python
def actualizar_estado_mesas(self, detecciones: list):
    # ... actualizar base de datos ...

    if mesas_actualizadas > 0:
        db.commit()
        # 🔴 NUEVO: Emitir evento SSE
        self.emit_mesa_update_event(db)
```

#### `emit_mesa_update_event()` hace:
1. Lee todas las mesas de la base de datos
2. Convierte a formato JSON
3. Llama a `broadcast_mesa_update(mesas_data)`
4. Los clientes conectados reciben el evento instantáneamente

---

### 3️⃣ Frontend: Componente React (`front-end/src/components/react/admin/MesasGrid.tsx`)

**Ubicación:** Líneas 26-80

#### ¿Qué hace?
Se conecta al endpoint SSE y escucha eventos:

```typescript
useEffect(() => {
  // Carga inicial
  loadMesas();

  // Conectar al stream SSE
  const API_BASE = 'http://localhost:8000';
  const eventSource = new EventSource(`${API_BASE}/api/v1/mesas/stream`);

  // Cuando llega un mensaje
  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'mesa_update') {
      setMesas(data.data); // ✨ Actualiza el estado automáticamente
    }
  };

  // Cleanup al desmontar
  return () => eventSource.close();
}, []);
```

#### EventSource API:
- **`onopen`**: Se ejecuta cuando la conexión se establece
- **`onmessage`**: Se ejecuta cuando llega un evento del servidor
- **`onerror`**: Se ejecuta si hay un error (reconexión automática)
- **`close()`**: Cierra la conexión

---

## 📊 Formato de Eventos SSE

### Evento de Conexión
```json
{
  "type": "connected",
  "message": "Conectado al stream de mesas"
}
```

### Evento de Actualización de Mesas
```json
{
  "type": "mesa_update",
  "data": [
    {
      "id_mesa": 1,
      "numero_mesa": 1,
      "estado": "ocupada",
      "id_tipo_mesa": 2,
      "tipo_mesa": {
        "id_tipo_mesa": 2,
        "descripcion": "Mesa para 4 personas",
        "cantidad_sillas": 4
      }
    }
  ],
  "timestamp": "1234567890.123"
}
```

---

## 🔍 Características Técnicas

### ✅ Ventajas de SSE sobre WebSockets

| Característica | SSE | WebSockets |
|----------------|-----|------------|
| Dirección | Unidireccional (servidor → cliente) | Bidireccional |
| Protocolo | HTTP | WS/WSS |
| Reconexión | Automática | Manual |
| Complejidad | Baja | Media-Alta |
| Uso en este caso | ✅ Perfecto | ⚠️ Sobrekill |

**¿Por qué SSE?**
- Solo necesitamos enviar datos del servidor al cliente (no al revés)
- Reconexión automática si se cae la conexión
- Más simple de implementar
- Compatible con proxies HTTP estándar

### 🔄 Reconexión Automática

EventSource reintenta automáticamente si se pierde la conexión:
- Espera 3 segundos
- Intenta reconectar
- Si falla, espera 6 segundos
- Intenta de nuevo...
- Hasta que se reconecta o se cierra manualmente

### 💓 Heartbeat (Keep-Alive)

Cada 30 segundos enviamos un heartbeat para mantener la conexión viva:
```python
except asyncio.TimeoutError:
    # Enviar heartbeat cada 30s
    yield f": heartbeat\n\n"
```

Esto evita que proxies o firewalls cierren la conexión por inactividad.

---

## 🚀 Cómo Probar

### 1. Iniciar Backend
```bash
cd back-end
uvicorn app.main:app --reload
```

### 2. Iniciar Frontend
```bash
cd front-end
npm run dev
```

### 3. Abrir Página de Mesas
Ir a: `http://localhost:4321/admin/mesas`

### 4. Ver la Conexión en la Consola del Navegador
Abre las DevTools (F12) y verás:
```
[SSE] ✅ Conectado al servidor en tiempo real
[SSE] 📡 Conectado al stream de mesas
```

### 5. Simular Cambio de Mesa

**Opción A: Usar el simulador de Raspberry Pi**
```bash
cd RaspberryPi
python simulador_edge.py
```

**Opción B: Actualizar manualmente desde la UI**
- Haz clic en una mesa
- Cambia su estado
- Todas las ventanas conectadas verán el cambio

### 6. Abrir Múltiples Pestañas
Abre `http://localhost:4321/admin/mesas` en 2-3 pestañas.
Cambia el estado de una mesa en una pestaña.
Verás cómo se actualiza en **todas** las pestañas automáticamente.

---

## 🐛 Debugging

### Ver Logs del Backend
Los logs de SSE aparecen en la consola de FastAPI:
```
[MQTT] Servicio MQTT iniciado
[OK] 2 mesa(s) actualizada(s):
   Mesa 1: disponible -> ocupada (2 persona(s) detectada(s))
   Mesa 3: ocupada -> disponible (Sin personas ni reservación)
[SSE] Evento emitido a clientes conectados
```

### Ver Logs del Frontend
Abre la consola del navegador (F12):
```javascript
[SSE] ✅ Conectado al servidor en tiempo real
[SSE] 📡 Conectado al stream de mesas
[SSE] 🔄 Mesas actualizadas automáticamente [Array]
```

### Verificar Conexión en Network Tab
1. Abre DevTools → Network
2. Filtra por "stream"
3. Verás una conexión permanente con `Type: eventsource`
4. Haz clic para ver los mensajes recibidos

---

## ⚙️ Configuración

### Variables de Entorno

**Backend** (`back-end/app/services/mqtt_service.py`)
```python
BROKER_HOST = "192.168.40.9"  # IP de tu Raspberry Pi
BROKER_PORT = 1883
TOPIC_OCUPACION = "restaurant/ocupacion"
```

**Frontend** (`front-end/.env`)
```env
PUBLIC_API_URL=http://localhost:8000
```

---

## 🔒 Consideraciones de Seguridad

### Actualmente:
- ❌ El endpoint SSE es **público** (no requiere autenticación)
- ⚠️ Cualquiera puede conectarse y ver las actualizaciones

### Para Producción:
Si necesitas proteger el endpoint, puedes agregar autenticación:

```python
@router.get("/stream")
async def stream_mesas(
    request: Request,
    current_user: UsuarioAdmin = Depends(get_current_user)  # ⬅️ Agregar esto
):
    # ...
```

Pero necesitarías enviar el token en la URL:
```javascript
const token = getToken();
const eventSource = new EventSource(
  `${API_BASE}/api/v1/mesas/stream?token=${token}`
);
```

---

## 📈 Escalabilidad

### ¿Cuántos clientes puede soportar?

**Configuración actual:**
- Cada cliente = 1 conexión SSE
- FastAPI con uvicorn puede manejar ~1000 conexiones simultáneas
- Para este proyecto (restaurante): **más que suficiente**

### Si necesitas más:
- Usar Redis Pub/Sub para distribuir eventos entre múltiples servidores
- Usar nginx con soporte de streaming
- Implementar límite de reconexiones

---

## 🎓 Conceptos Clave para Entender

### 1. Server-Sent Events (SSE)
Protocolo HTTP que permite al servidor enviar datos al cliente sin que el cliente tenga que pedirlos constantemente.

**Antes (Polling):**
```
Cliente: "¿Hay cambios?"
Servidor: "No"
[Espera 10 segundos]
Cliente: "¿Hay cambios?"
Servidor: "No"
[Espera 10 segundos]
Cliente: "¿Hay cambios?"
Servidor: "Sí, aquí están"
```

**Ahora (SSE):**
```
Cliente: "Quiero recibir actualizaciones"
Servidor: "OK, te mantendré informado"
[Pasa el tiempo...]
Servidor: "¡Hay cambios! Aquí están"
Cliente: "¡Recibido!"
```

### 2. Colas Asíncronas (asyncio.Queue)
Estructura de datos que permite comunicación entre tareas asíncronas:
```python
# Productor (broadcast_mesa_update)
queue.put_nowait(event)

# Consumidor (event_generator)
event = await queue.get()
```

### 3. Generadores Asíncronos
Funciones que pueden pausar y reanudar su ejecución:
```python
async def event_generator():
    while True:
        event = await queue.get()  # Espera aquí
        yield f"data: {event}\n\n"  # Envía y pausa
```

---

## 📚 Referencias

- [MDN: Using Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)
- [FastAPI: StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [MQTT Protocol](https://mqtt.org/)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)

---

## ✨ Resumen

### Backend:
1. ✅ Endpoint SSE en `/api/v1/mesas/stream`
2. ✅ Sistema de colas para distribuir eventos
3. ✅ Integración con MQTT para detectar cambios
4. ✅ Broadcast automático a todos los clientes

### Frontend:
1. ✅ Conexión SSE con `EventSource`
2. ✅ Actualización automática del estado
3. ✅ Indicador visual de conexión
4. ✅ Reconexión automática en caso de error
5. ✅ Botón de actualización manual como fallback

### Resultado:
🎉 **Actualizaciones en tiempo real sin necesidad de hacer clic en "Actualizar"**
