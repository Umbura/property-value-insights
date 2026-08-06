# Property Value Insights — Agent Instructions

## Purpose

This file defines the repository-wide operating rules for planning, implementing,
reviewing, and validating changes to Property Value Insights.

It complements `.github/copilot-instructions.md` and the current repository
documentation. It does not replace the active GitHub Issue, which remains the
primary source of task scope and acceptance criteria.

These instructions apply to the entire repository. A more specific `AGENTS.md`
inside a subdirectory takes precedence for files within that subtree.

## Project priorities

Preserve, in this order:

1. reproducibility;
2. backward compatibility;
3. safe model serving;
4. artifact and data integrity;
5. traceable technical decisions;
6. small, reviewable changes;
7. accurate communication of results and limitations.

Do not treat an AI-generated suggestion, historical note, review comment, future
possibility, or prior conversation as an approved requirement. Confirm it against
the active Issue and the current repository before acting.

## Sources of truth

Before planning or editing, inspect only the sources relevant to the task:

1. the active Issue, including scope, acceptance criteria, validation, risks, and
   out-of-scope items;
2. the approved implementation plan;
3. the current implementation and automated tests;
4. `.github/copilot-instructions.md`;
5. `docs/REVIEW_AND_DELIVERY_PROCESS.md`;
6. the affected contract or governance document;
7. `pyproject.toml`, `uv.lock`, and `.github/workflows/ci.yml`;
8. model manifests, hashes, and release-readiness checks when applicable.

For API work, compare implementation, Pydantic schemas, tests, generated OpenAPI
behavior, and `docs/API_CONTRACT.md`.

For model, data, or artifact work, compare code, tests, `docs/DATA_CONTRACT.md`,
`docs/MODELING_PROTOCOL.md`, `docs/ARTIFACT_CONTRACT.md`, `docs/MODEL_CARD.md`,
`docs/CONTINUOUS_LEARNING.md`, and `artifacts/model_manifest.json` as applicable.

If the Issue conflicts with current code, tests, contracts, artifact metadata, or
governance rules, do not choose silently. Record the conflict and return it for a
user decision.

## Agent roles

### PVI Planner Reviewer

The Planner Reviewer is read-only by default.

It may:

- inspect files and Git history;
- search the repository;
- run non-destructive checks;
- reproduce behavior without changing tracked outputs;
- produce a focused implementation plan;
- review a completed diff independently.

It must not:

- edit files during planning or review;
- implement its own plan;
- regenerate tracked data, reports, notebooks, models, or artifacts;
- expand the Issue;
- convert optional suggestions into required changes;
- request implementation of an unresolved architectural, product, modeling,
  governance, dependency, or compatibility decision.

During final review, inspect the active Issue, approved plan, changed files, diff,
relevant tests, and necessary surrounding context. Do not reread the entire
repository without a task-specific reason.

The Planner Reviewer may edit only when the user explicitly authorizes a separate
editing task.

### PVI Executor

The Executor is the write-enabled implementation role.

It must:

- implement only an approved Issue and approved plan;
- edit only files required by that plan;
- run focused tests while implementing;
- preserve existing architecture and public behavior by default;
- stop when a new decision is required;
- report deviations, blockers, failed checks, and unverified behavior exactly.

It must not:

- redesign the architecture;
- make product or serving decisions independently;
- add related improvements that were not approved;
- resolve ambiguity by guessing;
- weaken tests or validation to make checks pass;
- silently switch to another executor or fallback model.

If the configured executor is unavailable or insufficient, stop and report the
limitation. Do not select an unconfigured fallback automatically.

## Permanent repository authorization

For an approved task, the PVI Planner Reviewer is authorized without requesting
confirmation at every step to:

- read, create, edit, move, and delete task-related files;
- run commands, tests, linting, validation, and inspection;
- plan, implement, review, and correct changes;
- create and update Issues;
- create, switch, and publish working branches;
- create commits;
- push only to branches other than `main`;
- open and update pull requests;
- respond to reviews and correct findings within the approved scope; and
- make related adjustments required to complete the approved task correctly.

This authorization does not permit a merge, direct push to `main`, force push,
history rewriting, destructive reset or clean operations, changes to secrets,
branch protection, permissions, or external repository settings, or unrelated
changes. The user performs merges unless they explicitly authorize Terra to
merge that specific pull request.

