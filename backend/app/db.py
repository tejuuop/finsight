from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
import psycopg
from pgvector.psycopg import register_vector
from app.config import settings


def _clean_db_url(url: str) -> str:
    """Remove Prisma-specific query params like ?pgbouncer=true rejected by libpq."""
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query.pop("pgbouncer", None)
    clean_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=clean_query))


def get_connection() -> psycopg.Connection:
    """Open a PostgreSQL connection with pgvector type support registered."""
    if not settings.DATABASE_URL or "user:password@host" in settings.DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not configured. Add your Supabase Pooler URI to .env"
        )
    clean_url = _clean_db_url(settings.DATABASE_URL)
    conn = psycopg.connect(clean_url, prepare_threshold=None)
    register_vector(conn)
    return conn


def upsert_chunks(records: List[Dict[str, Any]]) -> int:
    """Insert or update document chunks and their embeddings in PostgreSQL."""
    sql = """
        INSERT INTO document_chunks (
            document_name, company, ticker, year, section,
            page_number, chunk_index, content, embedding
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (document_name, chunk_index)
        DO UPDATE SET
            company = EXCLUDED.company,
            ticker = EXCLUDED.ticker,
            year = EXCLUDED.year,
            section = EXCLUDED.section,
            page_number = EXCLUDED.page_number,
            content = EXCLUDED.content,
            embedding = EXCLUDED.embedding;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            for r in records:
                cur.execute(
                    sql,
                    (
                        r["document_name"],
                        r["company"],
                        r["ticker"],
                        r["year"],
                        r["section"],
                        r["page_number"],
                        r["chunk_index"],
                        r["content"],
                        r["embedding"],
                    ),
                )
        conn.commit()
    return len(records)


def search_similar_chunks(
    query_embedding: List[float],
    top_k: int = 4,
    ticker: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Retrieve top_k chunks ranked by cosine similarity (1 - cosine_distance)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            if ticker:
                cur.execute(
                    """
                    SELECT document_name, company, ticker, year, section,
                           page_number, chunk_index, content,
                           1 - (embedding <=> %s::vector) AS similarity
                    FROM document_chunks
                    WHERE ticker = %s
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s;
                    """,
                    (query_embedding, ticker.upper(), query_embedding, top_k),
                )
            else:
                cur.execute(
                    """
                    SELECT document_name, company, ticker, year, section,
                           page_number, chunk_index, content,
                           1 - (embedding <=> %s::vector) AS similarity
                    FROM document_chunks
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s;
                    """,
                    (query_embedding, query_embedding, top_k),
                )
            rows = cur.fetchall()

    results = []
    for row in rows:
        results.append(
            {
                "document_name": row[0],
                "company": row[1],
                "ticker": row[2],
                "year": row[3],
                "section": row[4],
                "page_number": row[5],
                "chunk_index": row[6],
                "content": row[7],
                "similarity": round(float(row[8]), 4),
            }
        )
    return results


def list_indexed_documents() -> List[Dict[str, Any]]:
    """Return distinct indexed documents and chunk counts."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT document_name, company, ticker, year, COUNT(*) AS chunk_count
                FROM document_chunks
                GROUP BY document_name, company, ticker, year
                ORDER BY ticker, year;
                """
            )
            rows = cur.fetchall()
    return [
        {
            "document_name": r[0],
            "company": r[1],
            "ticker": r[2],
            "year": r[3],
            "chunk_count": r[4],
        }
        for r in rows
    ]
