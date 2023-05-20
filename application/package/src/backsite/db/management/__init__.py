from sqlalchemy_utils import database_exists, create_database
# Import all tables we want to create below
from backsite.db.schema import User, Session, Permission, Group, Post
from backsite.db.schema import user_permissions, group_permissions, user_groups
# Import Base and DBSession
from backsite.db.schema import DBSession, Base
from backsite.db.connection import create_sql_engine

CONFIG_FILE = "/opt/config.json"

def create_db(engine):
    if not database_exists(engine.url):
        create_database(engine.url)

def initialize_db():
    engine = create_sql_engine()
    create_db(engine)
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)