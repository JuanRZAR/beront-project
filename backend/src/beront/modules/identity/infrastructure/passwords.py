import secrets

from werkzeug.security import check_password_hash, generate_password_hash


class WerkzeugPasswordHasher:
    def __init__(self):
        self.dummy_hash = self.hash(secrets.token_urlsafe(32))

    @staticmethod
    def hash(password):
        return generate_password_hash(password, method="scrypt")

    @staticmethod
    def verify(password_hash, password):
        return check_password_hash(password_hash, password)
