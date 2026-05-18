# scripts/05_embed_to_qdrant.py
import hashlib
import os

import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

EMBED_URL = os.environ.get("EMBED_NGROK_URL", "").rstrip("/")
qdrant = QdrantClient(host="localhost", port=6333)


def deterministic_embedding(text: str, size: int = 384) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return [((digest[i % len(digest)] / 255.0) * 2) - 1 for i in range(size)]


def embed_texts(records: list[dict]) -> list[list[float]]:
    if not EMBED_URL:
        return [deterministic_embedding(record["text"]) for record in records]

    response = requests.post(
        f"{EMBED_URL}/embed",
        json={"texts": [record["text"] for record in records]},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["embeddings"]


def embed_and_store(records: list[dict]):
    qdrant.recreate_collection(
        collection_name="documents",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    embeddings = embed_texts(records)
    points = [
        PointStruct(id=i + 1, vector=embedding, payload=record)
        for i, (embedding, record) in enumerate(zip(embeddings, records))
    ]
    qdrant.upsert(collection_name="documents", points=points)
    print(f"Integration 5 OK: {len(points)} vectors stored in Qdrant")


if __name__ == "__main__":
    embed_and_store(
        [
            {"id": "doc_001", "text": "AI platform integration test"},
            {"id": "doc_002", "text": "Kafka to Prefect pipeline"},
        ]
    )
