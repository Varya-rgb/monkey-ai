from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from loguru import logger

from database import init_db, get_db
from schemas import ArticleResponse, AskRequest, AskResponse
from services import add_article, search_similar_chunks
from models import Article

app = FastAPI(
    title="Monkey AI Expert",
    description="Нейросеть-эксперт по обезьянам на основе научных статей",
    version="0.1.0"
)

@app.on_event("startup")
def startup():
    logger.info("Запускаю API...")
    init_db()

@app.get("/")
def root():
    return {
        "message": "Привет! Я нейросеть про обезьян 🐒",
        "status": "работает",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ping")
def ping():
    return {"pong": True}


# ============ ЗАГРУЗКА СТАТЕЙ ============

@app.post("/upload", response_model=ArticleResponse)
async def upload_article(
    title: str = Form(...),
    source: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Загружает статью про обезьян (TXT или PDF)"""
    logger.info(f"Получен файл: {file.filename}")
    
    # 1. Читаем файл
    content_bytes = await file.read()
    
    # Пока поддерживаем только TXT
    if not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=400,
            detail="Пока поддерживаются только .txt файлы"
        )
    
    content = content_bytes.decode("utf-8")
    
    # 2. Сохраняем в БД
    article = add_article(db, title=title, content=content, source=source)
    
    return ArticleResponse(
        id=article.id,
        title=article.title,
        source=article.source,
        uploaded_at=article.uploaded_at,
        chunks_count=len(article.chunks)
    )


@app.get("/articles")
def list_articles(db: Session = Depends(get_db)):
    """Показывает список всех загруженных статей"""
    articles = db.query(Article).all()
    return [
        {
            "id": a.id,
            "title": a.title,
            "source": a.source,
            "chunks": len(a.chunks)
        }
        for a in articles
    ]


# ============ ВОПРОСЫ ============

@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    """Отвечает на вопрос, используя загруженные статьи"""
    logger.info(f"Вопрос: {request.question}")
    
    # 1. Ищем похожие чанки
    chunks = search_similar_chunks(db, request.question, request.top_k)
    
    if not chunks:
        return AskResponse(
            question=request.question,
            answer="В базе нет статей. Сначала загрузите их через /upload",
            sources=[]
        )
    
    # 2. Формируем промпт с найденными чанками
    context = "\n\n---\n\n".join([c["text"] for c in chunks])
    
    prompt = f"""Ты — эксперт по обезьянам. Ответь на вопрос пользователя, 
используя ТОЛЬКО информацию из этих фрагментов статей.

Фрагменты:
{context}

Вопрос: {request.question}

Отвечай на русском, кратко и по делу. Если в фрагментах нет ответа — так и скажи."""
    
    # 3. Пока LLM не подключена — возвращаем заглушку с контекстом
    # (на следующем шаге заменим на реальный вызов Groq)
    answer = f"[LLM ещё не подключена] Нашла {len(chunks)} релевантных фрагментов. Вот первый:\n\n{chunks[0]['text'][:300]}..."
    
    sources = list({c["title"] for c in chunks})
    
    return AskResponse(
        question=request.question,
        answer=answer,
        sources=sources
    )
