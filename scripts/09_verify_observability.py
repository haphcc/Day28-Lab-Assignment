# scripts/09_verify_observability.py
import os

import requests


def check_prometheus():
    resp = requests.get(
        "http://localhost:9090/api/v1/query",
        params={"query": "up{job='api-gateway'}"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    assert data["status"] == "success"
    assert data["data"]["result"], "Prometheus has not scraped api-gateway yet"
    print("Integration 9 OK: Prometheus metrics flowing")


def check_langsmith():
    api_key = os.environ.get("LANGCHAIN_API_KEY")
    if not api_key:
        print("Integration 10 SKIPPED: LANGCHAIN_API_KEY is not configured")
        return

    from langsmith import Client

    client = Client(api_key=api_key)
    runs = list(client.list_runs(project_name="lab28-platform", limit=1))
    assert len(runs) > 0
    print("Integration 10 OK: LangSmith traces visible")


if __name__ == "__main__":
    check_prometheus()
    check_langsmith()
