from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.core.deps import get_current_user
from app.core.rbac import require_roles
from app.models.user import User
from app.schemas.message import MessageCreate, MessageOut, UnreadCountOut, UserMessageOut
from app.services import message_service

router = APIRouter(prefix="/messages", tags=["Messages"])


def _enrich(db: Session, msgs):
    out = []
    for m in msgs:
        sender = db.query(User).filter(User.id == m.sender_id).first()
        receiver = db.query(User).filter(User.id == m.receiver_id).first() if m.receiver_id else None
        out.append(MessageOut(
            id=m.id,
            sender_id=m.sender_id,
            sender_name=sender.full_name or sender.username if sender else None,
            receiver_id=m.receiver_id,
            receiver_name=receiver.full_name or receiver.username if receiver else None,
            content=m.content,
            is_general=m.is_general,
            created_at=m.created_at,
            read_at=m.read_at,
        ))
    return out


@router.get("/usuarios-disponibles")
def usuarios_disponibles(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role == "consulta":
        return []
    allowed_roles = ["admin", "oficina", "deposito"] if user.role == "admin" else [user.role, "oficina" if user.role == "deposito" else "deposito", "admin"]
    if user.role == "oficina":
        allowed_roles = ["oficina", "deposito", "admin"]
    if user.role == "deposito":
        allowed_roles = ["deposito", "oficina", "admin"]
    q = db.query(User).filter(User.role.in_(allowed_roles), User.is_active == True, User.id != user.id)
    return [UserMessageOut(id=u.id, username=u.username, full_name=u.full_name, role=u.role) for u in q.all()]


@router.get("/general")
def list_general(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role == "consulta":
        raise HTTPException(status_code=403, detail="Sin permisos")
    msgs = message_service.get_general_messages(db)
    return _enrich(db, msgs)


@router.get("/privados")
def list_privados(other_id: int | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role == "consulta":
        raise HTTPException(status_code=403, detail="Sin permisos")
    if user.role == "admin":
        msgs = message_service.get_all_private_messages_admin(db)
    else:
        msgs = message_service.get_private_messages(db, user.id, other_id)
    return _enrich(db, msgs)


@router.post("/")
def send_message(data: MessageCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role == "consulta":
        raise HTTPException(status_code=403, detail="Sin permisos")
    msg = message_service.create_message(db, user.id, data)
    return _enrich(db, [msg])[0]


@router.get("/no-leidos")
def unread_count(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role == "consulta":
        return UnreadCountOut(total=0)
    count = message_service.get_unread_count(db, user.id)
    return UnreadCountOut(total=count)


@router.post("/{message_id}/leer")
def mark_read(message_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role == "consulta":
        raise HTTPException(status_code=403, detail="Sin permisos")
    message_service.mark_as_read(db, message_id, user.id)
    return {"ok": True}
