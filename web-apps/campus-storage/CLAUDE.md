# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**校园物品暂存平台 (Campus Item Storage Platform)** — a WeChat Mini Program + CloudBase (Tencent Cloud) serverless app for students to store and deliver items across campuses/cities. Core differentiator: "地址未定，物品先行" (ship items before destination is known).

## Tech Stack

- **Frontend**: WeChat Mini Program (native, no framework)
- **Backend (dev)**: Python 3.12+ — Flask + SQLite + pytest
- **Backend (prod)**: CloudBase Cloud Functions (Python 3.12 runtime) + CloudBase NoSQL
- **Database abstraction**: `db/adapter.py` — SQLite (local) ↔ CloudBase NoSQL (prod) switchable via `DB_MODE` env var
- **Scheduled tasks**: APScheduler (local) → CloudBase Timer Triggers (prod)

## Architecture

```
src/
├── common/                  # Shared modules
│   ├── errors.py            # ErrorCode class + response format
│   ├── auth.py              # Identity from X-OpenId header (local) / event.userInfo (prod)
│   ├── validator.py         # Input validation, enum checks
│   └── permission.py        # Role check (USER / ADMIN / SYSTEM)
├── db/                      # Database layer
│   ├── adapter.py           # DB abstraction interface
│   ├── sqlite_adapter.py    # SQLite implementation
│   ├── cloudbase_adapter.py # CloudBase NoSQL implementation
│   └── factory.py           # Adapter factory by DB_MODE
├── core/                    # Business logic
│   ├── order_service.py     # Order CRUD operations
│   └── order_state.py       # State machine validation
├── routes/                  # Flask routes
│   ├── auth.py              # Login endpoint
│   └── orders.py            # Order endpoints
└── tasks/                   # Scheduled tasks
    ├── timeout_checker.py   # Timeout check logic
    └── scheduler.py         # APScheduler config

Flask routes → /api/*        # Local dev, mirrors cloud function boundaries
Cloud functions → login, createOrder, updateOrderStatus, getOrderList, getOrderDetail
Timer functions → pendingTimeoutChecker, deliveringTimeoutChecker
```

### Key Architectural Decisions

1. **Local-first development**: All backend logic developed and tested locally (Flask + SQLite + pytest) before deploying to CloudBase
2. **Dual-mode DB layer**: `db/adapter.py` abstracts SQLite ↔ CloudBase NoSQL — business code never touches either directly
3. **Order state machine**: 6 states (PENDING, COLLECTED, STORED, DELIVERING, COMPLETED, CANCELLED), valid transitions matrix validation with terminal-state protection (COMPLETED/CANCELLED are immutable)
4. **Optimistic locking**: Version field for concurrency control
5. **Vertical slice tasks**: Each task delivers DB + logic + tests in 1-5 files

## Development Commands

```bash
# Environment setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run Flask dev server
python src/app.py
# or: flask run --port 5000

# Run all tests
pytest tests/ -v

# Run a single test file
pytest tests/test_order_service.py -v

# Run a specific test
pytest tests/test_order_service.py::test_create_order -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# DB mode switching
DB_MODE=local python src/app.py       # SQLite (default)
DB_MODE=production python src/app.py  # CloudBase NoSQL (requires env vars)

# Data migration (dry run)
python scripts/migrate_to_cloudbase.py --env-id <env-id> --dry-run

# Deploy cloud functions (dry run)
python scripts/deploy_cloudfunctions.py --env-id <env-id> --dry-run

# Full deployment
python scripts/full_deploy.py --env-id <env-id>

# Local dev auth header (curl example)
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -H "X-OpenId: mock_openid_123" \
  -d '{"itemType":"LUGGAGE", "warehouseId":"wh_001", "estimatedDuration":3}'
```

## Code Conventions

### Python
- Use type hints for function signatures
- Follow PEP 8 naming: `snake_case` for functions/variables, `PascalCase` for classes
- Use f-strings for string formatting
- Prefer `pathlib.Path` over `os.path`

