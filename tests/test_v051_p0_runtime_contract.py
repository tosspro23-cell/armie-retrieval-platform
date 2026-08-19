import unittest

from armie_retrieval.constraints import registry_snapshot
from armie_retrieval.indexing.elasticsearch.identity import LOGICAL_DENSE_INDEX, PHYSICAL_GATE6B_INDEX, configured_dense_index
from armie_retrieval.providers.elasticsearch.retrievers import PROVENANCE_SCHEMA_VERSION, ElasticsearchDenseRetriever
from armie_retrieval.indexing.elasticsearch import ElasticsearchClient


class _Response:
    def __init__(self, body): self._body = body
    def json(self): return self._body


class _MappingClient(ElasticsearchClient):
    def __init__(self):
        super().__init__(base_url="http://unused")

    def request(self, method, path, **kwargs):
        if path.startswith("_alias/"):
            return _Response({PHYSICAL_GATE6B_INDEX: {"aliases": {LOGICAL_DENSE_INDEX: {}}}})
        properties = {field: {} for field in ("years_experience", "industries", "roles", "locations", "seniority_rank")}
        properties["embedding"] = {"dims": 1024}
        return _Response({PHYSICAL_GATE6B_INDEX: {"mappings": {"_meta": {"projection_schema_version": "armie-v0.5-constraint-projection-v1", "projection_implementation_version": "constraint-projection-0.2-gate6b", "mapping_version": "expert-discovery-es-mapping-v2-gate6b", "embedding_model": "BAAI/bge-m3"}, "properties": properties}}})


class _Embedding:
    model_name = "BAAI/bge-m3"


class P0RuntimeContractTests(unittest.TestCase):
    def test_default_runtime_identity_is_logical(self):
        self.assertEqual(configured_dense_index(), LOGICAL_DENSE_INDEX)

    def test_alias_resolves_and_projection_is_compatible(self):
        retriever = ElasticsearchDenseRetriever(_MappingClient(), embedding_provider=_Embedding())
        compatibility = retriever._index_compatibility()
        self.assertEqual(retriever.index, LOGICAL_DENSE_INDEX)
        self.assertEqual(compatibility["status"], "compatible")
        self.assertEqual(compatibility["resolved_indices"], [PHYSICAL_GATE6B_INDEX])

    def test_registry_identity_and_canonical_labels_are_explicit(self):
        snapshot = registry_snapshot()
        self.assertEqual(snapshot["registry_id"], "v0.5-c1-capability-registry-1")
        self.assertEqual(snapshot["schema_version"], "constraint-registry-v1")
        self.assertIn("healthcare", snapshot["supported"]["industry"]["values"])
        self.assertEqual(snapshot["supported"]["industry"]["display_labels"]["healthcare"], "Healthcare")

    def test_execution_provenance_schema_identity_is_stable(self):
        self.assertEqual(PROVENANCE_SCHEMA_VERSION, "constraint-execution-provenance-v1")


if __name__ == "__main__":
    unittest.main()
