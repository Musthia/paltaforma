from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.message import Message
from app.schemas.message import MessageCreate

def create_message(db: Session, sender_id: int, data: MessageCreate) -> Message:
    msg = Message(
        sender_id=sender_id,
        receiver_id=data.receiver_id,
        content=data.content,
        is_general=data.is_general,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def get_general_messages(db: Session, skip: int = 0, limit: int = 50):
    return (
        db.query(Message)
        .filter(Message.is_general == True)
        .order_by(Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_private_messages(db: Session, user_id: int, other_id: int | None = None, skip: int = 0, limit: int = 50):
    q = db.query(Message).filter(Message.is_general == False)
    if other_id:
        q = q.filter(
            or_(
                (Message.sender_id == user_id) & (Message.receiver_id == other_id),
                (Message.sender_id == other_id) & (Message.receiver_id == user_id),
            )
        )
    else:
        q = q.filter(
            or_(Message.sender_id == user_id, Message.receiver_id == user_id)
        )
    return q.order_by(Message.created_at.desc()).offset(skip).limit(limit).all()

def get_unread_count(db: Session, user_id: int) -> int:
    return (
        db.query(Message)
        .filter(
            Message.receiver_id == user_id,
            Message.read_at == None,
        )
        .count()
    )

def mark_as_read(db: Session, message_id: int, user_id: int):
    from datetime import datetime, timezone
    msg = db.query(Message).filter(Message.id == message_id).first()
    if msg and msg.receiver_id == user_id and msg.read_at is None:
        msg.read_at = datetime.now(timezone.utc)
        db.commit()

def get_all_private_messages_admin(db: Session, skip: int = 0, limit: int = 50):
    return (
        db.query(Message)
        .filter(Message.is_general == False)
        .order_by(Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
