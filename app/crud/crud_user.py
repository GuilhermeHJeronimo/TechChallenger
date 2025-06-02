from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import user as user_model
from app.schemas import user_schemas
from app.core.security import get_password_hash

def get_user(db: Session, user_id: int) -> Optional[user_model.User]:

    return db.query(user_model.User).filter(user_model.User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[user_model.User]:

    return db.query(user_model.User).filter(user_model.User.username == username).first()

def create_user(db: Session, user_create_schema: user_schemas.UserCreate) -> user_model.User:

    hashed_password = get_password_hash(user_create_schema.password)
    
    db_user = user_model.User(
        username=user_create_schema.username,
        full_name=user_create_schema.full_name,
        hashed_password_sha256=hashed_password,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
