import base64
import hashlib
import hmac
import os

from app.domain.auth.services import PasswordHasher


class PBKDF2PasswordHasher(PasswordHasher):
    _iterations = 100_000
    _algorithm = "sha256"

    def hash_password(self, password: str) -> str:
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac(
            self._algorithm,
            password.encode("utf-8"),
            salt,
            self._iterations,
        )
        salt_encoded = base64.b64encode(salt).decode("utf-8")
        digest_encoded = base64.b64encode(digest).decode("utf-8")
        return f"{self._algorithm}${self._iterations}${salt_encoded}${digest_encoded}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        try:
            algorithm, iterations, salt_encoded, digest_encoded = password_hash.split("$", maxsplit=3)
            salt = base64.b64decode(salt_encoded.encode("utf-8"))
            expected_digest = base64.b64decode(digest_encoded.encode("utf-8"))
            actual_digest = hashlib.pbkdf2_hmac(
                algorithm,
                password.encode("utf-8"),
                salt,
                int(iterations),
            )
        except (ValueError, TypeError):
            return False

        return hmac.compare_digest(actual_digest, expected_digest)
