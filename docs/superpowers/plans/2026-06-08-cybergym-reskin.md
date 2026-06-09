# CyberGym Reskin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reskin OWASP Juice Shop into **CyberGym** — new brand, a custom yellow-on-dark Angular Material theme, modern styling polish, and a full content/narrative rebrand — without disabling or breaking any CTF challenge or the built-in Score Board.

**Architecture:** Brand through Juice Shop's own config-driven customization (`config/default.yml` → applied at startup by `lib/startup/customizeApplication.ts`). Add **one new** Material theme (`cybergym-dark`) alongside the existing 8. Rebrand content (products, challenge text, i18n, server templates) behind a strict protected-data boundary: challenge detection keys off product *fields* and challenge `key:` values, never display text, so renaming names/descriptions is safe. The startup `validateConfig.ts` boot check + the challenge test suites are the regression safety net.

**Tech Stack:** Angular 20 + Angular Material (M2 theming, SCSS), Node/TypeScript backend, YAML config + data, ngx-translate i18n.

**Source spec:** `docs/superpowers/specs/2026-06-08-cybergym-reskin-design.md`

---

## Protected-data boundary (read before editing data/config)

These must **never** change — they are what challenge detection and startup validation depend on:

- **Product fields** (edit only `name:` and `description:` on products; leave every other line byte-for-byte): `price`, `deluxePrice`, `quantity`, `limitPerUser`, `image`, `reviews` (text *and* author), `deletedDate`, and the challenge-coupling fields `useForChristmasSpecialChallenge`, `urlForProductTamperingChallenge`, `keywordsForPastebinDataLeakChallenge`, `fileForRetrieveBlueprintChallenge`, `exifForBlueprintChallenge`.
- **Product count and order** in `config/default.yml` (IDs are assigned by array position in `data/datacreator.ts`).
- **Challenge `key:` values** in `data/static/challenges.yml`.
- **`application.domain: juice-sh.op`** in `config/default.yml` (seeded emails like `admin@juice-sh.op` are referenced by challenges).
- **`config/default.yml` `challenges:` block** (e.g. `overwriteUrlForProductTamperingChallenge`, `xssBonusPayload`, `csafHashValue`) and the `memories:` / `ctf:` blocks.

Tripwire: `lib/startup/validateConfig.ts` aborts startup if the O-Saft (tampering), Rippertuer (pastebin keywords), or 3D-logo (blueprint) special products lose their fields. A clean boot proves these survived.

---

## Task 1: Add the `cybergym-dark` Material theme

**Files:**
- Modify: `frontend/src/theme.scss` (append after line 110)
- Modify: `frontend/src/styles.scss` (append a theme block after line 238; near the other `.<name>-theme` blocks)
- Modify: `views/themes/themes.ts` (add an entry to the `themes` object)

- [ ] **Step 1: Add the palette + theme + color class to `frontend/src/theme.scss`**

Append at the end of the file (after the `.lime-green-theme` block, line 110):

```scss

$cybergym-dark-primary: mat.m2-define-palette(mat.$m2-amber-palette, 500, 300, 700);
$cybergym-dark-accent: mat.m2-define-palette(mat.$m2-amber-palette, A400, A200, A700);
$cybergym-dark-warn: mat.m2-define-palette(mat.$m2-red-palette);
$cybergym-dark-theme: mat.m2-define-dark-theme((
  color: (
    primary: $cybergym-dark-primary,
    accent: $cybergym-dark-accent,
    warn: $cybergym-dark-warn,
  ),
));

.cybergym-dark-theme {
  @include mat.all-component-colors($cybergym-dark-theme); }
```

- [ ] **Step 2: Wire the custom-component theming + CSS variables in `frontend/src/styles.scss`**

After the `.lime-green-theme { … }` block (ends at line 238), add:

```scss
.cybergym-dark-theme {
  @include custom-components-theme($cybergym-dark-theme);
  @include css-vars($cybergym-dark-theme);
}
```

(`$cybergym-dark-theme` is in scope because `styles.scss` does `@use './theme' as *;` on line 10.)

- [ ] **Step 3: Register theme metadata for server-rendered pages in `views/themes/themes.ts`**

These values theme the two server-rendered pages (`routes/userProfile.ts`, `routes/videoHandler.ts`). Keep dark bg + light text for readability. Add as a new entry inside the `themes` object (e.g. after the `lime-green` entry, before the closing `}`):

