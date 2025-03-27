from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    password = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(TIMESTAMP)