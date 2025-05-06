from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict, List
from collections import defaultdict

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.ai import predict_emotion, predict_response
from core.db import get_db
from core.security import decode_jwt_token
from models.chat import ChatMessage, Chat
from pydantic import BaseModel

router = APIRouter()

class ChatCreate(BaseModel):
    chat_title: str
    user_id: int

class ChatMessageSchema(BaseModel):
    chat_id: int
    chat_session_id: UUID
    is_ai: bool
    chat_message: str

    class Config:
        orm_mode = True

class ChatSessionSchema(BaseModel):
    chat_session_id: UUID
    user_id: int
    title: str

    class Config:
        orm_mode = True

class ConnectionManager:
    def __init__(self):
        self.rooms: Dict[str, List[WebSocket]] = defaultdict(list)
        self.user_map: Dict[WebSocket, int] = {}  # Store user_id for each connection

    async def connect(self, room: str, websocket: WebSocket, user_id: int):
        """ Connect user to a room and save the user mapping. """
        await websocket.accept()
        self.rooms[room].append(websocket)
        self.user_map[websocket] = user_id
        return user_id

    def disconnect(self, room: str, websocket: WebSocket):
        """ Disconnect user from a room and clean up the mapping. """
        if websocket in self.rooms[room]:
            self.rooms[room].remove(websocket)
        self.user_map.pop(websocket, None)
        if not self.rooms[room]:
            del self.rooms[room]

    async def broadcast(self, room: str, message: str):
        """ Broadcast a message to all connected users in a room. """
        for connection in self.rooms.get(room, []):
            await connection.send_text(message)

manager = ConnectionManager()
logger = logging.getLogger(__name__)

@router.websocket("/ws/{chat_session_id}")
async def websocket_chat(websocket: WebSocket, chat_session_id: str):
    db_gen = get_db()
    db: AsyncSession = await anext(db_gen)  # Get session from generator

    # Step 1: Get token from cookies
    token = websocket.cookies.get("token")
    if not token:
        print("Websocket token is missing")
        await websocket.close(code=1008)  # Close if token is not provided
        return

    try:
        # Step 2: Decode the token and get user_id
        decoded_token = decode_jwt_token(token)  # Decode JWT token to get user_id
        user_id = int(decoded_token["sub"])  # Assuming 'sub' contains the user_id
        # Step 3: Ensure chat session exists (or create one if not)
        result = await db.execute(select(Chat).where(Chat.chat_session_id == chat_session_id))
        chat_session = result.scalars().first()

        if not chat_session:
            chat_session = Chat(chat_session_id=chat_session_id, user_id=user_id, title="New Chat")
            db.add(chat_session)
            await db.commit()  # Commit new chat session

        # Step 4: Connect the user to the chat session
        await manager.connect(chat_session_id, websocket, user_id)

        try:
            while True:
                # Step 5: Receive user message from WebSocket
                data = await websocket.receive_text()

                emotion_label = predict_emotion(data)
                print(f"Emotion Label: {emotion_label}")

                # Step 6: Save the user's message to the DB
                user_msg = ChatMessage(
                    chat_session_id=chat_session.chat_session_id,
                    user_id=user_id,
                    chat_message=data,
                    emotion=emotion_label,
                )
                db.add(user_msg)
                await db.commit()  # Commit the user message


                # Step 8: Generate AI response (this is a placeholder)
                ai_response = predict_response(data)
                print(ai_response)
                ai_msg = ChatMessage(
                    chat_session_id=chat_session.chat_session_id,
                    user_id=9,  # AI user ID (you can assign a specific AI user ID)
                    chat_message=ai_response,
                    emotion=emotion_label,
                )
                db.add(ai_msg)
                await db.commit()  # Commit the AI response

                # Step 9: Broadcast the AI response
                await manager.broadcast(chat_session_id, ai_response)

        except WebSocketDisconnect:
            # Handle WebSocket disconnection
            manager.disconnect(chat_session_id, websocket)

    except Exception as e:
        # Handle general exceptions (like token errors or DB issues)
        await websocket.close(code=1008)  # Close connection if error occurs
        print(f"Error: {e}")

    finally:
        # Close DB session generator after usage
        await db_gen.aclose()


@router.post("")
async def create_chat_session(payload: ChatCreate, db: AsyncSession = Depends(get_db)):
    new_chat_session = Chat(title=payload.chat_title, user_id=payload.user_id)
    db.add(new_chat_session)
    await db.commit()
    await db.refresh(new_chat_session)  # optional: get back the inserted values
    return {"message": "Chat created", "chat_session_id": str(new_chat_session.chat_session_id)}


@router.get("/{chat_session_id}", response_model=List[ChatMessageSchema])
async def get_chat_session(chat_session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatMessage).where(ChatMessage.chat_session_id == chat_session_id))
    chat = result.scalars().all()
    response = []
    if chat:
        for c in chat:
            response.append(ChatMessageSchema(
                chat_id=c.chat_id,
                chat_session_id=c.chat_session_id,
                chat_message=c.chat_message,
                is_ai=(c.user_id == 9)
            ))

    return response

@router.get("/profile/{user_id}", response_model=List[ChatSessionSchema])
async def get_all_chat_session(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Chat).where(Chat.user_id == user_id))
    chat_session = result.scalars().all()
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat not found")

    return chat_session


