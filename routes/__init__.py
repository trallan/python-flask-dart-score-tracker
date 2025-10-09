from .scoreboard import scoreboard_bp
from .adminPanel import adminPanel_bp

def register_blueprints(app):
    app.register_blueprint(scoreboard_bp)
    app.register_blueprint(adminPanel_bp)