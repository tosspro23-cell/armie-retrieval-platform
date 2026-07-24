# ARMIE AI Retrieval Platform — Architecture Freeze v1.0

**Status:** Frozen
**Purpose:** This document is the single source of truth for architecture decisions. Implementation must conform to it; ambiguity must be marked `REVIEW REQUIRED`, not resolved through architectural redesign.

## Mission

Build a production-oriented adaptive retrieval platform that standardises retrieval planning, execution, result processing, evaluation, and policy evolution across heterogeneous knowledge sources.

## Planes

```text
Runtime:  Query -> Planner -> RetrievalPlan -> Retriever -> RetrievalResult
                                                    -> Result Processors -> Evaluation

Learning: ExecutionObservation + EvaluationResult -> Learning Engine
          -> Policy Optimisation -> Policy Repository -> next runtime policy
```

Runtime never queries the historical observation store. It consumes only a published policy, preserving predictable latency and isolation from unbounded historical data.

## Responsibilities

| Component | Owns | Must not do |
|---|---|---|
| Planner | Declarative strategy and processor plan | Call infrastructure or execute retrieval |
| Retriever | Capability resolution and plan execution | Change the plan or choose a new strategy |
| Result processor | Refine a `RetrievalResult` | Change the plan or retrieve new source data |
| Evaluator | Measure quality and execution effectiveness | Modify runtime results or behaviour |
| Registry | Discover and resolve registered capabilities | Learn from history |
| Learning engine | Turn observations into future policies offline | Participate in request-time execution |

## Core domain-object flow

```text
Query -> RetrievalPlan -> RetrievalResult -> EvaluationResult -> ExecutionObservation -> Policy
```

`RetrievalResult` is the unified result envelope. A result item may represent an expert, document, memory, incident, company, or any other knowledge object; documents are not privileged first-class domain objects.

## Frozen ADRs

1. **Declarative planning:** `RetrievalPlan` describes what is wanted—strategy, ordered processors, parameters, filters and constraints—not providers, SDKs, indexes, or API calls.
2. **Execution never changes the plan:** a retriever or processor may apply a predefined fallback policy and emit an observation, but cannot mutate the plan. Replanning is a future planner concern.
3. **Planner knows capabilities, not implementations:** it reasons in terms such as `dense`, `sparse`, `hybrid`, `graph`, and `rerank`; providers are resolved at execution time through registries.
4. **Unified result envelope:** retrievers and processors exchange `RetrievalResult`; processors transform the envelope rather than inventing result types.
5. **Processing is a pipeline:** merge, normalise, de-duplicate, filter, rerank, compress, and enrich are processors. Their ordered selection belongs in the plan.
6. **Learning updates policy, not runtime context:** observations and evaluation drive offline policy optimisation, then a versioned policy is published for online use.
7. **Separate registries:** retriever, processor, and provider registrations have distinct lifecycle and metadata structures.

## MVP boundary

The first release implements rule-based planning; sparse, dense-style, and hybrid retrieval; ordered result processors; metrics; capability registries; and an Expert Discovery demonstration. LLM planners, graph providers, managed search engines, and offline policy optimisation are explicit extension points.
