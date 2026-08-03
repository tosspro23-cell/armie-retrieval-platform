"""Optional Elasticsearch index mapping and ingestion helpers."""

from .mapping import build_mapping, build_index_name
from .client import ElasticsearchClient, ElasticsearchPrerequisiteError
from .builder import ElasticsearchIndexBuilder

__all__ = ["ElasticsearchClient", "ElasticsearchIndexBuilder", "ElasticsearchPrerequisiteError", "build_index_name", "build_mapping"]
