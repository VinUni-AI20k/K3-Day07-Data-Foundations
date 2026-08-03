"""Create a Markdown summary from benchmark_results.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "evaluation" / "benchmark_results.json"
SUMMARY_PATH = ROOT / "evaluation" / "benchmark_summary.md"


def main() -> int:
    data = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    environment = data["environment"]
    lines = [
        "# Semantic Benchmark Summary",
        "",
        f"- Python: `{environment['python_version']}`",
        f"- Model: `{environment['embedding_model']}`",
        f"- Vector dimension: `{environment['vector_dimension']}`",
        f"- Corpus: {environment['corpus_document_count']} documents",
        f"- Queries: {environment['query_count']}",
        f"- Top-k: {environment['top_k']}",
        f"- Fallback: `{environment['fallback']}`",
        "",
        "| Strategy | Member | Chunks | Hit@1 | Hit@3 | MRR | Precision@3 | Coherence | Grounding |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for strategy in data["strategies"]:
        m = strategy["metrics"]
        lines.append(
            f"| {strategy['strategy_id']} | {strategy['member']} | {strategy['chunk_count']} | "
            f"{m['hit_at_1']:.4f} | {m['hit_at_3']:.4f} | {m['mrr']:.4f} | "
            f"{m['precision_at_3']:.4f} | {m['coherence']:.4f} | {m['grounding']:.4f} |"
        )

    lines.extend([
        "",
        "## Per-query evidence",
        "",
        "| Query | Strategy | Top-1 correct | Top-3 evidence | Correct rank | Score | Document |",
        "|---|---|---:|---:|---:|---:|---|",
    ])
    failures: list[str] = []
    for strategy in data["strategies"]:
        for trace in strategy["traces"]:
            rank = trace["first_relevant_rank"]
            evidence = next((r for r in trace["results"] if r["relevant"]), None)
            score = f"{evidence['score']:.6f}" if evidence else "—"
            document = evidence["document_id"] if evidence else "—"
            lines.append(
                f"| {trace['query_id']} | {strategy['strategy_id']} | "
                f"{'yes' if trace['hit_at_1'] else 'no'} | {'yes' if trace['hit_at_3'] else 'no'} | "
                f"{rank or '—'} | {score} | {document} |"
            )
            if not trace["hit_at_1"]:
                failures.append(
                    f"- {trace['query_id']} / {strategy['strategy_id']}: expected "
                    f"{', '.join(trace['expected_document_ids'])}; complete evidence first appears at "
                    f"rank {trace['first_relevant_rank'] or 'outside Top-3'}."
                )
    lines.extend(["", "## Failure cases", ""])
    lines.extend(failures or ["- No Top-1 or Top-3 evidence failures."])
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(SUMMARY_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
