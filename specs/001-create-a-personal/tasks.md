# Tasks: Personal Blog with Modern UI

**Input**: Design documents from `/specs/001-create-a-personal/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/api-spec.yaml

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Web app structure**: `backend/src/`, `backend/tests/`, `frontend/src/`, `frontend/tests/`
- Backend-first priority per user requirements
- Paths reflect the web application structure from plan.md

## Phase 3.1: Project Setup
- [ ] **T001** Create project structure with backend/ and frontend/ directories
- [ ] **T002** Initialize backend Python project with FastAPI, SQLAlchemy, Alembic, pytest dependencies
- [ ] **T003** Initialize frontend Vite + React + TypeScript project with dependencies
- [ ] **T004** [P] Configure backend linting (black, flake8, mypy) in backend/pyproject.toml
- [ ] **T005** [P] Configure frontend linting (ESLint, Prettier) in frontend/.eslintrc.js
- [ ] **T006** Setup PostgreSQL database connection configuration in backend/src/config.py
- [ ] **T007** Create Alembic configuration for database migrations in backend/alembic/
- [ ] **T008** Create Docker Compose configuration with PostgreSQL, backend, and frontend services in docker-compose.yml
- [ ] **T009** [P] Create backend Dockerfile with Python environment in backend/Dockerfile
- [ ] **T010** [P] Create frontend Dockerfile with Node.js environment in frontend/Dockerfile
- [ ] **T011** [P] Create Docker environment files (.env.docker, .env.local) for different deployment contexts
- [ ] **T012** Create development setup script with Docker commands in scripts/docker-setup.sh

## Phase 3.2: Database Schema & Models (Backend Priority)
⚠️ **CRITICAL: Tests MUST be written and MUST FAIL before ANY implementation**

### Database Schema Tests
- [ ] **T013** [P] Database schema test for User entity in backend/tests/integration/test_user_schema.py
- [ ] **T014** [P] Database schema test for BlogPost entity in backend/tests/integration/test_blogpost_schema.py
- [ ] **T015** [P] Database schema test for Project entity in backend/tests/integration/test_project_schema.py
- [ ] **T016** [P] Database schema test for Tag entity in backend/tests/integration/test_tag_schema.py
- [ ] **T017** [P] Database schema test for relationships (blog_post_tags, project_tags) in backend/tests/integration/test_relationships.py

### Model Implementation (ONLY after schema tests are failing)
- [ ] **T018** [P] User model with validation in backend/src/models/user.py
- [ ] **T019** [P] BlogPost model with validation in backend/src/models/blog_post.py
- [ ] **T020** [P] Project model with validation in backend/src/models/project.py
- [ ] **T021** [P] Tag model with validation in backend/src/models/tag.py
- [ ] **T022** Database migration for all entities in backend/alembic/versions/001_initial_schema.py

## Phase 3.3: API Contract Tests (TDD - MUST FAIL FIRST)
⚠️ **ALL TESTS BELOW MUST BE WRITTEN AND FAILING BEFORE IMPLEMENTATION**

### Authentication Contract Tests
- [ ] **T023** [P] Contract test POST /api/v1/auth/login in backend/tests/contract/test_auth_login.py
- [ ] **T024** [P] Contract test POST /api/v1/auth/logout in backend/tests/contract/test_auth_logout.py
- [ ] **T025** [P] Contract test POST /api/v1/auth/refresh in backend/tests/contract/test_auth_refresh.py

### User Profile Contract Tests  
- [ ] **T026** [P] Contract test GET /api/v1/users/me in backend/tests/contract/test_users_get_me.py
- [ ] **T027** [P] Contract test PUT /api/v1/users/me in backend/tests/contract/test_users_update_me.py

### Blog Posts Contract Tests
- [ ] **T028** [P] Contract test GET /api/v1/posts in backend/tests/contract/test_posts_list.py
- [ ] **T029** [P] Contract test POST /api/v1/posts in backend/tests/contract/test_posts_create.py
- [ ] **T030** [P] Contract test GET /api/v1/posts/{slug} in backend/tests/contract/test_posts_get.py
- [ ] **T031** [P] Contract test PUT /api/v1/posts/{slug} in backend/tests/contract/test_posts_update.py
- [ ] **T032** [P] Contract test DELETE /api/v1/posts/{slug} in backend/tests/contract/test_posts_delete.py

### Projects Contract Tests
- [ ] **T033** [P] Contract test GET /api/v1/projects in backend/tests/contract/test_projects_list.py
- [ ] **T034** [P] Contract test POST /api/v1/projects in backend/tests/contract/test_projects_create.py
- [ ] **T035** [P] Contract test GET /api/v1/projects/{slug} in backend/tests/contract/test_projects_get.py
- [ ] **T036** [P] Contract test PUT /api/v1/projects/{slug} in backend/tests/contract/test_projects_update.py
- [ ] **T037** [P] Contract test DELETE /api/v1/projects/{slug} in backend/tests/contract/test_projects_delete.py

### Tags Contract Tests
- [ ] **T038** [P] Contract test GET /api/v1/tags in backend/tests/contract/test_tags_list.py
- [ ] **T039** [P] Contract test POST /api/v1/tags in backend/tests/contract/test_tags_create.py

## Phase 3.4: Integration Tests (User Stories from Quickstart)
⚠️ **CRITICAL: These tests MUST be written and MUST FAIL before implementation**

- [ ] **T040** [P] Integration test: Homepage with featured content in backend/tests/integration/test_homepage_content.py
- [ ] **T041** [P] Integration test: Content readability and navigation in backend/tests/integration/test_content_readability.py
- [ ] **T042** [P] Integration test: MVP functionality without AI features in backend/tests/integration/test_mvp_functionality.py
- [ ] **T043** [P] Integration test: Authentication flow in backend/tests/integration/test_auth_flow.py
- [ ] **T044** [P] Integration test: Blog post CRUD operations in backend/tests/integration/test_blog_crud.py
- [ ] **T045** [P] Integration test: Project CRUD operations in backend/tests/integration/test_project_crud.py
- [ ] **T046** [P] Integration test: Tag filtering and management in backend/tests/integration/test_tag_operations.py

## Phase 3.5: Backend Service Layer (ONLY after contract tests are failing)

### Authentication Services
- [ ] **T047** JWT token service with refresh logic in backend/src/services/auth_service.py
- [ ] **T048** Password hashing and validation service in backend/src/services/security_service.py
- [ ] **T049** User authentication middleware in backend/src/middleware/auth_middleware.py

### Core Services  
- [ ] **T050** [P] User service with CRUD operations in backend/src/services/user_service.py
- [ ] **T051** [P] BlogPost service with CRUD and slug generation in backend/src/services/blog_service.py
- [ ] **T052** [P] Project service with CRUD and slug generation in backend/src/services/project_service.py
- [ ] **T053** [P] Tag service with CRUD and association management in backend/src/services/tag_service.py

### Utility Services
- [ ] **T054** [P] Slug generation utility in backend/src/utils/slug_utils.py
- [ ] **T055** [P] Pagination utility in backend/src/utils/pagination.py
- [ ] **T056** [P] Input validation schemas using Pydantic in backend/src/schemas/

## Phase 3.6: API Endpoints Implementation (ONLY after services exist)

### Authentication Endpoints
- [ ] **T057** POST /api/v1/auth/login endpoint in backend/src/api/auth.py
- [ ] **T058** POST /api/v1/auth/logout endpoint in backend/src/api/auth.py  
- [ ] **T059** POST /api/v1/auth/refresh endpoint in backend/src/api/auth.py

### User Profile Endpoints
- [ ] **T060** GET /api/v1/users/me endpoint in backend/src/api/users.py
- [ ] **T061** PUT /api/v1/users/me endpoint in backend/src/api/users.py

### Blog Posts Endpoints
- [ ] **T062** GET /api/v1/posts endpoint with pagination in backend/src/api/posts.py
- [ ] **T063** POST /api/v1/posts endpoint in backend/src/api/posts.py
- [ ] **T064** GET /api/v1/posts/{slug} endpoint in backend/src/api/posts.py
- [ ] **T065** PUT /api/v1/posts/{slug} endpoint in backend/src/api/posts.py
- [ ] **T066** DELETE /api/v1/posts/{slug} endpoint in backend/src/api/posts.py

### Projects Endpoints
- [ ] **T067** GET /api/v1/projects endpoint with pagination in backend/src/api/projects.py
- [ ] **T068** POST /api/v1/projects endpoint in backend/src/api/projects.py
- [ ] **T069** GET /api/v1/projects/{slug} endpoint in backend/src/api/projects.py
- [ ] **T070** PUT /api/v1/projects/{slug} endpoint in backend/src/api/projects.py
- [ ] **T071** DELETE /api/v1/projects/{slug} endpoint in backend/src/api/projects.py

### Tags Endpoints
- [ ] **T072** GET /api/v1/tags endpoint in backend/src/api/tags.py
- [ ] **T073** POST /api/v1/tags endpoint in backend/src/api/tags.py

## Phase 3.7: Backend Integration & Configuration

- [ ] **T074** FastAPI application setup and routing in backend/src/main.py
- [ ] **T075** Database session management and dependency injection in backend/src/database.py
- [ ] **T076** CORS configuration for frontend integration in backend/src/middleware/cors.py
- [ ] **T077** Error handling and logging middleware in backend/src/middleware/error_handler.py
- [ ] **T078** API documentation and OpenAPI configuration in backend/src/main.py
- [ ] **T079** Environment configuration and settings in backend/src/config.py

## Phase 3.8: CLI Tools (Library-First Architecture)

- [ ] **T080** [P] Blog management CLI in backend/src/cli/blog_cli.py (--create-post, --publish, --list)
- [ ] **T081** [P] User management CLI in backend/src/cli/user_cli.py (--create-user, --list-users)
- [ ] **T082** [P] Database management CLI in backend/src/cli/db_cli.py (--migrate, --seed, --reset)

## Phase 3.9: Frontend Setup & Testing (After Backend Core Complete)

### Frontend Test Setup
- [ ] **T083** [P] Component test setup with Vitest and Testing Library in frontend/tests/setup.ts
- [ ] **T084** [P] API client test setup with MSW (Mock Service Worker) in frontend/tests/mocks/

### Frontend Component Tests (MUST FAIL FIRST)
- [ ] **T085** [P] Component test for BlogPost card in frontend/tests/components/BlogPostCard.test.tsx
- [ ] **T086** [P] Component test for Project card in frontend/tests/components/ProjectCard.test.tsx  
- [ ] **T087** [P] Component test for Navigation in frontend/tests/components/Navigation.test.tsx
- [ ] **T088** [P] Component test for Auth forms in frontend/tests/components/AuthForms.test.tsx

### Frontend Page Tests (MUST FAIL FIRST)
- [ ] **T089** [P] Page test for Homepage in frontend/tests/pages/HomePage.test.tsx
- [ ] **T090** [P] Page test for Blog post detail in frontend/tests/pages/BlogPostPage.test.tsx
- [ ] **T091** [P] Page test for Project detail in frontend/tests/pages/ProjectPage.test.tsx
- [ ] **T092** [P] Page test for Admin dashboard in frontend/tests/pages/AdminDashboard.test.tsx

## Phase 3.10: Frontend Implementation (ONLY after tests are failing)

### API Client & Services
- [ ] **T093** [P] API client with authentication in frontend/src/services/api.ts
- [ ] **T094** [P] Auth service with token management in frontend/src/services/auth.ts
- [ ] **T095** [P] Blog posts API client in frontend/src/services/blog.ts
- [ ] **T096** [P] Projects API client in frontend/src/services/projects.ts

### React Components (Modern UI Focus)
- [ ] **T097** [P] BlogPost card component with modern styling in frontend/src/components/BlogPostCard.tsx
- [ ] **T098** [P] Project card component with modern styling in frontend/src/components/ProjectCard.tsx
- [ ] **T099** [P] Navigation component with responsive design in frontend/src/components/Navigation.tsx
- [ ] **T100** [P] Auth forms with polished UI in frontend/src/components/AuthForms.tsx
- [ ] **T101** [P] Tag component with filtering in frontend/src/components/Tag.tsx
- [ ] **T102** [P] Loading states and error boundaries in frontend/src/components/LoadingStates.tsx

### React Pages & Routing
- [ ] **T103** Homepage with featured content layout in frontend/src/pages/HomePage.tsx
- [ ] **T104** Blog post detail page with readability focus in frontend/src/pages/BlogPostPage.tsx
- [ ] **T105** Project detail page with modern presentation in frontend/src/pages/ProjectPage.tsx
- [ ] **T106** Admin dashboard for content management in frontend/src/pages/AdminDashboard.tsx
- [ ] **T107** React Router setup with protected routes in frontend/src/App.tsx

### Styling & UI Polish (Tailwind CSS)
- [ ] **T108** [P] Tailwind CSS configuration with custom theme in frontend/tailwind.config.js
- [ ] **T109** [P] Global styles and typography system in frontend/src/styles/globals.css
- [ ] **T110** [P] Component styles with responsive design in frontend/src/components/styles/
- [ ] **T111** [P] Dark/light mode toggle (optional enhancement) in frontend/src/hooks/useTheme.ts

## Phase 3.11: Integration & Polish

### End-to-End Integration
- [ ] **T112** Frontend-backend integration testing in backend/tests/e2e/test_integration.py
- [ ] **T113** API response time validation (<200ms requirement) in backend/tests/performance/test_api_performance.py
- [ ] **T114** Frontend page load performance (<500ms requirement) in frontend/tests/performance/test_page_load.ts
- [ ] **T115** Docker Compose integration testing with all services in tests/docker/test_compose_integration.py

### Security & Production Ready
- [ ] **T116** Input sanitization and XSS prevention in backend/src/utils/security.py
- [ ] **T117** Rate limiting middleware in backend/src/middleware/rate_limit.py
- [ ] **T118** Security headers configuration in backend/src/middleware/security_headers.py
- [ ] **T119** Environment-based configuration for production in backend/src/config.py
- [ ] **T120** Docker production optimization and multi-stage builds in backend/Dockerfile.prod and frontend/Dockerfile.prod

### Documentation & DevOps
- [ ] **T121** [P] API documentation generation and hosting in backend/docs/
- [ ] **T122** [P] Frontend component documentation (Storybook) in frontend/.storybook/
- [ ] **T123** [P] README.md with Docker Compose quickstart guide in repository root
- [ ] **T124** [P] Development setup scripts with Docker commands in scripts/setup.sh
- [ ] **T125** [P] Docker Compose production configuration in docker-compose.prod.yml

### Unit Tests (Final Polish)
- [ ] **T126** [P] Unit tests for utility functions in backend/tests/unit/test_utils.py
- [ ] **T127** [P] Unit tests for validation schemas in backend/tests/unit/test_schemas.py
- [ ] **T128** [P] Unit tests for React hooks in frontend/tests/unit/hooks.test.ts

## Dependencies

**Sequential Dependencies:**
- Setup (T001-T012) must complete before all other phases
- Database schema tests (T013-T017) → Model implementation (T018-T022)
- Contract tests (T023-T039) → Service layer (T047-T056) → API endpoints (T057-T073)
- Backend core (T001-T082) → Frontend tests (T085-T092) → Frontend implementation (T093-T111)
- Integration tests (T040-T046) can run after models exist (T018-T022)

**Parallel Execution Groups:**
```
Group 1 (Setup): T004, T005, T009, T010, T011 (linting configs, Dockerfiles, env files)
Group 2 (Schema Tests): T013, T014, T015, T016, T017
Group 3 (Models): T018, T019, T020, T021
Group 4 (Contract Tests): T023-T039 (all API contract tests)
Group 5 (Integration Tests): T040-T046 (all user story tests)  
Group 6 (Services): T050, T051, T052, T053 (core services)
Group 7 (Utils): T054, T055, T056 (utility functions)
Group 8 (CLI): T080, T081, T082 (CLI tools)
Group 9 (Frontend Components): T097-T102 (React components)
Group 10 (Frontend Styles): T108, T109, T110, T111 (styling)
Group 11 (Documentation): T121, T122, T123, T124, T125 (docs and Docker configs)
Group 12 (Unit Tests): T126, T127, T128 (final unit tests)
```

## Parallel Execution Example
```bash
# Backend Schema Tests (after T012 complete)
Task: "Database schema test for User entity in backend/tests/integration/test_user_schema.py"
Task: "Database schema test for BlogPost entity in backend/tests/integration/test_blogpost_schema.py" 
Task: "Database schema test for Project entity in backend/tests/integration/test_project_schema.py"
Task: "Database schema test for Tag entity in backend/tests/integration/test_tag_schema.py"

