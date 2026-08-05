# Property Value Insights — Copilot Instructions

## Project context

Property Value Insights is a machine learning project for property value prediction.

The repository includes model development, trained artifacts, a FastAPI inference API, Pydantic schemas, OpenAPI documentation, automated tests, Docker configuration, and model governance documentation.

Prioritize:

- reproducibility;
- backward compatibility;
- safe model serving;
- traceable technical decisions;
- small, reviewable changes;
- honest communication of model limitations.

## Sources of truth

Before making changes, inspect the relevant:

1. GitHub Issue and acceptance criteria;
2. existing implementation;
3. automated tests;
4. `README.md`;
5. `pyproject.toml` and lock files;
6. GitHub Actions workflows;
7. model manifests and technical documentation.

The current Issue defines the task scope.

Do not treat review notes, historical reports, recommendations, or future possibilities as approved requirements unless the Issue explicitly approves them.

## Before editing

Before changing files:

1. read the complete Issue;
2. inspect the affected code, tests, and documentation;
3. confirm whether the requested behavior already exists;
4. identify the smallest change that satisfies the Issue;
5. check compatibility, data, security, and model-governance risks;
6. prepare a concise implementation plan.

## Scope control

- Keep each change focused on one Issue.
- Modify only files required by the task.
- Do not perform unrelated refactoring or formatting.
- Do not rename public files, modules, endpoints, fields, or classes without a requirement.
- Do not silently expand the task.
- Report useful out-of-scope improvements in the pull request instead of implementing them.
- Do not implement optional or future ideas unless explicitly requested.

## Handling ambiguity

Do not guess when a task requires an undocumented architectural, breaking, modeling, governance, data-policy, or dependency decision.

When an important decision is unresolved:

1. preserve existing behavior;
2. implement only the unambiguous portion;
3. document the assumption or blocker in the pull request;
4. leave the disputed change unimplemented.

Prefer a safe incomplete change over an invented decision.

## Backward compatibility

Preserve backward compatibility by default.

Do not remove, rename, or change the meaning of existing:

- API endpoints;
- request or response fields;
- HTTP status codes;
- configuration variables;
- model metadata;
- public functions;
- documented behavior.

Prefer additive changes.

A breaking change is allowed only when the Issue explicitly approves it and documents why the benefit outweighs compatibility and migration risks.

Evaluate a proposed breaking change by considering:

- impact and probability of the current problem;
- expected benefit;
- compatibility cost;
- reversibility;
- availability of a compatible alternative.

Do not implement a breaking change without an approved versioning, migration, and rollback plan.

## Machine learning and artifact integrity

- Do not retrain models unless explicitly requested.
- Do not regenerate, replace, or manually modify model artifacts unless explicitly requested.
- Keep artifact, manifest, version, metadata, and SHA-256 hash consistent.
- Never invent metrics, dataset properties, or evaluation results.
- Do not change training or evaluation splits without approval.
- Do not present an inspected diagnostic period as an untouched test set.
- Treat possible target proxies, temporal leakage, and data leakage explicitly.
- Do not add a potentially leaking feature without documented analysis and approval.

## Model governance

Distinguish between:

- statistical experiment winner;
- model approved for serving;
- experimental candidate;
- future model possibility.

A statistically better result does not automatically authorize deployment.

The currently served physical-property model must not be replaced solely because another experiment achieved a marginally better metric.

Demographic features require explicit review of proxy risk, governance, explainability, maintainability, and serving approval.

A specialized high-value model and routing between multiple models are future possibilities. Do not implement them without a specific Issue.

Preserve documented limitations, including high-value underprediction and limited geographic or temporal coverage.

## API work

For API changes:

- preserve the existing contract by default;
- keep implementation, Pydantic schemas, tests, and OpenAPI documentation consistent;
- apply equivalent behavior to single and batch prediction where appropriate;
- distinguish syntactic validation, domain validation, and out-of-distribution detection;
- use correct HTTP semantics;
- do not document behavior that is not implemented and tested;
- never expose secrets, local paths, stack traces, or internal details;
- do not claim that a health check verifies something it does not verify.

API examples must be plausible and valid for the model domain.

## Code quality

- Follow the existing architecture and style.
- Prefer clear, explicit code over unnecessary abstraction.
- Use type hints consistently.
- Reuse existing utilities before creating new ones.
- Avoid duplicated validation and business logic.
- Do not suppress warnings or exceptions without justification.
- Do not add dependencies unless necessary for the Issue.
- Do not replace the package manager or development tools.
- Update lock files only when dependencies change.

## Commands and validation

Inspect repository configuration before running commands.

Expected commands include:

```bash
uv sync --frozen
uv run pytest
uv run ruff check .
uv run ruff format --check .
docker compose up --build
```

If repository configuration differs, follow the repository and report the actual commands used.

Never claim that a command passed if it was not executed successfully.

## Testing

After modifying code:

1. run tests directly related to the change;
2. add regression tests for corrected defects;
3. test relevant boundary and failure cases;
4. run the full test suite when feasible;
5. run configured linting and formatting checks;
6. verify documentation against actual behavior.

When relevant, verify individual and batch prediction consistency, artifact loading, manifest and hash consistency, invalid inputs, internal failures, and absence of information leakage.

If a command cannot be executed, state which command, why, and what remains unverified.

## Documentation and repository hygiene

- Keep documentation consistent with implementation.
- Preserve the existing language of each document.
- Use English for code identifiers, API fields, and established technical terms.
- Distinguish current behavior, approved decisions, recommendations, historical records, and future possibilities.
- Do not make unsupported claims about production readiness, accuracy, fairness, or security.
- Never commit secrets, credentials, tokens, local absolute paths, caches, logs, or temporary files.
- Do not disable tests or weaken validation merely to make checks pass.
- Do not change GitHub Actions permissions without an explicit requirement.

## Pull requests

Changes must be delivered through a pull request and must not be pushed directly to `main`.

Keep the pull request focused and include:

- problem addressed;
- implementation summary;
- reason for the chosen approach;
- compatibility impact;
- tests and commands executed;
- results and remaining limitations;
- assumptions and unverified points;
- relevant out-of-scope observations.

Before declaring completion, confirm that the Issue requirements were addressed, tests pass, documentation matches behavior, artifacts remain consistent, and no unrelated changes or sensitive files were introduced.
