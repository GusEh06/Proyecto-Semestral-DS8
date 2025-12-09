"""
Script de prueba para verificar la comunicación MQTT
entre el sistema de visión y el backend
"""
import json
import paho.mqtt.client as mqtt
import time

# Configuración (debe coincidir con tu setup)
BROKER_HOST = "100.81.10.77"
BROKER_PORT = 1883
TOPIC_OCUPACION = "restaurant/ocupacion"

def on_connect(client, userdata, flags, rc, properties=None):
    """Callback cuando se conecta al broker"""
    if rc == 0:
        print(f"[OK] Conectado al broker MQTT en {BROKER_HOST}:{BROKER_PORT}")
        # Suscribirse al topic para escuchar mensajes
        client.subscribe(TOPIC_OCUPACION, qos=1)
        print(f"[SUSCRITO] Escuchando mensajes en: {TOPIC_OCUPACION}")
    else:
        print(f"[ERROR] Error de conexión. Código: {rc}")

def on_message(client, userdata, message):
    """Callback cuando llega un mensaje"""
    try:
        print("\n" + "="*60)
        print(f"[MENSAJE RECIBIDO]")
        print(f"Topic: {message.topic}")
        print(f"QoS: {message.qos}")

        # Decodificar payload
        payload = json.loads(message.payload.decode())
        print(f"\nContenido:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))

        # Validar estructura
        print(f"\n[VALIDACION]")
        print(f"  - timestamp: {'✓' if 'timestamp' in payload else '✗ FALTA'}")
        print(f"  - device_id: {'✓' if 'device_id' in payload else '✗ FALTA'}")
        print(f"  - detecciones: {'✓' if 'detecciones' in payload else '✗ FALTA'}")

        if 'detecciones' in payload:
            print(f"\n[DETECCIONES] {len(payload['detecciones'])} mesa(s)")
            for det in payload['detecciones']:
                id_mesa = det.get('id_mesa', 'N/A')
                personas = det.get('personas_detectadas', 'N/A')
                confianza = det.get('confianza', 'N/A')
                print(f"  - Mesa {id_mesa}: {personas} persona(s) (confianza: {confianza})")

        print("="*60 + "\n")

    except json.JSONDecodeError as e:
        print(f"[ERROR] No se pudo decodificar JSON: {e}")
        print(f"Payload raw: {message.payload}")
    except Exception as e:
        print(f"[ERROR] Error procesando mensaje: {e}")

def test_publish():
    """Publica un mensaje de prueba para simular el sistema de visión"""
    print("\n[PRUEBA] Publicando mensaje de prueba...")

    test_payload = {
        "timestamp": "2025-12-08T15:30:00",
        "device_id": "test_device",
        "detecciones": [
            {
                "id_mesa": 1,
                "personas_detectadas": 2,
                "confianza": 0.95
            },
            {
                "id_mesa": 2,
                "personas_detectadas": 0,
                "confianza": 0.85
            }
        ]
    }

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="test_publisher")

    try:
        client.connect(BROKER_HOST, BROKER_PORT, 60)
        result = client.publish(
            TOPIC_OCUPACION,
            json.dumps(test_payload),
            qos=1
        )

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"[OK] Mensaje de prueba publicado exitosamente")
            print(f"     Topic: {TOPIC_OCUPACION}")
            print(f"     Contenido: {json.dumps(test_payload, indent=2, ensure_ascii=False)}")
        else:
            print(f"[ERROR] Error publicando mensaje. Código: {result.rc}")

        client.disconnect()

    except Exception as e:
        print(f"[ERROR] No se pudo conectar al broker: {e}")
        print(f"        Verifica que Mosquitto esté corriendo en {BROKER_HOST}")

def main():
    """Función principal"""
    print("""
    ========================================
    Test de Comunicación MQTT
    ========================================

    Este script:
    1. Se conecta al broker MQTT
    2. Escucha mensajes en el topic de ocupación
    3. Valida la estructura de los mensajes

    Configuración:
    - Broker: {BROKER_HOST}:{BROKER_PORT}
    - Topic: {TOPIC_OCUPACION}

    Presiona Ctrl+C para salir
    ========================================
    """.format(BROKER_HOST=BROKER_HOST, BROKER_PORT=BROKER_PORT, TOPIC_OCUPACION=TOPIC_OCUPACION))

    # Preguntar si quiere publicar un mensaje de prueba
    opcion = input("\n¿Quieres publicar un mensaje de prueba? (s/n): ").strip().lower()
    if opcion == 's':
        test_publish()
        print("\nEsperando 2 segundos antes de empezar a escuchar...\n")
        time.sleep(2)

    # Iniciar listener
    print("[INICIANDO] Escuchando mensajes MQTT...\n")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="mqtt_test_listener")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER_HOST, BROKER_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n\n[DETENIDO] Test finalizado por el usuario")
        client.disconnect()
    except Exception as e:
        print(f"\n[ERROR] Error de conexión: {e}")
        print(f"Verifica que Mosquitto esté corriendo en {BROKER_HOST}:{BROKER_PORT}")

if __name__ == "__main__":
    main()
