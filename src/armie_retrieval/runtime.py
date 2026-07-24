"""Stable runtime execution pipeline shared by all planner implementations."""

from __future__ import annotations

from armie_retrieval.models import Query, RetrievalPlan, RetrievalResult
from armie_retrieval.registries import ProcessorRegistry, RetrieverRegistry


class RetrievalRuntime:
    def __init__(self, retrievers: RetrieverRegistry, processors: ProcessorRegistry) -> None:
        self._retrievers = retrievers
        self._processors = processors

    def execute(self, query: Query, plan: RetrievalPlan) -> RetrievalResult:
        retriever = self._retrievers.resolve_capability(plan.strategy)
        result = retriever.retrieve(query, plan)
        for processor_name in plan.processor_names:
            processor = self._processors.resolve(processor_name)
            result = processor.process(result, plan)
        return result
