# Delivery Tasks

## Phase 0: Repository Foundation

- [x] Create React frontend scaffold.
- [x] Create Python backend scaffold.
- [x] Create CDK app scaffold.
- [x] Add Dockerfiles and Docker Compose.
- [x] Add GitHub Actions CI.
- [x] Add lint/test commands for frontend and backend.

### Completed: Foundation Alignment (2026-05-24)

**Agents used**: devops-release-lead, backend-platform-lead

**Summary**: Closed all Phase 0 gaps — repo is now locally installable, lintable, and testable end-to-end. No business logic added.

**Files changed**:

| File | Change |
|------|--------|
| `backend/pyproject.toml` | Added `[tool.mypy]` config |
| `backend/tests/conftest.py` | New — shared `client` test fixture |
| `backend/tests/test_health.py` | Refactored to use `client` fixture |
| `frontend/package.json` | Added 5 devDeps (eslint plugins, testing-library, jsdom, typescript-eslint) |
| `frontend/eslint.config.js` | New — ESLint 9 flat config for React/TS |
| `frontend/vite.config.ts` | Added vitest test config (jsdom env) |
| `frontend/src/App.test.tsx` | New — smoke test for App component |
| `frontend/package-lock.json` | Generated via npm install |
| `.github/workflows/ci.yml` | Added lint/test to frontend job, mypy to backend job, npm/pip caching |
| `Makefile` | New — root `install`, `lint`, `test`, `build`, `dev` targets |
| `.gitignore` | Added `.mypy_cache/` |

**Verification**:

| Check | Result |
|-------|--------|
| `ruff check .` | Pass |
| `pytest -v` | 1 passed |
| `mypy src` | No issues (2 files) |
| `npm run lint` | Clean |
| `npm run test` | 1 passed |
| `npm run build` | Built OK |

## Phase 1: Upload and Status MVP

- Build upload screen in React.
- [x] Implement `POST /submissions/upload-url`.
- Implement S3 presigned upload flow.
- [x] Implement `POST /submissions/{id}/start`.
- [x] Implement `GET /submissions/{id}` polling.
- Store submission metadata and events in DynamoDB.
- [x] Implement `GET /submissions/{id}/summary` (thin route, summary gating).
- [x] Implement `GET /submissions` (list with filters).

### Completed: Backend Package Structure & Thin Routes (2026-05-24)

**Agent used**: backend-platform-lead

**Summary**: Built full backend package layout with typed Pydantic schemas, domain constants, structured logging, ID generation, Protocol-based DI for storage/queue, in-memory fake services, thin route handlers for all 5 API endpoints, and 15 tests. No live AWS integration.

**Package structure created**:

```
src/risklens_api/
├── core/          constants, config, ids, logging, errors
├── schemas/       Pydantic request/response models (camelCase serialization)
├── services/      SubmissionService + fake storage/queue
├── api/           thin route handlers + DI deps
└── worker/        placeholder
```

**Files created/modified**:

| File | Change |
|------|--------|
| `src/risklens_api/core/__init__.py` | New — package init |
| `src/risklens_api/core/constants.py` | New — SubmissionStatus enum (9 values), content type allowlist, limits |
| `src/risklens_api/core/config.py` | New — Settings model loaded from env vars |
| `src/risklens_api/core/ids.py` | New — injectable UUID-based ID generator |
| `src/risklens_api/core/logging.py` | New — structured JSON log formatter |
| `src/risklens_api/core/errors.py` | New — domain exceptions (NotFound, InvalidContentType, FileTooLarge, SummaryNotAvailable) |
| `src/risklens_api/schemas/__init__.py` | New — package init |
| `src/risklens_api/schemas/submissions.py` | New — all request/response Pydantic models matching API contract |
| `src/risklens_api/services/__init__.py` | New — package init |
| `src/risklens_api/services/submission_service.py` | New — core business service with Protocol DI |
| `src/risklens_api/services/fakes.py` | New — FakeStorageService, FakeQueueService |
| `src/risklens_api/api/__init__.py` | New — package init |
| `src/risklens_api/api/deps.py` | New — FastAPI dependency injection wiring |
| `src/risklens_api/api/submissions.py` | New — 5 thin route handlers |
| `src/risklens_api/worker/__init__.py` | New — placeholder |
| `src/risklens_api/main.py` | Modified — mounts router, initializes logging |
| `tests/conftest.py` | Modified — fake service fixtures, DI overrides |
| `tests/test_submissions_api.py` | New — 11 API endpoint tests |
| `tests/test_schemas.py` | New — 3 schema serialization tests |

**Verification**:

| Check | Result |
|-------|--------|
| `ruff check .` | All checks passed |
| `pytest -v` | 15 passed (0.11s) |
| `mypy src` | No issues (17 source files) |

Acceptance:

- Upload returns a submission ID quickly.
- UI shows status transitions with no page reload.

## Phase 2: Processing Worker

- Add SQS queue and worker Lambda.
- Read uploaded object from S3.
- Extract text from text files directly.
- Add Textract path for PDF/image submissions.
- Store extracted text artifact in S3.
- Update processing status and event history.

Acceptance:

- A sample submission reaches `EXTRACTING`.
- OCR failure results in a readable `FAILED` state.

## Phase 3: Structured Extraction

- Add Bedrock extraction prompt.
- Add JSON schema validation.
- Extract insured name, address, industry, coverage, limits, and missing fields.
- Store normalized extracted fields in DynamoDB.

Acceptance:

- A synthetic sample produces valid JSON.
- Missing address routes to `NEEDS_REVIEW`.

## Phase 4: Public Data Enrichment

- Build local ingestion scripts for FEMA, OpenFEMA, and NOAA datasets.
- Normalize hazard records by county FIPS.
- Add Census Geocoder lookup.
- Join submission address to county hazard record.

Acceptance:

- A known US address returns county/FIPS and hazard context.
- Stale or missing hazard data is surfaced in the result.

## Phase 5: AI Risk Brief

- Add Bedrock summary prompt.
- Generate executive summary, risk flags, positive signals, broker questions, and confidence.
- Store generated report in S3 and summary metadata in DynamoDB.
- Display final result in React.

Acceptance:

- UI shows extracted facts, hazard enrichment, and AI brief.
- AI output avoids bind/decline/pricing recommendations.

## Phase 6: Infrastructure and CI

- Implement CDK stacks.
- Add budget alerts.
- Add CloudWatch alarms.
- Add GitHub OIDC deploy role.
- Add CI jobs for frontend, backend, Docker, and CDK synth.

Acceptance:

- CI passes on pull request.
- CDK synth succeeds.
- Manual dev deployment can be run from GitHub Actions.

## Phase 7: Demo Hardening

- Add sample synthetic submissions.
- Add seeded hazard cache for demo counties.
- Add error state UI.
- Add README demo script.
- Add screenshots or short demo recording.

Acceptance:

- End-to-end demo completes in under 10 minutes.
- Backend processing is observable through logs and statuses.

