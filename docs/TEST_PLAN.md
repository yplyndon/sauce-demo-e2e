# Test Plan – Sauce Demo Storefront

## 1. Scope
**In scope:** storefront browsing, product detail, search, cart, checkout entry, customer login/registration forms, content pages, footer, responsive layout, public Shopify Ajax/JSON endpoints.
**Out of scope:** completing payment (third-party Shopify checkout), Shopify admin, the Sauce social/wishlist widget internals, load testing.

## 2. Test levels
| Level | Folder | Purpose | Typical run |
|-------|--------|---------|-------------|
| API / contract | `tests/api` | Fast backend & schema validation, no browser | every commit |
| UI component/page | `tests/ui` | One behaviour per test through the browser | every commit (smoke) / nightly (all) |
| E2E journeys | `tests/e2e` | Real user flows across pages | nightly + pre-release |

## 3. Suites
- **Smoke** (`-m smoke`): page loads, product listing, PDP essentials, add to cart, cart basics, forms render, guest → checkout journey.
- **Regression** (`-m regression`): everything above plus negative cases, responsive checks, link health, cross-browser.

## 4. Coverage matrix
| Feature | UI | API | E2E |
|---------|:--:|:---:|:---:|
| Home / featured products | ✔ | ✔ | ✔ |
| Navigation & 404 handling | ✔ | ✔ | |
| Catalog / collections | ✔ | ✔ | |
| Product detail (price, image, related) | ✔ | ✔ | ✔ |
| Search (match, case, no match, empty) | ✔ | ✔ | ✔ |
| Cart (add, merge, update, remove, clear, persistence, isolation) | ✔ | ✔ | ✔ |
| Checkout entry | ✔ | | ✔ |
| Login / registration (positive opt-in, negative) | ✔ | | |
| Content pages & footer | ✔ | | |
| Responsive (375 / 768 / 1440) | ✔ | | |
| Transport & SEO basics (https redirect, robots, sitemap) | | ✔ | |

## 5. Entry / exit criteria
- **Entry:** target URL reachable, `pip install` + `playwright install` completed.
- **Exit:** 100 % smoke pass; regression pass rate ≥ 98 % with every failure triaged (defect, test issue, or environment).

## 6. Risks & mitigations
| Risk | Mitigation |
|------|------------|
| Public demo store content may change | Expected data isolated in `testdata/products.json`; ids resolved at runtime |
| Shopify bot protection on login/registration | Negative tests skip on `/challenge`; real registration is opt-in |
| Shared third-party environment, network variance | 1 retry, generous but bounded timeouts, traces/videos on failure |
| Theme markup changes | Locators centralised in page objects – one fix point |
