from pydantic import BaseModel
from datetime import datetime

class ArticleResponse(BaseModel):
    """Что отдаём клиенту при загрузке статьи"""
    id: int
    title: str
    source: str | None
    uploaded_at: datetime
    chunks_count: int  # сколько кусков получилось

    class Config:
        from_attributes = True

class AskRequest(BaseModel):
    """Что принимаем от клиента при вопросе"""
    question: str
    top_k: int = 5  # сколько чанков искать

class AskResponse(BaseModel):
    """Что отдаём в ответ на вопрос"""
    question: str
    answer: str
    sources: list[str]  # откуда взяли инфу
