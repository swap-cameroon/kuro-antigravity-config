---
name: llm-app-engineering
description: "Build reliable LLM-powered features: prompts, structured output, RAG, tool use, evals, cost and latency, safety. Use when integrating or reviewing LLM, agent or retrieval features in an application."
license: MIT
metadata:
  version: "1.0.0"
---

# LLM application engineering

Treat the model as an unreliable, probabilistic, costly dependency. Reliability comes from the system around it. Before choosing models, parameters or SDK usage, consult current provider docs: model names, limits and pricing change often.

## Design
1. **Is an LLM needed?** Prefer rules/search/classic ML when the task is deterministic. Use the smallest model that meets quality; route hard cases to larger models.
2. **Define the task contract**: inputs, output schema, quality bar, latency and cost budget, failure behavior (fallback, human review).
3. **Prompts as code**: versioned files, templated, system instructions separate from untrusted content; few-shot examples from real data; explicit refusal/unknown behavior ("answer only from the context; otherwise say you cannot").
4. **Structured output**: JSON schema / tool-call / constrained decoding, validate with Pydantic/Zod, retry once with the validation error, then fall back. Never `eval` model output.

## RAG
- Ingest: clean, chunk by semantic structure (headings/paragraphs, ~200-800 tokens, small overlap), attach metadata (source, date, ACL). Embed with one consistent model; store in pgvector/OpenSearch/Qdrant etc. (`postgres` for pgvector).
- Retrieve: hybrid (BM25 + vector) -> rerank -> top-k; filter by tenant/ACL **in the query**, not after. Query rewriting for follow-ups.
- Generate with citations to chunk IDs; reject answers without support. Evaluate retrieval separately (recall@k, MRR) from generation (faithfulness, relevance).

## Tools & agents
Small, well-described tools with typed args; least privilege per tool; read-only by default; human confirmation for destructive/financial actions; step and budget limits (max iterations, tokens, wall time); idempotent side effects; full trace of every tool call. Prefer deterministic workflows over autonomous loops unless the path is genuinely open-ended.

## Evals (non-negotiable)
Build a golden dataset from real and adversarial cases (start with 30-100). Automatic checks (schema, regex, exact match), LLM-as-judge with a rubric validated against human labels, and regression runs in CI on every prompt/model/retriever change. Track quality, latency p95, cost per request; compare variants before shipping. Monitor production with sampled human review and feedback signals.

## Safety & security
Treat retrieved documents, tool outputs and user input as **untrusted**: prompt injection can arrive via any of them. Never let model output choose credentials, SQL, shell commands or URLs without validation and allow-lists; isolate tools; strip secrets/PII before sending to third parties; log redacted. Output filtering for policy and PII; rate-limit and cap tokens per user (`threat-modeling` for LLM-specific abuse paths).

## Cost & latency
Cache (prompt/prefix caching, semantic cache with care), stream tokens, batch offline work, trim context (summarize history, send only needed chunks), set `max_tokens`, choose model by task, parallelize independent calls, timeouts + retries with backoff on 429/5xx. Track tokens in `observability` metrics.

## Delivery checklist
Schema-validated outputs - eval suite in CI - injection and abuse cases tested - budget and rate limits - fallback path - tracing of prompts/responses (redacted) - model/version pinned and upgrade plan.
