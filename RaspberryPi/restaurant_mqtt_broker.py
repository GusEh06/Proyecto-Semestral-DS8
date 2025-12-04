"""
MQTT Broker Listener - Sistema de Gestión de Mesas de Restaurante
==================================================================
Este script actúa como puente entre:
- Sistema de visión artificial (YOLO) que detecta ocupación de mesas
- Base de datos PostgreSQL en la nube
- Dashboard de administración
- Frontend de clientes para reservas

Flujo de trabajo:
1. Escucha mensajes MQTT del sistema de visión (laptop con YOLO)
2. Procesa el estado de las mesas (ocupada/disponible)
3. Actualiza la base de datos PostgreSQL en la nube
4. Respeta las reservas activas (no sobrescribe mesas reservadas)
"""

import paho.mqtt.client as mqtt
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import time

# ==================== CONFIGURACIÓN ====================

# Configuración del Broker MQTT
MQTT_CONFIG = {
    'broker': 'broker.emqx.io',  # Broker público (cambiar a tu broker privado)
    'port': 1883,
    'username': None,  # Agregar si tu broker requiere autenticación
    'password': None,
    'client_id': 'restaurant_cloud_listener',
    'keepalive': 60
}

# Topics MQTT
TOPICS = {
    'vision_updates': 'restaurante/mesas/vision',      # Mensajes del sistema de visión
    'manual_updates': 'restaurante/mesas/manual',      # Actualizaciones manuales del dashboard
    'reservations': 'restaurante/mesas/reservas',      # Nuevas reservas
    'status_response': 'restaurante/mesas/status'      # Respuestas de estado
}

# Configuración de la Base de Datos PostgreSQL en la Nube
DB_CONFIG = {
    'host': 'tu-servidor-cloud.com',  # Ejemplo: AWS RDS, Google Cloud SQL, DigitalOcean
    'database': 'restaurante_db',
    'user': 'admin_user',
    'password': 'secure_password',
    'port': 5432
}

# ==================== CONFIGURACIÓN DE LOGGING ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('restaurant_broker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== CLASE PRINCIPAL ====================

