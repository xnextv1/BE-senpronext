from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.security import hash_password
from models.users import User


async def create_user(username:str , password: str, email: str, usertype:str ,db: AsyncSession):
    new_user = User(username=username, email=email, password=hash_password(password), user_type=usertype)
    db.add(new_user)
    await db.commit()
    return {"message": "User created"}


async def get_users(db: AsyncSession):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    return user
