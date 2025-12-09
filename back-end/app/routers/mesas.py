from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import asyncio
import json
import time
from datetime import datetime
from app.database import get_db
from app.models.mesa import Mesa
from app.models.usuario_admin import UsuarioAdmin
from app.schemas.mesa import MesaCreate, MesaUpdate, MesaWithTipoResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/mesas", tags=["Gestión de Mesas"])

# ============= SISTEMA DE EVENTOS EN TIEMPO REAL =============
# Cola global para distribuir eventos a todos los clientes conectados
# Cada cliente SSE tendrá su propia cola para recibir actualizaciones
event_queues: List[asyncio.Queue] = []

# Event loop principal (se establece cuando arranca la aplicación)
main_event_loop: asyncio.AbstractEventLoop | None = None


async def event_generator(request: Request):
    """
    Generador de eventos SSE (Server-Sent Events).

    ¿Qué hace?
    - Crea una cola personal para este cliente
    - Se mantiene conectado enviando eventos cuando hay cambios
    - Se desconecta automáticamente si el cliente cierra la conexión

    Formato SSE:
    data: {"type": "mesa_update", "data": {...}}\n\n
    """
    # Guardar referencia al event loop principal si aún no lo hemos hecho
    global main_event_loop
    if main_event_loop is None:
        main_event_loop = asyncio.get_event_loop()

    # Crear cola personal para este cliente
    queue = asyncio.Queue()
    event_queues.append(queue)

    try:
        # Enviar evento inicial de conexión
        yield f"data: {json.dumps({'type': 'connected', 'message': 'Conectado al stream de mesas'})}\n\n"

        # Loop infinito esperando eventos
        while True:
            # Verificar si el cliente cerró la conexión
            if await request.is_disconnected():
                break

            try:
                # Esperar evento con timeout de 30 segundos
                # El timeout evita que la conexión se cierre por inactividad
                event = await asyncio.wait_for(queue.get(), timeout=30.0)

                # Enviar evento al cliente en formato SSE
                yield f"data: {json.dumps(event)}\n\n"

            except asyncio.TimeoutError:
                # Enviar heartbeat cada 30s para mantener conexión viva
                yield f": heartbeat\n\n"

    except asyncio.CancelledError:
        # Cliente desconectado
        pass
    finally:
        # Limpiar: remover cola cuando el cliente se desconecta
        event_queues.remove(queue)


def broadcast_mesa_update(mesas_data: List[dict]):
    """
    Difunde actualizaciones de mesas a TODOS los clientes conectados.

    Parámetros:
    - mesas_data: Lista de diccionarios con datos de las mesas actualizadas

    Llamado desde: mqtt_service.py cuando detecta cambios en las mesas

    NOTA: Esta función es llamada desde un thread MQTT (síncrono),
    por lo que debe ser thread-safe usando call_soon_threadsafe.
    """
    global main_event_loop

    if not event_queues:
        print("   [SSE] No hay clientes conectados")
        return  # No hay clientes conectados

    if main_event_loop is None:
        print("   [SSE] Event loop no disponible aún (esperando primera conexión)")
        return

    # Crear evento
    event = {
        "type": "mesa_update",
        "data": mesas_data,
        "timestamp": datetime.now().isoformat()
    }

    # Enviar a todas las colas de forma thread-safe
    eventos_enviados = 0
    for queue in event_queues[:]:  # Copiar lista para evitar problemas de concurrencia
        try:
            # Usar call_soon_threadsafe para que sea thread-safe desde otro thread
            main_event_loop.call_soon_threadsafe(queue.put_nowait, event)
            eventos_enviados += 1
        except Exception as e:
            print(f"   [SSE] Error enviando evento a cliente: {e}")

    print(f"   [SSE] ✅ Evento enviado a {eventos_enviados} cliente(s) conectado(s)")


@router.get("/", response_model=List[MesaWithTipoResponse])
def listar_mesas(
    estado: str | None = Query(None, description="Filtrar por estado"),
    id_tipo_mesa: int | None = Query(None, description="Filtrar por tipo de mesa"),
    db: Session = Depends(get_db)
):
    """
    Lista todas las mesas con sus tipos y reservaciones activas.
    Endpoint público para consulta.
    """
    from app.models.reservacion import Reservacion
    from datetime import date

    query = db.query(Mesa)

    if estado:
        query = query.filter(Mesa.estado == estado)
    if id_tipo_mesa:
        query = query.filter(Mesa.id_tipo_mesa == id_tipo_mesa)

    mesas = query.all()

    # Enriquecer con información de reservaciones activas
    hoy = date.today()
    mesas_con_info = []
    for mesa in mesas:
        mesa_dict = {
            "id_mesa": mesa.id_mesa,
            "id_tipo_mesa": mesa.id_tipo_mesa,
            "estado": mesa.estado,
            "personas_actuales": mesa.personas_actuales,
            "updated_at": mesa.updated_at,
            "tipo_mesa": mesa.tipo_mesa,
            "reservacion_activa": None
        }

        # Si la mesa está reservada, buscar la reservación activa
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
                    "fecha": reservacion.fecha,
                    "hora": reservacion.hora,
                    "estado": reservacion.estado
                }

        mesas_con_info.append(mesa_dict)

    return mesas_con_info