```ts
  ,'cybergym-dark': {
    bgColor: '#1a1c20',
    textColor: '#FFFFFF',
    navColor: '#26282D',
    primLight: '#FFD54F',
    primDark: '#FFA000'
  }
```

(If you prefer cleaner diffs, add a trailing comma to the `lime-green` block and drop the leading comma here — either is valid TS.)

- [ ] **Step 4: Lint + compile the SCSS to verify the theme builds**

Run:
```bash
cd frontend && npm run lint:scss
```
Expected: no errors for `theme.scss` / `styles.scss`.

Then verify Sass compiles the new theme (full build):
```bash
cd frontend && npm run build
```
Expected: build completes; no "undefined variable `$cybergym-dark-theme`" or palette errors.

- [ ] **Step 5: Commit**

```bash
cd /Users/nameoleg/Documents/Projects/cybergym
git add frontend/src/theme.scss frontend/src/styles.scss views/themes/themes.ts
git commit -s -m "Add cybergym-dark Material theme (yellow on dark)"
```

---

## Task 2: Add placeholder logo + favicon assets

The user will supply the real logo/favicon later; these placeholders keep the build valid and 404-free. Real files simply overwrite them.

**Files:**
- Create: `frontend/src/assets/public/images/CyberGym_Logo.svg`
- Create: `frontend/src/assets/public/favicon_cybergym.ico` (copy of an existing favicon)

- [ ] **Step 1: Create the placeholder SVG wordmark**

Write `frontend/src/assets/public/images/CyberGym_Logo.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 80" role="img" aria-label="CyberGym">
  <text x="2" y="56" font-family="'Segoe UI', Roboto, Arial, sans-serif" font-size="52" font-weight="800" fill="#FFC107">Cyber<tspan fill="#FFFFFF">Gym</tspan></text>
</svg>
```

- [ ] **Step 2: Create the placeholder favicon**

```bash
cd /Users/nameoleg/Documents/Projects/cybergym
cp frontend/src/assets/public/favicon_js.ico frontend/src/assets/public/favicon_cybergym.ico
```
Expected: file exists at `frontend/src/assets/public/favicon_cybergym.ico`.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/assets/public/images/CyberGym_Logo.svg frontend/src/assets/public/favicon_cybergym.ico
git commit -s -m "Add placeholder CyberGym logo + favicon assets"
```

---

## Task 3: Rebrand app identity (config + index.html)

**Files:**
- Modify: `config/default.yml` (the `application:` block, lines 5–45 region)
- Modify: `frontend/src/index.html`

- [ ] **Step 1: Update the `application` identity keys in `config/default.yml`**

Apply these exact value changes (leave `domain`, `altcoinName` decision to Step 2, and leave `social`, `securityTxt`, `googleOauth`, `recyclePage`, `easterEggPlanet`, `promotion` untouched):

- Line 7 `name: 'OWASP Juice Shop'` → `name: 'CyberGym'`
- Line 8 `logo: JuiceShop_Logo.png` → `logo: CyberGym_Logo.svg`
- Line 9 `favicon: favicon_js.ico` → `favicon: favicon_cybergym.ico`
- Line 10 `theme: bluegrey-lightgreen # …` → `theme: cybergym-dark # Custom yellow-on-dark CyberGym theme`

- [ ] **Step 2: Rebrand chatbot, welcome banner, cookie consent, altcoin in `config/default.yml`**

- Line 15 `altcoinName: Juicycoin` → `altcoinName: CyberCoin`
- Line 19 `name: 'Juicy'` (under `chatBot:`) → `name: 'Spotter'` (leave `greeting`, `trainingData`, `defaultResponse`, `avatar` unchanged)
- Line 39 `title: 'Welcome to OWASP Juice Shop!'` → `title: 'Welcome to CyberGym!'`
- Line 40 `message:` → replace the whole quoted value with:
```yaml
    message: "<p><strong>CyberGym</strong> is a deliberately insecure web application packed with a vast number of intended security vulnerabilities. It is an awareness, training, demonstration and CTF arena for security risks in modern web applications. Hunt the flaws, capture the flags, and track everything you solve on the <a href='/#/score-board'>Score Board</a>.</p>"
```
- Lines 42–45 `cookieConsent:` → replace with:
```yaml
  cookieConsent:
    message: 'This site uses cookies to give you the most exploitable browsing experience.'
    dismissText: 'Got it!'
    linkText: 'Learn more'
    linkUrl: '/#/score-board'
```

- [ ] **Step 3: Update `frontend/src/index.html` defaults (used by `ng serve`; the built app is rewritten from config at startup, but keep src consistent)**

