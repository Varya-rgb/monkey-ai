import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base
from loguru import logger

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://monkey:monkey_secret@db:5432/monkey_knowledge"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Активирует pgvector и создаёт все таблицы"""
    logger.info("Активирую расширение pgvector...")
    
    # Решение проблемы
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    
    logger.success("pgvector активирован!")
    
    logger.info("Создаю таблицы в БД...")
    Base.metadata.create_all(bind=engine)
    logger.success("Таблицы созданы!")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()