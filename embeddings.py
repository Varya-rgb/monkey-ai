from sentence_transformers import SentenceTransformer
from loguru import logger

# Загружаем модель (сначала скачается ~30 МБ, потом будет в кэше)
logger.info("Загружаю модель для эмбеддингов...")
model = SentenceTransformer("intfloat/multilingual-e5-small")
logger.success("Модель загружена!")

def get_embedding(text: str) -> list:
    """Превращает текст в вектор из 384 чисел"""
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

def get_embeddings(texts: list) -> list:
    """Превращает список текстов в список векторов (быстрее, чем по одному)"""
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    return embeddings.tolist()
