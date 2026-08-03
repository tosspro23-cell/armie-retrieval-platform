"""Conditional real Elasticsearch integration checks for the v0.4.0 gates."""

from __future__ import annotations

import os
import unittest

from armie_retrieval.indexing.elasticsearch import ElasticsearchClient


@unittest.skipUnless(
    os.getenv("ARMIE_RUN_ELASTICSEARCH_INTEGRATION") == "1",
    "set ARMIE_RUN_ELASTICSEARCH_INTEGRATION=1 to run against real Elasticsearch",
)
class ElasticsearchIntegrationTests(unittest.TestCase):
    index = os.getenv("ARMIE_ELASTICSEARCH_TEST_INDEX", "armie-experts-read")

    def test_pinned_cluster_and_index_are_available(self) -> None:
        client = ElasticsearchClient(timeout=10)
        health = client.health()
        self.assertEqual(health["version"], "8.15.3")
        self.assertEqual(health["cluster"]["status"], "green")
        count = client.request("GET", f"{self.index}/_count").json()["count"]
        self.assertGreaterEqual(count, 1)

    def test_dense_vector_mapping_is_indexed(self) -> None:
        client = ElasticsearchClient(timeout=10)
        mapping = client.request("GET", f"{self.index}/_mapping").json()
        properties = next(iter(mapping.values()))["mappings"]["properties"]
        self.assertTrue(properties["embedding"]["index"])


if __name__ == "__main__":
    unittest.main()
