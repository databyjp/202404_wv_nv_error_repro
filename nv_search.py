import weaviate
import weaviate.classes.query as wq
from weaviate.classes.config import Configure
import os

headers = {
    "X-OpenAI-Api-Key": os.getenv("OPENAI_APIKEY"),
    "X-Cohere-Api-Key": os.getenv("COHERE_APIKEY"),
}
client = weaviate.connect_to_local(
    headers=headers
)

for rep_factor, _, vectorizer_name in [
    (1, Configure.NamedVectors.text2vec_openai, "openai"),
    (3, Configure.NamedVectors.text2vec_openai, "openai"),
    (1, Configure.NamedVectors.text2vec_cohere, "cohere"),
    (3, Configure.NamedVectors.text2vec_cohere, "cohere"),
]:
    collection_name = f"MovieNVDemo{rep_factor}_{vectorizer_name}"

    movies = client.collections.get(collection_name)
    print(f"Collection: {collection_name}")

    for tgt_vector in ["title", "overview"]:
        print(f"NearText query on {vectorizer_name} vectors with target vector: {tgt_vector}")
        try:
            response = movies.query.near_text(
                query="A joyful holiday film",
                target_vector=tgt_vector,
                limit=5,
                return_metadata=wq.MetadataQuery(distance=True),
                return_properties=["title", "release_date", "tmdb_id"]
            )
        except Exception as e:
            print(f"Error: {e}")
            continue

    for tgt_vector in ["title", "overview"]:
        print(f"Hybrid query on {vectorizer_name} vectors with target vector: {tgt_vector}")
        try:
            response = movies.query.hybrid(
                query="A joyful holiday film",
                target_vector=tgt_vector,
                limit=5,
                return_metadata=wq.MetadataQuery(distance=True),
                return_properties=["title", "release_date", "tmdb_id"]
            )
        except Exception as e:
            print(f"Error: {e}")
            continue

client.close()
