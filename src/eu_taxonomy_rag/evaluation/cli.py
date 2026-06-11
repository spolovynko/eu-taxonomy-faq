import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from pydantic import TypeAdapter

from eu_taxonomy_rag.agent.factory import agent_factory
from eu_taxonomy_rag.config import get_settings
from eu_taxonomy_rag.evaluation.retrieval_evaluator import RetrievalEvaluator
from eu_taxonomy_rag.evaluation.schemas import EvaluationQuestion

QUESTIONS_PATH = Path("data/evaluation/retrieval_questions.jsonl")
REPORT_DIR = Path("logs/evaluation")


def load_questions(path: Path) -> list[EvaluationQuestion]:
    data = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    return TypeAdapter(list[EvaluationQuestion]).validate_python(data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="baseline")
    parser.add_argument("--top-k", type=int)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = get_settings()
    questions = load_questions(QUESTIONS_PATH)
    retriever = agent_factory.create().retriever
    top_k = args.top_k or settings.top_k
    evaluator = RetrievalEvaluator(retriever, top_k)

    retriever.retrieve(questions[0].question, top_k)
    report = evaluator.evaluate(questions)
    report["config"] = {
        "embedding_model": settings.embedding_model,
        "chunk_size": settings.chunk_size,
        "top_k": top_k,
        "warmup_runs": 1,
    }
    report["experiment"] = args.name
    report["created_at"] = datetime.now(UTC).isoformat()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"{args.name}.json"

    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    for result in report["results"]:
        rank = result["rank"] or "miss"
        print(
            f'{result["id"]}: rank={rank}, '
            f'score={result["top_score"]:.3f}, '
            f'top_faq={result["top_faq_id"]}'
        )

    print("\nRetrieval metrics")
    for name, value in report.items():
        if name in {"results", "config", "experiment", "created_at"}:
            continue

        if isinstance(value, float):
            print(f"{name}: {value:.3f}")
        else:
            print(f"{name}: {value}")

    print(f"report: {report_path}")


if __name__ == "__main__":
    main()
