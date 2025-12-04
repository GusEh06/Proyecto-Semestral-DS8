# 🍽️ Sistema de Gestión de Restaurante con MQTT y Visión Artificial

Sistema completo de gestión de mesas de restaurante que integra:
- 🎥 Visión artificial (YOLO) para detección de ocupación
- 📡 Broker MQTT para comunicación en tiempo real
- 🗄️ Base de datos PostgreSQL en la nube
- 🖥️ Dashboard de administración
- 📱 Frontend para clientes (reservas)

---

## 📋 Tabla de Contenidos

1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Componentes](#componentes)
3. [Instalación](#instalación)
4. [Configuración](#configuración)
5. [Uso](#uso)
6. [Flujo de Trabajo](#flujo-de-trabajo)
7. [Estructura de Mensajes](#estructura-de-mensajes)
8. [Troubleshooting](#troubleshooting)

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐
│   Laptop YOLO   │ ──┐
│  (Detección de  │   │
│   ocupación)    │   │
└─────────────────┘   │
                      │  MQTT Topics
┌─────────────────┐   │  - vision_updates
│   Dashboard     │ ──┤  - manual_updates  
│   Admin Web     │   │  - reservations
└─────────────────┘   │  - status_response
                      │
┌─────────────────┐   │
│  Frontend de    │ ──┘
│   Clientes      │
│  (Reservas)     │
└─────────────────┘
         │
         │
         ▼
┌─────────────────────────────────────┐
│      MQTT Broker (EMQX/Mosquitto)   │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   🤖 SCRIPT BROKER LISTENER         │
│   (restaurant_mqtt_broker.py)       │
│                                     │
│   - Escucha topics MQTT             │
│   - Valida mensajes                 │
│   - Gestiona lógica de negocio     │
│   - Actualiza base de datos        │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   PostgreSQL en la Nube             │
│   (AWS RDS / Google Cloud SQL /     │
│    DigitalOcean / Otro)             │
│                                     │
│   Tablas:                           │
│   - mesas                           │
│   - reservas                        │
└─────────────────────────────────────┘
```

---

## 🧩 Componentes

### 1. **Sistema de Visión (YOLO)**
- Detecta personas en mesas usando cámara
- Determina si mesa está ocupada o disponible
- Envía actualizaciones via MQTT

### 2. **Broker MQTT**
- Servidor de mensajería (EMQX, Mosquitto, etc.)
- Maneja comunicación entre componentes
- Topics específicos para cada tipo de mensaje

### 3. **Listener Script** (⭐ Este proyecto)
- **Archivo**: `restaurant_mqtt_broker.py`
- **Función**: Escucha MQTT y actualiza base de datos
- **Características**:
  - Valida mensajes entrantes
  - Respeta reservas activas
  - Libera reservas expiradas automáticamente
  - Maneja actualizaciones manuales del dashboard
  - Procesa nuevas reservas

### 4. **Base de Datos PostgreSQL**
- Almacena estado de mesas
- Gestiona reservas
- Triggers y funciones automáticas
- Vistas optimizadas para consultas

### 5. **Dashboard Admin** (Tu frontend)
- Visualiza estado en tiempo real
- Permite actualizaciones manuales
- Gestiona reservas

### 6. **Frontend Clientes** (Tu frontend)
- Sistema de reservas online
- Consulta disponibilidad
- Envía reservas via MQTT

---

## 📦 Instalación

### Requisitos Previos

- Python 3.8+
- PostgreSQL 12+
- Acceso a un broker MQTT (o instalar uno localmente)

### Paso 1: Clonar el Proyecto

```bash
# Descargar los archivos del proyecto
# (Coloca todos los archivos en una carpeta)
```

### Paso 2: Instalar Dependencias

```bash
# Crear entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 3: Configurar Base de Datos

```bash
# Conectar a PostgreSQL
psql -U postgres -h tu-servidor.com

# Crear base de datos
CREATE DATABASE restaurante_db;

# Ejecutar el esquema
psql -U postgres -h tu-servidor.com -d restaurante_db -f database_schema.sql
```

### Paso 4: Configurar Variables de Entorno

```bash
# Copiar archivo de configuración
cp config.env .env

# Editar con tus credenciales
nano .env
```

Actualiza los valores en `.env`:

```ini
DB_HOST=tu-servidor-cloud.com
DB_NAME=restaurante_db
DB_USER=tu_usuario
DB_PASSWORD=tu_password

MQTT_BROKER=broker.emqx.io
MQTT_PORT=1883
```

---

## ⚙️ Configuración

### Configuración del Broker MQTT

#### Opción 1: Broker Público (Desarrollo)
```python
MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883
```

#### Opción 2: Broker Local (Mosquitto)
```bash
# Instalar Mosquitto
sudo apt-get install mosquitto mosquitto-clients

# Iniciar servicio
sudo systemctl start mosquitto

# En el código:
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
```

#### Opción 3: Broker Privado con Autenticación
```python
MQTT_BROKER = 'tu-broker-privado.com'
MQTT_PORT = 1883
MQTT_USERNAME = 'restaurant_user'
MQTT_PASSWORD = 'tu_password'
```

### Configuración de PostgreSQL

Edita las credenciales en el script o usa variables de entorno:

```python
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'restaurante_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': int(os.getenv('DB_PORT', 5432))
}
```

---

## 🚀 Uso

### Iniciar el Broker Listener

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar el script principal
python restaurant_mqtt_broker.py
```

Verás algo como:
```
🚀 Iniciando Restaurant MQTT Broker...
✅ Conectado a PostgreSQL en la nube
✅ Conectado al broker MQTT
📡 Suscrito a: restaurante/mesas/vision
📡 Suscrito a: restaurante/mesas/manual
📡 Suscrito a: restaurante/mesas/reservas
✅ Broker iniciado y escuchando mensajes...
```

### Probar con el Simulador

En otra terminal:

```bash
# Ejecutar simulador de visión
python vision_simulator.py
```

Opciones del simulador:
1. **Modo Interactivo**: Control manual de cada mesa
2. **Modo Demo**: Secuencia predefinida de actualizaciones
3. **Modo Automático**: Actualizaciones aleatorias continuas

---

## 🔄 Flujo de Trabajo

### Escenario 1: Detección por Visión Artificial

```
1. Laptop YOLO detecta persona sentándose
   ↓
2. Publica mensaje a 'restaurante/mesas/vision'
   {
     "mesa_id": 3,
     "estado": "ocupada",
     "confianza": 0.95
   }
   ↓
3. Broker Listener recibe mensaje
   ↓
4. Verifica si mesa tiene reserva activa
   ↓
5. Si NO tiene reserva:
   - Actualiza BD: SET estado = 'ocupada'
   - Publica confirmación en 'status_response'
   ↓
6. Dashboard actualiza en tiempo real
```

### Escenario 2: Cliente Hace Reserva

```
1. Cliente selecciona mesa en frontend
   ↓
2. Frontend publica a 'restaurante/mesas/reservas'
   {
     "mesa_id": 5,
     "cliente": {
       "nombre": "Juan Pérez",
       "telefono": "+507 6123-4567",
       "fecha": "2024-01-20",
       "hora": "19:00:00"
     }
   }
   ↓
3. Broker Listener recibe reserva
   ↓
4. Verifica disponibilidad de mesa
   ↓
5. Crea registro en tabla 'reservas'
   ↓
6. Actualiza mesa: SET reservada = TRUE
   ↓
7. Publica confirmación con reserva_id
   ↓
8. Frontend muestra confirmación al cliente
```

### Escenario 3: Sistema de Visión vs Reserva

```
1. Mesa 5 tiene reserva para las 19:00
   ↓
2. A las 18:50, YOLO detecta mesa vacía
   ↓
3. Publica: {"mesa_id": 5, "estado": "disponible"}
   ↓
4. Broker Listener verifica:
   - mesa_info['reservada'] == TRUE
   - source == 'vision'
   ↓
5. 🔒 NO actualiza la mesa
   ↓
6. Log: "Mesa 5 tiene reserva activa. No se actualiza desde visión."
```

---

## 📨 Estructura de Mensajes

### Topic: `restaurante/mesas/vision`
**Desde**: Sistema YOLO  
**Hacia**: Broker Listener

```json
{
  "mesa_id": 1,
  "estado": "ocupada",
  "confianza": 0.95,
  "timestamp": "2024-01-15T14:30:00",
  "detector": "YOLO-v8",
  "personas_detectadas": 2
}
```

### Topic: `restaurante/mesas/manual`
**Desde**: Dashboard Admin  
**Hacia**: Broker Listener

```json
{
  "mesa_id": 3,
  "estado": "disponible",
  "usuario": "admin@restaurante.com",
  "razon": "Cliente pagó y se fue"
}
```

### Topic: `restaurante/mesas/reservas`
**Desde**: Frontend Clientes  
**Hacia**: Broker Listener

```json
{
  "mesa_id": 5,
  "cliente": {
    "nombre": "María González",
    "telefono": "+507 6123-4567",
    "email": "maria@example.com",
    "num_personas": 4,
    "fecha": "2024-01-20",
    "hora": "19:00:00"
  }
}
```

### Topic: `restaurante/mesas/status`
**Desde**: Broker Listener  
**Hacia**: Todos los suscriptores

```json
{
  "mesa_id": 1,
  "estado": "ocupada",
  "updated": true,
  "timestamp": "2024-01-15T14:30:05"
}
```

---

## 🛠️ Troubleshooting

### Problema: No se conecta a PostgreSQL

```bash
# Verificar conectividad
psql -U postgres -h tu-servidor.com -d restaurante_db

# Verificar que el servidor acepta conexiones remotas
# Editar postgresql.conf:
listen_addresses = '*'

# Editar pg_hba.conf:
host    all    all    0.0.0.0/0    md5
```

### Problema: No se conecta al broker MQTT

```bash
# Probar conexión con mosquitto_pub
mosquitto_pub -h broker.emqx.io -t test -m "hello"

# Verificar firewall
sudo ufw allow 1883/tcp
```

### Problema: Mensajes no se reciben

```bash
# Monitorear todos los topics
mosquitto_sub -h broker.emqx.io -t 'restaurante/#' -v

# Verificar logs
tail -f restaurant_broker.log
```

### Problema: Reservas no se liberan automáticamente

```sql
-- Ejecutar manualmente
SELECT liberar_reservas_expiradas();

-- Verificar reservas activas
SELECT * FROM reservas_activas;
```

---

## 📊 Monitoreo y Logs

### Ver logs en tiempo real

```bash
tail -f restaurant_broker.log
```

### Consultas útiles en PostgreSQL

```sql
-- Estado actual del restaurante
SELECT * FROM get_restaurant_status();

-- Mesas disponibles
SELECT * FROM mesas_disponibles;

-- Reservas del día
SELECT * FROM reservas_activas 
WHERE fecha_reserva = CURRENT_DATE;

-- Estadísticas
SELECT 
    COUNT(*) FILTER (WHERE estado = 'disponible') as disponibles,
    COUNT(*) FILTER (WHERE estado = 'ocupada') as ocupadas,
    COUNT(*) FILTER (WHERE estado = 'reservada') as reservadas
FROM mesas;
```

---

## 🔐 Seguridad

### Recomendaciones para Producción

1. **Usar broker MQTT privado con SSL/TLS**
```python
MQTT_USE_SSL = True
client.tls_set(ca_certs="/path/to/ca.crt")
```

2. **Autenticación MQTT**
```python
client.username_pw_set("usuario", "password_fuerte")
```

3. **Conexión segura a PostgreSQL**
```python
conn = psycopg2.connect(
    ...,
    sslmode='require'
)
```

4. **Variables de entorno para credenciales**
```bash
# Nunca hardcodear contraseñas en el código
export DB_PASSWORD="mi_password_seguro"
```

5. **Rate limiting en el broker**
```python
# Limitar frecuencia de actualizaciones por mesa
```

---

## 📝 Notas Adicionales

- El sistema verifica reservas expiradas cada 5 minutos
- Las reservas se liberan automáticamente 2 horas después de la hora reservada
- El umbral de confianza para YOLO es configurable (default: 0.70)
- El broker reconecta automáticamente si se pierde la conexión

---

## 🤝 Integración con tu Frontend

### Ejemplo React/Astro para Dashboard

```javascript
import mqtt from 'mqtt';

const client = mqtt.connect('ws://broker.emqx.io:8083/mqtt');

client.on('connect', () => {
  client.subscribe('restaurante/mesas/status');
});

client.on('message', (topic, message) => {
  const data = JSON.parse(message.toString());
  // Actualizar estado de la mesa en UI
  updateTableUI(data.mesa_id, data.estado);
});
```

### Ejemplo para enviar actualización manual

```javascript
const actualizarMesa = (mesaId, estado) => {
  const mensaje = {
    mesa_id: mesaId,
    estado: estado,
    usuario: 'admin@restaurante.com'
  };
  
  client.publish(
    'restaurante/mesas/manual',
    JSON.stringify(mensaje)
  );
};
```

---

## 📧 Contacto y Soporte

Para preguntas o problemas, consulta los logs o revisa la documentación de cada componente.

---

**¡Sistema listo para producción! 🚀**
