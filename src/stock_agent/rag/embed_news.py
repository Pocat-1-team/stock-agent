import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

EMBEDDING_MODEL = "text-embedding-3-small"


def get_supabase_client():
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def get_openai_client():
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is required")
    return OpenAI(api_key=OPENAI_API_KEY)


def create_embedding(text: str) -> list[float]:
    client = get_openai_client()
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def get_text_from_raw_news(news: dict[str, Any]) -> str:
    return (
        news.get("body")
        or news.get("content")
        or news.get("summary")
        or news.get("title")
        or ""
    )


def embed_raw_news(limit: int = 50) -> None:
    supabase = get_supabase_client()

    response = (
        supabase.table("raw_news")
        .select("*")
        .limit(limit)
        .execute()
    )

    raw_news = response.data or []

    if not raw_news:
        print("raw_news에 뉴스 데이터가 없습니다.")
        return

    for idx, news in enumerate(raw_news, start=1):
        text = get_text_from_raw_news(news)

        if not text:
            print(f"[{idx}] 본문/제목이 없어 skip")
            continue

        embedding = create_embedding(text)

        row = {
            "stock_code": news.get("stock_code"),
            "title": news.get("title"),
            "body": text,
            "source_url": news.get("url") or news.get("source_url"),
            "publisher": news.get("publisher") or news.get("source"),
            "published_at": news.get("published_at"),
            "event_type": news.get("event_type"),
            "sentiment": news.get("sentiment"),
            "embedding": embedding,
        }

        supabase.table("news_chunks").insert(row).execute()
        print(f"[{idx}/{len(raw_news)}] embedded: {row['title']}")


if __name__ == "__main__":
    embed_raw_news(limit=50)