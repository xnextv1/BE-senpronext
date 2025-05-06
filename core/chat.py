from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db


def post_chat_message(user_id ,chat_id, message, db: AsyncSession = Depends(get_db())):
