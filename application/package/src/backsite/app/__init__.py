'''
Package to run BackSite Flask Application
'''
from flask import Flask
from flask import request
from flask_cors import CORS
from backsite.app.basic import basic_app

# Create app and set CORS
def create_application():
    app = Flask(__name__)
    
    app.register_blueprint(basic_app)
    
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    
    app.config["CORS_HEADER"] = "Content-Type"
    
    return app