class RestaurantMQTTBroker:
    """
    Broker MQTT que gestiona la comunicación entre el sistema de visión,
    la base de datos en la nube y las interfaces de usuario.
    """
    
    def __init__(self):
        """Inicializa el broker y las conexiones"""
        self.mqtt_client = None
        self.db_connection = None
        self.is_connected = False
        
    # ==================== CONEXIÓN A BASE DE DATOS ====================
    
    def connect_database(self) -> bool:
        """
        Establece conexión con la base de datos PostgreSQL en la nube
        
        Returns:
            bool: True si la conexión fue exitosa
        """
        try:
            self.db_connection = psycopg2.connect(
                host=DB_CONFIG['host'],
                database=DB_CONFIG['database'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                port=DB_CONFIG['port'],
                connect_timeout=10
            )
            self.db_connection.autocommit = True
            logger.info("✅ Conectado a PostgreSQL en la nube")
            return True
        except psycopg2.Error as e:
            logger.error(f"❌ Error conectando a PostgreSQL: {e}")
            return False
    
    def ensure_db_connection(self) -> bool:
        """Verifica y reestablece la conexión a la BD si es necesario"""
        try:
            if self.db_connection is None or self.db_connection.closed:
                return self.connect_database()
            # Test the connection
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except psycopg2.Error:
            logger.warning("⚠️ Conexión a BD perdida, reconectando...")
            return self.connect_database()
    
    # ==================== OPERACIONES DE BASE DE DATOS ====================
    
    def get_table_info(self, mesa_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene información completa de una mesa desde la BD
        
        Args:
            mesa_id: ID de la mesa
            
        Returns:
            Dict con información de la mesa o None si no existe
        """
        if not self.ensure_db_connection():
            return None
        
        try:
            cursor = self.db_connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT 
                    id_mesa,
                    numero_mesa,
                    estado,
                    capacidad,
                    reservada,
                    id_reserva_actual,
                    updated_at,
                    vision_detected_at
                FROM mesas 
                WHERE id_mesa = %s
            """, (mesa_id,))
            
            result = cursor.fetchone()
            cursor.close()
            return dict(result) if result else None
            
        except psycopg2.Error as e:
            logger.error(f"❌ Error obteniendo info de mesa {mesa_id}: {e}")
            return None
    
    def update_table_status(self, mesa_id: int, estado: str, source: str = 'vision') -> bool:
        """
        Actualiza el estado de una mesa en la base de datos
        
        Args:
            mesa_id: ID de la mesa
            estado: 'ocupada' o 'disponible'
            source: Origen de la actualización ('vision', 'manual', 'reservation')
            
        Returns:
            bool: True si la actualización fue exitosa
        """
        if not self.ensure_db_connection():
            return False
        
        try:
            # Primero verificar si la mesa tiene una reserva activa
            mesa_info = self.get_table_info(mesa_id)
            
            if mesa_info is None:
                logger.warning(f"⚠️ Mesa {mesa_id} no existe en la BD")
                return False
            
            # Si la mesa está reservada, solo actualizar si viene de 'manual' o 'reservation'
            if mesa_info['reservada'] and source == 'vision':
                logger.info(f"🔒 Mesa {mesa_id} tiene reserva activa. No se actualiza desde visión.")
                return False
            
            cursor = self.db_connection.cursor()
            
            if source == 'vision':
                # Actualización desde sistema de visión
                cursor.execute("""
                    UPDATE mesas 
                    SET estado = %s, 
                        updated_at = NOW(),
                        vision_detected_at = NOW()
                    WHERE id_mesa = %s AND reservada = FALSE
                """, (estado, mesa_id))
            else:
                # Actualización manual o por reserva
                cursor.execute("""
                    UPDATE mesas 
                    SET estado = %s, 
                        updated_at = NOW()
                    WHERE id_mesa = %s
                """, (estado, mesa_id))
            
            rows_affected = cursor.rowcount
            cursor.close()
            
            if rows_affected > 0:
                logger.info(f"✅ Mesa {mesa_id} actualizada a '{estado}' (source: {source})")
                return True
            else:
                logger.warning(f"⚠️ No se actualizó mesa {mesa_id} (posiblemente reservada)")
                return False
                
        except psycopg2.Error as e:
            logger.error(f"❌ Error actualizando mesa {mesa_id}: {e}")
            return False
    
    def create_reservation(self, mesa_id: int, cliente_info: Dict) -> Optional[int]:
        """
        Crea una nueva reserva en la base de datos
        
        Args:
            mesa_id: ID de la mesa
            cliente_info: Información del cliente (nombre, teléfono, hora_reserva, etc.)
            
        Returns:
            ID de la reserva creada o None si falla
        """
        if not self.ensure_db_connection():
            return None
        
        try:
            cursor = self.db_connection.cursor()
            
            # Insertar reserva
            cursor.execute("""
                INSERT INTO reservas 
                (id_mesa, nombre_cliente, telefono, email, num_personas, 
                 fecha_reserva, hora_reserva, estado_reserva, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'confirmada', NOW())
                RETURNING id_reserva
            """, (
                mesa_id,
                cliente_info.get('nombre'),
                cliente_info.get('telefono'),
                cliente_info.get('email'),
                cliente_info.get('num_personas'),
                cliente_info.get('fecha'),
                cliente_info.get('hora')
            ))
            
            reserva_id = cursor.fetchone()[0]
            
            # Actualizar mesa como reservada
            cursor.execute("""
                UPDATE mesas 
                SET reservada = TRUE,
                    id_reserva_actual = %s,
                    estado = 'reservada',
                    updated_at = NOW()
                WHERE id_mesa = %s
            """, (reserva_id, mesa_id))
            
            cursor.close()
            logger.info(f"✅ Reserva {reserva_id} creada para mesa {mesa_id}")
            return reserva_id
            
        except psycopg2.Error as e:
            logger.error(f"❌ Error creando reserva: {e}")
            return None
    
    def check_and_release_expired_reservations(self):
        """
        Verifica y libera reservas que ya pasaron su hora (con margen de tolerancia)
        Ejecutar periódicamente
        """
        if not self.ensure_db_connection():
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # Liberar reservas expiradas (2 horas después de la hora de reserva)
            cursor.execute("""
                UPDATE mesas m
                SET reservada = FALSE,
                    id_reserva_actual = NULL,
                    estado = 'disponible',
                    updated_at = NOW()
                FROM reservas r
                WHERE m.id_reserva_actual = r.id_reserva
                AND r.estado_reserva = 'confirmada'
                AND (r.fecha_reserva + r.hora_reserva + INTERVAL '2 hours') < NOW()
            """)
            
            released = cursor.rowcount
            
            if released > 0:
                # Actualizar estado de las reservas
                cursor.execute("""
                    UPDATE reservas
                    SET estado_reserva = 'expirada'
                    WHERE estado_reserva = 'confirmada'
                    AND (fecha_reserva + hora_reserva + INTERVAL '2 hours') < NOW()
                """)
                
                logger.info(f"🔓 {released} reservas expiradas liberadas")
            
            cursor.close()
            
        except psycopg2.Error as e:
            logger.error(f"❌ Error liberando reservas expiradas: {e}")
    
    # ==================== MQTT CALLBACKS ====================
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback cuando se conecta al broker MQTT"""
        if rc == 0:
            self.is_connected = True
            logger.info("✅ Conectado al broker MQTT")
            
            # Suscribirse a todos los topics relevantes
            for topic_name, topic_path in TOPICS.items():
                if topic_name != 'status_response':  # No suscribirse al topic de respuestas
                    client.subscribe(topic_path)
                    logger.info(f"📡 Suscrito a: {topic_path}")
        else:
            logger.error(f"❌ Error conectando al broker MQTT. Código: {rc}")
            self.is_connected = False
    
    def on_disconnect(self, client, userdata, rc):
        """Callback cuando se desconecta del broker MQTT"""
        self.is_connected = False
        if rc != 0:
            logger.warning(f"⚠️ Desconexión inesperada del broker MQTT. Código: {rc}")
        else:
            logger.info("🔌 Desconectado del broker MQTT")
    
    def on_message(self, client, userdata, msg):
        """
        Callback principal cuando llega un mensaje MQTT
        Procesa mensajes de visión artificial, actualizaciones manuales y reservas
        """
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            logger.info(f"📨 Mensaje recibido en {topic}: {payload}")
            
            # ===== MENSAJES DEL SISTEMA DE VISIÓN =====
            if topic == TOPICS['vision_updates']:
                self.handle_vision_update(payload)
            
            # ===== ACTUALIZACIONES MANUALES DEL DASHBOARD =====
            elif topic == TOPICS['manual_updates']:
                self.handle_manual_update(payload)
            
            # ===== NUEVAS RESERVAS =====
            elif topic == TOPICS['reservations']:
                self.handle_reservation(payload)
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error decodificando JSON: {e}")
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")
    
    # ==================== MANEJADORES DE MENSAJES ====================
    
    def handle_vision_update(self, data: Dict):
        """
        Maneja actualizaciones del sistema de visión artificial
        
        Formato esperado:
        {
            "mesa_id": 1,
            "estado": "ocupada",
            "confianza": 0.95,
            "timestamp": "2024-01-15T14:30:00"
        }
        """
        mesa_id = data.get('mesa_id')
        estado = data.get('estado')
        confianza = data.get('confianza', 0)
        
        if not mesa_id or not estado:
            logger.warning("⚠️ Mensaje de visión incompleto")
            return
        
        # Filtrar por confianza mínima (opcional)
        if confianza < 0.7:
            logger.info(f"⚠️ Confianza baja ({confianza}) para mesa {mesa_id}, ignorando")
            return
        
        # Actualizar en la base de datos
        success = self.update_table_status(mesa_id, estado, source='vision')
        
        # Publicar respuesta de confirmación
        if success:
            response = {
                'mesa_id': mesa_id,
                'estado': estado,
                'updated': True,
                'timestamp': datetime.now().isoformat()
            }
            self.mqtt_client.publish(
                TOPICS['status_response'],
                json.dumps(response)
            )
    
    def handle_manual_update(self, data: Dict):
        """
        Maneja actualizaciones manuales desde el dashboard
        
        Formato esperado:
        {
            "mesa_id": 1,
            "estado": "disponible",
            "usuario": "admin@restaurante.com"
        }
        """
        mesa_id = data.get('mesa_id')
        estado = data.get('estado')
        usuario = data.get('usuario', 'unknown')
        
        if not mesa_id or not estado:
            logger.warning("⚠️ Actualización manual incompleta")
            return
        
        logger.info(f"👤 Actualización manual por {usuario}")
        success = self.update_table_status(mesa_id, estado, source='manual')
        
        # Confirmar actualización
        if success:
            response = {
                'mesa_id': mesa_id,
                'estado': estado,
                'updated': True,
                'source': 'manual',
                'timestamp': datetime.now().isoformat()
            }
            self.mqtt_client.publish(
                TOPICS['status_response'],
                json.dumps(response)
            )
    
    def handle_reservation(self, data: Dict):
        """
        Maneja nuevas reservas desde el frontend de clientes
        
        Formato esperado:
        {
            "mesa_id": 1,
            "cliente": {
                "nombre": "Juan Pérez",
                "telefono": "+507 6123-4567",
                "email": "juan@example.com",
                "num_personas": 4,
                "fecha": "2024-01-20",
                "hora": "19:00:00"
            }
        }
        """
        mesa_id = data.get('mesa_id')
        cliente_info = data.get('cliente', {})
        
        if not mesa_id or not cliente_info:
            logger.warning("⚠️ Datos de reserva incompletos")
            return
        
        # Verificar que la mesa esté disponible
        mesa_info = self.get_table_info(mesa_id)
        
        if mesa_info and mesa_info['reservada']:
            logger.warning(f"⚠️ Mesa {mesa_id} ya está reservada")
            # Publicar error
            self.mqtt_client.publish(
                TOPICS['status_response'],
                json.dumps({
                    'mesa_id': mesa_id,
                    'error': 'Mesa ya reservada',
                    'timestamp': datetime.now().isoformat()
                })
            )
            return
        
        # Crear reserva
        reserva_id = self.create_reservation(mesa_id, cliente_info)
        
        if reserva_id:
            response = {
                'mesa_id': mesa_id,
                'reserva_id': reserva_id,
                'estado': 'reservada',
                'created': True,
                'timestamp': datetime.now().isoformat()
            }
            self.mqtt_client.publish(
                TOPICS['status_response'],
                json.dumps(response)
            )
            logger.info(f"🎉 Reserva {reserva_id} confirmada para mesa {mesa_id}")
    
    # ==================== INICIO Y EJECUCIÓN ====================
    
    def setup_mqtt(self):
        """Configura el cliente MQTT"""
        self.mqtt_client = mqtt.Client(client_id=MQTT_CONFIG['client_id'])
        
        # Asignar callbacks
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_message = self.on_message
        
        # Configurar credenciales si existen
        if MQTT_CONFIG['username'] and MQTT_CONFIG['password']:
            self.mqtt_client.username_pw_set(
                MQTT_CONFIG['username'],
                MQTT_CONFIG['password']
            )
        
        return self.mqtt_client
    
    def start(self):
        """Inicia el broker y mantiene la conexión"""
        logger.info("🚀 Iniciando Restaurant MQTT Broker...")
        
        # Conectar a la base de datos
        if not self.connect_database():
            logger.error("❌ No se pudo conectar a la base de datos. Abortando.")
            return
        
        # Configurar MQTT
        self.setup_mqtt()
        
        # Conectar al broker MQTT
        try:
            self.mqtt_client.connect(
                MQTT_CONFIG['broker'],
                MQTT_CONFIG['port'],
                MQTT_CONFIG['keepalive']
            )
        except Exception as e:
            logger.error(f"❌ Error conectando al broker MQTT: {e}")
            return
        
        # Iniciar loop en segundo plano
        self.mqtt_client.loop_start()
        
        logger.info("✅ Broker iniciado y escuchando mensajes...")
        logger.info("Presiona Ctrl+C para detener")
        
        try:
            # Mantener el script corriendo
            last_check = time.time()
            while True:
                time.sleep(1)
                
                # Verificar y liberar reservas expiradas cada 5 minutos
                if time.time() - last_check > 300:  # 300 segundos = 5 minutos
                    self.check_and_release_expired_reservations()
                    last_check = time.time()
                    
        except KeyboardInterrupt:
            logger.info("\n🛑 Deteniendo broker...")
            self.stop()
    
    def stop(self):
        """Detiene el broker y cierra conexiones"""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        if self.db_connection:
            self.db_connection.close()
        
        logger.info("👋 Broker detenido correctamente")

# ==================== EJECUCIÓN PRINCIPAL ====================

if __name__ == "__main__":
    broker = RestaurantMQTTBroker()
    broker.start()
