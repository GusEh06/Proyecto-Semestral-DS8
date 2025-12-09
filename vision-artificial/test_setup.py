"""
Script de prueba para verificar la configuración del sistema
"""

import sys
import subprocess

def verificar_modulo(nombre_modulo, nombre_display=None):
    """Verifica si un módulo está instalado"""
    if nombre_display is None:
        nombre_display = nombre_modulo
    
    try:
        __import__(nombre_modulo)
        print(f" {nombre_display}: OK")
        return True
    except ImportError:
        print(f" {nombre_display}: NO INSTALADO")
        return False

def verificar_archivo(ruta, descripcion):
    """Verifica si un archivo existe"""
    import os
    if os.path.exists(ruta):
        print(f"{descripcion}: OK")
        return True
    else:
        print(f" {descripcion}: NO ENCONTRADO")
        print(f"   Ruta buscada: {ruta}")
        return False

def verificar_backend():
    """Verifica si el backend está accesible"""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print(f"Backend FastAPI: CORRIENDO")
            return True
        else:
            print(f" Backend FastAPI: Responde pero con error {response.status_code}")
            return False
    except Exception as e:
        print(f" Backend FastAPI: NO ACCESIBLE")
        print(f"   Error: {e}")
        print(f"   Asegúrate de iniciar el backend: cd back-end && uvicorn app.main:app --reload")
        return False

def verificar_camara_ip(ip):
    """Verifica si la cámara IP está accesible"""
    try:
        import requests
        response = requests.get(ip, timeout=3)
        print(f"Cámara IP: ACCESIBLE")
        return True
    except Exception as e:
        print(f"Cámara IP: NO ACCESIBLE")
        print(f"   URL probada: {ip}")
        print(f"   Error: {e}")
        return False

def verificar_webcam():
    """Verifica si hay una webcam disponible"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print(f" Webcam local: DISPONIBLE")
                return True
        print(f" Webcam local: NO DISPONIBLE")
        return False
    except Exception as e:
        print(f"Webcam local: ERROR")
        print(f"   Error: {e}")
        return False

def main():
    print("""
    ----------------------------------------------------
            Verificación de Sistema de Visión Artificial       
-------------------------------------------------------------
    """)
    
    errores = []
    
    # Verificar Python
    print("\nVERIFICANDO PYTHON")
    print("-" * 60)
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}: OK")
    else:
        print(f"Python {python_version.major}.{python_version.minor}: Versión muy antigua")
        print(f"   Se requiere Python 3.8 o superior")
        errores.append("Python version")
    
    # Verificar módulos
    print("\nVERIFICANDO MÓDULOS PYTHON")
    print("-" * 60)
    modulos_requeridos = [
        ("cv2", "OpenCV"),
        ("ultralytics", "Ultralytics (YOLO)"),
        ("numpy", "NumPy"),
        ("requests", "Requests"),
    ]
    
    for modulo, nombre in modulos_requeridos:
        if not verificar_modulo(modulo, nombre):
            errores.append(f"Módulo {nombre}")
    
    # Verificar archivos
    print("\nVERIFICANDO ARCHIVOS")
    print("-" * 60)
    archivos = [
        ("vision_system.py", "Script principal"),
        ("config.py", "Archivo de configuración"),
        ("Entrenamiendo_mesas/weights/best.pt", "Modelo de mesas entrenado"),
    ]
    
    for archivo, desc in archivos:
        if not verificar_archivo(archivo, desc):
            errores.append(f"Archivo {desc}")
    
    # Verificar backend
    print("\nVERIFICANDO BACKEND")
    print("-" * 60)
    if not verificar_backend():
        errores.append("Backend FastAPI")
    
    # Verificar cámaras
    print("\nVERIFICANDO CÁMARAS")
    print("-" * 60)
    
    print("\nWebcam local:")
    webcam_ok = verificar_webcam()
    
    print("\nCámara IP:")
    from config import IP_WEBCAM
    camara_ip_ok = verificar_camara_ip(IP_WEBCAM)
    
    if not webcam_ok and not camara_ip_ok:
        print("\nADVERTENCIA: No se detectó ninguna cámara disponible")
        print("   Opciones:")
        print("   1. Conecta una webcam USB")
        print("   2. Configura IP Webcam en tu smartphone")
        print("   3. Actualiza IP_WEBCAM en config.py")
        errores.append("Cámara")
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    if len(errores) == 0:
        print("\n¡TODO LISTO! El sistema está correctamente configurado.")
        print("\nPuedes iniciar el sistema con:")
        print("   python vision_system.py")
    else:
        print(f"\n Se encontraron {len(errores)} problema(s):")
        for i, error in enumerate(errores, 1):
            print(f"   {i}. {error}")
        
        print("\n🔧 SOLUCIONES:")
        
        if any("Módulo" in e for e in errores):
            print("\n   Para instalar módulos faltantes:")
            print("   pip install -r requirements.txt --break-system-packages")
        
        if any("best.pt" in e for e in errores):
            print("\n   Para el modelo de mesas:")
            print("   1. Asegúrate de tener el archivo best.pt")
            print("   2. Colócalo en: Entrenamiendo_mesas/weights/best.pt")
        
        if "Backend FastAPI" in errores:
            print("\n   Para iniciar el backend:")
            print("   cd back-end")
            print("   uvicorn app.main:app --reload")
        
        if "Cámara" in errores:
            print("\n   Para configurar cámara:")
            print("   1. Si usas webcam: Conéctala y reinicia el script")
            print("   2. Si usas IP Webcam:")
            print("      - Instala 'IP Webcam' en tu smartphone (Android)")
            print("      - Inicia el servidor en la app")
            print("      - Actualiza IP_WEBCAM en config.py")
    
    print("\n" + "=" * 60 + "\n")
    
    return len(errores) == 0

if __name__ == "__main__":
    exito = main()
    sys.exit(0 if exito else 1)