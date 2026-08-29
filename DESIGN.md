---
name: Plant Tracker
description: A personal plant-ID and history tool — a warm terracotta primary on a pure-white field-notebook canvas.
colors:
  background: "oklch(1 0 0)"
  foreground: "oklch(0.20 0.02 54)"
  card: "oklch(1 0 0)"
  primary: "oklch(0.56 0.15 54)"
  primary-foreground: "oklch(1 0 0)"
  secondary: "oklch(0.97 0.006 54)"
  secondary-foreground: "oklch(0.20 0.02 54)"
  muted: "oklch(0.97 0.006 54)"
  muted-foreground: "oklch(0.52 0.012 54)"
  accent: "oklch(0.95 0.01 54)"
  destructive: "oklch(0.55 0.19 25)"
  destructive-foreground: "oklch(1 0 0)"
  success: "oklch(0.50 0.13 150)"
  success-foreground: "oklch(1 0 0)"
  warning: "oklch(0.55 0.15 85)"
  warning-foreground: "oklch(1 0 0)"
  info: "oklch(0.28 0.07 235)"
  info-foreground: "oklch(1 0 0)"
  border: "oklch(0.90 0.008 54)"
typography:
  display:
    fontFamily: "ui-sans-serif, system-ui, sans-serif (Tailwind default stack)"
    fontSize: "2.25rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "normal"
  body:
    fontFamily: "ui-sans-serif, system-ui, sans-serif (Tailwind default stack)"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
rounded:
  sm: "0.25rem"
  md: "0.375rem"
  lg: "0.5rem"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.primary-foreground}"
    rounded: "{rounded.md}"
    padding: "8px 16px"
  button-primary-hover:
    backgroundColor: "{colors.primary}"
  card:
    backgroundColor: "{colors.card}"
    rounded: "{rounded.lg}"
    padding: "24px"
  badge-success:
    backgroundColor: "{colors.success}"
    textColor: "{colors.success-foreground}"
    rounded: "9999px"
  badge-warning:
    backgroundColor: "{colors.warning}"
    textColor: "{colors.warning-foreground}"
    rounded: "9999px"
  badge-destructive:
    backgroundColor: "{colors.destructive}"
    textColor: "{colors.destructive-foreground}"
    rounded: "9999px"
---

# Design System: Plant Tracker

## 1. Overview

**Creative North Star: "The Field Notebook"**

Plant Tracker feels plain, functional, and a little worn-in — something you'd actually carry outside while pointing a phone at a leaf. A single warm terracotta (oklch 0.56 0.15 54 — clay pots, dried botanical ink, sun-baked ground) is the only color the interface asserts on purpose; everything else is a pure-white canvas and a warm-tinted neutral scale built from the same hue. This deliberately sidesteps both the generic AI-green plant-app cliché and the SaaS-cream/parchment default: the warmth lives in the primary color and the icon badges, not in the page background, which stays true white (oklch(1 0 0)) exactly per the "mood lives in the brand color, not the surface" rule.

A second color, a deep ink-navy (oklch 0.28 0.07 235 — fountain-pen ink on a ledger page), exists solely as the `info` semantic role — currently used only for the "Watering" care-tip card. It is not a second brand color competing with primary; Restrained-strategy product design gets one accent, and this app follows that.

This replaces the previous baseline (documented in git history), which ran on shadcn's unmodified defaults plus ad hoc Tailwind `green-600`/`blue-600` swatches and a `green-50→blue-50` gradient background — that palette was explicitly flagged as inherited, not chosen. Every value below is now a deliberate decision, verified against WCAG contrast requirements (see Named Rules).

**Key Characteristics:**
- One committed brand color (terracotta primary) on a pure-white field, per the Restrained color strategy that's the product-register default
- Warm-tinted neutrals (chroma 0.006–0.02 toward hue 54) replace shadcn's cold blue-gray "slate" scale throughout
- A standardized 3-state semantic vocabulary (success / warning / destructive) replaces the old ad hoc green-500/yellow-500/red-500/purple-600/orange-600 rainbow
- Flat surfaces at rest; `shadow-lg` appears only on card hover (unchanged from baseline — a good instinct, kept)
- Full OKLCH token system in both light and dark mode, verified for ≥4.5:1 text contrast on every filled swatch

## 2. Colors