# API Contract Tests (after models complete)
Task: "Contract test POST /api/v1/auth/login in backend/tests/contract/test_auth_login.py"
Task: "Contract test GET /api/v1/posts in backend/tests/contract/test_posts_list.py"
Task: "Contract test GET /api/v1/projects in backend/tests/contract/test_projects_list.py"

# Docker Environment Setup (parallel with other setup tasks)
Task: "Create Docker Compose configuration with PostgreSQL, backend, and frontend services in docker-compose.yml"
Task: "Create backend Dockerfile with Python environment in backend/Dockerfile"
Task: "Create frontend Dockerfile with Node.js environment in frontend/Dockerfile"
```

## Critical TDD Reminders
⚠️ **NON-NEGOTIABLE REQUIREMENTS:**
1. Every test task MUST be completed and MUST FAIL before moving to implementation
2. Git commits must show tests before implementation (RED-GREEN-REFACTOR)
3. No implementation task can begin until its corresponding test task is complete and failing
4. Integration tests use real PostgreSQL database, not mocks
5. Backend development has priority over frontend per user requirements

## Notes
- [P] tasks = different files, no dependencies between them
- All paths assume web application structure with backend/ and frontend/ directories  
- Backend-first priority: Complete T001-T082 before starting frontend tasks
- Docker Compose manages all services (PostgreSQL, backend, frontend) in development
- Verify ALL tests fail before implementing (RED phase of TDD)
- Commit after each task completion
- Focus on modern, polished UI in frontend components (T097-T102)

## Task Generation Rules Applied

**From API Contracts (api-spec.yaml):**
- 15 endpoints → 15 contract test tasks (T023-T039)
- 15 endpoints → 15 implementation tasks (T057-T073)

**From Data Model (data-model.md):**  
- 4 entities (User, BlogPost, Project, Tag) → 4 model tasks (T018-T021)
- 2 relationship tables → 1 relationship test task (T017)

**From User Stories (quickstart.md):**
- 7 primary user flows → 7 integration test tasks (T040-T046)

**Constitution Compliance:**
- CLI tools for each library (T080-T082)
- Library-first architecture with services (T047-T053)
- TDD strictly enforced with failing tests first
- Real database usage in integration tests

**Docker Compose Integration:**
- All services containerized (PostgreSQL, backend, frontend)
- Development environment fully dockerized
- Production-ready configurations included

## Validation Checklist ✅

- [x] All 15 API contracts have corresponding test tasks (T023-T039)
- [x] All 4 entities have model creation tasks (T018-T021)
- [x] All test tasks come before implementation tasks
- [x] Parallel tasks ([P]) operate on different files
- [x] Each task specifies exact file path
- [x] Backend-first priority maintained (T001-T082 before frontend)
- [x] TDD approach strictly enforced with failing tests requirement
- [x] Modern UI requirements addressed in frontend component tasks
- [x] Performance requirements addressed (T113, T114)
- [x] Security requirements covered (T116-T119)
- [x] Docker Compose environment for all services (T008-T012, T115, T120, T125)