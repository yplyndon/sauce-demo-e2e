# Sauce Demo – E2E Test Automation (Playwright · Python · pytest)

Functional, UI, API, end-to-end and regression tests for
**https://sauce-demo.myshopify.com/** (a Shopify demo storefront).

## Highlights
- **Page Object Model** – all locators live in `pages/`, tests read like user stories
- **Hybrid UI + API testing** – the Shopify Ajax API (`/cart.js`, `/cart/add.js`, …) seeds and verifies cart state, so UI tests stay small and deterministic
- **Contract tests** – JSON-Schema validation for products, collections and cart payloads
- **No hard-coded IDs** – live variant ids/prices are resolved once per session (`product_catalog` fixture)
- **Layered markers** – `smoke ⊂ regression`, plus `ui / api / e2e / functional / negative / responsive`
- **Rich reporting** – self-contained HTML report with failure screenshots, plus Playwright traces and videos on failure
- **CI-ready** – GitHub Actions (smoke gate → cross-browser regression, nightly) and a Jenkinsfile
- **Parallel & cross-browser** – `pytest-xdist`, `--browser chromium|firefox|webkit`

## Project structure
```
sauce-demo-e2e/
├── conftest.py              # fixtures, Playwright overrides, hooks (auto markers, failure screenshots)
├── pytest.ini               # markers, reporting, artifacts, retries
├── requirements.txt
├── .env.example             # BASE_URL, timeouts, viewport, opt-in flags
├── config/settings.py       # typed, env-driven configuration
├── pages/                   # Page Objects (base, home, catalog, product, cart, search, login, register, content)
├── clients/shopify_api.py   # API client over Playwright's APIRequestContext
├── testdata/                # products.json (expected data) + JSON schemas
├── utils/                   # helpers, logger
├── tests/
│   ├── ui/                  # home, navigation, catalog, PDP, search, cart, login, register, footer, responsive, site health
│   ├── api/                 # products, collections, cart, storefront (https redirect, robots, sitemap)
│   └── e2e/                 # complete customer journeys
├── docs/TEST_PLAN.md        # scope, strategy, coverage matrix, risks
├── .github/workflows/tests.yml
└── Jenkinsfile
```

## Setup
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium        # add firefox webkit for cross-browser runs
cp .env.example .env               # optional (Windows: copy .env.example .env)
```

## Running
```bash
pytest                                  # everything (chromium, headless)
pytest -m smoke                         # fast critical-path gate
pytest -m regression -n 2               # full regression, parallel (keep workers low - see note)
pytest -m ui | -m api | -m e2e          # by layer
pytest -m "regression and not responsive"
pytest --headed --slowmo 300            # watch it run
pytest --browser firefox --browser webkit
pytest tests/ui/test_cart.py -k quantity
pytest --base-url https://another-store.myshopify.com   # other environment
```
Reports and artifacts land in `reports/` (`report.html`, `artifacts/` with traces & videos).
Open a trace with `playwright show-trace reports/artifacts/<test>/trace.zip`.

## Opt-in tests
| Test | Enable with |
|------|-------------|
| Real customer registration | `ALLOW_REGISTRATION=true` (creates real accounts on the demo store) |
| Valid customer login | `TEST_USER_EMAIL` and `TEST_USER_PASSWORD` |

Login/registration negative tests auto-skip if Shopify serves its bot challenge (`/challenge`).

## Design decisions
- **Locators prefer roles, text and stable Shopify attributes** (`name='customer[email]'`, `/cart/add` forms, `a[href*='/products/…']`) over theme CSS classes, because this is a 2014-era theme that gets re-skinned rarely but has no test ids.
- **Cart state is asserted through `/cart.js`**, not scraped from markup – the API is the contract, the UI is a view.
- **One failing layer is easy to spot**: API tests need no browser, so they run in seconds and isolate backend vs. UI defects.
- **Retries are limited to 1** (`--reruns=1`) to absorb network blips without hiding real flakiness.

## Rate limiting (HTTP 429)
The demo store sits behind Shopify's public rate limiter. Running many workers (`-n auto`) or hammering
it repeatedly can produce 429 responses. The API client and `goto_with_retry` back off and retry, failed
tests that saw a 429 are annotated in the HTML report, and the recommended parallelism is `-n 2`.
