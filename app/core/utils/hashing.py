from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hasher:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return bcrypt_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return bcrypt_context.hash(password)