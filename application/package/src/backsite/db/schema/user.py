import hashlib
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship, Mapped
from backsite.db.schema import Base
from backsite.db.connection import create_connection

HASH_FUNCTION = hashlib.sha512

class User(Base):
    __tablename__ = "backsite_user"

    user_id = Column(Integer, primary_key = True, autoincrement = True)
    email = Column(String(length=512), nullable = False, unique = True)
    username = Column(String(length=64), nullable = False, unique = True)
    password_hash = Column(String(length=128), nullable=False)

    sessions = relationship("Session", back_populates="user")
    permissions = relationship("Permission", secondary="user_permissions", back_populates="users")

    @property
    def json(self) -> dict:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "username": self.username,
        }
    
    @classmethod
    def create_user(cls, username, email, password):
        # FIXME: Prepend pre-generated salt to password
        u = User(username=username, email=email, password_hash=HASH_FUNCTION(password.encode()).hexdigest())
        return u
    
    @classmethod
    def authenticate(cls, username, password):
        # FIXME: Prepend pre-generated salt to password
        given_hash = HASH_FUNCTION(password.encode()).hexdigest()
        conn = create_connection()
        user = conn.query(cls).where(cls.username == username, cls.password_hash == given_hash).first()
        conn.close()

        return user