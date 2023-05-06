from sqlalchemy import Column, String, Integer
from backsite.db.schema import Base

class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key = True, autoincrement = True)
    email = Column(String(length=512), nullable = False, unique = True)
    username = Column(String(length=64), nullable = False, unique = True)
    password_hash = Column(String(length=128), nullable=False)

    @property
    def json(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "username": self.username,
        }