- Line 10 `<title>OWASP Juice Shop</title>` → `<title>CyberGym</title>`
- Line 11 `content="Probably the most modern and sophisticated insecure web application"` → `content="CyberGym — a deliberately insecure web app for security training and CTFs"`
- Line 13 `href="assets/public/favicon_js.ico"` → `href="assets/public/favicon_cybergym.ico"`
- Line 26 inline cookieconsent `"content": { … }` → `"content": { "message": "This site uses cookies to give you the most exploitable browsing experience.", "dismiss": "Got it!", "link": "Learn more", "href": "/#/score-board" }`
- Line 30 `<body class="mat-app-background mat-typography bluegrey-lightgreen-theme">` → `<body class="mat-app-background mat-typography cybergym-dark-theme">`

- [ ] **Step 4: Build the frontend so the served `dist` exists for the startup customizer**

```bash
cd /Users/nameoleg/Documents/Projects/cybergym && npm run build:frontend
```
Expected: build succeeds.

- [ ] **Step 5: Boot the app and verify branding + clean config validation**

```bash
cd /Users/nameoleg/Documents/Projects/cybergym
npx ts-node app.ts
```
In a second shell (then stop the server with Ctrl-C):
```bash
curl -s http://localhost:3000/rest/admin/application-configuration | grep -o '"name":"CyberGym"'
```
Expected: prints `"name":"CyberGym"`. The server log shows **no** "configuration validation" error (special challenge products intact). The page `<title>` and favicon reflect CyberGym; the body uses `cybergym-dark-theme`.

- [ ] **Step 6: Commit**

```bash
git add config/default.yml frontend/src/index.html
git commit -s -m "Rebrand app identity to CyberGym (config + index.html)"
```

---

## Task 4: Rebrand the product catalog (names + descriptions)

**Files:**
- Modify: `config/default.yml` (the `products:` block, lines 94–421)

**Rule (re-stated):** edit only `name:` and `description:` text. Do **not** touch any other line. Keep all 46 products in the same order. In descriptions, preserve every `<a href=...>` link, every `/#/...` path, and the lore sentences flagged below.

- [ ] **Step 1: Apply the name mapping**

Rename each product's `name:` exactly as follows (line numbers from the current file):

