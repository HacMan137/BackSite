import json
from flask import Blueprint, request, jsonify
from backsite.db.schema import User, Session
from backsite.db.connection import create_connection
from backsite.app.utils import requires, pattern, send_rabbitmq_message, optional, log
from backsite.app.utils import PASSWORD_REGEX, EMAIL_REGEX, USERNAME_REGEX
from functools import wraps

user_app = Blueprint("user", __name__, template_folder="templates")

def get_token():
    '''
    Retrieve the session token from request cookies
    '''
    return request.cookies.get("session", "")

def get_session_user(conn):
    token = get_token()
    session = Session.validate(token, conn)
    return session.user

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
            for required in required_permissions:
                if required not in user.all_permissions:
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
    conn = create_connection()
    u = User.authenticate(username, password, conn)

    if u is None:
        conn.close()
        return json.dumps({"success": False, "msg": "Invalid username or password"})
    
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
    "username": (USERNAME_REGEX, 'Username must be at least 6 characters long'),
    "email": (EMAIL_REGEX, 'Email must be in the form XXX@XXX.XXX'),
    "password": (PASSWORD_REGEX, 'Password must be at least 8 characters long'),
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

@user_app.route("/api/user/<user_id>", methods=["PATCH"])
@authorized()
@optional({
    "username": (USERNAME_REGEX, 'Username must be at least 6 characters long'),
    "email": (EMAIL_REGEX, 'Email must be in the form XXX@XXX.XXX'),
    "old_password": str,
    "password": (PASSWORD_REGEX, 'Password must be at least 8 characters long'),
})
def update_user(username: str, email: str, old_password: str, password: str, user_id: str):
    # Open a database connection 
    user_id = int(user_id)
    conn = create_connection()
    session_user = get_session_user(conn)
    log(f"Session user id: {session_user.user_id}")
    # Verify that we have proper permissions to modify this user
    if session_user.user_id != user_id and "ModifyUser" not in session_user.all_permissions:
        return {"success": False, "msg": f"You do not have the proper permissions to modify this user"}
    # Lookup user by ID
    user = conn.query(User).where(User.user_id == user_id).first()
    if user is None:
        return {"success": False, "msg": f"Couldn't find user with ID {user_id}"}
    success = True
    error_message = ""
    # Modify username
    if username != "":
        if not User.username_in_use(username):
            user.username = username
        else:
            error_message += f"Couldn't update username, username {username} is already in use. "
    # Modify email
    if email != "":
        if not User.email_in_use(email):
            user.email = email
            user.verified = False
        else:
            error_message += f"Couldn't update email address, address {email} is already in use. "
    # Modify password
    passwordChangeSuccess = False
    if old_password != "" and password != "":
        passwordChangeSuccess = user.change_password(old_password, password)
        if not passwordChangeSuccess:
            error_message += "Couldn't update password. Check that you provided the correct current password. "
        success = success and passwordChangeSuccess
    # Check that all modifications were successful,
    # Update user in DB and trigger any needed jobs from modification changes
    if success:
        if email != "":
            send_verification_email(user)
        if passwordChangeSuccess:
            user.clear_sessions(conn)
        conn.add(user)
        conn.commit()
        conn.close()
        return {"success": True, "msg": "Changes made successfully"}
    return {"success": False, "msg": error_message.strip()}