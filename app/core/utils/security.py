from app.core.config import settings
from fastapi_login import LoginManager

login_manager = LoginManager(settings.SECRET, settings.TOKEN_URL)

class Hasher:
    @staticmethod
    def hash_password(plaintext: str):
        return login_manager.pwd_context.hash(plaintext)

    @staticmethod
    def verify_password(plaintext: str, hashed: str):
        return login_manager.pwd_context.verify(plaintext, hashed)
