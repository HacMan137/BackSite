from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship, Mapped
from backsite.db.schema import Base
from backsite.db.connection import create_connection
from uuid import uuid4
from datetime import datetime, timedelta

DEFAULT_PERMISSIONS = [
    "ModifyUserInformation",
    "ModifyUserPermissions"
    "DeleteUser",
    "CreatePost",
    "DeletePost",
    "Comment",
]

user_permissions = Table(
    "user_permissions",
    Base.metadata,
    Column("user_id", ForeignKey("backsite_user.user_id")),
    Column("permission", ForeignKey("permission.permission_name"))
)

class Permission(Base):
    __tablename__ = "permission"

    permission_name = Column(String(length=255), primary_key=True)
    
    users = relationship("User", secondary=user_permissions, back_populates="permissions")
    groups = relationship("Group", secondary="group_permissions", back_populates="permissions")

    @property
    def json(self):
        return {
            "permission_name": self.permission_name
        }

    @classmethod
    def create_default_permissions(cls, conn):
        default_permissions = []
        for p in DEFAULT_PERMISSIONS:
            pObj = Permission(permission_name=p)
            default_permissions.append(pObj)
            conn.add(pObj)
        conn.commit()
        return default_permissions