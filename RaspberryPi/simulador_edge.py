#!/usr/bin/env python3
"""
Simulador del dispositivo Edge Computing
Publica detecciones simuladas al broker MQTT
"""

import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

# ============= CONFIGURACIÓN =============
# ⚠️ CAMBIAR ESTA IP POR LA DE TU RASPBERRY PI
BROKER_HOST = "192.168.40.9"  # <-- CAMBIAR AQUÍ
BROKER_PORT = 1883
TOPIC_BASE = "restaurant/mesas"
TOPIC_GENERAL = "restaurant/ocupacion"

# Número de mesas en tu restaurante
NUM_MESAS = 12
# =========================================

def generar_deteccion_simulada():
    """Genera datos simulados de detección de mesas"""
    detecciones = []
    
    for id_mesa in range(1, NUM_MESAS + 1):
        # Simular ocupación aleatoria (70% vacías, 30% ocupadas)
        ocupada = random.random() > 0.7
        
        if ocupada:
            personas = random.randint(1, 6)
            confianza = round(random.uniform(0.85, 0.98), 2)
            coords = [
                [random.randint(100, 500), random.randint(100, 500)]
                for _ in range(personas)
            ]
        else:
            personas = 0
            confianza = round(random.uniform(0.90, 0.99), 2)
            coords = []
        
        detecciones.append({
            "id_mesa": id_mesa,
            "personas_detectadas": personas,
            "confianza": confianza,
            "coordenadas": coords
        })
    
    return {
        "timestamp": datetime.now().isoformat(),
        "device_id": "simulador_edge_01",
        "detecciones": detecciones,
        "metadata": {
            "procesamiento_ms": random.randint(30, 60),
            "fps": round(random.uniform(20.0, 30.0), 1),
            "simulado": True
        }
    }

def on_connect(client, userdata, flags, rc):
    """Callback cuando se conecta al broker"""
    if rc == 0:
        print(f"✅ Conectado al broker en {BROKER_HOST}:{BROKER_PORT}")
        print(f"   Device ID: simulador_edge_01\n")
    else:
        print(f"❌ Error de conexión. Código: {rc}")
        print(f"   Verifica que Mosquitto esté corriendo en {BROKER_HOST}")

def on_publish(client, userdata, mid):
    """Callback cuando se publica un mensaje"""
    # No imprimir cada mensaje individual para no saturar
    pass

def on_disconnect(client, userdata, rc):
    """Callback cuando se desconecta"""
    if rc != 0:
        print(f"\n⚠️  Desconectado del broker inesperadamente")

def main():
    print("=" * 60)
    print("🤖 SIMULADOR DE EDGE DEVICE - Sistema de Reservaciones")
    print("=" * 60)
    print(f"\n📡 Configuración:")
    print(f"   Broker MQTT: {BROKER_HOST}:{BROKER_PORT}")
    print(f"   Topic principal: {TOPIC_GENERAL}")
    print(f"   Número de mesas: {NUM_MESAS}")
    print(f"   Frecuencia: cada 5 segundos\n")
    
    # Crear cliente MQTT
    client = mqtt.Client(client_id="simulador_edge_01")
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    
    # Configurar Last Will Testament
    client.will_set(
        "restaurant/dispositivos/simulador_edge_01/estado",
        payload="offline",
        qos=1,
        retain=True
    )
    
    try:
        # Conectar al broker
        print(f"🔌 Intentando conectar al broker...")
        client.connect(BROKER_HOST, BROKER_PORT, 60)
        client.loop_start()
        
        # Publicar estado online
        client.publish(
            "restaurant/dispositivos/simulador_edge_01/estado",
            payload="online",
            qos=1,
            retain=True
        )
        
        print(f"🚀 Iniciando publicación de detecciones...")
        print(f"   Presiona Ctrl+C para detener\n")
        print("-" * 60)
        
        contador = 0
        while True:
            contador += 1
            
            # Generar detección simulada
            payload = generar_deteccion_simulada()
            
            # Publicar en topic general
            result = client.publish(
                TOPIC_GENERAL,
                payload=json.dumps(payload, ensure_ascii=False),
                qos=1,
                retain=True
            )
            
            # Publicar en topics individuales por mesa
            for det in payload["detecciones"]:
                topic = f"{TOPIC_BASE}/{det['id_mesa']}/estado"
                mesa_payload = {
                    "id_mesa": det["id_mesa"],
                    "personas_detectadas": det["personas_detectadas"],
                    "confianza": det["confianza"],
                    "timestamp": payload["timestamp"]
                }
                client.publish(topic, json.dumps(mesa_payload), qos=1)
            
            # Mostrar resumen
            ocupadas = sum(1 for d in payload["detecciones"] 
                          if d["personas_detectadas"] > 0)
            disponibles = NUM_MESAS - ocupadas
            
            print(f"📤 [{contador:04d}] {datetime.now().strftime('%H:%M:%S')} | "
                  f"Ocupadas: {ocupadas:2d} | Disponibles: {disponibles:2d} | "
                  f"Total: {NUM_MESAS}")
            
            # Esperar 5 segundos
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("🛑 Deteniendo simulador...")
        client.publish(
            "restaurant/dispositivos/simulador_edge_01/estado",
            payload="offline",
            qos=1,
            retain=True
        )
        client.loop_stop()
        client.disconnect()
        print("✅ Simulador detenido correctamente")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()