# Architecture Review & Portfolio-Ready Roadmap

## Executive Summary

The project already has strong foundations (POM, typed settings, reusable components), but it can be improved to become **portfolio-grade** by tightening boundaries and introducing extension points for AI-powered capabilities.

This review focuses on:

1. **Separation of layers**
2. **Composition over inheritance**
3. **Scalability and flexibility**
4. **AI readiness (auto-healing locators and future intelligent features)**

---

## Current Strengths

- Clear use of Page Object Model (`pages/` + `pages/components/`).
- Shared authenticated behavior is centralized in `AuthenticatedPage`.
- Configuration is typed and centralized in `config/settings.py`.
- Tests are grouped by domain and keep assertions readable.

---

## Current Pain Points (Architectural)

### 1) Multi-responsibility modules
- Checkout flow previously lived in a single `checkout_page.py` file with multiple classes.
- This creates a hotspot and makes future evolution harder (especially when adding AI hooks per checkout step).

### 2) Layer mixing
- Page objects currently combine:
  - locator knowledge,
  - flow orchestration,
  - domain calculations/parsing (e.g., price parsing),
  - and direct logging concerns.

This is acceptable for small projects but does not scale cleanly.

### 3) No explicit extension boundary for AI
- There is no dedicated abstraction for locator strategy or fallback policy.
- AI capabilities should plug into a strategy interface, not be embedded directly in page classes.

### 4) Test-data and domain concepts are still implicit
- Data is mostly dictionaries and primitives.
- Adding lightweight domain models (DTOs/value objects) will improve clarity without increasing test volume.

---

## Refactoring Applied in This Change

To reduce immediate structural debt, checkout classes were split by responsibility:

- `pages/checkout/info_page.py`
- `pages/checkout/overview_page.py`
- `pages/checkout/complete_page.py`
- `pages/checkout/__init__.py`
- `pages/checkout_page.py` kept as backward-compatible re-export

This preserves existing imports while improving modularity.

---

## Target Architecture (Next Iterations)

Recommended layered structure:

```text
framework/
  config/
  core/
    browser/
    logging/
    errors/
  ui/
    locators/
    components/
    pages/
  domain/
    models/
    services/
  application/
    flows/           # high-level business workflows
  ai/
    locator_healing/
    assertions/
  tests/
```

### Layer responsibilities

- **ui/pages**: only page concerns (elements + page actions)
- **application/flows**: cross-page user journeys (e.g., purchase flow)
- **domain/models**: typed structures (`UserData`, `OrderSummary`)
- **ai/locator_healing**: pluggable locator strategy and fallback engine

---

## AI-Ready Design (Auto-Healing)

Introduce an interface-driven locator resolution pipeline:

```python
class LocatorResolver(Protocol):
    def resolve(self, page: Page, semantic_id: str) -> Locator: ...
```

Resolvers (composed in order):
1. Static test-id resolver
2. CSS/XPath fallback resolver
3. AI semantic resolver
4. Cached successful locator resolver

### Key principle
AI should be an **optional strategy plugin**, not a hard dependency in page objects.

---

## Portfolio Guidelines

To maximize portfolio impact with moderate test volume:

- Keep test count focused on critical business journeys.
- Invest heavily in architecture docs and ADRs.
- Add diagrams showing layer boundaries and dependency rules.
- Add a short `docs/adr/` decision log (e.g., composition-over-inheritance, AI plugin boundary).

---

## Suggested Next 3 Milestones

1. **Introduce `application/flows`** and move full user journeys out of tests.
2. **Create `ai/locator_healing` interface + noop implementation**.
3. **Add 3 ADRs + architecture dependency map** in `docs/`.

These three steps will strongly improve maintainability and portfolio quality without bloating test count.
