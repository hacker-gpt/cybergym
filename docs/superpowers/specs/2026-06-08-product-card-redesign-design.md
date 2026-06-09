# Product Item Card Redesign — Design (as built)

Date: 2026-06-08
Branch: `cybergym-reskin`
Scope: `frontend/src/app/search-result/` (the product grid + per-item card)

## Goal

Redesign the product grid and per-item card from the original horizontal layout
(image left ~60%, info right ~40%, in a `mat-grid-list`) into a modern, responsive
**vertical** e-commerce card: square image on top, then name, short description,
amber price, and a full-width "Add to Basket" button — laid out in a content-sized
CSS grid.

> Note: this evolved through iteration. The first cut was a CSS-only restyle that
> kept `mat-grid-list`. Square images exposed a structural problem: `mat-grid-list`
> positions tiles absolutely at a fixed row height, so a square image filled the
> whole tile and the text overflowed/overlapped. The final design replaces the grid
> mechanism with a flowing CSS grid so cards size to their content.

## Constraints (CTF-safety)

CTF platform (OWASP Juice Shop reskinned as CyberGym). Overriding rule: **must NOT
disable or break any challenge.** Verified against the search-result component:

- The live DOM-XSS challenge (`localXssChallenge` / `xssBonusChallenge`) lives in
  the search-results **heading** (`<span id="searchValue" [innerHTML]="searchValue">`),
  NOT in the per-item card. That block is left untouched.
- The karma spec asserts only component logic (`bypassSecurityTrustHtml` calls,
  socket events) — no card selectors or element ordering. Cypress targets
  `#searchQuery`. So restructuring the card/grid breaks no test.
- No product/challenge **data** touched (IDs, prices, quantities, reviews,
  `deletedDate`, challenge keys) — the protected boundary is intact.

### Guardrails (preserved verbatim)
- The `searchValue` heading XSS block.
- Every binding/handler: `(click)="showDetail(item)"`, `(click)="addToBasket(item.id)"`,
  `isLoggedIn()`, `isDeluxe()`, the deluxe-price `@if` logic, `item.quantity` ribbon
  conditions, `item.image/name/description/price/id`, and `trustProductDescription()`.
- Pagination (`MatPaginator` + `MatTableDataSource`) and the responsive column logic
  (`breakpoint` set by `onResize`).
- "Add to Basket" stays logged-in-only.

## Implementation (3 files)

### `search-result.component.html`
1. Replace `<mat-grid-list [cols]="breakpoint" gutterSize="30px">` + `<mat-grid-tile>`
   with `<div class="product-grid" (window:resize)="onResize($event)"
   [style.grid-template-columns]="'repeat(' + breakpoint + ', minmax(0, 1fr))'">`.
   Each `<mat-card>` becomes a direct grid item. `onResize`/`breakpoint` preserved, so
   the 1→6 responsive column logic still drives the layout. Removed the unused
   `#table` ref and the `[style.width]` inline style.
2. Wrap the product image in `<div class="product-image">` (clip container for the
   hover zoom + full-bleed). No bindings affected.
3. Add inside `.info-box`, between name and price:
   `<div class="item-description" [innerHTML]="item.description"></div>`.

`item.description` is already `bypassSecurityTrustHtml`-trusted by the existing
`trustProductDescription()` and already rendered via `[innerHTML]` in the
product-details dialog. Plain interpolation is not viable because seed descriptions
contain HTML (`<br/>`, `<span style>`, `<em>`, `<a href>`).

### `search-result.component.scss`
- `.product-grid`: `display: grid; gap: 24px;` columns bound inline from `breakpoint`.
  No absolute positioning; cards flow and size to content; grid auto-equalizes card
  heights per row.
- `.ribbon-card` (mat-card): borderless flat surface, `display: flex` so the inner
  card fills the stretched grid cell; soft resting shadow `0 2px 10px` lifting to
  `0 16px 34px` + `translateY(-6px)` on hover.
- `.mdc-card`: `border-radius: 8px !important` (scoped override of the global 14px
  card radius); `flex: 1` so the button can pin to the bottom.
- `.product` / `.product-image`: vertical stack; image full-bleed to the card edges
  (negative margin), `overflow: hidden` to clip the hover zoom, top corners rounded
  `8px` to match the card.
- `.product-image img`: **square** via `aspect-ratio: 1 / 1`, `width: 100%`,
  `object-fit: cover`; borders/padding/background removed; `scale(1.07)` on hover.
- `.item-name`: white, 1rem, 2-line clamp with reserved min-height (uniform cards).
- `.item-description`: muted (`rgba(255,255,255,.55)`), 2-line clamp,
  `pointer-events: none` so inner links don't swallow the card click; amber links.
- `.item-price`: bold 1.2rem **amber accent**; deluxe `<s>` muted.
- `.basket-btn-container`: `margin-top: auto` pins the button to the bottom so rows
  align. `.btn-basket`: full-width pill.
- Stock ribbon restyled in place (HTML/`@if` unchanged) into a pill badge: amber for
  "only N left", red for "sold out".

### `search-result.component.ts`
- Removed the now-unused `MatGridList` / `MatGridTile` imports (import line + the
  standalone `imports` array). No functional change.

## Known consequence (accepted)

Rendering the trusted description on the listing means a stored-XSS product
description (the `restfulXssChallenge` payload) would also execute on the listing
page, not only the detail dialog. This does **not** disable or break the challenge —
it broadens where the existing payload renders, which is acceptable (and thematically
fine) for a CTF. Seed descriptions are benign formatting only.

## Verification (done)

- ✅ `npx stylelint` on the component SCSS.
- ✅ `npx ng lint` — all files pass.
- ✅ `npx ng build --configuration production` — exit 0 (only the pre-existing
  unrelated `footer.component.ts` `RouterLink` warning).
- ✅ Rendered via headless Chrome against the running app on `:3000` at **3-col
  (1440)**, **2-col (1100)**, and **1-col (820)** — content-sized cards, no overlap,
  no absolute positioning, responsive columns intact.
- ✅ Logged-in screenshot confirms the full card incl. the bottom-pinned "Add to
  Basket" pill; logging in as admin incidentally confirmed challenge solving still
  fires. The local `data/juiceshop.sqlite` (git-ignored) was then wiped to reset the
  CTF state to 0 solved.
- Karma spec (`search-result.component.spec.ts`) is DOM-agnostic and no component
  logic changed, so it is unaffected. (It cannot run in this checkout: `angular.json`
  points at a missing `src/karma.conf.js` — a pre-existing repo condition.)
- No backend/data changes, so the `validateConfig` boot tripwire is unaffected.
