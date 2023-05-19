from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped
from backsite.db.schema import Base
from backsite.db.schema.permission import DEFAULT_PERMISSIONS, Permission
from backsite.db.connection import create_connection

DEFAULT_GROUPS = {
    "Administrators": DEFAULT_PERMISSIONS,
    "Moderators": [
        "ModifyUserInformation",
        "DeleteUser",
        "CreatePost",
        "DeletePost",
        "Comment"
    ],
    "Standard Users": [
        "CreatePost",
        "Comment"
    ]
}

user_groups = Table(
    "user_groups",
    Base.metadata,
    Column("user_id", ForeignKey("backsite_user.user_id")),
    Column("group", ForeignKey("group.group_name"))
)

group_permissions = Table(
    "group_permissions",
    Base.metadata,
    Column("group", ForeignKey("group.group_name")),
    Column("permission", ForeignKey("permission.permission_name"))
)

class Group(Base):
    __tablename__ = "group"

    group_name = Column(String(length=255), primary_key=True)
    
    users = relationship("User", secondary=user_groups, back_populates="groups")
    permissions = relationship("Permission", secondary=group_permissions, back_populates="groups")

    @property
    def json(self):
        return {
            "group_name": self.group_name
        }

    @classmethod
    def create_default_groups(cls, conn):
        new_groups = []
        for group in DEFAULT_GROUPS.keys():
            permissions = DEFAULT_GROUPS[group]
            newGroup = Group(group_name=group)
            for permission in permissions:
                permission_obj = conn.query(Permission).where(Permission.permission_name == permission).first()
                if permission_obj is not None:
                    newGroup.permissions.append(permission_obj)
            conn.add(newGroup)
            conn.commit()
            new_groups.append(newGroup)
        return new_groups