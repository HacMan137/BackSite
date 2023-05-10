import hashlib
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship, Mapped
from backsite.db.schema import Base
from backsite.db.connection import create_connection
from uuid import uuid4

HASH_FUNCTION = hashlib.sha512

def generate_salt():
    '''
    Generate a random salt value to be used for hash generation
    '''
    return str(uuid4()).replace("-","")

def generate_user_identifier():
    '''
    Generate a random user identifier to be used for user-specific links
    '''
    return (str(uuid4()) + str(uuid4())).replace("-","")

class User(Base):
    __tablename__ = "backsite_user"

    # Auto-incrementing unique user ID
    user_id = Column(Integer, primary_key = True, autoincrement = True)
    # User email address
    email = Column(String(length=512), nullable = False, unique = True)
    # Username
    username = Column(String(length=64), nullable = False, unique = True)
    # Salted password hash
    password_hash = Column(String(length=128), nullable=False)
    # Salt used to generate password hash
    salt = Column(String(length=32), nullable=False, default=generate_salt)
    # Boolean indicating whether user has successfully completed email verification
    verified = Column(Boolean, nullable=False, default=False)
    # Unique user identifier used to generation user-specific links
    user_identifier = Column(String(length=64), nullable=False, default=generate_user_identifier)

    # List of active sessions attributed to this user
    sessions = relationship("Session", back_populates="user")
    # List of permissions assigned to the user
    permissions = relationship("Permission", secondary="user_permissions", back_populates="users")

    @property
    def json(self) -> dict:
        '''
        Return JSON representation of the user
        '''
        return {
            "user_id": self.user_id,
            "email": self.email,
            "username": self.username,
            "verified": self.verified,
        }
    
    @classmethod
    def calculate_salted_hash(cls, salt: str, password: str):
        '''
        Generate a hash based on the given salt and password
        '''
        # Take half the salt and prepend it to the password
        pre_salt = salt[:16]
        # Take the other half and append it to the password
        post_salt = salt[16:]
        salted_password = pre_salt + password + post_salt
        # Calculate salted hash
        return HASH_FUNCTION(salted_password.encode()).hexdigest()

    @classmethod
    def create_user(cls, username: str, email: str, password: str, verified: bool =False):
        '''
        Create a new user
        '''
        # Generate new salt for user
        salt = generate_salt()
        # Apply salt to given password and calculate the hash
        salted_password_hash = cls.calculate_salted_hash(salt, password)
        # Create new user
        u = User(username=username, email=email, password_hash=salted_password_hash, salt=salt, verified=verified)
        return u
    
    @classmethod
    def authenticate(cls, username: str, password: str):
        '''
        Authenticate a user with the given credentials
        '''
        # Identify user by given username
        conn = create_connection()
        user = conn.query(cls).where(cls.username == username).first()
        # If we couldn't find the user, return None
        if user is None or not user.verified:
            conn.close()
            return None
        # Calculate salted hash using the user's salt and the given password
        salted_password_hash = cls.calculate_salted_hash(user.salt, password)
        
        conn.close()

        # If the calculated hash doesn't match the user's hash, return None
        if salted_password_hash != user.password_hash:
            return None
        
        return user