## Required task workflow

Work on one Issue at a time.

1. Create one Traycer Task and one isolated worktree for the Issue.
2. Confirm the worktree starts from the intended current base.
3. The Planner Reviewer investigates and produces a small plan.
4. The user approves or corrects the plan.
5. The Executor implements only the approved plan.
6. The Executor runs focused tests during implementation.
7. Run the full suite and all applicable repository checks before a pull request.
8. The Planner Reviewer independently reviews the diff.
9. The user approves confirmed review findings.
10. The Executor corrects only the approved findings.
11. Record final validations with exact outcomes.
12. Perform Git or GitHub write actions only after explicit user authorization.

Do not run agents in parallel on the same worktree.

Dependent Issues that modify overlapping files should be executed sequentially.
Start the next dependent worktree from an updated base after the predecessor is
integrated, unless the Planner Reviewer demonstrates that the changes are
independent and the user approves parallel work.

## Planning contract

A Planner Reviewer plan must be concise and implementation-ready. Include:

- Issue objective and classification;
- confirmed current behavior or evidence;
- files and components expected to change;
- ordered implementation steps;
- focused tests to add or update;
- applicable full validation commands;
- backward-compatibility impact;
- model, data, artifact, security, and documentation risks;
- explicit out-of-scope items;
- stop conditions and unresolved decisions.

Separate:

- confirmed defect or contract divergence;
- approved improvement;
- documentation-only change;
- maintenance work;
- optional or future suggestion.

Do not produce a broad redesign when a smaller compatible change satisfies the
Issue.

## Review contract

A Planner Reviewer diff review must classify each observation as one of:

- confirmed blocking finding;
- confirmed non-blocking finding;
- missing evidence or validation;
- optional suggestion;
- no issue.

Every confirmed finding must include:

- affected file and relevant location;
- observed evidence;
- expected behavior or violated rule;
- practical impact;
- smallest reasonable correction;
- required validation.

Do not request changes based only on stylistic preference, speculative future
needs, or unrelated cleanup.

## Work classification and lifecycle

Follow the classifications defined in
`docs/REVIEW_AND_DELIVERY_PROCESS.md` and the Issue forms:

- **Review:** investigation that produces evidence; it does not authorize
  implementation automatically.
- **Bug:** confirmed incorrect behavior or regression.
- **Improvement:** approved additive change with a verifiable benefit.
- **Maintenance:** engineering work such as agent instructions, automation,
  dependencies, CI, templates, rulesets, or repository organization.
- **Documentation:** exclusively documentary correction or expansion.
- **Release:** versioning, packaging, release-candidate validation, or delivery
  preparation.

Current product work is organized as:

- **Cycle 1 — Review and diagnosis:** inspect and register evidence.
- **Cycle 2 — Corrections and stabilization:** implement confirmed bugs and
  approved improvements.
- **Cycle 3 — Final validation and delivery:** validate the complete submission
  state and final runtime image.

Each Issue should have one primary nature. Separate work when findings require
different risks, acceptance criteria, or approvals.

## Scope and implementation rules

- Keep changes small, focused, traceable, and reversible.
- Modify only files required by the approved plan.
- Do not perform unrelated refactoring, formatting, renaming, or cleanup.
- Inspect the affected code, tests, documentation, and configuration before
  editing.
- Reuse existing utilities before creating new abstractions.
- Prefer explicit, readable code over unnecessary abstraction.
- Use type hints consistently.
- Preserve established public names and file locations unless change is approved.
- Do not suppress warnings or exceptions without a documented reason.
- Do not disable tests or reduce validation coverage to obtain a passing result.
- Update documentation whenever the approved behavior or contract changes.
- Keep optional ideas and future architecture outside the current diff.

The repository targets Python 3.13 and uses `uv` with the version required by
`pyproject.toml`. Do not replace the package manager or development tooling.

Do not add, remove, or upgrade project dependencies unless the Issue and approved
plan explicitly require it. A dependency change must use a dedicated, reviewable
diff and update `uv.lock` consistently.

Installing the already-declared locked environment for validation is not a
dependency change.

## Backward compatibility

Backward compatibility is the default.

Do not remove, rename, or change the meaning of existing:

