import uuid

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    password = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    user_type = Column(String)
    created_at = Column(TIMESTAMP)
    username = Column(String)
    description = Column(String)
    image = Column(String)


class Appointment(Base):
    __tablename__ = 'appointment'
    appointment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    therapist_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    patient_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    appointment_time = Column(TIMESTAMP, nullable=False)

