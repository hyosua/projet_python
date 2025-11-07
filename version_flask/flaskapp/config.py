import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # ⚠️ change la clé en prod
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    # Dossier pour les uploads facultatifs si tu en ajoutes plus tard
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
