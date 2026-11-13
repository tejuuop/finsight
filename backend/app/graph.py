from typing import Any, Dict, List, Literal, Optional, TypedDict
from langgraph.graph import END, StateGraph
from app.rag import generate_grounded_answer, retrieve_context
from app.tools import detect_ticker, run_financial_calculation

CALC_KEYWORDS = (
    "calculate",
    "change in",
    "percentage change",
    "growth rate",
    "how much did",
    "difference between",
    "operating margin",
    "net margin",
    "profit margin",
    "% change",
)


class ResearchState(TypedDict, total=False):
    question: str
    ticker: Optional[str]
    route: Literal["rag", "calculator"]
    answer: str
    route_used: str
    insufficient_evidence: bool
    citations: List[Dict[str, Any]]


def classify_node(state: ResearchState) -> ResearchState:
    """Node 1: Classify whether the question requires deterministic math or document RAG."""
    q_low = state["question"].lower()
    is_calc = any(kw in q_low for kw in CALC_KEYWORDS)
    route: Literal["rag", "calculator"] = "calculator" if is_calc else "rag"
    return {"route": route}


def route_decision(state: ResearchState) -> Literal["calculator_node", "rag_node"]:
    """Conditional edge router."""
    if state.get("route") == "calculator":
        return "calculator_node"
    return "rag_node"


def calculator_node(state: ResearchState) -> ResearchState:
    """Node 2A: Run deterministic Python calculation and attach supporting 10-K citations."""
    question = state["question"]
    ticker = state.get("ticker")
    calc_res = run_financial_calculation(question, explicit_ticker=ticker)

    # If the question cannot be answered by the deterministic calculator, fall back cleanly to RAG
    if not calc_res.get("supported"):
        chunks = retrieve_context(question, ticker=ticker, top_k=4)
        rag_res = generate_grounded_answer(question, chunks)
        return {
            "answer": rag_res["answer"],
            "route_used": "rag_fallback",
            "insufficient_evidence": rag_res["insufficient_evidence"],
            "citations": rag_res["citations"],
        }

    resolved_ticker = calc_res["ticker"]
    chunks = retrieve_context(
        f"{resolved_ticker} Consolidated Financial Highlights revenue operating income",
        ticker=resolved_ticker,
        top_k=2,
    )
    citations = []
    for idx, c in enumerate(chunks, start=1):
        content = c["content"]
        citations.append(
            {
                "source_id": idx,
                "document_name": c["document_name"],
                "company": c["company"],
                "ticker": c["ticker"],
                "year": c["year"],
                "section": c["section"],
                "page_number": c["page_number"],
                "similarity": c["similarity"],
                "excerpt": content[:240] + ("..." if len(content) > 240 else ""),
            }
        )

    return {
        "answer": calc_res["summary"],
        "route_used": "calculator",
        "insufficient_evidence": False,
        "citations": citations,
    }


def rag_node(state: ResearchState) -> ResearchState:
    """Node 2B: Standard qualitative RAG retrieval and grounded Gemini answer."""
    question = state["question"]
    ticker = state.get("ticker") or detect_ticker(question)
    chunks = retrieve_context(question, ticker=ticker, top_k=4)
    result = generate_grounded_answer(question, chunks)
    return {
        "answer": result["answer"],
        "route_used": "rag",
        "insufficient_evidence": result["insufficient_evidence"],
        "citations": result["citations"],
    }


def build_research_graph():
    builder = StateGraph(ResearchState)
    builder.add_node("classify_node", classify_node)
    builder.add_node("calculator_node", calculator_node)
    builder.add_node("rag_node", rag_node)

    builder.set_entry_point("classify_node")
    builder.add_conditional_edges(
        "classify_node",
        route_decision,
        {
            "calculator_node": "calculator_node",
            "rag_node": "rag_node",
        },
    )
    builder.add_edge("calculator_node", END)
    builder.add_edge("rag_node", END)
    return builder.compile()


research_graph = build_research_graph()


def run_workflow(question: str, ticker: Optional[str] = None) -> Dict[str, Any]:
    """Execute the compiled LangGraph workflow with a strict step limit."""
    final_state = research_graph.invoke(
        {"question": question, "ticker": ticker},
        config={"recursion_limit": 4},
    )
    return {
        "answer": final_state["answer"],
        "route_used": final_state["route_used"],
        "insufficient_evidence": final_state["insufficient_evidence"],
        "citations": final_state["citations"],
    }
