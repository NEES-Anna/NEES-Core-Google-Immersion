# Phase 2 Roadmap — NEES Core Engine

This document outlines the key objectives, migration paths, and feature roadmap for the **NEES Core Engine — Google Immersion Demo** during Phase 2 of the Google for Startups Immersion program.

## Objective

The primary objective of Phase 2 is to move the NEES Core Engine demo from a public developer preview into a Google Cloud-ready runtime governance architecture.

The focus is not only model access, but production readiness:

* governed AI request/response flow
* memory boundary protection
* policy-based response control
* traceability and audit logging
* cloud deployment readiness
* dashboard-ready governance visibility

---

## 1. Platform Infrastructure Migration

### Gemini API First, Vertex AI-Ready Later

The current demo uses a Gemini-ready provider layer and mock mode for safe public evaluation.

In Phase 2, the first goal is to enable live Gemini API integration while keeping deterministic mock mode available for testing and demos.

Future enterprise deployments can explore Vertex AI as a more managed path for model access, evaluation workflows, and production operations.

### Google Cloud Run Deployment

Deploy the containerized FastAPI backend on Google Cloud Run after the current Google Cloud billing/project access issue is resolved.

Planned work:

* configure Cloud Run service
* set environment variables securely
* connect service account permissions
* expose health and governance endpoints
* validate deployed API using demo scenarios
* keep Render deployment as an external fallback until Cloud Run is stable

### Google-Native Frontend Hosting

Evaluate Google-native hosting options for the frontend, including Firebase Hosting or Google Cloud Storage with Cloud CDN.

The current Vercel frontend will remain available as the public review demo while a Google-hosted path is tested.

---

## 2. Governance & Memory Security Enhancements

### Advanced Memory Boundary Policy Validation

Extend the memory boundary system beyond keyword checks by adding semantic detection for:

* prompt injection attempts
* system prompt extraction attempts
* private memory access attempts
* developer instruction override attempts
* internal configuration exposure attempts

The first Phase 2 milestone is to create a structured evaluation dataset for memory-boundary attacks and measure detection quality.

### Semantic Policy Layer

Explore a semantic policy layer using embeddings/vector similarity to detect complex or indirect attacks that do not match obvious keywords.

Possible future Google Cloud integration:

* Vertex AI embeddings
* Vertex AI Vector Search
* Firestore or BigQuery for trace/evaluation records

### Policy Evaluation Before Fine-Tuning

Before any classifier fine-tuning, Phase 2 should focus on:

* evaluation test sets
* precision/recall measurement
* false-positive analysis
* policy category refinement
* deterministic regression tests

Fine-tuning or model-based classification can be explored later only if rule-based and semantic policy checks are not sufficient.

---

## 3. Traceability, Monitoring & Operations

### Cloud Logging & Cloud Monitoring

Add Google Cloud Logging for backend runtime events and governance decisions.

The public demo will continue returning trace JSON for transparency, while Cloud Logging will provide backend observability.

Planned logging fields:

* trace ID
* scenario
* intent
* risk band
* policy decision
* model route
* mock/live mode
* latency
* response hash prefix
* escalation or block reason

### Firestore / BigQuery Trace Storage

Evaluate Firestore or BigQuery as a storage layer for governance traces.

Firestore may be used for lightweight dashboard-ready trace views, while BigQuery may be better for long-term analytics and evaluation reports.

### Dashboard-Ready Governance Visibility

Build a simple dashboard view for:

* total requests
* risk distribution
* policy decisions
* block/modify/allow rates
* memory-boundary attempts
* model route and fallback counts
* trace search by trace ID

### Future Model Monitoring

Vertex AI Model Monitoring can be explored later for production model endpoints.

For Phase 2, the immediate monitoring priority is governance trace visibility, Cloud Logging, and policy evaluation metrics.

---

## 4. Phase 2 Success Criteria

Phase 2 will be considered successful if the demo can show:

1. Cloud Run deployment of the backend API.
2. Live Gemini API integration with mock mode retained.
3. Secure environment variable and secret management.
4. Governance traces streamed to Cloud Logging.
5. Memory-boundary evaluation test cases.
6. A dashboard-ready trace structure.
7. Clear documentation showing how NEES governance sits between the app and model provider.

---

## 5. Long-Term Direction

The long-term goal is to evolve NEES Core Engine into a runtime governance layer for production AI applications.

The engine should help AI teams manage:

* behavior governance
* memory boundaries
* escalation logic
* audit trails
* model routing
* cost-aware execution
* policy evaluation
* production traceability

The Phase 2 build will focus on proving this direction using the Google Cloud and Gemini ecosystem.
