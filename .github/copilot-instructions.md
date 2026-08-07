# Property Value Insights — Copilot Instructions

## Project context

Property Value Insights is a machine learning project for residential property value prediction.

The repository includes model development, trained artifacts, a FastAPI inference API, Pydantic schemas, OpenAPI documentation, automated tests, Docker configuration, observability, and model governance documentation.

The published `v1.0.0` is the first stable integrated release and the baseline for review. It does not mean that the technical challenge has already been submitted.

Prioritize:

- reproducibility;
- backward compatibility;
- safe model serving;
- traceable technical decisions;
- small, reviewable changes;
- honest communication of model limitations.

## Project lifecycle

The historical Phases 0–7 record the construction of `v1.0.0`. Current work follows three cycles:

1. **Ciclo 1 — Revisão e diagnóstico:** inspect, test, and record evidence without silently implementing findings;
2. **Ciclo 2 — Correções e estabilização:** correct confirmed bugs and implement approved improvements with regression coverage;
3. **Ciclo 3 — Validação final e entrega:** validate the complete submission state, including clean installation, documentation, CI, artifacts, hashes, and the final Docker runtime image.

The final Docker image intended for submission belongs to Cycle 3. Reviews in Cycle 1 may build and inspect the current image, but must not publish or present it as the final delivery image.

Use `docs/REVIEW_AND_DELIVERY_PROCESS.md` as the source of truth for the current lifecycle. Use `docs/process/PROCESSO_GIT_GITHUB.md` as the historical record of Phases 0–7.

## Work classification

Each Issue should record, or be labeled with:

- one primary nature;
- one or more affected areas;
- cycle or approved maintenance context;
- priority.

### Primary nature

- **Review:** test, audit, or investigation that produces evidence. It does not authorize a correction or improvement automatically.
- **Bug:** confirmed incorrect behavior or regression against code, tests, contract, or current documentation.
- **Improvement:** approved additive change with a verifiable benefit.
- **Maintenance:** engineering maintenance that is not a new product capability.
- **Documentation:** exclusively documentary correction or expansion.
- **Release:** versioning, packaging, release-candidate validation, or delivery preparation.

### Areas

Use one or more of:

- API;
- Model;
- Data;
- Testing;
- Docker;
- CI;
- Documentation;
- Governance;
- Repository;
- Automation.

### Priority

- **High:** blocks delivery or compromises reliability, security, reproducibility, or a main workflow;
- **Medium:** relevant impact with an available workaround or no immediate delivery block;
- **Low:** non-blocking refinement, cleanup, or minor improvement.

Copilot, ChatGPT, AI integrations, templates, automations, dependency maintenance, CI configuration, rulesets, and repository organization must be classified as **Maintenance**, normally in **Repository**, **Automation**, **CI**, or **Governance**, unless they also change product behavior.

Pull requests do not need to repeat classification metadata unless it materially
helps the review.

## Sources of truth

Before making changes, inspect the relevant:

1. GitHub Issue and acceptance criteria;
2. existing implementation;
3. automated tests;
4. `README.md`;
5. `docs/REVIEW_AND_DELIVERY_PROCESS.md`;
6. `pyproject.toml` and `uv.lock`;
7. GitHub Actions workflows;
8. model manifests and technical documentation.

The current Issue defines the approved task scope. AI suggestions are not autonomous sources of truth.

Do not treat review notes, historical reports, recommendations, Copilot comments, or future possibilities as approved requirements unless the Issue explicitly approves them.

## Issue, branch, and pull request flow

Every repository change must follow this flow:

1. read or create an Issue with objective, scope, acceptance criteria, and
   out-of-scope items;
2. create a short branch from `main`;
3. implement only the approved scope;
4. open a pull request linked to the Issue;
5. record validations actually executed and any relevant limitations;
6. address review findings;
7. merge only after explicit supervised approval and required checks.

Use `Closes #<number>` only when the pull request fully completes that Issue. Use a descriptive reference such as `Relacionado a #<number>` when the relationship must not close the Issue automatically.

Do not push changes directly to `main`.

## Before editing

Before changing files:

1. read the complete Issue;
2. confirm its scope and acceptance criteria, plus any relevant classification
   or labels;
3. inspect the affected code, tests, documentation, and current branch state;
4. confirm whether the requested behavior already exists;
5. identify the smallest change that satisfies the Issue;
6. check compatibility, data, security, artifact, and model-governance risks;
7. prepare a concise implementation plan.

## Scope control

- Keep each change focused on one Issue.
- Modify only files required by the task.
- Do not perform unrelated refactoring or formatting.
- Do not rename public files, modules, endpoints, fields, or classes without a requirement.
- Do not silently expand the task.
- Report useful out-of-scope improvements in the pull request instead of implementing them.
- Do not implement optional or future ideas unless explicitly requested.
- During a Review, record findings and open derived Issues instead of applying silent corrections.
- Separate findings with different nature, risk, or acceptance criteria into different Issues.