One saturated brand color, a pure-white field, and a warm-tinted neutral scale built from the same hue family — the Restrained strategy this product register defaults to.

### Primary
- **Terracotta** (oklch(0.56 0.15 54)): The only color the interface asserts on purpose. Used for primary CTAs (Sign in, Identify Plant, Choose Image), the leaf wordmark icon, both home-screen action-card icon badges (unified — see The One Meaning Rule), the taxonomy chart's connective ink, and focus rings. White text/icons on top (`oklch(1 0 0)`, 4.89:1 contrast, verified ≥4.5 AA).

### Neutral
- **Pure White** (oklch(1 0 0)): The entire page canvas and card surfaces. Deliberately NOT tinted cream/sand/parchment — the brand's warmth comes from primary, not the background (see The Mood-Lives-In-Primary Rule).
- **Ink** (oklch(0.20 0.02 54)): Body text and headings. Carries a faint warm tint toward the primary hue rather than shadcn's cold blue-gray. 18:1 contrast against white.
- **Surface** (oklch(0.97 0.006 54)): `secondary` / `muted` background role — barely-tinted, used for image letterboxing, subtle panel fills.
- **Muted Ink** (oklch(0.52 0.012 54)): Secondary/supporting text (timestamps, captions, empty states). 5.5:1 contrast against white.
- **Hover Neutral** (oklch(0.95 0.01 54)): shadcn's generic `accent` role — light neutral hover wash for menu items and similar chrome, distinct from the `info` brand-adjacent color.
- **Border** (oklch(0.90 0.008 54)): Hairline card and input borders.

### Semantic
- **Success** (oklch(0.50 0.13 150)): Confidence badges ≥90%, "Saved!" notes confirmation, "Soil" care tip.
- **Warning** (oklch(0.55 0.15 85)): Confidence badges 70–89%, "Light" care tip. An ochre/mustard rather than caution-yellow — reads as pigment, not hazard tape, fitting the field-notebook register.
- **Destructive** (oklch(0.55 0.19 25)): Confidence badges <70%, delete actions, camera error states.
- **Info** (oklch(0.28 0.07 235)): "Watering" care tip only. Not a second brand accent — one deliberate use, not decoration.

### Named Rules
**The Mood-Lives-In-Primary Rule.** Body background is pure white (chroma 0) in every state, always. Warmth and personality come from primary, icon badges, and typography — never from tinting the canvas cream, sand, or parchment. If a future pass wants more color presence, spend it on primary's usage frequency, not on desaturating the background.

**The One Meaning Rule.** Every instance of primary means the same thing: "the action that moves you toward an identification." Camera and Upload entry cards on the home screen intentionally share the same terracotta rather than being color-coded differently — an earlier draft tried camera=primary/upload=info, but that invented a distinction with no real semantic weight. Reserve `info` for its one real job (the Watering tip) until a second meaning actually earns it.

**The Verified-Contrast Rule.** Every filled semantic/brand swatch (primary, destructive, success, warning, info) carries white text/icons and was tuned in OKLCH so that white-on-fill contrast clears 4.5:1 in both light and dark mode — not assumed, computed. If you introduce a new filled color, verify it the same way before shipping; warm hues (orange, gold) especially tend to read brighter than their OKLCH lightness suggests, and white text can fail even when the "L 0.42–0.78 → white text" heuristic says it should work.

## 3. Typography

