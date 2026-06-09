# CyberGym Reskin — Design Spec

**Date:** 2026-06-08
**Base project:** OWASP Juice Shop v19.1.1 (Angular 20 + Angular Material frontend, Node/TypeScript backend)
**Goal:** Reskin Juice Shop into **CyberGym** — new brand, a custom yellow-on-dark theme, modernized styling, and a full content/narrative rebrand — **without changing any functionality**. The site is used as a CTF; every existing vulnerability/challenge and the built-in Score Board must keep working.

---

## 1. Decisions (locked)

| Decision | Choice |
|---|---|
| Reskin depth | **Full rebrand** — brand + custom theme + content/narrative |
| CTF requirement | **Preserve all challenges + built-in Score Board.** No external CTF platform. The reskin must not disable or break any challenge. |
| Logo/favicon | **User supplies** the CyberGym logo + favicon. We wire up the filenames and use a placeholder wordmark until they land. |
| Theme vibe | **Balanced yellow-on-dark** — dark charcoal base, bright-but-not-harsh yellow primary, modern rounded cards and spacing. |
| Approach | **A — config-first + custom theme + careful content rebrand** (see §3). |

---

## 2. How branding/theming/content work in this codebase (grounding)

- **Branding is config-driven.** `config/default.yml` holds `application.name`, `.logo`, `.favicon`, `.theme`, `.welcomeBanner`, `.chatBot`, `.social`, `.cookieConsent`. At startup, `lib/startup/customizeApplication.ts` applies these to the built `index.html` (title, favicon link, body theme class, logo copy, welcome/cookie text). So name/logo/favicon/theme/welcome changes need **no code edits**.
- **Themes are Angular Material.** Theme palettes live in `frontend/src/theme.scss` (8 built-in themes, each a `.<name>-theme` class). Matching nav/bg/text color metadata lives in `views/themes/themes.ts`. Global styles + theme CSS variables (`--theme-primary`, `--theme-background`, `--theme-text`, …) live in `frontend/src/styles.scss`. The selected theme is `application.theme`.
- **Products are config data**, not a static products file. The active catalog is the `products:` array in `config/default.yml`. Challenge detection keys off **product fields**, not display names:
  - `useForChristmasSpecialChallenge`, `urlForProductTamperingChallenge`, `fileForRetrieveBlueprintChallenge`, `keywordsForPastebinDataLeakChallenge`, `deletedDate`.
  - Read in `data/datacreator.ts` and `routes/verify.ts` (note: `verify.ts` substring-matches the tampering **URL** inside the product description).
  - **Validated at startup** by `lib/startup/validateConfig.ts` — the app refuses to boot if the special challenge products are missing. This is our safety tripwire.
- **Challenges** (110) live in `data/static/challenges.yml`, detected by `key:`. Names/descriptions/hints are cosmetic; `key` is the anchor.
- **UI copy** is i18n JSON in `frontend/src/assets/i18n/en.json` (English is default; brand-string footprint is small). Other narrative lives in product/challenge data, `data/static/legal.md`, `data/static/botDefaultTrainingData.json`, and a few `views/`/`index.html` strings.

---

## 3. Approach A (chosen)

Brand through Juice Shop's own customization machinery, add **one new** Material theme, apply modern polish to high-traffic surfaces, and rebrand content behind a strict protected-data boundary. The challenge test suite + the `validateConfig.ts` boot check are the regression safety net.

Rejected alternatives:
- **Config-only** — ruled out; user wants a full rebrand/modern look.
- **Approach B (full visual overhaul)** — restyle every component + broad layout surgery. Rejected: Juice Shop's own e2e/Cypress tests and some challenges assert on DOM structure/selectors, so heavy template changes risk breaking challenge detection for the same brand outcome.

---

## 4. Design

### 4.1 Branding & identity (config-driven, no code changes)
In `config/default.yml`:
- `application.name: 'CyberGym'` (drives title, navbar, sidebar, emails).
- `application.logo` / `application.favicon` → user-supplied filenames in `frontend/src/assets/public/images/` and `frontend/src/assets/public/`; placeholder wordmark until provided.
- `application.theme: 'cybergym-dark'`.
- Reword `application.welcomeBanner.title`/`.message`, `application.chatBot.name`/`.greeting`, `application.social.*`, `application.cookieConsent.*`.
- OG/meta + any hardcoded title in `frontend/src/index.html`.

