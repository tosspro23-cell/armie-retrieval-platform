"""Stable runtime execution pipeline shared by all planner implementations."""

from __future__ import annotations

from armie_retrieval.models import Query, RetrievalPlan, RetrievalResult
from armie_retrieval.registries import ProcessorRegistry, RetrieverRegistry


class RetrievalRuntime:
    def __init__(self, retrievers: RetrieverRegistry, processors: ProcessorRegistry) -> None:
        self._retrievers = retrievers
        self._processors = processors

    def execute(self, query: Query, plan: RetrievalPlan) -> RetrievalResult:
        return self._execute(query, plan)

    def execute_with_trace(self, query: Query, plan: RetrievalPlan, collector) -> RetrievalResult:
        """Optional observability extension that preserves normal execution behavior."""
        return self._execute(query, plan, collector=collector)

    def _execute(self, query: Query, plan: RetrievalPlan, collector=None) -> RetrievalResult:
        retriever = self._retrievers.resolve_capability(plan.strategy)
        result = retriever.retrieve(query, plan)
        if collector:
            collector.record_retrieval(retriever, result)
        for processor_name in plan.processor_names:
            processor = self._processors.resolve(processor_name)
            before = result
            if hasattr(processor, "bind_query"):
                processor.bind_query(query)
            result = processor.process(result, plan)
            if collector:
                collector.record_processor(processor, before, result)
        if collector:
            collector.record_final(result)
        return result
