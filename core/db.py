import os
import ssl
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

ssl_context = ssl.create_default_context(cafile="ca.pem")  # ✅ Reference to your cert file

engine = create_async_engine(
    os.getenv("DATABASE_URL"),
    echo=True,
    connect_args={"ssl": ssl_context}  # ✅ Pass SSL context properly
)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as session:
        yield session