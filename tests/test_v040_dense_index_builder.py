import json
from pathlib import Path

import pytest

from armie_retrieval.datasets.models import ExpertProfile
from armie_retrieval.indexing.elasticsearch.builder import ElasticsearchIndexBuilder


class FakeEmbedding:
    dimension = 3
    _model = None

    def __init__(self, model="fake-model"):
        self.model_name = model
        self.batches = []

    def embed(self, texts):
        self.batches.append(len(texts))
        return [[float(i), 1.0, 0.5] for i, _ in enumerate(texts)]


class FakeClient:
    def __init__(self):
        self.created = []
        self.bulk = []
        self.aliases = []

    def create_index(self, index, mapping):
        self.created.append((index, mapping))

    def bulk_index(self, index, documents):
        self.bulk.append((index, list(documents)))
        return {"indexed": len(documents), "rejected": 0}

    def alias(self, alias, index, *, write=False):
        self.aliases.append((alias, index, write))


def profiles(count=5):
    return [
        ExpertProfile(
            expert_id=f"e-{i}", display_name=f"Expert {i}", headline="Engineer",
            summary=f"Summary {i}", source_type="synthetic", search_document={"expert_id": f"e-{i}"}
        )
        for i in range(count)
    ]


def test_builder_batches_and_persists_checkpoint(tmp_path: Path):
    client, provider = FakeClient(), FakeEmbedding()
    checkpoint, artifact = tmp_path / "checkpoint.json", tmp_path / "vectors.jsonl"
    result = ElasticsearchIndexBuilder(client, provider).build(
        profiles(), build_id="test-dense", batch_size=2,
        checkpoint_path=checkpoint, embedding_artifact=artifact,
    )
    assert provider.batches == [2, 2, 1]
    assert result["document_count"] == 5
    assert result["embedding_dimensions"] == 3
    assert len(client.bulk) == 3
    assert len(artifact.read_text().splitlines()) == 5
    saved = json.loads(checkpoint.read_text())
    assert saved["processed"] == 5
    assert saved["vectors_persisted"] == 5


def test_builder_resume_does_not_duplicate_embeddings_or_indexing(tmp_path: Path):
    checkpoint = tmp_path / "checkpoint.json"
    first_client, first_provider = FakeClient(), FakeEmbedding()
    ElasticsearchIndexBuilder(first_client, first_provider).build(
        profiles(), build_id="resume-dense", batch_size=2, checkpoint_path=checkpoint,
    )
    second_client, second_provider = FakeClient(), FakeEmbedding()
    ElasticsearchIndexBuilder(second_client, second_provider).build(
        profiles(), build_id="resume-dense", batch_size=2, checkpoint_path=checkpoint,
    )
    assert second_provider.batches == []
    assert second_client.bulk == []
    assert second_client.created == []


def test_builder_refuses_checkpoint_identity_mismatch(tmp_path: Path):
    checkpoint = tmp_path / "checkpoint.json"
    ElasticsearchIndexBuilder(FakeClient(), FakeEmbedding()).build(
        profiles(), build_id="identity-dense", checkpoint_path=checkpoint,
    )
    with pytest.raises(ValueError, match="identity mismatch"):
        ElasticsearchIndexBuilder(FakeClient(), FakeEmbedding("other-model")).build(
            profiles(), build_id="identity-dense", embedding_model="other-model",
            checkpoint_path=checkpoint,
        )
