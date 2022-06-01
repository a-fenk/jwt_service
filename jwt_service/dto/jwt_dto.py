from uuid import UUID

from ..dto_model import DTOModel


class JWTDTO(DTOModel):
    access_token: str
    refresh_token: UUID