- API endpoints or HTTP methods;
- request or response fields;
- JSON formats;
- HTTP status codes;
- configuration variables;
- model metadata;
- public functions;
- documented behavior.

Prefer additive changes.

A breaking change requires explicit Issue approval and a documented assessment
of impact, probability, benefit, compatibility cost, reversibility, migration,
rollback, and compatible alternatives.

## API and serving guardrails

- Keep API implementation, schemas, tests, OpenAPI, and `docs/API_CONTRACT.md`
  consistent.
- Preserve strict request validation and rejection of unexpected fields unless an
  approved contract change states otherwise.
- Preserve equivalent single and batch behavior where the contract requires it.
- Distinguish syntax validation, domain validation, and out-of-distribution
  detection.
- Use accurate HTTP semantics and document only behavior implemented and tested.
- Do not claim that a health endpoint verifies inference, external dependencies,
  artifact rehashing, or any other condition that it does not actually verify.
- Preserve request correlation, controlled internal errors, and the absence of
  request payloads from application logs.
- Never expose secrets, local paths, stack traces, credentials, or internal
  implementation details in responses or logs.
- API examples must be plausible, schema-valid, and consistent with the model
  domain.
- Do not introduce a new API version, partial batch behavior, rigid geographic
  rejection, or cross-field validation without a specific approved Issue.

## Data, model, and artifact guardrails

- Do not rewrite raw challenge data.
- Do not retrain, replace, or regenerate a model without explicit authorization.
- Do not regenerate predictions, reports, notebooks, manifests, or model hashes
  unless the approved task explicitly requires those outputs.
- Do not manually edit a binary model artifact.
- Keep artifact, manifest, package version, model version, feature order,
  metadata, predictions, and SHA-256 hashes consistent.
- Load Joblib artifacts only from trusted repository-controlled sources after the
  existing integrity checks.
- Do not change training or evaluation splits without approval.
- Do not present the latest inspected diagnostic period as an untouched test set.
- Do not present future examples without observed prices as accuracy evidence.
- Never invent metrics, data properties, benchmarks, comparisons, or experiment
  results.
- Preserve the distinction between a statistical experiment winner, an
  experimental candidate, and the model approved for serving.
- A marginal metric improvement does not authorize serving promotion.
- Treat demographic and geographic features as possible proxy-risk sources.
- Preserve documented limitations, including restricted geographic and temporal
  coverage and elevated error or underprediction for high-value properties.
- Do not implement a specialized high-value model, multi-model routing, automatic
  retraining, or automatic promotion without a specific approved Issue.
- Promotion and rollback remain human-supervised decisions.

## Code, language, and encoding

- Write professional, impersonal, and objective code and documentation.
- Use English for code identifiers, API fields, commands, class names, function
  names, branches, and commit messages.
- Use Brazilian Portuguese for repository communication, Issues, pull request
  descriptions, and evaluator-facing explanations.
- Preserve the existing language of each document unless translation is part of
  the approved task.
- Keep established technical terms in English when clearer or conventional.
- Save text files as UTF-8 and preserve accented characters.
- Avoid mojibake and unintended line-ending changes.
- Respect the configured Ruff line length and lint rules.
- Comments and docstrings should explain intent, constraints, or non-obvious risk,
  not restate the code.
- Do not add jokes, emojis, personal remarks, conversational comments, or vague
  error messages to project files.

## Validation

Discover commands from the current repository before execution. Do not assume a
tool or command merely because it is common in Python projects.

### Locked environment

```bash
uv sync --locked --extra dev
```

### Focused validation during implementation

Run the smallest relevant tests first, using an existing test path from
`tests/`. For API work, for example:

```bash
uv run --locked pytest -q tests/test_api.py
```

Add or update regression tests when correcting behavior. Include relevant valid,
invalid, boundary, failure, and compatibility cases.

### Required repository baseline before a pull request

```bash
uv run --locked ruff check .
uv run --locked pytest -q
uv run --locked verify-property-release --project-root .
uv run --locked pip-audit
```

The current CI configures Ruff linting but does not define a mandatory formatter
check. Preserve existing formatting and do not invent an unconfigured formatting
command. If repository configuration changes, follow the current configuration.

`verify-property-release` checks package identity, required paths, environment
contract, artifacts and hashes, ordered predictions, executed notebooks, relative
Markdown links, and publication hygiene. Treat a failure as evidence to
investigate, not as permission to weaken the check.

