from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

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
