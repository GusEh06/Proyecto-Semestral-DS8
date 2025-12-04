"""
SIMULADOR DE SISTEMA DE VISIÓN - YOLO
======================================
Este script simula el comportamiento del sistema de visión artificial
que envía actualizaciones sobre el estado de las mesas al broker MQTT.

Útil para probar el broker sin necesidad de tener el sistema YOLO corriendo.
"""

import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

# ==================== CONFIGURACIÓN ====================

MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883
TOPIC_VISION = 'restaurante/mesas/vision'
TOPIC_STATUS = 'restaurante/mesas/status'

# IDs de las mesas a simular
MESAS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# ==================== CLIENTE MQTT ====================

client = mqtt.Client(client_id='vision_simulator')

def on_connect(client, userdata, flags, rc):
    """Callback al conectarse"""
    if rc == 0:
        print("✅ Simulador conectado al broker MQTT")
        client.subscribe(TOPIC_STATUS)
    else:
        print(f"❌ Error conectando. Código: {rc}")

def on_message(client, userdata, msg):
    """Callback al recibir mensajes de confirmación"""
    try:
        data = json.loads(msg.payload.decode())
        print(f"📥 Confirmación recibida: Mesa {data.get('mesa_id')} -> {data.get('estado')}")
    except:
        pass

client.on_connect = on_connect
client.on_message = on_message

# ==================== FUNCIONES DE SIMULACIÓN ====================

def simular_deteccion_mesa(mesa_id: int, forzar_estado: str = None):
    """
    Simula una detección del sistema de visión para una mesa
    
    Args:
        mesa_id: ID de la mesa
        forzar_estado: Si se proporciona, usa este estado en lugar de aleatorio
    """
    # Estado aleatorio o forzado
    if forzar_estado:
        estado = forzar_estado
    else:
        estado = random.choice(['ocupada', 'disponible'])
    
    # Confianza aleatoria (simulando precisión del modelo YOLO)
    confianza = random.uniform(0.75, 0.98)
    
    # Crear mensaje
    mensaje = {
        'mesa_id': mesa_id,
        'estado': estado,
        'confianza': round(confianza, 2),
        'timestamp': datetime.now().isoformat(),
        'detector': 'YOLO-v8',
        'personas_detectadas': random.randint(0, 4) if estado == 'ocupada' else 0
    }
    
    # Publicar al broker
    client.publish(TOPIC_VISION, json.dumps(mensaje))
    print(f"📤 Enviado: Mesa {mesa_id} -> {estado} (confianza: {confianza:.2f})")

def modo_interactivo():
    """Modo interactivo para controlar manualmente las actualizaciones"""
    print("\n" + "="*50)
    print("MODO INTERACTIVO - SIMULADOR DE VISIÓN")
    print("="*50)
    print("\nComandos disponibles:")
    print("  1-10: Cambiar estado de mesa específica")
    print("  all: Actualizar todas las mesas aleatoriamente")
    print("  auto: Modo automático continuo")
    print("  quit: Salir\n")
    
    while True:
        comando = input("Comando: ").strip().lower()
        
        if comando == 'quit':
            break
        
        elif comando == 'all':
            print("\n🔄 Actualizando todas las mesas...")
            for mesa in MESAS:
                simular_deteccion_mesa(mesa)
                time.sleep(0.5)
        
        elif comando == 'auto':
            print("\n🤖 Modo automático activado (Ctrl+C para detener)")
            try:
                while True:
                    mesa_random = random.choice(MESAS)
                    simular_deteccion_mesa(mesa_random)
                    time.sleep(random.uniform(3, 8))  # Entre 3 y 8 segundos
            except KeyboardInterrupt:
                print("\n⏸️  Modo automático detenido")
        
        elif comando.isdigit():
            mesa_id = int(comando)
            if mesa_id in MESAS:
                # Preguntar estado
                estado = input(f"Estado para mesa {mesa_id} (ocupada/disponible): ").strip()
                if estado in ['ocupada', 'disponible']:
                    simular_deteccion_mesa(mesa_id, forzar_estado=estado)
                else:
                    print("⚠️ Estado inválido")
            else:
                print("⚠️ Mesa no válida")
        
        else:
            print("⚠️ Comando no reconocido")

def modo_demo():
    """Modo demostración con secuencia predefinida"""
    print("\n" + "="*50)
    print("MODO DEMO - SECUENCIA AUTOMÁTICA")
    print("="*50)
    
    secuencia = [
        (1, 'ocupada', 2),
        (2, 'ocupada', 2),
        (3, 'disponible', 3),
        (1, 'disponible', 4),
        (4, 'ocupada', 2),
        (5, 'ocupada', 3),
        (2, 'disponible', 3),
        (6, 'ocupada', 2),
    ]
    
    print("\nEjecutando secuencia de detecciones...\n")
    
    for mesa_id, estado, espera in secuencia:
        simular_deteccion_mesa(mesa_id, forzar_estado=estado)
        time.sleep(espera)
    
    print("\n✅ Secuencia de demo completada")

# ==================== MENÚ PRINCIPAL ====================

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🎬 SIMULADOR DE SISTEMA DE VISIÓN ARTIFICIAL - YOLO")
    print("="*60)
    print(f"\nBroker MQTT: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Topic: {TOPIC_VISION}")
    print(f"Mesas monitoreadas: {MESAS}")
    
    # Conectar al broker
    print("\n🔌 Conectando al broker MQTT...")
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        time.sleep(2)  # Esperar conexión
    except Exception as e:
        print(f"❌ Error conectando al broker: {e}")
        return
    
    # Menú de opciones
    print("\n" + "="*60)
    print("MODOS DISPONIBLES")
    print("="*60)
    print("1. Modo Interactivo (control manual)")
    print("2. Modo Demo (secuencia predefinida)")
    print("3. Modo Automático (actualizaciones aleatorias continuas)")
    
    opcion = input("\nSelecciona un modo (1-3): ").strip()
    
    if opcion == '1':
        modo_interactivo()
    elif opcion == '2':
        modo_demo()
    elif opcion == '3':
        print("\n🤖 Modo automático iniciado (Ctrl+C para detener)")
        try:
            while True:
                mesa_random = random.choice(MESAS)
                simular_deteccion_mesa(mesa_random)
                time.sleep(random.uniform(4, 10))
        except KeyboardInterrupt:
            print("\n\n⏹️  Simulación detenida")
    else:
        print("⚠️ Opción no válida")
    
    # Desconectar
    print("\n👋 Desconectando...")
    client.loop_stop()
    client.disconnect()
    print("✅ Simulador finalizado")

if __name__ == "__main__":
    main()
