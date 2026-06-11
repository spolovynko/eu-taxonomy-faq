import argparse
import json
from pathlib import Path

REPORT_DIR = Path("logs/evaluation")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("reports", nargs="*")
    parser.add_argument(
        "--output",
        type=Path,
        default=REPORT_DIR / "comparison.md",
    )
    return parser.parse_args()


def load_reports(paths: list[str]) -> list[dict]:
    if paths:
        report_paths = [Path(path) for path in paths]
    else:
        report_paths = sorted(REPORT_DIR.glob("*-answers.json"))

    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in report_paths
    ]


def main() -> None:
    args = parse_args()
    reports = load_reports(args.reports)

    if not reports:
        raise RuntimeError("No answer evaluation reports found")

    lines = [
        "# Answer Experiment Comparison",
        "",
        (
            "| Experiment | Fact coverage | Refusal accuracy | "
            "Citation validity | Retrieval Hit@K | p95 total latency |"
        ),
        "|---|---:|---:|---:|---:|---:|",
    ]

    for report in reports:
        lines.append(
            "| "
            f'{report["experiment"]} | '
            f'{report["average_fact_coverage"]:.3f} | '
            f'{report["refusal_accuracy"]:.3f} | '
            f'{report["citation_validity_rate"]:.3f} | '
            f'{report["retrieval_hit_at_k"]:.3f} | '
            f'{report["p95_total_latency_seconds"]:.3f}s |'
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(args.output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
