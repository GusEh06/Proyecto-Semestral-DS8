"""
Servicio MQTT para recibir detecciones del Edge Device
y actualizar el estado de las mesas en la base de datos
"""

import paho.mqtt.client as mqtt
import json
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.mesa import Mesa
from app.models.tipo_mesa import TipoMesa
from app.models.reservacion import Reservacion, EstadoReservacion

# ============= CONFIGURACIÓN =============
# ⚠️ CAMBIAR ESTA IP POR LA DE TU RASPBERRY PI
BROKER_HOST = "192.168.40.9"  # <-- CAMBIAR AQUÍ
BROKER_PORT = 1883
TOPIC_OCUPACION = "restaurant/ocupacion"
TOPIC_DISPOSITIVOS = "restaurant/dispositivos/+/estado"
# =========================================

class MQTTService:
    """Servicio para gestionar la conexión MQTT y procesar mensajes"""
    
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="backend_fastapi")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.connected = False
        
    def on_connect(self, client, userdata, flags, rc, properties=None):
        """Callback cuando se conecta al broker"""
        if rc == 0:
            self.connected = True
            print(f"[OK] Backend conectado al broker MQTT")
            print(f"   Host: {BROKER_HOST}:{BROKER_PORT}")

            # Suscribirse a los topics
            client.subscribe(TOPIC_OCUPACION, qos=1)
            client.subscribe(TOPIC_DISPOSITIVOS, qos=1)

            print(f"[SUSCRITO] Topics:")
            print(f"   - {TOPIC_OCUPACION}")
            print(f"   - {TOPIC_DISPOSITIVOS}")
            print()
        else:
            self.connected = False
            print(f"[ERROR] Error de conexión MQTT. Código: {rc}")
            print(f"   Verifica que Mosquitto esté corriendo en {BROKER_HOST}")
    
    def on_disconnect(self, client, userdata, rc, properties=None):
        """Callback cuando se desconecta"""
        self.connected = False
        if rc != 0:
            print(f"[ADVERTENCIA] Desconexión inesperada del broker MQTT (código: {rc})")
            print(f"   Intentando reconectar...")
    
    def on_message(self, client, userdata, message):
        """Callback cuando llega un mensaje"""
        try:
            topic = message.topic
            
            # Procesar mensajes de estado de dispositivos
            if topic.startswith("restaurant/dispositivos/"):
                estado = message.payload.decode()
                device_id = topic.split("/")[2]
                print(f"[DISPOSITIVO] {device_id}: {estado}")
                return
            
            # Procesar detecciones de ocupación
            if topic == TOPIC_OCUPACION:
                payload = json.loads(message.payload.decode())

                timestamp = payload.get('timestamp')
                device_id = payload.get('device_id')
                detecciones = payload.get('detecciones', [])

                print(f"\n[MENSAJE] Mensaje recibido")
                print(f"   Timestamp: {timestamp}")
                print(f"   Device: {device_id}")
                print(f"   Detecciones: {len(detecciones)} mesas")

                # Procesar detecciones
                self.actualizar_estado_mesas(detecciones)
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] Error decodificando JSON: {e}")
        except Exception as e:
            print(f"[ERROR] Error procesando mensaje: {e}")
    
    def actualizar_estado_mesas(self, detecciones: list):
        """
        Actualiza el estado de las mesas en la base de datos
        según las detecciones recibidas del edge device.

        ✨ NUEVO: También emite eventos SSE a los clientes conectados
        para que reciban actualizaciones en tiempo real.
        """
        db: Session = SessionLocal()

        try:
            mesas_actualizadas = 0
            cambios = []

            # Obtener o crear tipo de mesa predeterminado
            tipo_predeterminado = db.query(TipoMesa).first()
            if not tipo_predeterminado:
                # Crear tipo de mesa genérico si no existe
                tipo_predeterminado = TipoMesa(
                    descripcion="Mesa estándar",
                    cantidad_sillas=4
                )
                db.add(tipo_predeterminado)
                db.commit()
                db.refresh(tipo_predeterminado)
                print(f"   [INFO] Tipo de mesa predeterminado creado")

            for det in detecciones:
                id_mesa = det.get("id_mesa")
                personas = det.get("personas_detectadas", 0)
                confianza = det.get("confianza", 0)

                # Obtener o crear mesa en la BD
                mesa = db.query(Mesa).filter(Mesa.id_mesa == id_mesa).first()
                if not mesa:
                    # Crear mesa automáticamente
                    estado_inicial = "ocupada" if personas > 0 else "disponible"
                    mesa = Mesa(
                        id_mesa=id_mesa,
                        id_tipo_mesa=tipo_predeterminado.id_tipo_mesa,
                        estado=estado_inicial
                    )
                    db.add(mesa)
                    db.commit()
                    db.refresh(mesa)
                    print(f"   [NUEVA] Mesa {id_mesa} creada automáticamente (estado: {estado_inicial})")

                estado_anterior = mesa.estado

                # Verificar si hay una reservación activa para hoy
                hoy = date.today()
                reservacion_activa = db.query(Reservacion).filter(
                    Reservacion.id_mesa == id_mesa,
                    Reservacion.fecha == hoy,
                    Reservacion.estado.in_(["pendiente", "confirmada"])
                ).first()

                # Lógica de actualización de estado basada en detecciones
                if personas > 0:
                    # Hay personas detectadas → mesa ocupada
                    nuevo_estado = "ocupada"
                    razon = f"{personas} persona(s) detectada(s)"
                else:
                    # No hay personas detectadas
                    if reservacion_activa:
                        # Hay una reservación activa → mantener como reservada
                        nuevo_estado = "reservada"
                        razon = f"Reservada (ID: {reservacion_activa.id_reserva})"
                    else:
                        # No hay reservación → disponible
                        nuevo_estado = "disponible"
                        razon = "Sin personas"

                # Actualizar solo si cambió el estado
                if estado_anterior != nuevo_estado:
                    mesa.estado = nuevo_estado
                    mesa.updated_at = datetime.now()

                    cambios.append({
                        "mesa": id_mesa,
                        "anterior": estado_anterior,
                        "nuevo": nuevo_estado,
                        "razon": razon
                    })

                    mesas_actualizadas += 1

            # Guardar cambios en la BD
            if mesas_actualizadas > 0:
                db.commit()

                print(f"\n   [OK] {mesas_actualizadas} mesa(s) actualizada(s):")
                for cambio in cambios:
                    print(f"      Mesa {cambio['mesa']}: "
                          f"{cambio['anterior']} -> {cambio['nuevo']} "
                          f"({cambio['razon']})")
                print()

                # 🔴 NUEVO: Emitir evento SSE a todos los clientes conectados
                # Obtener todas las mesas actualizadas para enviar al frontend
                self.emit_mesa_update_event(db)
            else:
                print(f"   [INFO] Sin cambios de estado")

        except Exception as e:
            print(f"[ERROR] Error actualizando mesas en BD: {e}")
            db.rollback()
        finally:
            db.close()

    def emit_mesa_update_event(self, db: Session):
        """
        🔴 Emite un evento SSE con el estado actualizado de todas las mesas.

        Este método es llamado después de actualizar las mesas en la BD.
        Obtiene todas las mesas y las envía a los clientes conectados vía SSE.
        """
        try:
            # Importar aquí para evitar importación circular
            from app.routers.mesas import broadcast_mesa_update

            # Obtener todas las mesas con sus relaciones
            mesas = db.query(Mesa).all()
            hoy = date.today()

            # Convertir a formato JSON serializable
            mesas_data = []
            for mesa in mesas:
                mesa_dict = {
                    "id_mesa": mesa.id_mesa,
                    "estado": mesa.estado,
                    "id_tipo_mesa": mesa.id_tipo_mesa,
                    "updated_at": mesa.updated_at.isoformat() if mesa.updated_at else None,
                    "reservacion_activa": None
                }

                # Incluir datos del tipo de mesa si existe
                if mesa.tipo_mesa:
                    mesa_dict["tipo_mesa"] = {
                        "id_tipo_mesa": mesa.tipo_mesa.id_tipo_mesa,
                        "descripcion": mesa.tipo_mesa.descripcion,
                        "cantidad_sillas": mesa.tipo_mesa.cantidad_sillas
                    }

                # Si la mesa está reservada, incluir información de la reservación activa
                if mesa.estado == "reservada":
                    reservacion = db.query(Reservacion).filter(
                        Reservacion.id_mesa == mesa.id_mesa,
                        Reservacion.fecha == hoy,
                        Reservacion.estado.in_(["pendiente", "confirmada"])
                    ).first()

                    if reservacion:
                        mesa_dict["reservacion_activa"] = {
                            "id_reserva": reservacion.id_reserva,
                            "nombre": reservacion.nombre,
                            "apellido": reservacion.apellido,
                            "telefono": reservacion.telefono,
                            "correo": reservacion.correo,
                            "cantidad_personas": reservacion.cantidad_personas,
                            "fecha": reservacion.fecha.isoformat(),
                            "hora": reservacion.hora.isoformat(),
                            "estado": reservacion.estado
                        }

                mesas_data.append(mesa_dict)

            # Broadcast a todos los clientes conectados
            broadcast_mesa_update(mesas_data)
            print(f"   [SSE] Evento emitido a clientes conectados")

        except Exception as e:
            print(f"[ERROR] Error emitiendo evento SSE: {e}")
    
    def start(self):
        """Inicia el cliente MQTT"""
        try:
            print(f"[MQTT] Iniciando servicio MQTT...")
            print(f"   Conectando a: {BROKER_HOST}:{BROKER_PORT}")

            self.client.connect(BROKER_HOST, BROKER_PORT, 60)
            self.client.loop_start()  # Loop en thread separado

            print(f"[MQTT] Servicio MQTT iniciado")

        except Exception as e:
            print(f"[ERROR] Error iniciando servicio MQTT: {e}")
            print(f"   Verifica que Mosquitto esté corriendo en {BROKER_HOST}")
    
    def stop(self):
        """Detiene el cliente MQTT"""
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            print("[MQTT] Servicio MQTT detenido")

# Instancia global del servicio
mqtt_service = MQTTService()