from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class AuthUser:
    id: UUID
    email: str
    full_name: str
    password_hash: str
    created_at: datetime
