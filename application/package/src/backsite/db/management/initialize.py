import time
import json
import sys
from sqlalchemy import inspect
from backsite.db.management import initialize_db
from backsite.db.connection import create_sql_engine, create_connection
from backsite.db.schema import User, Permission, Group
from backsite.utils import get_configuration

def populate_db():
    # Get configuration file
    config_data = get_configuration()
    # Create default admin user
    conn = create_connection()
    admin = User.create_user(
        username="admin", 
        email=config_data['ADMIN_EMAIL'], 
        password="admin",
        verified=True
    )
    conn.add(admin)
    # Create default permissions
    default_permissions = Permission.create_default_permissions(conn)
    # Create default groups
    Group.create_default_groups(conn)
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
            sys.stdout.flush()
            retries -= 1
            time.sleep(5)