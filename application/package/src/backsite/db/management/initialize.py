import time
import hashlib
from sqlalchemy import inspect
from backsite.db.management import initialize_db
from backsite.db.connection import create_sql_engine, create_connection
from backsite.db.schema import User, Permission

def populate_db():
    # Create default admin user
    conn = create_connection()
    admin = User.create_user(
        username="admin", 
        email="admin@admin.com", 
        password="admin"
    )
    conn.add(admin)
    # Create default permissions
    default_permissions = Permission.create_default_permissions(conn)
    # Give admin all permissions
    for perm in default_permissions:
        admin.permissions.append(perm)
    # Save database changes
    conn.commit()
    conn.close()


if __name__ == "__main__":
    retries = 30
    while retries > 0:
        try:
            engine = create_sql_engine()
            insp = inspect(engine)
            if (insp.has_table(User.__tablename__)):
                print("Database has already been initialized. Exiting...")
                exit(0)
            initialize_db()
            populate_db()
            break
        except Exception as e:
            print(f"Failed to connect to DB.\n{e}\nRetries left: {retries}")
            retries -= 1
            time.sleep(5)