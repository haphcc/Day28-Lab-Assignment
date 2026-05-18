# scripts/01_ingest_to_kafka.py
import json
import time

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "data.raw"


def wait_for_kafka(timeout_seconds: int = 60) -> KafkaProducer:
    deadline = time.time() + timeout_seconds
    last_error = None
    while time.time() < deadline:
        try:
            return KafkaProducer(
                bootstrap_servers=BOOTSTRAP_SERVERS,
                value_serializer=lambda value: json.dumps(value).encode("utf-8"),
            )
        except Exception as exc:
            last_error = exc
            time.sleep(2)
    raise RuntimeError(f"Kafka is not ready: {last_error}")


def ensure_topic() -> None:
    admin = KafkaAdminClient(bootstrap_servers=BOOTSTRAP_SERVERS, client_id="lab28-admin")
    try:
        admin.create_topics([NewTopic(name=TOPIC, num_partitions=1, replication_factor=1)])
    except TopicAlreadyExistsError:
        pass
    finally:
        admin.close()


def ingest_data(records: list[dict]):
    producer = wait_for_kafka()
    ensure_topic()
    for record in records:
        producer.send(TOPIC, value=record)
        print(f"Sent: {record['id']}")
    producer.flush()
    producer.close()


if __name__ == "__main__":
    sample_data = [
        {"id": "doc_001", "text": "AI platform integration test", "timestamp": time.time()},
        {"id": "doc_002", "text": "Kafka to Prefect pipeline", "timestamp": time.time()},
    ]
    ingest_data(sample_data)
    print("Integration 1 OK: Data -> Kafka")
