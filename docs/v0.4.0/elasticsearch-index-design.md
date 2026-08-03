# Elasticsearch Index Design

The optional local data plane pins Elasticsearch 8.15.3 and uses versioned names `armie-experts-v1-<build_id>` with read/write aliases. BM25 fields preserve explicit boosts; dense vectors record model and dimensions in mapping metadata.

The requests adapter never creates an index during online retrieval. Index creation and bulk writes are offline operations; credentials and URLs are environment variables.
