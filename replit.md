# Naql.ai — Replit Project

## Overview
Next-generation autonomous logistics ecosystem for Egypt. Real-time fleet tracking, AI-driven dispatching, and automated pricing.

## Architecture
This is a microservices project. In this Replit environment, **only the Next.js frontend is running**. The full backend (Python FastAPI microservices, CockroachDB, TimescaleDB, Redis, NATS, MQTT) requires Docker and external infrastructure.

## Project Structure
```
frontend/          # Next.js 16 + React 19 + Tailwind v4 frontend
gateway/           # GraphQL gateway (Strawberry + FastAPI, Python)
services/          # Python FastAPI microservices
  identity-service/
  fleet-service/
  matching-engine/
  fintrack-service/
  agent-orchestrator/
  telemetry-ingress/
shared/            # Shared Python libraries (naql-common)
migrations/        # Database migrations
scripts/           # Dev/infra scripts
docs/              # Architecture and API docs
proto/             # Protobuf definitions
```

## Running the App
The frontend runs via the "Start application" workflow:
- Command: `cd frontend && npm run dev`
- Port: 5000 (bound to 0.0.0.0 for Replit proxy compatibility)

## Frontend Tech Stack
- Next.js 16 (App Router)
- React 19
- Tailwind CSS v4
- Apollo Client (GraphQL)
- Mapbox GL JS (fleet map visualization)
- TypeScript

## Key Config Changes for Replit
- `frontend/package.json`: dev/start scripts use `-p 5000 -H 0.0.0.0`
- `frontend/next.config.ts`: `allowedDevOrigins` includes the active Replit preview domain plus Replit wildcard domains for dev HMR support

## Environment Variables Needed (for full backend)
See `.env.example` for all required variables:
- `COCKROACH_URL` — CockroachDB connection string
- `TIMESCALE_URL` — TimescaleDB connection string
- `REDIS_URL` — Redis connection string
- `NATS_URL` — NATS JetStream URL
- `MQTT_BROKER_HOST` / `MQTT_BROKER_PORT` — EMQX broker
- `OPENAI_API_KEY` — OpenAI (AI agent brain)
- `PINECONE_API_KEY` / `PINECONE_INDEX_NAME` / `PINECONE_ENVIRONMENT` — Vector memory
- `FAWRY_API_KEY` / `FAWRY_SECRET` — Egyptian payment gateway
- `PAYMOB_API_KEY` / `PAYMOB_INTEGRATION_ID` — Egyptian payment gateway
- `JWT_SECRET_KEY` / `JWT_ALGORITHM` — Auth tokens

## Package Manager
- Frontend: npm (package-lock.json)
- Backend: uv/pip (pyproject.toml)
