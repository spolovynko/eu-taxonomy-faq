from time import perf_counter

from eu_taxonomy_rag.agent.retrieval.retriever import Retriever
from eu_taxonomy_rag.evaluation.schemas import EvaluationQuestion


class RetrievalEvaluator:
    def __init__(self, retriever: Retriever, top_k: int) -> None:
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        self.retriever = retriever
        self.top_k = top_k

    def evaluate(self, questions: list[EvaluationQuestion]) -> dict:
        answerable_count = 0
        hit_at_1 = 0
        hit_at_k = 0
        reciprocal_rank_total = 0.0
        answerable_top_scores: list[float] = []
        unanswerable_top_scores: list[float] = []
        latencies: list[float] = []
        results = []

        for item in questions:
            started_at = perf_counter()
            chunks = self.retriever.retrieve(item.question, self.top_k)
            latency_seconds = perf_counter() - started_at
            latencies.append(latency_seconds)

            top_score = chunks[0].score if chunks else 0.0
            rank = self._find_rank(item.expected_faq_ids, chunks)

            if item.answerable:
                answerable_count += 1
                answerable_top_scores.append(top_score)
                hit_at_1 += rank == 1
                hit_at_k += rank is not None

                if rank is not None:
                    reciprocal_rank_total += 1 / rank
            else:
                unanswerable_top_scores.append(top_score)

            results.append(
                {
                    "id": item.id,
                    "question": item.question,
                    "answerable": item.answerable,
                    "expected_faq_ids": item.expected_faq_ids,
                    "rank": rank,
                    "top_score": top_score,
                    "top_faq_id": chunks[0].faq_id if chunks else None,
                    "top_question": chunks[0].question if chunks else None,
                    "latency_seconds": latency_seconds,
                    "retrieved": [
                        {
                            "rank": chunk_rank,
                            "faq_id": chunk.faq_id,
                            "chunk_id": chunk.chunk_id,
                            "question": chunk.question,
                            "score": chunk.score,
                        }
                        for chunk_rank, chunk in enumerate(chunks, start=1)
                    ],
                }
            )

        minimum_answerable_score = min(answerable_top_scores, default=0.0)
        maximum_unanswerable_score = max(unanswerable_top_scores, default=0.0)

        return {
            "questions": len(questions),
            "answerable_questions": answerable_count,
            "hit_at_1": hit_at_1 / answerable_count if answerable_count else 0.0,
            f"hit_at_{self.top_k}": (
                hit_at_k / answerable_count if answerable_count else 0.0
            ),
            "mrr": (
                reciprocal_rank_total / answerable_count
                if answerable_count
                else 0.0
            ),
            "average_answerable_top_score": self._average(answerable_top_scores),
            "average_unanswerable_top_score": self._average(unanswerable_top_scores),
            "minimum_answerable_top_score": minimum_answerable_score,
            "maximum_unanswerable_top_score": maximum_unanswerable_score,
            "candidate_score_threshold": self._candidate_threshold(
                minimum_answerable_score,
                maximum_unanswerable_score,
            ),
            "average_retrieval_latency_seconds": self._average(latencies),
            "median_retrieval_latency_seconds": self._percentile(latencies, 0.5),
            "p95_retrieval_latency_seconds": self._percentile(latencies, 0.95),
            "results": results,
        }

    def _find_rank(self, expected_faq_ids: list[str], chunks) -> int | None:
        for rank, chunk in enumerate(chunks, start=1):
            if chunk.faq_id in expected_faq_ids:
                return rank

        return None

    def _average(self, values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    def _percentile(self, values: list[float], percentile: float) -> float:
        if not values:
            return 0.0

        ordered = sorted(values)
        index = round((len(ordered) - 1) * percentile)
        return ordered[index]

    def _candidate_threshold(
        self,
        minimum_answerable_score: float,
        maximum_unanswerable_score: float,
    ) -> float | None:
        if minimum_answerable_score <= maximum_unanswerable_score:
            return None

        return (minimum_answerable_score + maximum_unanswerable_score) / 2