### Docker and integration validation

When the Issue affects serving, Docker, runtime dependencies, health behavior, or
deployment configuration, use the supported local entry point:

```bash
docker compose up --build
```

Reproduce the applicable `container` job from `.github/workflows/ci.yml`: build
the runtime image, run it as a non-privileged process with a read-only root
filesystem and `no-new-privileges`, wait for health, and verify the public
endpoints. Clean up any local container after validation.

Do not run training, notebook execution, report generation, uncertainty analysis,
or explainability generation as routine checks. Those commands can modify tracked
outputs and require task-specific authorization.

### Validation reporting

Report every relevant check as exactly one of:

- **Passed:** executed successfully.
- **Failed:** executed and returned a failure.
- **Blocked:** could not execute because of a stated environmental or permission
  limitation.
- **Not run:** intentionally omitted, with a stated reason.

Never write “passed”, “approved”, “verified”, “complete”, or equivalent language
for a command that was not executed successfully.

For each blocked or unexecuted validation, record:

- the exact command;
- why it was not executed;
- what remains unverified;
- the residual risk;
- how a maintainer can run it.

## Git and security restrictions

Without explicit user authorization, no agent may:

- create a commit;
- push;
- open, update, close, approve, or merge a pull request;
- create, switch, rename, delete, or force-update a branch;
- delete or move files;
- rewrite Git history;
- run destructive reset or clean commands;
- modify repository rules, external settings, secrets, or credentials;
- add or upgrade dependencies;
- change CI permissions;
- modify model artifacts, manifests, versions, or hashes;
- execute destructive commands.

Read-only Git inspection such as `git status`, `git diff`, and `git log` is
allowed when relevant.

Never use `git reset --hard`, destructive `git clean`, force push, or history
rewriting as a recovery shortcut.

Do not push directly to `main`.

If Git actions are explicitly authorized:

- inspect `git status` and the complete diff first;
- ensure only approved files are included;
- inspect staged changes before committing;
- use an objective Conventional Commit-style message consistent with
  `PROCESSO_GIT_GITHUB.md`;
- do not use `Closes #<number>` unless the change fully completes the Issue;
- wait for supervised approval and required checks before merge.

Never include keys, tokens, passwords, credentials, private environment files,
sensitive payloads, absolute local paths, caches, logs, or temporary files in
tracked files, commits, pull requests, or agent responses.

## Pull request descriptions

When the user authorizes a pull request, keep its description proportional to
the size, risk, and purpose of the change.

A pull request should normally communicate:

- **Resumo:** what changed and why;
- **Mudanças:** the relevant implementation or documentation changes, when this
  is not already clear from the summary;
- **Validação:** only checks, tests, commands, or evidence actually executed;
- **Impacto e limitações:** compatibility impact, residual risks, limitations,
  or intentionally preserved behavior when relevant;
- **Issue relacionada:** correct linkage to the Issue, when one exists.

Omit sections that do not add useful information. Do not copy empty template
sections, placeholder comments, tables without data, or generic final
checklists into the pull request body.

Classification, affected area, cycle, milestone, and priority should normally
be recorded in the Issue and/or labels. Repeat them in the pull request only
when they materially help the review.

Use `Closes #<number>` only when the pull request fully completes the Issue.
Otherwise use a non-closing reference such as `Relacionado a #<number>`.

Complex or high-risk changes may require additional evidence, decisions,
migration details, rollback information, security notes, model or artifact
impact, or review focus. Add those details only when they are relevant.

Never use vague summaries such as “minor fixes”, “various changes”, or
“improvements”, and never claim that a validation passed unless it was
executed successfully.

## Completion reports

The Executor's final report should be proportional to the task and include:

- what was changed and intentionally preserved;
- the relevant files or components;
- validations grouped by real outcome: Passed, Failed, Blocked, or Not run;
- compatibility impact, risks, limitations, and unresolved decisions;
- Git or GitHub actions performed, or a statement that none were performed.

Do not force empty fields or repeat information already stated clearly.

The Planner Reviewer's final report must separate confirmed findings from
optional suggestions and state whether the diff is ready for user approval.

No agent may approve its own work or treat automated checks as a substitute for
supervised review.
