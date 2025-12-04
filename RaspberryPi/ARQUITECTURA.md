# 🏗️ ARQUITECTURA DEL SISTEMA - DIAGRAMA DETALLADO

## Flujo Completo de Comunicación

```
┌──────────────────────────────────────────────────────────────────────┐
│                        CAPA DE DETECCIÓN                             │
└──────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────┐
    │  💻 LAPTOP con YOLO v8          │
    │  ─────────────────────────────  │
    │  • Captura video de cámaras     │
    │  • Detecta personas en mesas    │
    │  • Calcula ocupación/vacío      │
    │  • Publica via MQTT             │
    └───────────────┬─────────────────┘
                    │
                    │ MQTT Publish
                    │ Topic: restaurante/mesas/vision
                    │
                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      CAPA DE MENSAJERÍA                              │
└──────────────────────────────────────────────────────────────────────┘

         ┌────────────────────────────────┐
         │   📡 MQTT BROKER (EMQX)        │
         │   ──────────────────────────   │
         │   Topics:                      │
         │   • restaurante/mesas/vision   │
         │   • restaurante/mesas/manual   │
         │   • restaurante/mesas/reservas │
         │   • restaurante/mesas/status   │
         └────────────┬───────────────────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
         ▼            ▼            ▼
    ┌────────┐  ┌─────────┐  ┌──────────┐
    │Dashboard│  │Frontend │  │Raspberry │
    │ Admin  │  │Clientes │  │   Pi     │
    └────────┘  └─────────┘  └──────────┘
         │            │            │
         │ Manual     │ Reservas   │ Local
         │ Updates    │            │ Updates
         │            │            │
         └────────────┴────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    CAPA DE PROCESAMIENTO                             │
└──────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────┐
    │  🤖 BROKER LISTENER (Python)                │
    │  ─────────────────────────────────────────  │
    │  restaurant_mqtt_broker.py                  │
    │                                             │
    │  Funciones:                                 │
    │  1️⃣  Escuchar mensajes MQTT                 │
    │  2️⃣  Validar confianza de detección         │
    │  3️⃣  Verificar estado de reservas           │
    │  4️⃣  Aplicar lógica de negocio              │
    │  5️⃣  Actualizar base de datos               │
    │  6️⃣  Publicar confirmaciones                │
    │  7️⃣  Liberar reservas expiradas             │
    └──────────────────┬──────────────────────────┘
                       │
                       │ SQL Queries
                       │ INSERT/UPDATE
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     CAPA DE PERSISTENCIA                             │
└──────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────┐
    │  🗄️  PostgreSQL en la Nube                  │
    │  ───────────────────────────────────────    │
    │  (AWS RDS / Google Cloud SQL / DO)          │
    │                                             │
    │  📋 Tabla: mesas                            │
    │  ├── id_mesa                                │
    │  ├── numero_mesa                            │
    │  ├── estado (disponible/ocupada/reservada)  │
    │  ├── capacidad                              │
    │  ├── reservada (boolean)                    │
    │  ├── id_reserva_actual                      │
    │  ├── vision_detected_at                     │
    │  └── updated_at                             │
    │                                             │
    │  📋 Tabla: reservas                         │
    │  ├── id_reserva                             │
    │  ├── id_mesa                                │
    │  ├── nombre_cliente                         │
    │  ├── telefono                               │
    │  ├── fecha_reserva                          │
    │  ├── hora_reserva                           │
    │  ├── estado_reserva                         │
    │  └── num_personas                           │
    └─────────────────────────────────────────────┘
```

## 🔄 FLUJOS DE TRABAJO PRINCIPALES

### FLUJO 1: Detección de Ocupación (Visión → BD)

