import uuid6
from sqlalchemy import Column, String, Float, Integer, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID 
from .database import Base 


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
    name = Column(String, unique=True, nullable=False)
    gender = Column(String)
    gender_probability = Column(Float)
    age = Column(Integer)
    age_group = Column(String)
    country_id = Column(String(2))
    country_name = Column(String)
    country_probability = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_profiles_search', 'gender', 'age_group', 'country_id'),
    )