### 4.2 Theme system — new `cybergym-dark`
- Add a yellow-primary / amber-accent **dark** theme in `frontend/src/theme.scss`, exposed as `.cybergym-dark-theme`, using Angular Material's dark-theme mixin. Charcoal base (~`#1a1c20`), yellow primary (~`#FFD60A`/`#F5C518`).
- Register matching `bgColor`/`textColor`/`navColor` metadata in `views/themes/themes.ts` so runtime switching and server-side customization agree.
- **Add**, do not mutate, the 8 existing themes — zero blast radius on other themes.

### 4.3 Modern styling polish (visual only)
Targeted SCSS in `frontend/src/styles.scss` + specific component styles, all driven by theme CSS variables:
- Navbar: spacing, yellow accents, refined logo treatment.
- Welcome / welcome-banner: modern dark hero + yellow CTA.
- Buttons: consistent rounded, filled-yellow primary / outlined secondary; sensible repositioning of primary actions (e.g. right-aligned in dialogs/forms). **This is where "change some button positions" lands.**
- Product cards, login/register, Score Board: rounded cards, improved elevation/spacing, dark surfaces.
- Global: typography scale, spacing rhythm, focus/hover states.
- **Constraint:** style via classes/CSS only; do not delete or rename elements that tests or challenges select on.

### 4.4 Content rebrand + protected-data boundary
Rebrand:
- `frontend/src/assets/i18n/en.json` brand strings (other locales optional).
- `config/default.yml` product `name`/`description`/`image` → cyber theme.
- `data/static/challenges.yml` names/descriptions/hints that mention "Juice Shop"; update hints that name a product to its new name so hints stay accurate.
- `data/static/legal.md`, `data/static/botDefaultTrainingData.json`, photo-wall/about text, and "OWASP Juice Shop" strings in `views/`/`index.html`.

**Protected — must NOT change:**
- Product **IDs and ordering** in `config/default.yml`.
- The challenge-coupling fields and the products that carry them: `useForChristmasSpecialChallenge`, `urlForProductTamperingChallenge` (including the exact URL string, since `verify.ts` substring-matches it), `fileForRetrieveBlueprintChallenge`, `keywordsForPastebinDataLeakChallenge`, `deletedDate`.
- All challenge `key:` values in `challenges.yml`.

### 4.5 Explicitly untouched (functionality guarantee)
Routes/controllers, challenge detection logic, the vulnerabilities themselves, the Score Board page and its logic, auth, DB models, API contracts. The reskin is **brand + theme + display-text + CSS only**.

---

## 5. Verification
- `npm run lint` and `npm run lint:scss` pass.
- Frontend builds; server boots cleanly → confirms `validateConfig.ts` passes (special challenge products intact).
- Challenge/integration tests (`npm test`, `npm run frisby`) green; Cypress e2e where feasible — confirms no challenge detection regressed.
- `npm run rsn` only if any coding-challenge-referenced **source** file was touched (expected: none — work stays in config/theme/i18n/data).
- Manual smoke: theme renders (yellow-on-dark), brand shows "CyberGym" in title/navbar/sidebar, Score Board loads, a couple of representative challenges still solvable.

---

## 6. Rollout
Single feature branch, committed in logical, individually-verified chunks:
1. New `cybergym-dark` theme (theme.scss + themes.ts) — set as default.
2. Branding/config (name, logo/favicon wiring, welcome/chatbot/social/cookie text).
3. Content rebrand (i18n, products, challenges text, narrative) — protected fields untouched.
4. Modern styling polish (navbar, hero, buttons, cards, login/register, score board).

Each chunk: lint + build + boot + relevant tests before proceeding.

---

## 7. Out of scope
- External CTF platform integration (CTFd/FBCTF) and flag-code mode.
- Translating non-English locales (optional follow-up).
- Renaming product IDs, challenge keys, or any backend logic.
- Unrelated refactoring.
