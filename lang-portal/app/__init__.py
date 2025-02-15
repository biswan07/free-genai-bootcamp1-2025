from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()

def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    if test_config == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lang_portal.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import models to ensure they are registered with SQLAlchemy
    from . import models
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        
        # Add sample data if database is empty
        if not models.Word.query.first():
            # Add sample words
            words = [
                {'french': 'bonjour', 'english': 'hello'},
                {'french': 'au revoir', 'english': 'goodbye'},
                {'french': 'merci', 'english': 'thank you'},
                {'french': 'oui', 'english': 'yes'},
                {'french': 'non', 'english': 'no'},
                {'french': 'chat', 'english': 'cat'},
                {'french': 'chien', 'english': 'dog'},
                {'french': 'maison', 'english': 'house'},
                {'french': 'école', 'english': 'school'},
                {'french': 'livre', 'english': 'book'},
                {'french': 'table', 'english': 'table'},
                {'french': 'chaise', 'english': 'chair'},
                {'french': 'fenêtre', 'english': 'window'},
                {'french': 'porte', 'english': 'door'},
                {'french': 'voiture', 'english': 'car'}
            ]
            for word_data in words:
                word = models.Word(**word_data)
                db.session.add(word)
            
            # Add sample groups
            groups = ['Basic Greetings', 'Numbers', 'Colors']
            for group_name in groups:
                group = models.Group(name=group_name)
                db.session.add(group)
            
            db.session.commit()
    
    from .routes import api
    app.register_blueprint(api)
    
    return app
