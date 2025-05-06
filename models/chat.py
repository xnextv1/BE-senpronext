from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid



Base = declarative_base()

class Chat(Base):
    __tablename__ = 'chat'
    chat_session_id = Column(UUID(as_uuid=True), primary_key=True,default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    title = Column(String)


class ChatMessage(Base):
    __tablename__ = 'chat_message'
    chat_id = Column(Integer, primary_key=True)
    chat_session_id = Column(UUID(as_uuid=True), ForeignKey('chat.chat_session_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    chat_message = Column(String)
    emotion = Column(String)


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    password = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    user_type = Column(String)
    created_at = Column(TIMESTAMP)
    username = Column(String)