```
1. 🎥 Cámara captura frame
        ↓
2. 🧠 YOLO procesa imagen
        ↓
3. ✅ Detecta personas (confianza: 0.95)
        ↓
4. 📤 Publica MQTT:
   {
     "mesa_id": 3,
     "estado": "ocupada",
     "confianza": 0.95
   }
        ↓
5. 📡 Broker MQTT recibe mensaje
        ↓
6. 🤖 Listener procesa:
   - ¿Confianza > 0.70? ✅
   - ¿Mesa tiene reserva? ❌
        ↓
7. 💾 UPDATE mesas SET estado='ocupada' WHERE id_mesa=3
        ↓
8. 📢 Publica confirmación en 'status'
        ↓
9. 🖥️ Dashboard actualiza UI en tiempo real
```

### FLUJO 2: Cliente Hace Reserva (Frontend → BD)

```
1. 📱 Cliente selecciona mesa en app
        ↓
2. 📝 Completa formulario de reserva
        ↓
3. 📤 Frontend publica MQTT:
   {
     "mesa_id": 5,
     "cliente": {
       "nombre": "Juan Pérez",
       "fecha": "2024-01-20",
       "hora": "19:00"
     }
   }
        ↓
4. 📡 Broker MQTT recibe
        ↓
5. 🤖 Listener verifica:
   - ¿Mesa disponible? ✅
   - ¿Fecha válida? ✅
        ↓
6. 💾 INSERT INTO reservas (...)
        ↓
7. 💾 UPDATE mesas SET reservada=TRUE, estado='reservada'
        ↓
8. 📧 Publica confirmación con ID de reserva
        ↓
9. 📱 App muestra: "Reserva #123 confirmada"
```

### FLUJO 3: Conflicto Visión vs Reserva

```
1. 📋 Mesa 5 tiene reserva para 19:00
        ↓
2. ⏰ Son las 18:50, mesa aún vacía
        ↓
3. 🎥 YOLO detecta: "mesa_5: disponible"
        ↓
4. 📤 Publica actualización
        ↓
5. 🤖 Listener verifica:
   query = "SELECT reservada FROM mesas WHERE id_mesa=5"
   result = TRUE
        ↓
6. 🔒 BLOQUEADO: "Mesa tiene reserva activa"
        ↓
7. 📝 Log: "No se actualiza desde visión"
        ↓
8. ✅ Mesa permanece como 'reservada'
```

### FLUJO 4: Liberación Automática de Reservas

```
1. ⏰ Cada 5 minutos, Listener ejecuta:
   check_and_release_expired_reservations()
        ↓
2. 🔍 Query busca reservas expiradas:
   SELECT * FROM reservas 
   WHERE (fecha_reserva + hora_reserva + '2 hours') < NOW()
        ↓
3. 💾 UPDATE mesas SET reservada=FALSE, estado='disponible'
        ↓
4. 💾 UPDATE reservas SET estado_reserva='expirada'
        ↓
5. 📢 Publica cambio de estado
        ↓
6. 🖥️ Dashboard muestra mesa como disponible
```

## 📊 ESTADOS POSIBLES DE UNA MESA

```
┌─────────────────────────────────────────────────┐
│                ESTADOS DE MESA                  │
├─────────────────────────────────────────────────┤
│                                                 │
│  🟢 DISPONIBLE                                  │
│     • Sin ocupantes                             │
│     • Sin reserva activa                        │
│     • Puede recibir clientes                    │
│                                                 │
│  🔴 OCUPADA                                     │
│     • Detectada con personas                    │
│     • Sin reserva (walk-in)                     │
│     • YOLO confirma ocupación                   │
│                                                 │
│  🟡 RESERVADA                                   │
│     • Tiene reserva activa                      │
│     • No puede ser modificada por visión        │
│     • Solo admin/sistema puede cambiar          │
│                                                 │
│  ⚪ MANTENIMIENTO                               │
│     • Fuera de servicio                         │
│     • Requiere limpieza/reparación              │
│     • No disponible para reservas               │
│                                                 │
└─────────────────────────────────────────────────┘
```

## 🔐 SEGURIDAD Y VALIDACIONES

### Validaciones del Listener

