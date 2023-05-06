from sqlalchemy.orm import scoped_session, sessionmaker
# Import Base
from backsite.db.schema.base import Base
# Import all table classes for easy access
from backsite.db.schema.user import User

DBSession = scoped_session(sessionmaker())