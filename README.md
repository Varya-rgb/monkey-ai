 Monkey AI Expert

AI-система для ответов на вопросы по приматологии на основе RAG-архитектуры.
Веб-приложение, которое отвечает на вопросы об обезьянах, используя только загруженные научные статьи.

 Как работает
1. Пользователь загружает статьи (TXT)
2. Текст разбивается на чанки по 500 символов
3. Для каждого чанка считается эмбеддинг (384 числа)
4. Эмбеддинги сохраняются в PostgreSQL + pgvector
5. Пользователь задаёт вопрос → вопрос кодируется в вектор
6. pgvector находит top-5 похожих чанков
7. LLM (Llama 3) генерирует ответ на основе найденных чанков

 Стек
- **Backend:** Python 3.11, FastAPI, SQLAlchemy
- **БД:** PostgreSQL 16 + pgvector
- **ML:** sentence-transformers (multilingual-e5-small)
- **LLM:** Llama 3 через Groq API
- **Инфраструктура:** Docker, Docker Compose, Redis

 Установка

```bash
git clone https://github.com/Varya-rgb/monkey-ai.git
cd monkey-ai
cp .env.example .env
# Добавь GROQ_API_KEY в .env
docker-compose up -d