### Error Handling
- Use custom exceptions from `common/errors.py`
- Always return JSON response with `{"code": int, "message": str, "data": any}` format
- Log errors with context before returning

### Database
- Never use raw SQL outside of adapter classes
- Use parameterized queries to prevent SQL injection
- Always include `create_time` and `update_time` fields

### Testing
- Write tests before or alongside implementation (TDD preferred)
- Use descriptive test names: `test_<action>_<condition>_<expected_result>`
- Mock external dependencies (DB, API calls)
- Target >80% code coverage

## State Machine

| Status | Next Valid States |
|--------|-------------------|
| PENDING | COLLECTED, CANCELLED |
| COLLECTED | STORED |
| STORED | DELIVERING |
| DELIVERING | COMPLETED |
| COMPLETED | (terminal) |
| CANCELLED | (terminal) |

## API Response Format

```json
{"code": 0, "message": "success", "data": {}}
```

Error codes:
- 1001: Parameter error
- 1002: Unauthorized
- 1003: Forbidden
- 2001: Not found
- 2002: Invalid state transition
- 5001: System error

## Project Structure

```
campus-storage/
├── src/                     # Backend source
├── miniprogram/            # WeChat Mini Program
├── admin/                  # Admin H5 panel
├── cloudfunctions/         # CloudBase cloud functions
├── scripts/                # Utility scripts
├── tests/                  # Test cases
├── docs/                   # Documentation
│   ├── decisions/          # ADRs (Architecture Decision Records)
│   ├── 01_产品需求文档_PRD.md
│   ├── 02_系统设计说明书_SDD.md
│   └── ...
├── README.md               # Project overview
├── CHANGELOG.md            # Change log
└── CLAUDE.md               # This file
```

## Design Docs (Chinese)

All design documents are in `docs/`:
- `01_产品需求文档_PRD.md` — Product requirements
- `02_系统设计说明书_SDD.md` — System design
- `03_UI设计说明.md` — UI design spec
- `04_数据库设计文档.md` — Database design (SQLite + NoSQL)
- `05_API接口文档.md` — API documentation
- `06_云函数设计文档.md` — Cloud function design
- `07_定时任务设计文档.md` — Scheduled task design
- `08_测试计划与测试用例.md` — Test plan
- `09_部署与运维说明.md` — Deployment
- `10_项目复盘与踩坑记录.md` — Retrospective
- `11_开发任务拆分.md` — Task breakdown (Phases 0-7)
- `12_集成测试报告.md` — Integration test report
- `13_前后端联调测试指南.md` — Integration testing guide
- `14_生产部署检查清单.md` — Production deployment checklist

## ADRs

See `docs/decisions/` for Architecture Decision Records:
- ADR-001: Database dual-mode design
- ADR-002: State machine implementation
- ADR-003: Local-first development workflow
- ADR-004: CloudBase serverless deployment

## Common Tasks

### Adding a New API Endpoint

1. Define route in `src/routes/`
2. Implement business logic in `src/core/`
3. Add tests in `tests/`
4. Update API documentation
5. Create cloud function version in `cloudfunctions/`

### Adding a New Database Field

1. Update schema in `src/db/schema.sql`
2. Update adapter methods in `src/db/`
3. Update model transformation in migration scripts
4. Add tests for new field

### Deploying to Production

1. Run tests: `pytest tests/ -v`
2. Preview deployment: `python scripts/full_deploy.py --env-id <id> --dry-run`
3. Execute deployment: `python scripts/full_deploy.py --env-id <id>`
4. Follow checklist in `docs/14_生产部署检查清单.md`

## Gotchas

- **DB_MODE must be set before importing db modules**: Set env var before running app
- **CloudBase SDK is not available locally**: Use mock implementations for local testing
- **Timer tasks run differently in prod**: Local uses APScheduler, prod uses CloudBase triggers
- **State transitions are strictly validated**: Check `order_state.py` before adding new transitions
