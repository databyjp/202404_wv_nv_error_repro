import weaviate
import weaviate.classes.config as wc
from weaviate.classes.config import Configure
from weaviate.util import generate_uuid5
from datetime import datetime, timezone
from tqdm import tqdm
import os
import requests
import pandas as pd
import json

headers = {
    "X-OpenAI-Api-Key": os.getenv("OPENAI_APIKEY"),
    "X-Cohere-Api-Key": os.getenv("COHERE_APIKEY"),
}
client = weaviate.connect_to_local(headers=headers)

for rep_factor, vectorizer, vectorizer_name in [
    (1, Configure.NamedVectors.text2vec_openai, "openai"),
    (3, Configure.NamedVectors.text2vec_openai, "openai"),
    (1, Configure.NamedVectors.text2vec_cohere, "cohere"),
    (3, Configure.NamedVectors.text2vec_cohere, "cohere"),
]:
    collection_name = f"MovieNVDemo{rep_factor}_{vectorizer_name}"

    client.collections.delete(collection_name)

    # CreateMovieCollection
    client.collections.create(
        name=collection_name,
        properties=[
            wc.Property(name="title", data_type=wc.DataType.TEXT),
            wc.Property(name="overview", data_type=wc.DataType.TEXT),
            wc.Property(name="vote_average", data_type=wc.DataType.NUMBER),
            wc.Property(name="genre_ids", data_type=wc.DataType.INT_ARRAY),
            wc.Property(name="release_date", data_type=wc.DataType.DATE),
            wc.Property(name="tmdb_id", data_type=wc.DataType.INT),
        ],
        # Define & configure the vectorizer module
        vectorizer_config=[
            # NamedVectorConfig  # CreateMovieCollection
            # Vectorize the movie title
            vectorizer(
                name="title", source_properties=["title"]
            ),
            # Vectorize the movie overview (summary)
            vectorizer(
                name="overview", source_properties=["overview"]
            ),
        ],
        # Define the generative module
        generative_config=wc.Configure.Generative.cohere(),
        replication_config=wc.Configure.replication(factor=rep_factor)
    )

    # BatchImportData
    data_url = "https://raw.githubusercontent.com/weaviate-tutorials/edu-datasets/main/movies_data_1990_2024.json"
    resp = requests.get(data_url)
    df = pd.DataFrame(resp.json())

    # Get the collection
    movies = client.collections.get(collection_name)

    with movies.batch.fixed_size(50) as batch:
        # Loop through the data
        for i, movie in tqdm(df.iterrows()):
            # Convert data types
            # Convert a JSON date to `datetime` and add time zone information
            release_date = datetime.strptime(movie["release_date"], "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
            # Convert a JSON array to a list of integers
            genre_ids = json.loads(movie["genre_ids"])

            # Build the object payload
            movie_obj = {
                "title": movie["title"],
                "overview": movie["overview"],
                "vote_average": movie["vote_average"],
                "genre_ids": genre_ids,
                "release_date": release_date,
                "tmdb_id": movie["id"],
            }

            # Add object to batch queue
            batch.add_object(
                properties=movie_obj,
                uuid=generate_uuid5(movie["id"]),
            )
            # Batcher automatically sends batches

    # Check for failed objects
    if len(movies.batch.failed_objects) > 0:
        print(f"Failed to import {len(movies.batch.failed_objects)} objects")
        for failed in movies.batch.failed_objects:
            print(f"e.g. Failed to import object with error: {failed.message}")

client.close()
