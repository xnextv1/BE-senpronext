from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.security import hash_password
from models.users import User


async def create_user(password: str, email: str, db: AsyncSession):
    new_user = User(email=email, password=hash_password(password))
    db.add(new_user)
    await db.commit()
    return {"message": "User created"}


async def get_users(db: AsyncSession):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


async def get_user_by_email(email: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    return user
