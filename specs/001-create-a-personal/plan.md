# Implementation Plan: Personal Blog with Modern UI

**Branch**: `001-create-a-personal` | **Date**: September 12, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-create-a-personal/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, or `GEMINI.md` for Gemini CLI).
6. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Personal blog platform showcasing writing and projects with modern, professional UI. MVP focuses on visual design and readability, with future AI features (tagging, spellcheck, finder agent). Built as full-stack web application with TDD methodology.

## Technical Context
**Language/Version**: Python 3.11+ (backend), TypeScript/TSX (frontend)  
**Primary Dependencies**: FastAPI (backend), Vite + React 18 (frontend), SQLAlchemy, Alembic  
**Storage**: PostgreSQL  
**Testing**: pytest (backend), Vitest + Testing Library (frontend)  
**Target Platform**: Web application (Linux server + modern browsers)
**Project Type**: web - determines source structure as backend/ and frontend/  
**Performance Goals**: <500ms page load, <200ms API response times  
**Constraints**: TDD MANDATORY (Test-Driven Development strictly enforced), Backend development priority  
**Scale/Scope**: Single-user blog, ~100 posts, responsive design for all screen sizes
**Additional Context**: We are going to generate this using vite (react tsx), using Postgres as the database. The frontend should use react tsx and backend should be in python. I want it to STRICTLY FOLLOW the TDD (Test Driven Development) Approach. This is gonna have both frontend and backend in same project but under more directories. First Priorities should be on Backend

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 2 (backend, frontend) - within limit of 3
- Using framework directly? YES (FastAPI, React directly without wrappers)
- Single data model? YES (shared schema between frontend/backend)
- Avoiding patterns? YES (direct ORM usage, no Repository pattern initially)

**Architecture**:
- EVERY feature as library? YES (blog_core, blog_api, blog_ui libraries planned)
- Libraries listed: blog_core (data models + business logic), blog_api (FastAPI endpoints), blog_ui (React components)
- CLI per library: blog_core --help (data operations), blog_api --help (server management)
- Library docs: llms.txt format planned? YES

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? YES - STRICTLY ENFORCED per user requirements
- Git commits show tests before implementation? YES - mandatory TDD approach
- Order: Contract→Integration→E2E→Unit strictly followed? YES
- Real dependencies used? YES (actual PostgreSQL, not mocks for integration)
- Integration tests for: new libraries, contract changes, shared schemas? YES
- FORBIDDEN: Implementation before test, skipping RED phase - VIOLATION WILL BE REJECTED

**Observability**:
- Structured logging included? YES (using structlog for backend)
- Frontend logs → backend? YES (unified logging stream planned)
- Error context sufficient? YES (detailed error tracking)

**Versioning**:
- Version number assigned? 0.1.0 (MAJOR.MINOR.BUILD)
- BUILD increments on every change? YES
- Breaking changes handled? YES (parallel tests, migration plan)

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure]
```

**Structure Decision**: Option 2 (Web application) - detected "frontend" + "backend" in user requirements

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `/scripts/update-agent-context.sh [claude|gemini|copilot]` for your AI assistant
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Backend-first priority as per user requirements
- Each contract endpoint → contract test task [P]
- Each data model entity → model creation task [P] 
- Each user story from quickstart → integration test task
- Implementation tasks to make tests pass (TDD mandatory)

**Ordering Strategy**:
- TDD order: Tests before implementation (NON-NEGOTIABLE)
- Backend-first priority: Database → Models → API → Frontend
- Dependency order: Models before services before endpoints before UI
- Mark [P] for parallel execution (independent files)
- Each task must include failing test first (RED phase)

**Backend Task Sequence**:
1. Database schema and migrations
2. Model classes with validation
3. API endpoint contract tests  
4. Repository/service layer tests
5. Authentication system tests
6. Implementation to make tests pass

**Frontend Task Sequence**:
1. Component contract tests
2. Page integration tests
3. API client tests
4. Implementation to make tests pass

**Estimated Output**: 35-40 numbered, ordered tasks in tasks.md with strict TDD enforcement

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [x] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*