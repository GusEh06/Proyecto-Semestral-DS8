from ultralytics import YOLO
import cv2

#esto se cambia dependiendo de la ip que se les generé
IP_WEBCAM = "http://192.168.1.125:8080/video"
RUTA_MODELO_MESAS = 'Entrenamiendo_mesas/weights/best.pt'

def dibujar_detecciones(frame, results, color=(0, 255, 0), label="Objeto"):
    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f'{label} {conf:.2f}', (x1, y1-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    return frame

#cargar los modelos: el COCO, y el modelo previamente entrenado
model_coco = YOLO('yolov8n.pt')
model_mesas = YOLO(RUTA_MODELO_MESAS)

print("Modelos cargados")

#conectar a la ip de la cámara
cap = cv2.VideoCapture(IP_WEBCAM)

if not cap.isOpened():
    print("Verifica la IP y que esten en la misma red")
    exit()

print("Conectado")
print("Presiona 'q' para salir\n")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Conexion perdida")
            break
        
        results_coco = model_coco(frame, classes=[0, 56], verbose=False)
        results_mesas = model_mesas(frame, verbose=False)
        
        annotated = results_coco[0].plot()
        annotated = dibujar_detecciones(annotated, results_mesas, color=(0, 255, 0), label="Mesa")
        
        cv2.imshow('Detecciones', annotated)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\nInterrumpido")
except Exception as e:
    print(f"\nError: {e}")
finally:
    cap.release()
    cv2.destroyAllWindows()
    print("\nFinalizado")