| Line | Old name | New name |
|---|---|---|
| 96 | Apple Juice (1000ml) | Recon Energy Drink (1000ml) |
| 105 | Orange Juice (1000ml) | Brute-Force Booster (1000ml) |
| 113 | Eggfruit Juice (500ml) | Payload Punch (500ml) |
| 120 | Raspberry Juice (1000ml) | Pi Overclock Cola (1000ml) |
| 125 | Lemon Juice (500ml) | Zero-Day Zest (500ml) |
| 132 | Banana Juice (1000ml) | Script-Kiddie Smoothie (1000ml) |
| 139 | OWASP Juice Shop T-Shirt | CyberGym T-Shirt |
| 145 | OWASP Juice Shop CTF Girlie-Shirt | CyberGym CTF Girlie-Shirt |
| 150 | OWASP SSL Advanced Forensic Tool (O-Saft) | SSL Advanced Forensic Tool (O-Saft) |
| 156 | Christmas Super-Surprise-Box (2014 Edition) | CyberGym Christmas Super-Surprise-Box (2014 Edition) |
| 162 | Rippertuer Special Juice | Rippertuer Special Brew |
| 170 | OWASP Juice Shop Sticker (2015/2016 design) | CyberGym Sticker (2015/2016 design) |
| 176 | OWASP Juice Shop Iron-Ons (16pcs) | CyberGym Iron-Ons (16pcs) |
| 181 | OWASP Juice Shop Magnets (16pcs) | CyberGym Magnets (16pcs) |
| 186 | OWASP Juice Shop Sticker Page | CyberGym Sticker Page |
| 191 | OWASP Juice Shop Sticker Single | CyberGym Sticker Single |
| 196 | OWASP Juice Shop Temporary Tattoos (16pcs) | CyberGym Temporary Tattoos (16pcs) |
| 203 | OWASP Juice Shop Mug | CyberGym Mug |
| 208 | OWASP Juice Shop Hoodie | CyberGym Hoodie |
| 213 | OWASP Juice Shop-CTF Velcro Patch | CyberGym CTF Velcro Patch |
| 223 | Woodruff Syrup "Forest Master X-Treme" | Overflow Syrup "Forest Master X-Treme" |
| 228 | Green Smoothie | Green-Hat Smoothie |
| 235 | Quince Juice (1000ml) | Quantum Quince Fuel (1000ml) |
| 240 | Apple Pomace | Compiled Pomace |
| 246 | Fruit Press | Data Press |
| 251 | OWASP Juice Shop Logo (3D-printed) | CyberGym Logo (3D-printed) |
| 259 | Juice Shop Artwork | CyberGym Artwork |
| 266 | Global OWASP WASPY Award 2017 Nomination | Global AppSec Award 2017 Nomination |
| 272 | Strawberry Juice (500ml) | SQL-Berry Shot (500ml) |
| 277 | Carrot Juice (1000ml) | Root-Access Carrot Fuel (1000ml) |
| 284 | OWASP Juice Shop Sweden Tour 2017 Sticker Sheet (Special Edition) | CyberGym Sweden Tour 2017 Sticker Sheet (Special Edition) |
| 290 | Pwning OWASP Juice Shop | Pwning CyberGym |
| 297 | Melon Bike (Comeback-Product 2018 Edition) | Mainframe Melon Bike (Comeback-Product 2018 Edition) |
| 304 | OWASP Juice Shop Coaster (10pcs) | CyberGym Coaster (10pcs) |
| 310 | OWASP Snakes and Ladders - Web Applications | OWASP Snakes and Ladders - Web Applications *(unchanged — real external OWASP product)* |
| 318 | OWASP Snakes and Ladders - Mobile Apps | OWASP Snakes and Ladders - Mobile Apps *(unchanged — real external OWASP product)* |
| 326 | OWASP Juice Shop Holographic Sticker | CyberGym Holographic Sticker |
| 336 | OWASP Juice Shop "King of the Hill" Facemask | CyberGym "King of the Hill" Facemask |
| 346 | Juice Shop Adversary Trading Card (Common) | CyberGym Adversary Trading Card (Common) |
| 356 | Juice Shop Adversary Trading Card (Super Rare) | CyberGym Adversary Trading Card (Super Rare) |
| 367 | Juice Shop "Permafrost" 2020 Edition | CyberGym "Permafrost" 2020 Edition |
| 376 | Best Juice Shop Salesman Artwork | Best CyberGym Salesman Artwork |
| 385 | OWASP Juice Shop Card (non-foil) | CyberGym Card (non-foil) |
| 394 | 20th Anniversary Celebration Ticket | 20th Anniversary Celebration Ticket *(unchanged — real OWASP event)* |
| 403 | OWASP Juice Shop LEGO™ Tower | CyberGym LEGO™ Tower |
| 412 | DSOMM & Juice Shop User Day Ticket | DSOMM & CyberGym User Day Ticket |

- [ ] **Step 2: Rebrand descriptions (text only), preserving flagged content**

For every product, reword `description:` to fit its new cyber name. In every description, apply the brand substitutions `OWASP Juice Shop → CyberGym` and `Juice Shop → CyberGym`, and re-theme juice/fruit flavor text to a security/gym vibe. **Preserve exactly** the following because they carry challenge lore or functional links:

- **Line 151 (O-Saft):** keep the existing SSL-tool description text unchanged (it is already security-themed and the tampering challenge augments it at runtime). Do **not** remove `urlForProductTamperingChallenge` (line 154).
- **Line 157 (Christmas box):** keep the "Contains a random selection of 10 bottles … extra fan shirt" gift-box meaning and the word context; keep `useForChristmasSpecialChallenge` (line 160).
- **Line 163 (Rippertuer):** keep the sentence `<span style="color:red;">This item has been made unavailable because of lack of safety standards.</span>` verbatim (it is the challenge hint). Keep `keywordsForPastebinDataLeakChallenge` (lines 166–168).
- **Line 252 (3D logo):** keep the "designed and handcrafted in Sweden" lore; keep `fileForRetrieveBlueprintChallenge` + `exifForBlueprintChallenge` (lines 255–257).
- **Lines 241, 247 (Compiled Pomace / Data Press):** keep the recycle link `<a href="/#recycle">…</a>` / "send back to us for recycling" meaning.
- Any product whose name is left unchanged (lines 310, 318, 394) — leave its description unchanged too.
- Keep all `<a href=...>` URLs and `/#/...` paths in every description intact.

- [ ] **Step 3: Verify counts and structure are intact**

