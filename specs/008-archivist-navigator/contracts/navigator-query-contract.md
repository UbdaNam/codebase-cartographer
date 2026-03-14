# Contract: Navigator Query Interface

## Purpose

Define the request, state, and response contract for the LangGraph-based
Navigator query interface so CLI consumers and future wrappers can retrieve
architectural intelligence through stable, evidence-backed responses.

## Required Tools

- `find_implementation(concept)`
- `trace_lineage(dataset, direction)`
- `blast_radius(module_path)`
- `explain_module(path)`

## Required LangGraph Stages

- `classify_query`
- `retrieve_relevant_artifacts`
- `select_tool`
- `execute_tool`
- `synthesize_response`
- `attach_citations_and_trust_metadata`

## Request Schema

- **`query_type`**: one of the four required tool types
- **`query_text`**: free-text request or target concept
- **`target_identifier`**: module path, dataset name, or symbol-like target
- **`direction`**: lineage direction when required
- **`include_inference`**: whether bounded synthesis may run when retrieval is
  insufficient
- **`run_id`**: optional analyzed run to target; defaults to the latest valid
  run

## LangGraph State Requirements

State must track:

- user query
- chosen tool
- retrieved context
- evidence references
- response draft
- trust metadata

## Response Schema

- **`request`**: normalized typed request
- **`summary`**: concise answer summary
- **`results`**: ordered structured answer items
- **`partial_result_flags`**: degraded-result markers
- **`trace_event_ids`**: linked trace records for the query
- **`used_model_synthesis`**: whether model-backed synthesis contributed

## Citation Requirements

Every response must include citations containing:

- source file
- line range when available
- analysis method used
- whether the answer comes from static analysis, graph/lineage reasoning,
  reused artifact evidence, or LLM inference

## Behavioral Guarantees

- Navigator retrieves from stored artifacts and semantic index entries before
  any optional synthesis.
- Responses distinguish direct observations from inferred conclusions.
- Identical inputs against unchanged artifacts produce deterministically ordered
  results.
- Provider unavailability does not prevent useful responses when artifact-based
  evidence exists.

## Error and Partial-Result Contract

- Navigator emits structured partial-result markers for:
  - unsupported targets
  - no matching evidence
  - incomplete citation ranges
  - unavailable synthesis
  - stale or inconsistent upstream artifacts
- Navigator must never return unsupported certainty when evidence is weak or
  absent.