@router.get("/stream-updates")
async def stream_mesas(request: Request):
    """
    🔴 ENDPOINT DE ACTUALIZACIONES EN TIEMPO REAL (SSE)

    Este endpoint mantiene una conexión abierta con el cliente y envía
    actualizaciones automáticamente cuando cambia el estado de las mesas.

    Protocolo: Server-Sent Events (SSE)
    URL: GET /api/v1/mesas/stream
    Content-Type: text/event-stream

    ¿Cómo funciona?
    1. El cliente se conecta a este endpoint
    2. El servidor mantiene la conexión abierta
    3. Cuando MQTT detecta cambios en las mesas, se envía un evento
    4. El cliente recibe el evento automáticamente y actualiza la UI

    Eventos emitidos:
    - connected: Confirmación de conexión exitosa
    - mesa_update: Actualización de estado de mesas
    - heartbeat: Señal cada 30s para mantener conexión viva

    Ejemplo de uso en JavaScript:
    ```javascript
    const eventSource = new EventSource('http://localhost:8000/api/v1/mesas/stream');
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'mesa_update') {
            console.log('Mesas actualizadas:', data.data);
        }
    };
    ```
    """
    return StreamingResponse(
        event_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Deshabilitar buffering en Nginx
        }
    )


@router.get("/{mesa_id}", response_model=MesaWithTipoResponse)
def obtener_mesa(
    mesa_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles de una mesa específica.
    """
    mesa = db.query(Mesa).filter(Mesa.id_mesa == mesa_id).first()

    if not mesa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada"
        )

    return mesa


@router.post("/", response_model=MesaWithTipoResponse, status_code=status.HTTP_201_CREATED)
def crear_mesa(
    mesa_data: MesaCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_user)
):
    """
    Crea una nueva mesa.
    Requiere autenticación de administrador.
    """
    from app.models.tipo_mesa import TipoMesa

    # Verificar que el tipo de mesa existe
    tipo_mesa = db.query(TipoMesa).filter(TipoMesa.id_tipo_mesa == mesa_data.id_tipo_mesa).first()
    if not tipo_mesa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de mesa no encontrado"
        )

    nueva_mesa = Mesa(**mesa_data.model_dump())
    db.add(nueva_mesa)
    db.commit()
    db.refresh(nueva_mesa)

    return nueva_mesa


@router.put("/{mesa_id}", response_model=MesaWithTipoResponse)
def actualizar_mesa(
    mesa_id: int,
    mesa_data: MesaUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_user)
):
    """
    Actualiza una mesa existente.
    Requiere autenticación de administrador.
    """
    mesa = db.query(Mesa).filter(Mesa.id_mesa == mesa_id).first()

    if not mesa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada"
        )

    update_data = mesa_data.model_dump(exclude_unset=True)

    # Si se actualiza el tipo de mesa, verificar que existe
    if "id_tipo_mesa" in update_data:
        from app.models.tipo_mesa import TipoMesa
        tipo_mesa = db.query(TipoMesa).filter(TipoMesa.id_tipo_mesa == update_data["id_tipo_mesa"]).first()
        if not tipo_mesa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de mesa no encontrado"
            )

    for key, value in update_data.items():
        setattr(mesa, key, value)

    db.commit()
    db.refresh(mesa)

    return mesa


@router.delete("/{mesa_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_mesa(
    mesa_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_user)
):
    """
    Elimina una mesa.
    Requiere autenticación de administrador.
    """
    mesa = db.query(Mesa).filter(Mesa.id_mesa == mesa_id).first()

    if not mesa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada"
        )

    # Verificar que no tenga reservaciones activas
    from app.models.reservacion import Reservacion
    reservaciones_activas = db.query(Reservacion).filter(
        Reservacion.id_mesa == mesa_id,
        Reservacion.estado.in_(["pendiente", "confirmada"])
    ).first()

    if reservaciones_activas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar una mesa con reservaciones activas"
        )

    db.delete(mesa)
    db.commit()
    return None
