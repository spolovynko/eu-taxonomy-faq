from time import perf_counter

from eu_taxonomy_rag.agent.generation.llm_client import LLMClient
from eu_taxonomy_rag.agent.retrieval.retriever import Retriever
from eu_taxonomy_rag.evaluation.schemas import AnswerEvaluationQuestion


class AnswerEvaluator:
    def __init__(
        self,
        retriever: Retriever,
        llm_client: LLMClient,
        top_k: int,
    ) -> None:
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        self.retriever = retriever
        self.llm_client = llm_client
        self.top_k = top_k

    def evaluate(self, questions: list[AnswerEvaluationQuestion]) -> dict:
        results = [self._evaluate_question(item) for item in questions]
        answerable = [result for result in results if result["answerable"]]
        unanswerable = [result for result in results if not result["answerable"]]

        return {
            "questions": len(results),
            "answerable_questions": len(answerable),
            "unanswerable_questions": len(unanswerable),
            "generation_success_rate": self._average(
                [result["error"] is None for result in results]
            ),
            "average_fact_coverage": self._average(
                [result["fact_coverage"] for result in answerable]
            ),
            "refusal_accuracy": self._average(
                [result["correct_refusal"] for result in unanswerable]
            ),
            "false_refusal_rate": self._average(
                [
                    result["insufficient_context"] is True
                    for result in answerable
                ]
            ),
            "citation_validity_rate": self._average(
                [result["citations_valid"] for result in results]
            ),
            "retrieval_hit_at_k": self._average(
                [result["expected_faq_retrieved"] for result in answerable]
            ),
            **self._latency_metrics(results),
            "robustness": self._robustness_metrics(results),
            "results": results,
        }

    def _evaluate_question(self, item: AnswerEvaluationQuestion) -> dict:
        total_started_at = perf_counter()

        retrieval_started_at = perf_counter()
        chunks = self.retriever.retrieve(item.question, self.top_k)
        retrieval_seconds = perf_counter() - retrieval_started_at

        generation_started_at = perf_counter()
        try:
            answer = self.llm_client.generate(item.question, chunks)
            error = None
        except Exception as exception:
            answer = None
            error = str(exception)

        generation_seconds = perf_counter() - generation_started_at
        total_seconds = perf_counter() - total_started_at

        retrieved_faq_ids = [chunk.faq_id for chunk in chunks]
        retrieved_chunk_ids = {chunk.chunk_id for chunk in chunks}
        expected_faq_retrieved = any(
            faq_id in item.expected_faq_ids
            for faq_id in retrieved_faq_ids
        )
        if answer is None:
            citations_valid = False
        elif answer.insufficient_context:
            citations_valid = not answer.used_chunk_ids
        else:
            citations_valid = bool(answer.used_chunk_ids) and all(
                chunk_id in retrieved_chunk_ids
                for chunk_id in answer.used_chunk_ids
            )

        fact_coverage = None
        if item.answerable:
            fact_coverage = (
                self._fact_coverage(answer.answer, item.expected_facts)
                if answer
                else 0.0
            )

        insufficient_context = (
            answer.insufficient_context
            if answer
            else None
        )
        correct_refusal = False

        if answer:
            correct_refusal = (
                answer.insufficient_context
                if not item.answerable
                else not answer.insufficient_context
            )

        return {
            "id": item.id,
            "question": item.question,
            "answerable": item.answerable,
            "variant_group": item.variant_group,
            "expected_faq_ids": item.expected_faq_ids,
            "expected_faq_retrieved": expected_faq_retrieved,
            "retrieved_faq_ids": retrieved_faq_ids,
            "answer": answer.answer if answer else "",
            "confidence": answer.confidence if answer else None,
            "insufficient_context": insufficient_context,
            "correct_refusal": correct_refusal,
            "fact_coverage": fact_coverage,
            "used_chunk_ids": answer.used_chunk_ids if answer else [],
            "citations_valid": citations_valid,
            "error": error,
            "retrieval_latency_seconds": retrieval_seconds,
            "generation_latency_seconds": generation_seconds,
            "total_latency_seconds": total_seconds,
        }

    def _fact_coverage(
        self,
        answer: str,
        expected_facts: list[list[str]],
    ) -> float:
        normalized_answer = answer.lower()
        matched_facts = sum(
            any(term.lower() in normalized_answer for term in alternatives)
            for alternatives in expected_facts
        )
        return matched_facts / len(expected_facts)

    def _latency_metrics(self, results: list[dict]) -> dict:
        metrics = {}

        for stage in ("retrieval", "generation", "total"):
            values = [
                result[f"{stage}_latency_seconds"]
                for result in results
            ]
            metrics[f"average_{stage}_latency_seconds"] = self._average(values)
            metrics[f"median_{stage}_latency_seconds"] = self._percentile(
                values,
                0.5,
            )
            metrics[f"p95_{stage}_latency_seconds"] = self._percentile(
                values,
                0.95,
            )

        return metrics

    def _robustness_metrics(self, results: list[dict]) -> list[dict]:
        groups: dict[str, list[dict]] = {}

        for result in results:
            group = result["variant_group"]
            if group:
                groups.setdefault(group, []).append(result)

        robustness = []
        for name, variants in groups.items():
            coverages = [
                result["fact_coverage"]
                for result in variants
                if result["fact_coverage"] is not None
            ]
            robustness.append(
                {
                    "group": name,
                    "variants": len(variants),
                    "average_fact_coverage": self._average(coverages),
                    "fact_coverage_range": (
                        max(coverages) - min(coverages)
                        if coverages
                        else 0.0
                    ),
                    "refusal_consistent": len(
                        {
                            result["insufficient_context"]
                            for result in variants
                        }
                    ) == 1,
                }
            )

        return robustness

    def _average(self, values: list) -> float:
        return sum(values) / len(values) if values else 0.0

    def _percentile(self, values: list[float], percentile: float) -> float:
        if not values:
            return 0.0

        ordered = sorted(values)
        index = round((len(ordered) - 1) * percentile)
        return ordered[index]
