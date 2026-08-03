"""Evaluate the group's 5 benchmark questions on the `uet_handbook` corpus
using the personal `src` implementation, across the 3 chunking strategies.

Data & questions: report/REPORT_NHOM.md (Nhóm K3-RAG).
Corpus: data/uet_handbook/ (7 documents, copied from the group repo).
"""
import argparse
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.embeddings import OpenAIEmbedder, MockEmbedder
from src.chunking import FixedSizeChunker, SentenceChunker, RecursiveChunker
from src.store import EmbeddingStore
from src.agent import KnowledgeBaseAgent
from src.models import Document

CORPUS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'uet_handbook'))

# Metadata per document (from REPORT_NHOM.md data inventory).
DOC_META = {
    "hoc_bong_diem_ren_luyen.md": ("hoc_bong_diem_ren_luyen", "scholarship-evaluation", "student"),
    "hoc_phi_che_do_chinh_sach.md": ("hoc_phi_che_do_chinh_sach", "tuition-policy", "student"),
    "kham_chua_benh.md": ("kham_chua_benh", "medical-insurance", "student"),
    "ky_tuc_xa.md": ("ky_tuc_xa", "dormitory", "student"),
    "lich_su_truyen_thong.md": ("lich_su_truyen_thong", "history-culture", "all"),
    "thong_tin_lien_he.md": ("thong_tin_lien_he", "contact-directory", "all"),
    "thu_tuc_hanh_chinh_mot_cua.md": ("thu_tuc_hanh_chinh_mot_cua", "administrative-services", "student"),
}

# The group's 5 benchmark questions (REPORT_NHOM.md section 3).
QUESTIONS = [
    "Điều kiện xét cấp học bổng khuyến khích học tập cho sinh viên là gì?",
    "Mức điểm chuẩn chung khi đánh giá điểm rèn luyện cho sinh viên không vi phạm là bao nhiêu?",
    "Đối tượng sinh viên nào được hưởng chính sách giảm 50% học phí?",
    "Sinh viên liên hệ đơn vị nào để làm thủ tục khám chữa bệnh và thanh toán BHYT?",
    "Cổng thủ tục hành chính một cửa giải quyết công việc gì cho sinh viên?",
]

# Optional per-question metadata filter (group insight: helps Q3/Q4/Q5).
META_FILTERS = {
    2: {"doc_id": "hoc_phi_che_do_chinh_sach"},
    3: {"doc_id": "kham_chua_benh"},
    4: {"doc_id": "thu_tuc_hanh_chinh_mot_cua"},
}

# The 3 chunking strategies compared by the group.
STRATEGIES = {
    "FixedSize (250/50)": FixedSizeChunker(chunk_size=250, overlap=50),
    "Sentence (max=3)": SentenceChunker(max_sentences_per_chunk=3),
    "Recursive (300)": RecursiveChunker(chunk_size=300),
}


def load_corpus():
    """Return list of (filename, text, doc_id, category, audience)."""
    docs = []
    for fname in sorted(os.listdir(CORPUS_DIR)):
        if not fname.endswith(".md"):
            continue
        with open(os.path.join(CORPUS_DIR, fname), encoding="utf-8") as fh:
            text = fh.read().strip()
        doc_id, category, audience = DOC_META.get(
            fname, (fname.replace(".md", ""), "unknown", "student")
        )
        docs.append((fname, text, doc_id, category, audience))
    return docs


def chunk_corpus(chunker, corpus):
    """Chunk every document; return a flat list of Document objects."""
    documents = []
    for fname, text, doc_id, category, audience in corpus:
        for i, chunk in enumerate(chunker.chunk(text), 1):
            documents.append(Document(
                id=doc_id,
                content=chunk,
                metadata={
                    "doc_id": doc_id,
                    "category": category,
                    "audience": audience,
                    "source": fname,
                    "chunk_idx": i,
                },
            ))
    return documents


def print_baseline(corpus):
    print("=" * 80)
    print("BASELINE CHUNKING — number of chunks per document per strategy")
    print("=" * 80)
    header = f"{'Document':<34}" + "".join(f"{name:<22}" for name in STRATEGIES)
    print(header)
    for fname, text, doc_id, *_ in corpus:
        counts = []
        for chunker in STRATEGIES.values():
            counts.append(len(chunker.chunk(text)))
        row = f"{fname:<34}" + "".join(f"{c:<22}" for c in counts)
        print(row)


def evaluate(embedder, corpus, only: str | None = None, show_top3: bool = False, use_filter: bool = False):
    for strategy_name, chunker in STRATEGIES.items():
        if only and only.lower() not in strategy_name.lower():
            continue
        documents = chunk_corpus(chunker, corpus)
        store = EmbeddingStore(embedding_fn=embedder)
        store.add_documents(documents)

        print("\n" + "=" * 80)
        print(f"STRATEGY: {strategy_name}  |  {store.get_collection_size()} chunks"
              + ("  |  +metadata filter" if use_filter else ""))
        print("=" * 80)

        for qidx, q in enumerate(QUESTIONS):
            if use_filter and qidx in META_FILTERS:
                results = store.search_with_filter(q, top_k=3, metadata_filter=META_FILTERS[qidx])
            else:
                results = store.search(q, top_k=3)
            if not results:
                print(f"\nQ: {q}\n   -> NO RESULTS")
                continue
            top1 = results[0]
            doc_id = top1["metadata"].get("doc_id", "?")
            snippet = top1["content"].replace("\n", " ")[:130]
            print(f"\nQ: {q}")
            print(f"   Top-1 [{doc_id}]  score={top1['score']:.4f}")
            print(f"   Content: {snippet}...")
            if show_top3:
                for rank, rec in enumerate(results, 1):
                    d = rec["metadata"].get("doc_id", "?")
                    print(f"     Top-{rank} [{d}] score={rec['score']:.4f} | {rec['content'].replace(chr(10), ' ')[:80]}")


def main():
    parser = argparse.ArgumentParser(description="Run group benchmark questions on uet_handbook.")
    parser.add_argument("--strategy", help="Only evaluate this strategy name (substring match).")
    parser.add_argument("--top3", action="store_true", help="Print top-3 results per question.")
    parser.add_argument("--filter", action="store_true", help="Apply per-question metadata filter (Q3/Q4/Q5).")
    args = parser.parse_args()

    try:
        embedder = OpenAIEmbedder()
        print("Embedder: OpenAI text-embedding-3-small")
    except Exception as exc:
        print(f"OpenAIEmbedder failed ({exc}); falling back to MockEmbedder.")
        embedder = MockEmbedder()

    corpus = load_corpus()
    print(f"Corpus: {len(corpus)} documents from {CORPUS_DIR}")

    if not args.strategy:
        print_baseline(corpus)
    evaluate(embedder, corpus, only=args.strategy, show_top3=args.top3, use_filter=args.filter)


if __name__ == "__main__":
    main()
