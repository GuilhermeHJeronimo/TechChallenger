from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password_sha256 = Column(String, nullable=False)
    full_name = Column(String, index=True, nullable=True)
    disabled = Column(Boolean, default=False)

    def __repr__(self):
        return f"<User(username='{self.username}', full_name='{self.full_name}')>"