```bash
cd /Users/nameoleg/Documents/Projects/cybergym
# product count unchanged (expect the same count as before edits)
grep -cE "^  -$" config/default.yml
# the three special-product fields still present (expect 1 each)
grep -c "useForChristmasSpecialChallenge" config/default.yml
grep -c "urlForProductTamperingChallenge" config/default.yml
grep -c "fileForRetrieveBlueprintChallenge" config/default.yml
grep -c "keywordsForPastebinDataLeakChallenge" config/default.yml
```
Expected: product count matches pre-edit value; each special field count is `1`.

- [ ] **Step 4: Boot to confirm `validateConfig` passes with the rebranded catalog**

```bash
npx ts-node app.ts
```
Expected: server starts with **no** configuration validation error; product seeding succeeds. Stop with Ctrl-C.

- [ ] **Step 5: Commit**

```bash
git add config/default.yml
git commit -s -m "Rebrand product catalog to CyberGym (names + descriptions)"
```

---

## Task 5: Rebrand remaining copy (i18n, challenges, server templates)

**Files:**
- Modify: `frontend/src/assets/i18n/en.json` (lines 252, 469)
- Modify: `data/static/challenges.yml` (brand strings only; never `key:`)
- Modify: server-rendered templates that mention the brand (`views/dataErasureResult.hbs`, `views/dataErasureForm.hbs`, `views/promotionVideo.pug`)

- [ ] **Step 1: Fix the two hardcoded brand strings in `en.json`**

(The `{{juiceshop}}` interpolations elsewhere auto-resolve to the configured name and need no edit.)

- Line 252 `"SCORE_BOARD_HACKING_INSTRUCTOR": "Launch a tutorial to get you started hacking the Juice Shop."` → `… hacking CyberGym."`
- Line 469 `"NFT_SBT_BOX_TEXT": "Hurray! Find the Juice Shop SBT on {{link}}. …"` → `"… Find the CyberGym SBT on {{link}}. …"` (keep `{{link}}` and the rest of the sentence)

- [ ] **Step 2: Replace brand strings in `challenges.yml` (key-safe global replace)**

Challenge `key:` values are camelCase identifiers with no spaces, so replacing the multi-word brand strings cannot touch them. URLs (`pwning.owasp-juice.shop`) are lowercase/hyphenated and unaffected.

```bash
cd /Users/nameoleg/Documents/Projects/cybergym
sed -i '' 's/OWASP Juice Shop/CyberGym/g; s/Juice Shop/CyberGym/g' data/static/challenges.yml
# verify no brand strings remain and keys are untouched
grep -c "Juice Shop" data/static/challenges.yml   # expect 0
grep -c "^  key:" data/static/challenges.yml       # expect unchanged (110)
```
Expected: `Juice Shop` count `0`; `key:` count `110` (unchanged).

- [ ] **Step 3: Replace brand strings in server-rendered templates**

```bash
cd /Users/nameoleg/Documents/Projects/cybergym
sed -i '' 's/OWASP Juice Shop/CyberGym/g; s/Juice Shop/CyberGym/g' views/dataErasureResult.hbs views/dataErasureForm.hbs views/promotionVideo.pug
grep -rc "Juice Shop" views/ | grep -v ':0' || echo "no brand strings left in views/"
```
Expected: no remaining `Juice Shop` in those templates. (Do **not** sed `views/themes/themes.ts` — its keys were set in Task 1.)

- [ ] **Step 4: Verify i18n JSON is still valid and the app builds**

```bash
cd /Users/nameoleg/Documents/Projects/cybergym
node -e "JSON.parse(require('fs').readFileSync('frontend/src/assets/i18n/en.json','utf8')); console.log('en.json valid')"
npm run build:frontend
```
Expected: `en.json valid`; frontend build succeeds.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/assets/i18n/en.json data/static/challenges.yml views/dataErasureResult.hbs views/dataErasureForm.hbs views/promotionVideo.pug
git commit -s -m "Rebrand remaining copy to CyberGym (i18n, challenges, templates)"
```

---

## Task 6: Modern styling polish (yellow-on-dark, rounded, button positions)

Visual-only. Style via classes/CSS variables — do not delete or rename DOM elements (tests/challenges select on them).

**Files:**
- Modify: `frontend/src/styles.scss` (append global polish after line 308)
- Modify: `frontend/src/app/navbar/navbar.component.scss` (append after line 59 `.logo` block)

- [ ] **Step 1: Global polish in `frontend/src/styles.scss`**

Append at the end of the file:

```scss
/* ---- CyberGym modern polish ---- */

