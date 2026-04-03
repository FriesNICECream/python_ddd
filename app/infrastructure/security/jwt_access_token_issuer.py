from datetime import UTC, datetime, timedelta

import jwt

from app.config import settings
from app.domain.auth.services import AccessTokenIssuer


class JwtAccessTokenIssuer(AccessTokenIssuer):
    def issue_for_user(self, *, user_id: str, email: str) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": user_id,
            "email": email,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=settings.access_token_expire_minutes)).timestamp()),
        }
        return jwt.encode(payload, settings.access_token_secret, algorithm=settings.access_token_algorithm)