```python
# 1. Validación de Confianza
if confianza < 0.70:
    logger.warning("Confianza baja, ignorando")
    return

# 2. Validación de Reserva
mesa_info = get_table_info(mesa_id)
if mesa_info['reservada'] and source == 'vision':
    logger.info("Mesa reservada, no actualizar desde visión")
    return

# 3. Validación de Disponibilidad (para reservas)
if mesa_info and mesa_info['reservada']:
    response = {'error': 'Mesa ya reservada'}
    return

# 4. Validación de Conexión BD
if not ensure_db_connection():
    logger.error("Sin conexión a BD")
    return
```

## 📈 MÉTRICAS Y MONITOREO

```
Dashboard debe mostrar:

┌─────────────────────────────────────┐
│  📊 ESTADO DEL RESTAURANTE          │
├─────────────────────────────────────┤
│  Mesas Disponibles:    5 🟢         │
│  Mesas Ocupadas:       3 🔴         │
│  Mesas Reservadas:     2 🟡         │
│  ─────────────────────────────────  │
│  Tasa Ocupación:      50%           │
│  Reservas Hoy:        12            │
│  Última Actualización: 14:32        │
└─────────────────────────────────────┘

Logs del Sistema:
✅ Mesa 3 actualizada a 'ocupada' (vision)
🔒 Mesa 5 tiene reserva activa. No actualizada.
🎉 Reserva #124 confirmada para mesa 8
🔓 2 reservas expiradas liberadas
```

## 🛠️ COMPONENTES TÉCNICOS

```
┌──────────────────────────────────────┐
│  TECNOLOGÍAS UTILIZADAS              │
├──────────────────────────────────────┤
│                                      │
│  Backend:                            │
│  • Python 3.8+                       │
│  • paho-mqtt (cliente MQTT)          │
│  • psycopg2 (PostgreSQL driver)      │
│                                      │
│  Base de Datos:                      │
│  • PostgreSQL 12+                    │
│  • Triggers automáticos              │
│  • Índices optimizados               │
│                                      │
│  Mensajería:                         │
│  • MQTT Protocol                     │
│  • QoS 0/1 (configurable)            │
│  • Retained messages                 │
│                                      │
│  Visión Artificial:                  │
│  • YOLOv8                            │
│  • OpenCV (cv2)                      │
│  • Ultralytics library               │
│                                      │
│  Frontend (Tu parte):                │
│  • React / Astro / Next.js           │
│  • MQTT.js (cliente web)             │
│  • WebSockets                        │
│                                      │
└──────────────────────────────────────┘
```

## 🚀 DEPLOYMENT

```
OPCIÓN 1: Servidor Único (Pequeña Escala)
┌─────────────────────────────────┐
│  VPS (DigitalOcean/Linode)      │
│  ─────────────────────────────  │
│  • MQTT Broker (Mosquitto)      │
│  • Python Listener Service      │
│  • PostgreSQL Database          │
│  • Nginx (Frontend)             │
└─────────────────────────────────┘

OPCIÓN 2: Cloud Distribuido (Producción)
┌─────────────────────────────────┐
│  AWS/GCP/Azure                  │
├─────────────────────────────────┤
│  • RDS/Cloud SQL (PostgreSQL)   │
│  • EC2/Compute Engine (Listener)│
│  • IoT Core (MQTT Managed)      │
│  • S3/Cloud Storage (Logs)      │
│  • Lambda/Functions (Serverless)│
└─────────────────────────────────┘

OPCIÓN 3: Híbrido (Local + Cloud)
┌─────────────────────────────────┐
│  Local (Restaurante):           │
│  • Raspberry Pi (YOLO)          │
│  • Router (VPN)                 │
│                                 │
│  Cloud:                         │
│  • Managed PostgreSQL           │
│  • MQTT Broker                  │
│  • Listener Service             │
└─────────────────────────────────┘
```

---

Este archivo proporciona una visión completa y visual de cómo funciona todo el sistema!
