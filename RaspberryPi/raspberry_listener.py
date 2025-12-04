import paho.mqtt.client as mqtt
import psycopg2
import json
from datetime import datetime

BROKER = "localhost"
TOPIC = "restaurante/mesas"

# Conexión a PostgreSQL
conn = psycopg2.connect(
    host="IP_DEL_SERVIDOR",
    database="restaurante",
    user="postgres",
    password="TU_PASSWORD"
)
cursor = conn.cursor()

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    
    mesa_id = data["mesa_id"]
    estado_detectado = data["estado"]
    timestamp = data.get("timestamp", datetime.now().isoformat())
    
    # Verificar si la mesa tiene reserva activa
    cursor.execute("""
        SELECT id_reserva, estado_reserva, hora_reserva 
        FROM reservas 
        WHERE id_mesa = %s 
        AND estado_reserva = 'confirmada'
        AND DATE(hora_reserva) = CURRENT_DATE
        AND hora_reserva <= NOW() + INTERVAL '15 minutes'
        AND hora_reserva >= NOW() - INTERVAL '30 minutes'
    """, (mesa_id,))
    
    reserva = cursor.fetchone()
    
    if reserva:
        # Hay reserva activa - aplicar lógica de negocio
        if estado_detectado == "ocupada":
            # Cliente llegó a su reserva
            estado_final = "reservada_ocupada"
            cursor.execute("""
                UPDATE reservas 
                SET estado_reserva = 'en_curso', 
                    hora_llegada = %s
                WHERE id_reserva = %s
            """, (timestamp, reserva[0]))
        else:
            # Mesa reservada pero aún vacía
            estado_final = "reservada"
            print(f"Mesa {mesa_id} reservada pero vacía - esperando cliente")
    else:
        # No hay reserva - actualizar según detección
        estado_final = estado_detectado
        
        # Verificar si había una reserva recién terminada
        cursor.execute("""
            SELECT id_reserva 
            FROM reservas 
            WHERE id_mesa = %s 
            AND estado_reserva = 'en_curso'
            ORDER BY hora_reserva DESC LIMIT 1
        """, (mesa_id,))
        
        reserva_activa = cursor.fetchone()
        if reserva_activa and estado_detectado == "disponible":
            # Cliente se fue - cerrar reserva
            cursor.execute("""
                UPDATE reservas 
                SET estado_reserva = 'completada',
                    hora_salida = %s
                WHERE id_reserva = %s
            """, (timestamp, reserva_activa[0]))
    
    # Actualizar estado de la mesa
    query = """
        UPDATE mesas 
        SET estado = %s, 
            updated_at = NOW(),
            ultimo_cambio_ia = %s
        WHERE id_mesa = %s
    """
    cursor.execute(query, (estado_final, timestamp, mesa_id))
    conn.commit()
    
    print(f"Mesa {mesa_id} actualizada a {estado_final}")

# Configurar cliente MQTT
client = mqtt.Client()
client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC)
client.on_message = on_message

print("Esperando mensajes...")
client.loop_forever()
