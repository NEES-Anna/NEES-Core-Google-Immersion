# Google Immersion Session Learnings

This document details the architectural concepts and design patterns adopted in the NEES Core Engine Google Immersion Demo, based on session learnings from the Google for Startups Immersion program.

## Core Security & Architecture Patterns

### 1. Dual-Path Input & Output Sanitation
A major theme in building secure AI agents is that LLMs themselves are non-deterministic and cannot be fully secured solely through system prompts. If prompt injection occurs, safety instructions are easily bypassed.
* **NEES Core Approach**: We implement an independent, deterministic backend governance analyzer. The prompt is classified *before* being sent to the model, and the response is scrutinized and restructured *after* generation.

### 2. Sandbox Memory Boundaries
In a production AI system, models often ingest private context data, internal configuration rules, and system credentials. Attackers can craft malicious prompts to trick the model into revealing these parameters.
* **NEES Core Approach**: We introduced a "Memory Boundary" scenario to demonstrate this defense. The governance system intercepts attempts to leak internal system markers, blocking the response and returning a secure response.

### 3. API Resilience & Degradation
Production-grade systems cannot fail completely when third-party APIs experience downtime or throttling.
* **NEES Core Approach**: We use a cascading client pattern that attempts to access primary models, falls back to alternative model variations, and degrades to structured mocks in extreme cases.

## Google Cloud Roadmap

During Phase 2, we plan to implement Google Cloud platform features to strengthen the runtime security of the NEES Core Engine:
* **Gemini API first, Vertex AI-ready later**: Startups require fast developer setup. Using the Gemini API allows rapid development. We are designing the system to be Vertex AI-ready for enterprise clients who need dedicated VPC endpoints.
* **Google Cloud KMS & Secret Manager**: Storing API keys in `.env` files is a common source of vulnerability. We plan to migrate all backend keys and credential validation logic to Secret Manager.
