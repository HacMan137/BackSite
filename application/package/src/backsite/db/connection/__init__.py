import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

DATABASE_NAME = os.environ.get("POSTGRES_DB_NAME", "backsite")
DATABASE_HOST = os.environ.get("POSTGRES_HOST", "db")
DATABASE_PORT = os.environ.get("POSTGRES_PORT", "5432")
DATABASE_USERNAME = os.environ.get("POSTGRES_USER", "backsite")
DATABASE_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "backsite")

def create_sql_engine():
    db_string = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

    db = create_engine(db_string)

    return db

def create_connection():
    db = create_sql_engine()

    return Session(db)