"""
Script para probar la comunicación con el backend
Sin necesidad de cámara - Usa datos simulados
"""

import requests
import time
import random
from datetime import datetime

BACKEND_URL = "http://localhost:8000/api/v1/vision/actualizar-estado-mesas"
NUMERO_MESAS = 5  # Número de mesas a simular

def generar_datos_simulados():
    """Genera datos simulados de ocupación de mesas"""
    detecciones = []
    
    for i in range(1, NUMERO_MESAS + 1):
        # Simular ocupación aleatoria (0-4 personas)
        personas = random.choice([0, 0, 0, 1, 2, 3, 4])
        
        detecciones.append({
            "id_mesa": i,
            "personas_detectadas": personas
        })
    
    return detecciones

def enviar_al_backend(detecciones):
    """Envía los datos al backend"""
    payload = {
        "detecciones": detecciones
    }
    
    print(f"\nEnviando actualización al backend...")
    print(f"URL: {BACKEND_URL}")
    print(f"Datos: {payload}")
    
    try:
        response = requests.post(
            BACKEND_URL,
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            print("\nRespuesta exitosa!")
            data = response.json()
            
            print(f"\nMensaje del servidor: {data.get('message', 'N/A')}")
            print("\nResultados:")
            print("-" * 70)
            
            for resultado in data.get('resultados', []):
                if resultado['success']:
                    mesa_id = resultado['id_mesa']
                    estado_ant = resultado['estado_anterior']
                    estado_nuevo = resultado['estado_nuevo']
                    personas = resultado['personas_detectadas']
                    
                    emoji = "🟢" if estado_nuevo == "disponible" else "🔴" if estado_nuevo == "ocupada" else "🔵"
                    
                    print(f"{emoji} Mesa {mesa_id}: {estado_ant} → {estado_nuevo} "
                          f"({personas} persona{'s' if personas != 1 else ''})")
                else:
                    print(f"Mesa {resultado['id_mesa']}: {resultado.get('message', 'Error')}")
            
            print("-" * 70)
            return True
        else:
            print(f"\nError del servidor")
            print(f"Código de estado: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("\nNo se pudo conectar con el backend")
        print("Verifica que el servidor esté corriendo en:")
        print("  cd back-end")
        print("  uvicorn app.main:app --reload")
        return False
    
    except requests.exceptions.Timeout:
        print("\nTimeout al conectar con el backend")
        return False
    
    except Exception as e:
        print(f"\n Error inesperado: {e}")
        return False

def test_manual():
    """Prueba manual con datos personalizados"""
    print("\n" + "=" * 70)
    print("TEST MANUAL - Ingresa los datos de ocupación")
    print("=" * 70)
    
    detecciones = []
    
    for i in range(1, NUMERO_MESAS + 1):
        while True:
            try:
                personas = int(input(f"Mesa {i} - ¿Cuántas personas? [0-6]: "))
                if 0 <= personas <= 6:
                    detecciones.append({
                        "id_mesa": i,
                        "personas_detectadas": personas
                    })
                    break
                else:
                    print("Por favor ingresa un número entre 0 y 6")
            except ValueError:
                print("Por favor ingresa un número válido")
    
    return detecciones

def test_automatico(duracion_segundos=30, intervalo=5):
    """Prueba automática con datos aleatorios"""
    print("\n" + "=" * 70)
    print(f"TEST AUTOMÁTICO - {duracion_segundos} segundos, actualizando cada {intervalo}s")
    print("=" * 70)
    
    inicio = time.time()
    envios_exitosos = 0
    envios_totales = 0
    
    while time.time() - inicio < duracion_segundos:
        print(f"\n{datetime.now().strftime('%H:%M:%S')}")
        
        detecciones = generar_datos_simulados()
        envios_totales += 1
        
        if enviar_al_backend(detecciones):
            envios_exitosos += 1
        
        print(f"\nEsperando {intervalo} segundos...")
        time.sleep(intervalo)
    
    # Estadísticas finales
    print("\n" + "=" * 70)
    print("ESTADÍSTICAS FINALES")
    print("=" * 70)
    print(f"Envíos totales: {envios_totales}")
    print(f"Envíos exitosos: {envios_exitosos}")
    print(f"Envíos fallidos: {envios_totales - envios_exitosos}")
    if envios_totales > 0:
        tasa = (envios_exitosos / envios_totales) * 100
        print(f"Tasa de éxito: {tasa:.1f}%")
    print("=" * 70)

def test_verificar_backend():
    """Verifica que el backend esté accesible"""
    print("\n🔍 Verificando backend...")
    
    try:
        # Primero intentar el endpoint de health
        health_url = "http://localhost:8000/health"
        response = requests.get(health_url, timeout=3)
        
        if response.status_code == 200:
            print("Backend FastAPI está corriendo")
            data = response.json()
            print(f"   Status: {data.get('status', 'N/A')}")
            return True
        else:
            print(f"Backend responde pero con código {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("Backend no está accesible")
        print("\n   Para iniciar el backend:")
        print("   cd back-end")
        print("   uvicorn app.main:app --reload")
        return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():

    # Verificar que el backend esté corriendo
    if not test_verificar_backend():
        return
    
    print("\n" + "=" * 70)
    print("OPCIONES DE PRUEBA")
    print("=" * 70)
    print("1. Test manual (ingresas los datos)")
    print("2. Test automático con datos aleatorios (30 segundos)")
    print("3. Test único (envío simple)")
    print("4. Salir")
    
    while True:
        opcion = input("\nSelecciona una opción [1-4]: ").strip()
        
        if opcion == '1':
            detecciones = test_manual()
            enviar_al_backend(detecciones)
        
        elif opcion == '2':
            test_automatico()
        
        elif opcion == '3':
            print("\nGenerando datos aleatorios...")
            detecciones = generar_datos_simulados()
            enviar_al_backend(detecciones)
        
        elif opcion == '4':
            print("\n¡Hasta luego!")
            break
        
        else:
            print("Opción no válida. Por favor selecciona 1, 2, 3 o 4.")
        
        continuar = input("\n¿Realizar otra prueba? (s/n) [s]: ").strip().lower()
        if continuar == 'n':
            print("\n¡Hasta luego!")
            break

if __name__ == "__main__":
    main()