import json
from flask import Blueprint, request, jsonify
from backsite.db.schema import User, Session
from backsite.db.connection import create_connection

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
            user_permissions = [p.permission_name for p in user.permissions]
            for required in required_permissions:
                if required not in user_permissions:
                    conn.close()
                    return {"success": False, "msg": "Unauthorized."}, 401

            conn.close()
            return f(*args, **kwargs)
        return __authorized
    
    return _authorized

@user_app.route('/api/user/session', methods=["POST"])
def authenticate():
    '''
    Authenticate the user and create a new user session if successful
    '''
    data = request.get_json()
    username = data['username']
    password = data['password']
    
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