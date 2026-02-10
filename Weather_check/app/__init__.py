from flask import Flask
from config import config

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Register blueprints
    from app.routes import weather_bp
    app.register_blueprint(weather_bp)
    
    return app
