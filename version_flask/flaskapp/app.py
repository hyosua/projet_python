from flask import Flask
from flask_login import LoginManager, current_user
from config import Config
from storage import get_user
from schemas import LoginUser

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(email: str):
        u = get_user(email)
        return LoginUser(u) if u else None

    @app.get("/")
    def index():
        # Petite page texte pour test rapide
        # (ton template index.html est optionnel)
        if getattr(current_user, "is_authenticated", False):
            return "OK – Flask (Pickle only) – Connecté"
        return "OK – Flask (Pickle only)"

    # Blueprints
    from auth import bp as auth_bp
    from author import bp as author_bp
    from public import bp as public_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(author_bp)
    app.register_blueprint(public_bp)

    return app

if __name__ == "__main__":
    create_app().run(debug=True)
