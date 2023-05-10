from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backsite.db.schema import Base
from backsite.db.connection import create_connection
from uuid import uuid4
from datetime import datetime, timedelta

def generate_uuid():
    return uuid4().hex

def generate_expiration():
    '''
    Helper function to generate the expiration date of a session
    '''
    return datetime.utcnow() + timedelta(days=14)

def clear_expired_sessions(conn):
    now = datetime.utcnow()
    sessions = conn.query(Session).where(Session.expiration <= now).all()
    for s in sessions:
        conn.delete(s)
    conn.commit()

class Session(Base):
    '''
    Class for the table used to keep track of user sessions
    '''
    __tablename__ = "session"

    user_id = Column(ForeignKey("backsite_user.user_id", ondelete="CASCADE"), primary_key = True, nullable=False)
    expiration = Column(
        DateTime,
        nullable=False,
        default=generate_expiration
    )
    token = Column(
        String(length=32),
        nullable=False,
        primary_key=True,
        default=generate_uuid
    )

    user = relationship("User", back_populates="sessions")

    @property
    def json(self):
        return {
            "user_id": self.user_id,
            "expiration": self.expiration.toisoformat(),
            "token": self.token
        }
    
    @classmethod
    def validate(cls, token: str, conn):
        '''
        Validate the given token
        '''
        session = conn.query(cls).where(cls.token == token).first()

        clear_expired_sessions(conn)

        return session