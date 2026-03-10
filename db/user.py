from sqlalchemy import Column, Integer, String
from .base import Base, SessionLocal

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="editor") # admin, editor, viewer

def authenticate(username, password):
    """
    Verifies the user's credentials.
    Returns the user's role if successful, otherwise None.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username, User.password == password).first()
        return user.role if user else None
    finally:
        db.close()