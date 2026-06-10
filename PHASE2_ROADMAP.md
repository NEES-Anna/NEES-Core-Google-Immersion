# Phase 2 Roadmap — NEES Core Engine

This document outlines the key objectives, migration paths, and feature roadmap for the NEES Core Engine during Phase 2 of the Google for Startups Immersion program.

## Objectives & Focus Areas

The main objective of Phase 2 is to scale the NEES Core Engine into an enterprise-ready runtime governance solution utilizing Google Cloud Platform (GCP).

### 1. Platform Infrastructure Migration
* **Gemini API first, Vertex AI-ready later**: We will continue using the direct Gemini API for rapid developer prototyping. For enterprise workloads, we will transition to Vertex AI Model Garden endpoints to deploy models in private VPCs and utilize Google-managed infrastructure.
* **Google Cloud Run Deployment**: Resolve the suspended Google Cloud billing account and deploy containerized backend services on Cloud Run with autoscaling and secure service accounts.
* **Google Cloud Storage (GCS)**: Move static frontend assets to GCS and serve via Google Cloud CDN for global, low-latency distribution.

### 2. Governance & Memory Security Enhancements
* **Advanced Memory Boundary Policy Validation**: Enhance detection of prompt injections and system overrides by implementing semantic search checks and vector-similarity comparison on system prompts using Vertex AI Vector Search.
* **Granular Policy Fine-tuning**: Fine-tune governance model classifiers using Vertex AI pipelines, improving safety metrics (precision/recall on hostile tones, sensitive advice, and unauthorized agent commands).

### 3. Traceability, Monitoring & Operations
* **Google Cloud Logging & Cloud Monitoring**: Re-engineer the backend tracing module to stream audit logs directly to Cloud Logging instead of returning trace JSON payloads in the response object.
* **Vertex AI Model Monitoring**: Hook up inferences to Vertex AI Model Monitoring to detect data drift, safety violations, and fallback rates over time.
