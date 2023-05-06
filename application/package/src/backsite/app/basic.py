from flask import Blueprint

basic_app = Blueprint("basic", __name__, template_folder="templates")

# Test Route
@basic_app.route('/')
def hello_world():
    return 'BackSite Web API'