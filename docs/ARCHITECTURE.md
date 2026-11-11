# Engineering decisions

## Scope
A complete, reproducible *bounded* repair workflow rather than a general automated programmer. We intentionally separate diagnosis, patch selection, test evidence, policy review, and human approval.

## State machine
`issue → baseline → diagnosis → proposed_source + diff → verification → decision → human review → patch export`.

`RepoMedic State` holds role outputs and audit events. The default run does not mutate a repository. Review releases a portable unified diff only.

## Failure policy
The developer aborts if the baseline unexpectedly passes. A source mismatch is refused. If patched tests fail, the auditor rejects release. The API maps unknown run IDs to HTTP 404, and closed review gates to HTTP 409. There is no automatic retry, hidden model call, or PR submission.

## Threat model
Only project-owned fixture files may be executed. A Python subprocess is not a sandbox for untrusted source. Production would require execution isolation, quotas, policy-enforced I/O and code provenance, stronger validation and auth.

## Why deterministic?
A deterministic benchmark example is reproducible on a recruiter's laptop, including offline. It avoids pretending that an LLM accurately repaired arbitrary repositories. The structure may later support an LLM investigator, but that is a future feature, not a present claim.
