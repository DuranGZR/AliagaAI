"""
AliağaAI RAG değerlendirme scripti.

Kullanım:
  python run_rag_eval.py
  python run_rag_eval.py --eval-set evaluation/rag_eval_set.json --target-size 200
"""
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from app.database import async_session, close_db, init_db
from app.services.rag_eval import (
    DEFAULT_EVAL_SET_PATH,
    evaluate_rag,
    generate_bootstrap_eval_set,
    load_eval_set,
    write_eval_report,
)


async def _run(eval_set_path: Path, target_size: int, retrieval_only: bool) -> None:
    await init_db()
    try:
        async with async_session() as session:
            eval_items = load_eval_set(eval_set_path)
            if len(eval_items) < target_size:
                eval_items = await generate_bootstrap_eval_set(
                    session,
                    target_size=target_size,
                    output_path=eval_set_path,
                )

            report = await evaluate_rag(session, eval_items, run_generation=not retrieval_only)
            report_path = write_eval_report(report)

            summary = report["summary"]
            print("\n=== RAG Evaluation Summary ===")
            print(f"Total: {summary['total']}")
            print(f"Retrieval Count: {summary['retrieval_count']}")
            print(f"Recall@k: {summary['recall_at_k']:.4f}")
            print(f"MRR: {summary['mrr']:.4f}")
            print(f"Citation Precision: {summary['citation_precision']:.4f}")
            print(f"No-Answer Accuracy: {summary['no_answer_accuracy']:.4f}")
            print(f"Faithfulness Proxy: {summary['faithfulness_proxy']:.4f}")
            print(f"Report: {report_path}")
    finally:
        await close_db()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-set", type=str, default=str(DEFAULT_EVAL_SET_PATH))
    parser.add_argument("--target-size", type=int, default=200)
    parser.add_argument("--retrieval-only", action="store_true")
    args = parser.parse_args()

    eval_set_path = Path(args.eval_set)
    asyncio.run(_run(eval_set_path, args.target_size, args.retrieval_only))


if __name__ == "__main__":
    main()
