import re
from pathlib import Path
from typing import List
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.rag import embed_texts, embed_query
from app.db import upsert_chunks, search_similar_chunks

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

DOCUMENT_CATALOG = {
    "AAPL_10K_2024.pdf": {"company": "Apple Inc.", "ticker": "AAPL", "year": 2024},
    "MSFT_10K_2024.pdf": {"company": "Microsoft Corporation", "ticker": "MSFT", "year": 2024},
}


def detect_section(page_text: str) -> str:
    """Extract the 10-K section name from the page text if present."""
    normalized = " ".join(page_text.split())
    if "Item 1A. Risk Factors" in normalized:
        return "Item 1A. Risk Factors"
    if "Item 7. Management Discussion" in normalized or "Item 7. MD&A" in normalized:
        return "Item 7. MD&A"
    match = re.search(r"Section:\s*(.+)", page_text)
    return match.group(1).strip() if match else "General Filing Text"


def load_and_chunk_pdfs(
    data_dir: Path = DATA_DIR,
    chunk_size: int = 500,
    chunk_overlap: int = 80,
) -> List[Document]:
    raw_pages: List[Document] = []
    pdf_files = sorted(data_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {data_dir}")

    for pdf_path in pdf_files:
        reader = PdfReader(str(pdf_path))
        doc_info = DOCUMENT_CATALOG.get(
            pdf_path.name,
            {"company": pdf_path.stem, "ticker": "UNKNOWN", "year": 0},
        )
        for page_idx, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if not text:
                continue
            raw_pages.append(
                Document(
                    page_content=text,
                    metadata={
                        "document_name": pdf_path.name,
                        "company": doc_info["company"],
                        "ticker": doc_info["ticker"],
                        "year": doc_info["year"],
                        "section": detect_section(text),
                        "page_number": page_idx,
                    },
                )
            )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(raw_pages)
    for idx, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = idx
    return chunks


def run_ingestion() -> int:
    chunks = load_and_chunk_pdfs()
    texts = [c.page_content for c in chunks]
    print(f"Generating embeddings for {len(texts)} chunks...")
    vectors = embed_texts(texts)

    records = []
    for chunk, vec in zip(chunks, vectors):
        records.append(
            {
                "document_name": chunk.metadata["document_name"],
                "company": chunk.metadata["company"],
                "ticker": chunk.metadata["ticker"],
                "year": chunk.metadata["year"],
                "section": chunk.metadata["section"],
                "page_number": chunk.metadata["page_number"],
                "chunk_index": chunk.metadata["chunk_index"],
                "content": chunk.page_content,
                "embedding": vec,
            }
        )

    count = upsert_chunks(records)
    print(f"Successfully stored {count} chunks in PostgreSQL (pgvector).")
    return count


if __name__ == "__main__":
    run_ingestion()
    test_q = "What supply chain risks does Apple face?"
    print(f"Testing vector search for: '{test_q}'")
    q_vec = embed_query(test_q)
    hits = search_similar_chunks(q_vec, top_k=2)
    for h in hits:
        print(f"  [{h['ticker']} | {h['section']} | p.{h['page_number']} | sim={h['similarity']}] {h['content'][:110]}...")
