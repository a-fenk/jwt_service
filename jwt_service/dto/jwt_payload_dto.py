from datetime import datetime
from uuid import UUID

from ..dto_model import DTOModel


class JWTPayloadDTO(DTOModel):
    id: str
    exp: datetime
    iat: datetime

    @property
    def uuid(self):
        return UUID(self.id)
