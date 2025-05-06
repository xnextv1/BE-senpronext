from datetime import datetime

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException, Form
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from core.article import rate_article
from models.article import Article
from core.db import get_db
from typing import List

import cloudinary
import cloudinary.uploader
import os

load_dotenv()
router = APIRouter()

cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure = True
)

class ArticleOut(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        orm_mode = True

class PaginatedArticles(BaseModel):
    total: int
    total_pages: int
    offset: int
    limit: int
    data: List[ArticleOut]



@router.get("/articles", response_model=PaginatedArticles)
async def get_articles(
    db: AsyncSession = Depends(get_db),
    pageSize: int = Query(10, ge=5, le=100),
    page: int = Query(1, ge=1)
):
    # Get total count
    total_query = await db.execute(select(func.count()).select_from(Article))
    total = total_query.scalar_one()

    # Get paginated data
    result = await db.execute(
        select(Article).offset(page * pageSize).limit(pageSize)
    )
    articles = result.scalars().all()

    # Calculate total pages
    total_pages = (total + pageSize - 1) // pageSize  # ceil division

    return PaginatedArticles(
        total=total,
        total_pages=total_pages,
        page=page,
        pageSize=pageSize,
        data=articles
    )

@router.get("/articles/{id}")
async def get_article(
        id: int,
        db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Article).where(Article.article_id == id))
    article = result.scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"data": {
            "title": article.title,
            "article_rating": article.article_rating,
            "article_content": article.article_content,
            "image": article.image,
            "article_date": article.article_date,
            "article_rating_count": article.article_rating_count
        }
    }

@router.post("/articles")
async def create_article(
        content: str = Form(...),
        title: str = Form(...),
        img: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
):
    upload_result = cloudinary.uploader.upload(img.file)
    image_url = upload_result.get("secure_url")

    article = Article(image=image_url,
                      article_date=datetime.now(),
                      article_content=content,
                      title=title,
                      article_rating= 0,
                      article_rating_count= 0)

    db.add(article)
    await db.commit()


    return { "message": "Article successfully created" }


@router.post("/articles/rating/{id}")
async def article_rating(
        id: int,
        rating: int,
        db: AsyncSession = Depends(get_db),
):
    await rate_article(rating, id, db)


    return {"message": "Article successfully rated"}