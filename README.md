### repro failure

Neartext and hybrid searches fail after upgrading Weaviate, using named vectors. Reproducible with both OpenAI & Cohere embeddings.

```text
vector search: knn search: distance between entrypoint and query node: got a nil or zero-length vector at docID x.
```

### System details

### Setup

weaviate-local-k8s project (wait-for-raft-sync branch)
upgrade-journey-raft e2e tests (upgrade-journey-raft branch)

```shell
docker pull semitechnologies/contextionary:en0.16.0-v1.2.1
docker pull semitechnologies/weaviate:1.24.10
```

Set up venv & install packages

```shell
pip install -r requirements.txt
```

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

run `nv_search.py` again

This will reproduce the errors.
