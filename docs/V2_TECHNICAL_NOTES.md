# RepoMedic AI v2 — Engineering notes

## Request flow

1. `POST /dashboard/runs` creates a new immutable-ID run in memory.
2. `POST /dashboard/runs/{id}/next` advances exactly one stage, running the Python stage synchronously.
3. Investigator executes the original failing tests. Developer generates an allowlisted, verified one-line diff. Tester executes the patched test fixture. Auditor checks the evidence.
4. `POST /runs/{id}/review` applies explicit human approval/rejection. A patch and audit record can only be exported following all four successful steps.
5. The frontend always renders server data. No fake pass/fail values are generated client-side.

## Limits and threat model

Localhost only, unauthenticated demo API; single-process in-memory run storage. The fixture is fixed, the patch function rejects unrecognized source, the subprocess command is fixed with a timeout, and source repositories are never modified. Python subprocess execution here is **not an OS-level sandbox**. An attacker must not be allowed to supply arbitrary code. There are no LLM calls or autonomous diagnostic claims.

## Next engineering milestones

- Persist immutable run histories with SQLite and a signed artifact digest.
- Add real repository adapters in an isolated container with explicit allowlists.
- Add optional model-generated hypotheses under tool permissions with model trace/cost accounting.
- Strengthen concurrency and audit event storage before multi-user deployment.
