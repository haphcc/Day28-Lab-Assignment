# Hướng Dẫn Nộp Bài - Lab #28: Full Platform Integration Sprint

## Yêu Cầu Nộp Bài

**Full AI infrastructure platform demo** - từ data ingestion đến model serving với full observability.

## Các Artifacts Cần Nộp

### 1. Source Code
- Folder `lab28/` hoàn chỉnh với tất cả files
- Tất cả integration scripts hoạt động
- Prefect flows đã deploy và schedule

### 2. Screenshots Demo
Chụp màn hình các bước:
- Prefect UI: http://localhost:4200 (flow đang chạy)
- API Gateway call: `curl http://localhost:8000/health`
- Grafana dashboard: http://localhost:3000

### 3. Kết Quả Smoke Tests
Chạy và chụp màn hình kết quả:
```bash
cd lab28
pytest smoke-tests/ -v
```
Kỳ vọng: 5/5 tests passing

### 4. Production Readiness Score
```bash
python scripts/production_readiness_check.py
```
Kỳ vọng: Score >80%

### 5. Documentation
- `README.md` giải thích cách:
  - Start platform: `docker compose up -d`
  - Deploy Prefect flows
  - Run smoke tests
  - Access dashboards (Grafana:3000, Prometheus:9090, Prefect:4200)

## Định Dạng Nộp Bài

Tạo Repo GitHub chứa:
```
lab28_submission_[student_id]
├── lab28/                    # Source code hoàn chỉnh
│   ├── docker-compose.yml
│   ├── prefect/flows/
│   ├── scripts/
│   ├── api-gateway/
│   └── monitoring/
├── screenshots/              # Screenshots demo
│   ├── prefect_ui.png
│   ├── api_gateway.png
│   └── grafana_dashboard.png
├── smoke_tests_results.png   # Screenshot kết quả pytest
├── production_readiness.png  # Screenshot readiness score
└── README.md                # Hướng dẫn setup
```

## Địa Điểm Nộp
Nộp link repo GitHub qua LMS

## Tiêu Chí Chấm Điểm

| Tiêu Chí | Trọng Số | Mô Tả |
|----------|----------|-------|
| Integration Completeness | 40% | Tất cả 10 integration points hoạt động, data flow end-to-end |
| Observability | 25% | Logs, metrics, traces hiển thị; alerts configured |
| Performance | 20% | Latency trong SLO; load tested; không có memory leaks |
| Architecture Quality | 15% | Clean separation, GitOps config, documented decisions |

## Các Vấn Đề Cần Tránh

- Config drift giữa các environments
- Thiếu error handling tại integration points
- Monitoring coverage không hoàn chỉnh
- Không có rollback strategy
- Demo không test trước khi nộp

## 5 Câu Hỏi Cần Trả Lời Khi Nộp

### 1. Architecture trade-offs

The platform separates local orchestration and observability from GPU-heavy model serving. Kafka, Prefect, Redis, Qdrant, Prometheus, Grafana, and the API gateway run locally for repeatable development and easier debugging. vLLM and optional embeddings run on Kaggle GPU to avoid local GPU requirements. This improves cost and accessibility, while the fallback path in the API keeps the demo reliable when the tunnel is not available. The main trade-off is added network latency and tunnel fragility between local services and Kaggle.

### 2. Hybrid local + Kaggle disconnect handling

The API gateway reads `VLLM_NGROK_URL` as optional configuration. If it is missing or the remote vLLM call fails, the gateway returns a deterministic local fallback answer instead of crashing. Embedding ingestion also supports `EMBED_NGROK_URL` when available and uses deterministic local embeddings otherwise. This provides graceful degradation for local smoke tests and demos.

### 3. Kafka event-driven decoupling

Kafka decouples data producers from downstream processors. Producers only publish records to `data.raw`; they do not need to know whether Prefect, Delta Lake, Redis, or Qdrant are currently processing the data. Consumers can be restarted independently, replay from offsets, and scale separately. This makes ingestion more resilient and keeps component responsibilities clean.

### 4. Observability implementation

The FastAPI gateway exposes Prometheus metrics at `/metrics` using `prometheus-fastapi-instrumentator`. Prometheus scrapes the API gateway through `monitoring/prometheus.yml`, and Grafana is included for dashboards. The API also exposes `/health` for readiness checks. The readiness script verifies API health, metrics, Prometheus, Grafana, Qdrant, Redis, and Kafka topic availability.

### 5. Service crash and graceful degradation

If Qdrant or Redis restarts, Docker Compose brings the services back and the API gateway seeds the demo collection/features again on startup. If Kaggle vLLM is down, the API falls back to local generation. Kafka provides buffering between ingestion and downstream processing, so a temporary Prefect outage does not require producers to change. For production, the next improvements would be persistent volumes for every stateful service, retries with backoff, alert rules, and explicit recovery runbooks.

## Câu Hỏi Thêm?
Liên hệ giảng viên qua LMS hoặc office hours.