// Deeper charcoal app background for the CyberGym theme
.cybergym-dark-theme.mat-app-background {
  background-color: #15171c;
}

// Rounded, modern cards
div.mdc-card {
  border-radius: 14px;
}

// Pill-style buttons with a touch more weight
.mat-mdc-raised-button,
.mat-mdc-unelevated-button,
.mat-mdc-outlined-button,
.mat-mdc-button {
  border-radius: 24px;
  font-weight: 600;
  letter-spacing: 0.2px;
}

// Consistent primary-action placement: right-align dialog/card actions with even spacing
.mat-mdc-dialog-actions,
.mat-mdc-card-actions {
  justify-content: flex-end;
  gap: 8px;
  padding: 8px 16px 16px;
}
```

- [ ] **Step 2: Navbar accent in `frontend/src/app/navbar/navbar.component.scss`**

Append at the end of the file:

```scss
/* ---- CyberGym navbar polish ---- */
mat-toolbar {
  border-bottom: 2px solid var(--theme-primary);
}

#homeButton span {
  font-weight: 700;
  letter-spacing: 0.3px;
}

.logo {
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.4));
}
```

- [ ] **Step 3: Lint SCSS and build**

```bash
cd /Users/nameoleg/Documents/Projects/cybergym/frontend && npm run lint:scss && npm run build
```
Expected: lint clean; build succeeds.

- [ ] **Step 4: Visual smoke check**

```bash
cd /Users/nameoleg/Documents/Projects/cybergym && npx ts-node app.ts
```
Open `http://localhost:3000` and confirm: yellow-on-dark theme, deep charcoal background, yellow toolbar underline, rounded cards/pill buttons, CyberGym logo + name in the navbar, Score Board (`/#/score-board`) loads. Stop with Ctrl-C.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/styles.scss frontend/src/app/navbar/navbar.component.scss
git commit -s -m "Modernize CyberGym styling (theme polish, rounded cards, button layout)"
```

---

## Task 7: Full regression verification

No new code — prove the reskin broke nothing.

- [ ] **Step 1: Full lint**

```bash
cd /Users/nameoleg/Documents/Projects/cybergym && npm run lint
```
Expected: eslint + Angular lint + stylelint all pass.

- [ ] **Step 2: Server unit/integration tests**

```bash
cd /Users/nameoleg/Documents/Projects/cybergym && npm run test:server
```
Expected: all server tests pass (this exercises config validation and product/challenge wiring).

- [ ] **Step 3: API challenge tests (the main detection safety net)**

```bash
cd /Users/nameoleg/Documents/Projects/cybergym && npm run frisby
```
Expected: the Frisby/Jest API suite passes — confirms challenge solving/detection (incl. the tampering, Christmas, pastebin-keyword, and blueprint product challenges) still works after the content rebrand.

- [ ] **Step 4: (Optional, fuller) Frontend unit tests**

```bash
cd /Users/nameoleg/Documents/Projects/cybergym/frontend && npm run test -- --watch=false
```
Expected: pass. The `navbar.component.spec.ts` should still pass since we changed only SCSS, not the component API.

- [ ] **Step 5: Manual challenge spot-check**

Boot the app (`npx ts-node app.ts`), then verify a few representative challenges still register on the Score Board, e.g.:
- DOM XSS / search (generic),
- Christmas special order (SQLi to find the renamed Christmas box, then order it),
- the product-tampering challenge on the O-Saft product.

Expected: each still solves and appears solved on the Score Board.

- [ ] **Step 6: Finalize**

If any test fails, fix it within the protected-data rules (most likely cause: a description lost a flagged lore sentence/link, or a special field was edited — revert that line). Re-run the failing suite. When green:

```bash
cd /Users/nameoleg/Documents/Projects/cybergym
git status   # should be clean (all work committed across Tasks 1-6)
```

Then choose how to integrate the `cybergym-reskin` branch (merge / PR) via the finishing-a-development-branch workflow.

---

## Self-review notes (spec coverage)

- Spec §4.1 (branding) → Task 3. §4.2 (theme) → Task 1. §4.3 (modern polish + button positions) → Task 6. §4.4 (content rebrand + protected boundary) → Tasks 4 & 5 + the boundary section. §4.5 (untouched functionality) → enforced by the boundary rule + Task 7. §5 (verification) → Task 7. §6 (rollout chunks) → Task ordering 1→6. §2 logo/favicon "user supplies" → Task 2 placeholders. All spec sections map to a task.
