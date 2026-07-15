import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.solicitud import Solicitud
from app.core.ws_manager import manager

router = APIRouter()

POLL_SECONDS = 5


async def poll_new():
    max_pendiente = 0
    max_respondida = 0
    ready = False

    while True:
        await asyncio.sleep(POLL_SECONDS)
        try:
            db = SessionLocal()

            pendiente_max = db.query(func.max(Solicitud.id)).filter(
                Solicitud.estado == "pendiente"
            ).scalar() or 0

            respondida_max = db.query(func.max(Solicitud.id)).filter(
                Solicitud.estado == "respondida"
            ).scalar() or 0

            db.close()

            if not ready:
                max_pendiente = pendiente_max
                max_respondida = respondida_max
                ready = True
                continue

            if pendiente_max > max_pendiente:
                await manager.broadcast_json({
                    "tipo": "pendiente",
                    "max_id": pendiente_max,
                })
                max_pendiente = pendiente_max

            if respondida_max > max_respondida:
                await manager.broadcast_json({
                    "tipo": "respondida",
                    "max_id": respondida_max,
                })
                max_respondida = respondida_max

        except Exception:
            pass


@router.websocket("/ws/notificaciones")
async def notificaciones(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)


def start_poller():
    asyncio.create_task(poll_new())
