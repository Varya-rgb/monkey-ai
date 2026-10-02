from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Article(Base):
    """Статья про обезьян (PDF, TXT и т.д.)"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    source = Column(String(500))  # откуда статья (URL, имя файла)
    uploaded_at = Column(DateTime, server_default=func.now())
    
    # Связь: одна статья → много чанков
    chunks = relationship("Chunk", back_populates="article", cascade="all, delete-orphan")


class Chunk(Base):
    """Кусочек статьи (500 символов) + его вектор"""
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"))
    text = Column(Text, nullable=False)  # сам текст куска
    embedding = Column(Vector(384))      # вектор размером 384 (модель bge-small)
    
    # Связь: много чанков → одна статья
    article = relationship("Article", back_populates="chunks")