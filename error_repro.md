### repro failure

```python
weaviate.exceptions.WeaviateQueryError: Query call with protocol GRPC search failed with message explorer: get class: vector search: object vector search at index movienvdemo: shard movienvdemo_Cla6BaZ6D0E0: vector search: knn search: distance between entrypoint and query node: got a nil or zero-length vector at docID 223.
```

### Setup

weaviate-local-k8s project (wait-for-raft-sync branch)
upgrade-journey-raft e2e tests (upgrade-journey-raft branch)

```shell
docker pull semitechnologies/contextionary:en0.16.0-v1.2.1
docker pull semitechnologies/weaviate:1.24.10
```

Set up venv

From `weaviate-local-k8s` in `wait-for-raft-sync` branch:

```bash
MODULES="text2vec-contextionary,text2vec-openai,generative-openai,text2vec-cohere,generative-cohere" WEAVIATE_VERSION="1.24.10" REPLICAS=3 ./local-k8s.sh setup --local-images
```

run `nv_import.py`
run `nv_search.py`

Upgrade Weaviate

```shell
MODULES="text2vec-contextionary,text2vec-openai,generative-openai,text2vec-cohere,generative-cohere" WEAVIATE_VERSION="1.25.0-raft-ac8cbc4" HELM_BRANCH="raft-configuration" REPLICAS=3 ./local-k8s.sh upgrade
```

run `nv_search.py`
