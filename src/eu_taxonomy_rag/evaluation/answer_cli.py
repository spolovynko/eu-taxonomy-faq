import argparse
import csv
import json
from datetime import UTC, datetime
from pathlib import Path

from pydantic import TypeAdapter

from eu_taxonomy_rag.agent.factory import agent_factory
from eu_taxonomy_rag.config import get_settings
from eu_taxonomy_rag.evaluation.answer_evaluator import AnswerEvaluator
from eu_taxonomy_rag.evaluation.schemas import AnswerEvaluationQuestion

QUESTIONS_PATH = Path("data/evaluation/answer_questions.jsonl")
REPORT_DIR = Path("logs/evaluation")


def load_questions(path: Path) -> list[AnswerEvaluationQuestion]:
    data = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return TypeAdapter(list[AnswerEvaluationQuestion]).validate_python(data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="baseline")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--top-k", type=int)
    parser.add_argument("--human-review", action="store_true")
    return parser.parse_args()


def save_human_review(results: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "id",
                "question",
                "answer",
                "generation_error",
                "correctness_0_to_2",
                "faithfulness_0_to_2",
                "relevance_0_to_2",
                "clarity_0_to_2",
                "notes",
            ],
        )
        writer.writeheader()

        for result in results:
            writer.writerow(
                {
                    "id": result["id"],
                    "question": result["question"],
                    "answer": result["answer"],
                    "generation_error": result["error"] or "",
                    "correctness_0_to_2": "",
                    "faithfulness_0_to_2": "",
                    "relevance_0_to_2": "",
                    "clarity_0_to_2": "",
                    "notes": "",
                }
            )


def main() -> None:
    args = parse_args()
    settings = get_settings()
    questions = load_questions(QUESTIONS_PATH)

    if args.limit:
        questions = questions[: args.limit]

    top_k = settings.top_k if args.top_k is None else args.top_k
    agent = agent_factory.create()
    evaluator = AnswerEvaluator(
        retriever=agent.retriever,
        llm_client=agent.llm_client,
        top_k=top_k,
    )

    agent.answer(questions[0].question)
    report = evaluator.evaluate(questions)
    report["experiment"] = args.name
    report["created_at"] = datetime.now(UTC).isoformat()
    report["config"] = {
        "embedding_model": settings.embedding_model,
        "llm_model": settings.llm_model,
        "temperature": settings.llm_temperature,
        "chunk_size": settings.chunk_size,
        "top_k": top_k,
        "warmup_runs": 1,
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"{args.name}-answers.json"
    review_path = REPORT_DIR / f"{args.name}-human-review.csv"

    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.human_review:
        save_human_review(report["results"], review_path)

    print("Answer metrics")
    for name, value in report.items():
        if name in {"results", "config", "robustness", "experiment", "created_at"}:
            continue

        if isinstance(value, float):
            print(f"{name}: {value:.3f}")
        else:
            print(f"{name}: {value}")

    failed = [result["id"] for result in report["results"] if result["error"]]
    if failed:
        print(f"failed generations: {', '.join(failed)}")

    print(f"report: {report_path}")

    if args.human_review:
        print(f"human review: {review_path}")


if __name__ == "__main__":
    main()
