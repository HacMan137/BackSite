import json
from flask import Blueprint, request, jsonify
from backsite.db.schema import User, Session
from backsite.db.connection import create_connection
from backsite.app.utils import requires, pattern, send_rabbitmq_message
from functools import wraps

user_app = Blueprint("user", __name__, template_folder="templates")

def get_token():
    '''
    Retrieve the session token from request cookies
    '''
    return request.cookies.get("session", "")

def authorized(required_permissions = []):
    '''
    Decorator function to wrap API endpoints that require certain permissions
    '''
    def _authorized(f):
        '''
        Receives pointer to the decorated function
        '''
        @wraps(f)
        def __authorized(*args, **kwargs):
            '''
            Receives arguments intended for decorated function
            '''
            conn = create_connection()
            token = get_token()
            session = Session.validate(token, conn)
            if session is None:
                conn.close()
                return {"success": False, "msg": "Unauthorized."}, 401
            
            user = session.user
            user_permissions = user.all_permissions
            for required in required_permissions:
                if required not in user_permissions:
                    conn.close()
                    return {"success": False, "msg": "Unauthorized."}, 401

            conn.close()
            return f(*args, **kwargs)
        return __authorized
    
    return _authorized

@user_app.route('/api/user/session', methods=["POST"])
@requires({
    "username": str,
    "password": str
})
def authenticate(username: str, password: str):
    '''
    Authenticate the user and create a new user session if successful
    '''
    data = request.get_json()
    
    u = User.authenticate(username, password)

    if u is None:
        return json.dumps({"success": False, "msg": "Invalid username or password"})
    
    conn = create_connection()

    s = Session(user_id = u.user_id)

    conn.add(s)
    conn.commit()

    response = jsonify({
        "success": True,
        "user": u.json
    })

    response.set_cookie(
        "session",
        value = s.token,
        httponly = True,
        max_age = 14 * 60 * 60 * 24
    ),

    conn.close()

    return response

@user_app.route("/api/user/session", methods=["DELETE"])
@authorized()
def logout():
    '''
    Logout the authenticated user
    '''
    token = get_token()
    conn = create_connection()
    session = Session.validate(token, conn)
    
    conn.delete(session)
    conn.commit()
    conn.close()

    response = jsonify({"success": True})
    response.delete_cookie("session")

    return response

@user_app.route("/api/user", methods=["POST"])
@requires({
    "username": (r'^.{6,}$', 'Username must be at least 6 characters long'),
    "email": (r'^\w+@\w+\.\w{1,}$', 'Email must be in the form XXX@XXX.XXX'),
    "password": (r'^.{8,}$', 'Password must be at least 8 characters long'),
})
def create_user(username: str, email: str, password: str):
    # Open a database connection and create the user
    conn = create_connection()
    # Make sure username and email are unique
    if User.email_in_use(email):
        return {"success": False, "msg": f"Email {email} is already in use."}
    if User.username_in_use(username):
        return {"success": False, "msg": f"Username {username} is already in use"}
    # Create user object
    u = User.create_user(username, email, password)
    # Add it to the database
    conn.add(u)
    conn.commit()
    # Trigger job to send verification email
    job_sent = send_verification_email(u)
    conn.close()
    # Return error if we couldn't complete the request
    if not job_sent:
        return {"success": False, "msg": "Unable to communicate with backend services. Please try again later."}
    # Return success
    return {"success": True, "msg": "User created!"}

def send_verification_email(user: User):

    data = {
        "command": "sendVerificationEmail",
        "params": {
            "username": user.username,
            "email": user.email,
            "secret": user.user_secret
        }
    }

    return send_rabbitmq_message(data, "email_jobs")

@user_app.route('/api/user/verification', methods=["POST"])
@requires({
    "username": str,
    "password": str,
    "secret": str
})
def verify_email(username: str, password: str, secret: str):
    '''
    Authenticate the user and verify their account with the given secret
    '''
    data = request.get_json()
    conn = create_connection()
    u = User.verify(username, password, secret, conn)

    if u is None:
        conn.close()
        return {"success": False, "msg": f"Couldn't verify user {username}"}

    # Create new user session
    s = Session(user_id = u.user_id)

    conn.add(s)
    conn.commit()

    # Build response
    response = jsonify({
        "success": True,
        "user": u.json
    })
    # Set session cookie
    response.set_cookie(
        "session",
        value = s.token,
        httponly = True,
        max_age = 14 * 60 * 60 * 24
    ),
    # Close connection
    conn.close()
    # Return response
    return response
