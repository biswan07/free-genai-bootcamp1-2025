from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .models import db
from .routes import api

def create_app(test_config=None):
    app = Flask(__name__)
    
    if test_config is None:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lang_portal.db'
    else:
        app.config.update(test_config)
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    app.register_blueprint(api)
    
    return app
