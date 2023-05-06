from flask import Flask
from flask import request
from flask_cors import CORS

# Create app and set CORS
app = Flask(__name__)
CORS(app)

# Test Route
@app.route('/')
def hello_world():
    return 'BackSite Web API'