## Handling ambiguity

Do not guess when a task requires an undocumented architectural, breaking, modeling, governance, data-policy, security, dependency, or serving decision.

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
- keep implementation, Pydantic schemas, tests, OpenAPI documentation, and `docs/API_CONTRACT.md` consistent;
- apply equivalent behavior to single and batch prediction where appropriate;
- distinguish syntactic validation, domain validation, and out-of-distribution detection;
- use correct HTTP semantics;
- do not document behavior that is not implemented and tested;
- never expose secrets, local paths, stack traces, or internal details;
- do not claim that a health check verifies something it does not verify.

API examples must be plausible and valid for the model domain.

## Code quality

- Follow the existing architecture and style.
- Write code in a professional, impersonal, and objective style.
- Avoid colloquial language, jokes, personal remarks, emojis, and conversational comments in code.
- Use clear and descriptive names for variables, functions, classes, modules, and tests.
- Comments and docstrings must explain intent, constraints, non-obvious decisions, and relevant risks.
- Do not add comments that merely restate what the code already expresses.
- Error messages and logs must be clear, neutral, and appropriate for a professional system.
- Prefer clear, explicit code over unnecessary abstraction.
- Use type hints consistently.
- Reuse existing utilities before creating new ones.
- Avoid duplicated validation and business logic.
- Do not suppress warnings or exceptions without justification.
- Do not add dependencies unless necessary for the Issue.
- Do not replace the package manager or development tools.
- Update lock files only when dependencies change.

## Commands and validation

Inspect repository configuration before running commands. The locked development and CI baseline is:

```bash
uv sync --locked --extra dev
uv run --locked ruff check .
uv run --locked pytest -q
uv run --locked verify-property-release --project-root .
uv run --locked pip-audit
```

For local runtime validation when relevant:

```bash
docker compose up --build
```

The CI container job builds the image directly and verifies the public endpoints under a read-only filesystem and a non-privileged runtime. Follow `.github/workflows/ci.yml` when reproducing that validation.

Run only commands relevant to the Issue, but do not omit configured required checks from the pull request evidence. If repository configuration changes, follow the current repository and report the actual commands used.

Never claim that a command passed if it was not executed successfully.

## Testing

After modifying code:

1. run tests directly related to the change;
2. add regression tests for corrected defects;
3. test relevant boundary and failure cases;
4. run the full test suite when feasible;
5. run configured linting and release-readiness checks;
6. verify documentation against actual behavior.

When relevant, verify individual and batch prediction consistency, artifact loading, manifest and hash consistency, invalid inputs, internal failures, and absence of information leakage.

If a command cannot be executed, state which command, why, and what remains unverified.

## Language and encoding

- Save and edit text files using UTF-8 encoding.
- Preserve accented characters and verify that changes do not introduce encoding corruption or mojibake.
- Use Portuguese for communication, explanations, Issue responses, and pull request descriptions.
- Keep established technical terms in English when they are clearer or conventional.
- Use English for code identifiers, API fields, commands, class names, function names, and technical keywords.
- Preserve the existing language of each document unless the Issue explicitly requests a translation.
- Do not translate library names, protocol names, metrics, HTTP concepts, or established software terminology unnecessarily.

## Documentation and repository hygiene

- Keep documentation consistent with implementation.
- Preserve the existing language of each document.
- Use English for code identifiers, API fields, and established technical terms.
- Distinguish current behavior, approved decisions, recommendations, historical records, and future possibilities.
- Do not make unsupported claims about production readiness, accuracy, fairness, or security.
- Never commit secrets, credentials, tokens, local absolute paths, caches, logs, or temporary files.
- Do not disable tests or weaken validation merely to make checks pass.
- Do not change GitHub Actions permissions without an explicit requirement.
- Do not merge dependency or tooling upgrades into an unrelated product or review change.

## Pull requests

Keep each pull request focused, professional, impersonal, and reviewable.

Follow `.github/pull_request_template.md`. The description must include:

- a concise summary of what changed and why;
- relevant changes, when the summary is not sufficient;
- only validation actually executed;
- compatibility impact, risks, limitations, or preserved behavior when relevant;
- correct Issue linkage, when one exists.

Omit irrelevant sections. Complex, risky, breaking, model, data, security,
dependency, CI, or release changes require proportionally more evidence and
detail. Classification, areas, cycle, and priority normally belong in the Issue
or labels rather than being repeated in the pull request.

Do not use vague descriptions such as "minor fixes", "improvements", or "various changes".

Do not claim that a pull request is complete while acceptance criteria, tests, required checks, review conversations, or relevant validations remain unresolved.

Before declaring completion, confirm that the Issue requirements were addressed, tests pass, documentation matches behavior, artifacts remain consistent, required checks are successful, and no unrelated changes or sensitive files were introduced.
