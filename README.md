# Naql.ai - Autonomous Logistics Ecosystem for Egypt

> Next-generation AI-driven logistics platform designed for the Egyptian landscape — high-density urban centers, long-haul desert highways, and everything in between.

## Architecture Overview

Naql.ai uses an **Event-Driven Microservices Architecture (EDMA)** with regional sharding ("Cells") for nation-scale reliability.

### Core Services

| Service | Purpose | Port |
|---------|---------|------|
| **Identity Service** | Auth, RBAC, KYC | 8001 |
| **Fleet Service** | Truck lifecycle, telemetry, maintenance | 8002 |
| **Matching Engine** | Geo-spatial indexing, driver assignment | 8003 |
| **FinTrack Service** | Ledger, payments, multi-party escrow | 8004 |
| **Agent Orchestrator** | LLM-driven system brain (LangGraph) | 8005 |
| **Telemetry Ingress** | MQTT broker + Flink stream processing | 8006 |
| **GraphQL Gateway** | External API (Apollo-style) | 4000 |

### Tech Stack

- **Language**: Python 3.12+
- **Framework**: FastAPI (REST/gRPC), Strawberry (GraphQL)
- **Databases**: CockroachDB (transactional), TimescaleDB (time-series), Redis Stack (geospatial)
- **Messaging**: NATS JetStream (event bus), EMQX (MQTT broker)
- **AI/ML**: LangGraph, Google OR-Tools, Pinecone (vector DB)
- **Infrastructure**: Docker, Kubernetes (EKS), Terraform
- **Communication**: gRPC (internal), GraphQL (external), MQTT (telemetry)

### Egyptian Context Features

- **Micro-Geofencing**: Sokhna Port, Damietta, 10th of Ramadan industrial zones
- **Fragmented Payments**: Fawry, Paymob, Valu + bank transfers
- **Dynamic Toll Logic**: Automated "Cartas" calculation
- **Hybrid Map Engine**: Google Maps + OpenStreetMap (truck-restricted roads)

## Project Structure

```
naql-ai/
├── proto/                    # gRPC Protocol Buffer definitions
├── services/
│   ├── identity-service/     # Auth & RBAC
│   ├── fleet-service/        # Fleet management
│   ├── matching-engine/      # Driver/truck matching
│   ├── fintrack-service/     # Financial operations
│   ├── agent-orchestrator/   # AI Agent (LangGraph)
│   └── telemetry-ingress/    # MQTT + stream processing
├── gateway/                  # GraphQL API Gateway
├── shared/                   # Shared libraries
├── migrations/               # Database migrations
├── infra/                    # Kubernetes & Docker configs
├── docs/                     # Architecture documentation
├── scripts/                  # Utility scripts
└── tests/                    # Test suites
```

## Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Protocol Buffers compiler (`protoc`)

### Development Setup

```bash
# Clone the repository
git clone https://github.com/ibrahimhady131-cloud/BIG-DEV.git
cd BIG-DEV

# Start infrastructure services
docker-compose up -d

# Install Python dependencies
pip install -e "shared/[dev]"
pip install -e "services/identity-service/[dev]"
pip install -e "services/fleet-service/[dev]"
pip install -e "services/matching-engine/[dev]"
pip install -e "services/fintrack-service/[dev]"
pip install -e "services/agent-orchestrator/[dev]"
pip install -e "services/telemetry-ingress/[dev]"
pip install -e "gateway/[dev]"

# Run database migrations
python scripts/migrate.py

# Start all services
python scripts/start_all.py
```

### Running Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests (requires Docker)
pytest tests/integration/ -v

# Type checking
mypy services/ gateway/ shared/

# Linting
ruff check .
ruff format --check .
```

## API Documentation

- **GraphQL Playground**: http://localhost:4000/graphql
- **Identity Service**: http://localhost:8001/docs
- **Fleet Service**: http://localhost:8002/docs
- **Matching Engine**: http://localhost:8003/docs
- **FinTrack Service**: http://localhost:8004/docs
- **Agent Orchestrator**: http://localhost:8005/docs

## License

Proprietary - All rights reserved.
