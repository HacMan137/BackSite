from sqlalchemy.orm import scoped_session, sessionmaker
# Import Base
from backsite.db.schema.base import Base
# Import all table classes for easy access
from backsite.db.schema.user import User
from backsite.db.schema.session import Session
from backsite.db.schema.permission import Permission, user_permissions
from backsite.db.schema.group import Group, user_groups, group_permissions

DBSession = scoped_session(sessionmaker())