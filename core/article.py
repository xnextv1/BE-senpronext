from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.db import get_db
from models.article import Article, ArticleRating


async def rate_article(
    rating: int,
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Article).where(Article.article_id == article_id))
    article = result.scalars().first()

    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    article_rating = ArticleRating(article_id=article_id, rating=rating)
    db.add(article_rating)
    await db.commit()

    await update_article_average(article_id=article_id, db=db)


async def update_article_average(article_id: int, db: AsyncSession = Depends(get_db)):
    # Calculate average
    result = await db.execute(
        select(func.avg(ArticleRating.rating)).where(ArticleRating.article_id == article_id)
    )
    avg_rating = result.scalar()

    # Fetch and update article
    result = await db.execute(select(Article).where(Article.article_id == article_id))
    article = result.scalars().first()

    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    article.article_rating = avg_rating
    article.article_rating_count += 1
    await db.commit()
