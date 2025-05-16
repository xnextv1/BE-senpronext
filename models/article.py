from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Article(Base):
    __tablename__ = 'article'
    article_id = Column(Integer, primary_key=True)
    image = Column(String)
    title = Column(String, index=True)
    article_content = Column(String)
    article_date = Column(TIMESTAMP)
    article_rating = Column(Float)
    article_rating_count = Column(Integer)

class ArticleRating(Base):
    __tablename__ = 'article_rating'
    rating_id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('article.article_id'))
    rating = Column(Integer)