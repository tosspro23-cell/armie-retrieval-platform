# v0.4.0 Validation Report

Implementation validation is staged. Local deterministic gates cover dataset generation, checksum validation, 120-query taxonomy coverage, graded metrics, failure classification, profile manifests, and Elasticsearch mapping/client contracts without requiring Docker or model downloads.

Current local results: **44 Python tests passed**, deterministic 20-record dataset smoke build passed, six benchmark profile reports emitted, package build for `armie_retrieval_platform-0.4.0` passed, and `git diff --check` passed. Docker is not installed in this environment, so the Elasticsearch container gate remains pending rather than being claimed as complete.

The Elasticsearch integration gate requires a locally running pinned 8.15.3 container. It must report reachability, version, cluster health, mapping, aliases, and document count before BM25/dense benchmark runs are described as complete.