**Display Font:** ui-sans-serif / system-ui (Tailwind's default sans stack — no webfont loaded)
**Body Font:** ui-sans-serif / system-ui (same stack)
**Label/Mono Font:** none in use

**Character:** Unchanged from baseline — plain and functional, no typographic point of view yet. This colorize pass deliberately left type alone; a future `/impeccable typeset` pass is the right place to give the pairing more character (see Do's and Don'ts).

### Hierarchy
- **Display** (700, `text-5xl` / 3rem, tight): App name on the signed-out screen.
- **Headline** (700, `text-4xl` / 2.25rem, tight): Signed-in home header, section titles.
- **Title** (600, `text-2xl` / 1.5rem, snug): Card headings.
- **Body** (400, `text-base`–`text-xl` / 1–1.25rem, relaxed): Supporting copy, capped by container width.
- **Label** (500, `text-sm` / 0.875rem, normal case): Button and form labels.

## 4. Elevation

Unchanged from baseline: flat at rest, `shadow-lg` only on hover for the two home-screen action cards. No tonal-elevation system — everything sits on one of two surfaces (white cards, white canvas), delineated by a 1px warm-tinted border rather than a surface-lightness step.

### Shadow Vocabulary
- **Hover lift** (`box-shadow: Tailwind shadow-lg` ≈ `0 10px 15px -3px rgb(0 0 0 / 0.1)`): Home-screen action cards on hover.

### Named Rules
**The Flat-at-Rest Rule.** Nothing carries a shadow until the user's cursor or touch says otherwise. Kept unchanged from baseline — it already fit the calm, unfussy field-notebook feel.

## 5. Components

### Buttons
- **Shape:** `rounded-md` (6px), unchanged shadcn default.
- **Primary:** `bg-primary` (terracotta) / white text. This is now the shadcn Button default, so screens no longer need a `bg-green-600 hover:bg-green-700` override — removed everywhere it appeared.
- **Outline:** `border-primary text-primary hover:bg-primary/10` for the "View History" CTA — same brand color as the primary button, just outlined, rather than an independent green override.
- **Hover / Focus:** Default shadcn opacity shift; focus ring now uses primary (`--ring` = primary) instead of shadcn's default near-black ring.

### Badges (confidence / status)
- **Shape:** `rounded-full`, no border (`border-none` on top of shadcn's `outline` variant, which otherwise draws a hairline border that read oddly against a filled semantic background).
- **Fill:** One of success / warning / destructive, chosen by confidence tier (≥90 / 70–89 / <70). Each pairs with its own `-foreground` token — never assume white text works for every fill (see The Verified-Contrast Rule).

### Cards
- **Corner Style:** `rounded-lg` (8px), unchanged.
- **Background:** White (`bg-card`), 1px `border-border`.
- **Shadow Strategy:** See Elevation.
- **Internal Padding:** `p-6 md:p-8` (24px / 32px), unchanged.

### Icon Badges
- 64px circular container (`w-16 h-16 rounded-full bg-primary/10`), primary-colored icon inside, `group-hover:bg-primary/15` on card hover. Both home-screen entry points (Camera, Upload) share this treatment — see The One Meaning Rule.

### Care-Tip Cards (signature component)
- Three-column grid (`bg-info/10` / `bg-warning/10` / `bg-success/10`), each with a colored heading (`text-info` / `text-warning` / `text-success`) and body copy in plain `text-foreground` (not tinted — tinted body text on a tinted background was the original's contrast risk, avoided here by keeping only the heading colored).

### Taxonomy Chart (signature component)
- Inline SVG: primary-colored nodes and connective lines (`oklch(0.56 0.15 54)`), white initials inside each node, `fill-foreground` labels below. Replaces the previous hardcoded `#22c55e` / `#4ade80` green hexes, which weren't theme-aware and didn't participate in the token system.

## 6. Do's and Don'ts

### Do:
- **Do** keep body background pure white in every state — the field-notebook warmth comes from primary usage, not canvas tint (The Mood-Lives-In-Primary Rule).
- **Do** verify any new filled color's white-text contrast computationally, not by eye — warm hues are deceptive (The Verified-Contrast Rule).
- **Do** keep primary meaning one thing across the app; resist color-coding entry points or categories unless the distinction is real (The One Meaning Rule).
- **Do** keep the flat-at-rest, lift-on-hover shadow behavior.

### Don't:
- **Don't** let this read as a corporate SaaS dashboard — no sidebar nav, no dense stat-tile grids treated as a KPI board, no boxy enterprise chrome (PRODUCT.md anti-reference). The "Your Plant Journey" stat row is a personal-recap moment, not a metrics panel — keep it small and keep every number the same primary color, not a rainbow.
- **Don't** reintroduce raw Tailwind palette classes (`green-600`, `blue-50`, `purple-600`, etc.) — every color in the UI should resolve through a token (`primary`, `success`, `warning`, `destructive`, `info`, or a neutral).
- **Don't** add uppercase tracked eyebrow labels or numbered section markers — nothing about a personal plant log calls for landing-page scaffolding.
- **Don't** treat this colorize pass as having finished the typography or layout work — the type scale is still the unexamined Tailwind default (a `/impeccable typeset` candidate) and the taxonomy chart's mobile font sizes are off-ramp literals worth a look in a future `/impeccable audit` pass.
