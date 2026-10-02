from sqlalchemy.orm import Session
from sqlalchemy import text
from loguru import logger

from models import Article, Chunk
from embeddings import get_embedding, get_embeddings


def split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Режет длинный текст на куски по ~500 символов.
    overlap — перекрытие, чтобы не терять смысл на границах.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap  # сдвигаемся с перекрытием
    return chunks


def add_article(db: Session, title: str, content: str, source: str = None) -> Article:
    """Добавляет статью в БД, режет на чанки, считает эмбеддинги"""
    logger.info(f"Добавляю статью: {title}")
    
    # 1. Создаём статью
    article = Article(title=title, source=source)
    db.add(article)
    db.flush()  # чтобы получить article.id
    
    # 2. Режем на куски
    chunks_text = split_into_chunks(content)
    logger.info(f"Получилось {len(chunks_text)} чанков")
    
    # 3. Считаем эмбеддинги батчем (быстрее)
    embeddings = get_embeddings(chunks_text)
    
    # 4. Сохраняем чанки
    for chunk_text, emb in zip(chunks_text, embeddings):
        chunk = Chunk(
            article_id=article.id,
            text=chunk_text,
            embedding=emb
        )
        db.add(chunk)
    
    db.commit()
    db.refresh(article)
    logger.success(f"Статья '{title}' сохранена с {len(chunks_text)} чанками")
    return article


def search_similar_chunks(db: Session, question: str, top_k: int = 5) -> list[dict]:
    """Ищет top_k чанков, наиболее похожих на вопрос по смыслу"""
    logger.info(f"Ищу чанки по вопросу: {question[:50]}...")
    
    # 1. Превращаем вопрос в вектор
    question_embedding = get_embedding(question)
    
    # 2. Преобразуем список в строку формата pgvector: [1.0, 2.0, 3.0]
    embedding_str = "[" + ",".join(str(x) for x in question_embedding) + "]"
    
    # 3. Ищем в pgvector
    query = text("""
        SELECT 
            c.text,
            c.article_id,
            a.title,
            1 - (c.embedding <=> CAST(:embedding AS vector)) AS similarity
        FROM chunks c
        JOIN articles a ON c.article_id = a.id
        ORDER BY c.embedding <=> CAST(:embedding AS vector)
        LIMIT :limit
    """)
    
    results = db.execute(
        query,
        {"embedding": embedding_str, "limit": top_k}
    ).fetchall()
    
    logger.info(f"Найдено {len(results)} чанков")
    
    return [
        {
            "text": row.text,
            "article_id": row.article_id,
            "title": row.title,
            "similarity": float(row.similarity)
        }
        for row in results
    ]
