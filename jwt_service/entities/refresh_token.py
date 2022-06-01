import uuid

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID

from libs.domain.database import Base


class RefreshToken(Base):
    __tablename__ = 'refresh_token'

    token = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exp = Column(DateTime)

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    user = relationship('User', backref=backref('refresh_token', uselist=False))
