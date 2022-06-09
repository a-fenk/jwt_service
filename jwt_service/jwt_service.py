from uuid import UUID, uuid4
from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, status
from redis import Redis

from .dto import JWTPayloadDTO, JWTDTO, AccessTokenDTO
from .error_messages import ErrorMessages

class JWTService:
    def __init__(
            self,
            secret: str,
            algorithm: str,
            access_token_expire_minutes: int,
            refresh_token_expire_minutes: int,
            client: Redis,
            access_token_prefix: str = 'bearer ',
    ):
        self.__secret = secret
        self.__algorithm = algorithm
        self.__access_token_expire_minutes = access_token_expire_minutes
        self.__refresh_token_expire_minutes = refresh_token_expire_minutes
        self.__client = client
        self.__access_token_prefix = access_token_prefix

    def _generate_access_token(self, payload: JWTPayloadDTO) -> AccessTokenDTO:
        return AccessTokenDTO(
            token=self.__access_token_prefix + jwt.encode(
                payload=payload.dict(),
                key=self.__secret,
                algorithm=self.__algorithm,
            )
        )

    def _generate_refresh_token(self, user_id: UUID) -> UUID:
        token = uuid4()

        while self.__client.exists(token.bytes):
            if self.__client.get(token.bytes) == user_id:
                self.__client.delete(token.bytes)
            else:
                token = uuid4()

        self.__client.set(
            name=token.bytes,
            value=user_id.bytes,
            ex=timedelta(minutes=self.__refresh_token_expire_minutes)
        )
        return token

    def _decode_access_token(self, token: str) -> JWTPayloadDTO:
        token = token.removeprefix(self.__access_token_prefix)
        return JWTPayloadDTO(
            **jwt.decode(
                jwt=token,
                key=self.__secret,
                algorithms=[self.__algorithm],
            )
        )

    def decode_jwt(self, token) -> JWTPayloadDTO:
        try:
            return self._decode_access_token(token)

        except jwt.ExpiredSignatureError:
            error = ErrorMessages.TOKEN_EXPIRED

        except jwt.InvalidTokenError:
            error = ErrorMessages.INVALID_TOKEN

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={'WWW-Authenticate': 'Bearer'},
        )

    def generate_jwt(
            self,
            user_id: UUID
    ) -> JWTDTO:
        now = datetime.utcnow()

        return JWTDTO(
            access_token=self._generate_access_token(
                payload=JWTPayloadDTO(
                    id=user_id.hex,
                    iat=now,
                    exp=now + timedelta(minutes=self.__access_token_expire_minutes),
                )
            ).token,
            refresh_token=self._generate_refresh_token(
                user_id,
            ),
        )

    def refresh_jwt(self, data: JWTDTO) -> JWTDTO:
        try:
            self._decode_access_token(data.access_token)

        except jwt.ExpiredSignatureError:
            if self.__client.exists(data.refresh_token.bytes):
                user_id = UUID(bytes=bytes(self.__client.get(data.refresh_token.bytes)))
                return self.generate_jwt(user_id)

        except jwt.InvalidTokenError as e:
            if self.__client.exists(data.refresh_token.bytes):
                self.__client.delete(data.refresh_token.bytes)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessages.INVALID_TOKEN,
        )

    def invalidate_jwt(self, data: JWTDTO) -> None:
        try:
            self._decode_access_token(data.access_token)

        except jwt.ExpiredSignatureError:
            if self.__client.exists(data.refresh_token.bytes):
                self.__client.delete(data.refresh_token.bytes)

        except jwt.InvalidTokenError as e:
            if self.__client.exists(data.refresh_token.bytes):
                self.__client.delete(data.refresh_token.bytes)
