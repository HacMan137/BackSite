import json
from flask import Blueprint, request, jsonify
from backsite.db.schema import User, Session
from backsite.db.connection import create_connection

user_app = Blueprint("user", __name__, template_folder="templates")

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
def logout():
    '''
    Logout the authenticated user
    '''
    token = get_token()
    conn = create_connection()

    session = conn.query(Session).where(Session.token == token).first()

    if session is None:
        conn.close()
        return json.dumps({"success": False, "msg": "Couldn't find a session"})
    
    conn.delete(session)
    conn.commit()
    conn.close()

    response = jsonify({"success": True})
    response.delete_cookie("session")

    return response

def get_token():
    return request.cookies.get("session", "")