---
name: saas-redesign
description: Redesign a Vue 3 (Vite) application's UI into a modern SaaS-style interface - a fixed vertical navigation sidebar on the left in place of a top nav bar, a slim top bar for global controls, a design-token layer (CSS custom properties) for consistent spacing, color, radius, shadow and type, inline SVG nav icons, and restyled cards, tables, badges, buttons and forms. Use this skill whenever the user wants to modernize, polish, re-skin or "make professional" a Vue app's look, move navigation into a sidebar, switch from top tabs to a side nav, add an app shell or dashboard layout, or fix inconsistent spacing and styling across Vue views - even if they don't say "SaaS" or "redesign". Not for React/Svelte/Angular apps, single-component tweaks, or apps built on Tailwind or a component library (Vuetify, PrimeVue, Element Plus, Quasar) without first confirming with the user.
---

# SaaS redesign for Vue 3 apps

Turn an existing Vue 3 app into a calm, consistent SaaS-style product: sidebar navigation on the left, a slim top bar, and every surface drawn from one set of design tokens. This is a visual and layout change only. Users of the app should find every feature where its route says it is, behaving exactly as before.

Why tokens first: most "unpolished" apps look that way because each view invented its own spacing, greys and radii. Fixing the shell alone doesn't help if the pages inside still use fifteen different paddings. Tokens give one vocabulary; the shell and the component sweep both speak it.

## Before you start: who edits the `.vue` files

Read the project's `CLAUDE.md` files first. If they require a specific subagent for `.vue` work:

- **You are the main session and that agent type exists:** do phases 1-2 yourself, then hand phases 3-6 to that agent in one delegation. Give it the path to this SKILL.md and your audit notes, and ask it to report what it couldn't verify.
- **The agent type isn't available, or you are already running inside a subagent:** read that agent's brief (often `.claude/agents/<name>.md`) and follow it yourself. Don't nest delegations.

Where the agent brief and the project's CLAUDE.md disagree (for example `<script setup>` vs `setup()`), CLAUDE.md wins, then the dominant style in the existing views. New files should look like their neighbours.

## Workflow

Work through these phases in order. Each one leaves the app building, so you can stop and show progress at any point.

### 1. Audit (read only)

Write the findings down as a few bullets; they become your "nothing got lost" list.

- **Stack.** Read `package.json`. If Tailwind, UnoCSS or a component library (Vuetify, PrimeVue, Element Plus, Naive UI, Quasar, Ant Design Vue) is in use, stop and ask the user. This skill restyles plain CSS; fighting a framework's theme produces a mess.
- **Nav.** Find where nav links render (usually `App.vue`). Record each link's label source (hard-coded vs i18n key) and its **order as shown in the nav**. That order is what users know, so it wins over the order routes are declared in the router.
- **Routes.** Find `createRouter(...)`. Note routes missing from the nav and view files that aren't registered. Don't add them; mention them in the summary.
- **Header contents.** Everything else in the old header: brand/logo (and whether it's the page's `<h1>`), search, language switcher, profile menu, notifications, global filters. Also note any `position: sticky` / `top: Npx` offsets tied to the old header's height; they will break.
- **Global styles.** Unscoped `<style>` blocks and imported CSS. Note the existing reset (`* { margin: 0; ... }`), the base `body` font-size, the shared class names views rely on (`.card`, `.badge`, `.table-container`...), and existing z-index values for modals and dropdowns.
- **Width risks.** The sidebar takes ~240px from every page, and phones are ~400px wide. Search the views for fixed minimums that will overflow or squeeze: `minmax(` with a px minimum above ~280px, `min-width:` above ~300px, fixed `repeat(2, 1fr)` / `repeat(3, ...)` chart grids, fixed `width:` on wide elements. List them for phase 5.
- **Stray glyphs.** Search templates and CSS `content:` for emojis and symbol characters (such as ▶ ✓ ★ ⚠). Many render as color emoji on some platforms.

### 2. Design tokens

Copy `references/design-tokens.css` to `src/styles/tokens.css`, delete its "how to use this template" comment, and import it as the first line of the entry file (`main.js`), so global and scoped styles can all use it.

Then adapt the values rather than using them blindly:

- **Map existing brand colors onto the token names.** Use what's in CLAUDE.md, existing CSS variables, or the dominant accent in current styles. Keep the token *names*; change the *values*.
  - If the app already has an established status hue (say orange for warnings), set `--color-warning` to it, so existing meaning survives.
- **Keep the existing base font size.** If `body` was 16px, don't silently drop it to 14px. Change it only as a deliberate, mentioned decision.
- **Round off-scale sizes to the nearest token** (13px → `--text-sm`, 15px → `--text-base` or `--text-sm`), unless rounding would merge two sizes that signal different hierarchy levels on the same screen. In that case keep the hierarchy, and pick the next token up or down for one of them.
- **Keep the spacing scale on the 4px grid.** Consistency comes from using few values, not from the particular numbers.

### 3. App shell

Replace the top navigation with a two-column grid: a fixed-width sidebar, and a main column holding the header and scrolling content. Follow `references/app-shell.md` for the template and CSS, and `references/AppSidebar.vue` for the sidebar.

- **Sidebar items** are the audited nav links, in nav order, with the same label source.
  - If a label was hard-coded and the app uses i18n, add a key to every locale file. Otherwise keep the text.
- **Nothing from the old header is deleted.**
  - Brand goes to the top of the sidebar. If it was the page's only `<h1>`, keep it an `<h1>`.
  - Global controls go to the top bar.
  - **Filters:** put them in the top bar's left side only if they fit beside the right-hand controls at 1280px without wrapping. As a rule of thumb, more than two selects won't fit. Otherwise render them as their own row directly beneath the top bar.
  - **Empty left side:** if nothing goes on the left, leave `topbar-start` empty rather than inventing content.
- **Sticky header.** Wrap the top bar and any filter row in one sticky container, so they stay together with no hard-coded offsets. Remove the old `top: Npx` offsets you found in the audit. Below ~900px, make the header static, because wrapped filters become a tall block that would cover the content.
- **Active state.** Use the `custom` v-slot on `router-link`, as the template does. Vue Router 4 has no `exact` prop, and `/` needs exact matching or "Overview" lights up on every page.
- **Responsive fallback.** Below ~900px the grid becomes one column and the sidebar a horizontal scrolling strip. Keep it deliberately simple: no drawer, no JavaScript.
- **Modals and overlays** mounted in `App.vue` stay at the same level, outside the grid.

### 4. Icons

Each sidebar item gets a 20px inline SVG from the set in `references/AppSidebar.vue` (`stroke="currentColor"`, `aria-hidden="true"`), so icons follow the link's color in every state.

Choose by what the route means:

| Route | Icon |
|---|---|
| Overview | home |
| Inventory, products | box |
| Orders | cart |
| Finance, spending | wallet |
| Forecasts, analytics | trend |
| Restocking, procurement, shipping | truck |
| Reports | file |
| Settings | settings |

When nothing fits, use `grid`. Never use emojis or symbol characters as icons. Replace stray glyphs found in the audit with CSS shapes or inline SVG; they render inconsistently and read as unprofessional.

### 5. Restyle shared styles, then sweep

Work outward from the highest-leverage edits:

1. **Global shared classes.** Page header, cards, KPI cards, tables, badges, buttons, inputs, loading, error and empty states. Follow the role table in `references/app-shell.md`. **Merge with the existing reset instead of replacing it.** Views were written assuming it, and dropping `margin: 0` brings back browser margins on every heading.
2. **Components that live in the shell**: the filter bar, language switcher and profile menu now sit in the top bar, so they must match it.
   - Give buttons in the top bar the same height.
   - Modals get a light token pass only (radius, border, shadow, text colors).
3. **Each view's scoped `<style>`:**
   - **Delete overrides that only existed to fight the old global styles.** They are now duplicates of the shared classes.
   - **Swap visually equivalent values for tokens:** hard-coded greys, borders, radii, shadows, spacing, font sizes.
   - **Check state pairs.** When a base color and its hover/active color would map to the same token, pick different tokens (for example `--color-surface` → `--color-surface-muted`, or `--color-accent` → `--color-accent-hover`). Otherwise the hover state silently disappears.
   - **Fix the width risks from the audit.** Write `minmax(min(320px, 100%), 1fr)` instead of a fixed px minimum. Give chart grids a minimum column width instead of a fixed column count, because the content area is now narrower. Let wide tables scroll inside `.table-container`.
   - **Leave data-meaningful colors alone:** chart series, heatmaps, trend up/down, and status colors with a meaning. Changing them can change what the data says.
4. **Domain badges** (trend, priority, stock level...) follow the badge shape from the role table: radius, size, padding.
   - **Color by meaning:** map each to the status token that matches it (increasing/in stock → success, stable → info, high priority → danger), keeping the hue the app already uses for that meaning.
   - "Consistent badges" means one shape. It doesn't mean recoloring meanings.
5. **KPI cards:** keep any existing convention of coloring the value by status. An optional 3px left border in the same status color is fine; don't remove meaning the app already shows.
6. **Z-index:** use the `--z-*` tokens for the sidebar and header. Leave existing modal and dropdown z-index values alone if they are already above the shell's. Only raise values that would now end up underneath it.

Keep the diff to styles, layout wrappers and class names. Don't rename variables, restructure logic, change props, or touch API calls, even when you notice problems. List those instead.

### 6. Verify

1. **Run the build.** Run every automated test suite the repo has that could be affected: frontend unit tests if any exist, and backend tests only if shared code changed.
2. **Grep for undefined tokens:** every `var(--x)` used must be defined in `tokens.css`.
3. **Go through `references/checklist.md`.**
   - **With browser automation available** (for example Playwright MCP): open every route at ~1280px and ~400px and screenshot it.
   - **In the main session, without automation:** open the pages for the user.
   - **In a subagent or headless run:** do neither. Mark the visual and interactive checklist items as unverified.

   Don't pretend to have seen what you haven't.

## Ground rules

- **Behaviour is frozen.** No changes to data fetching, state, routing targets, i18n strings (other than adding missing nav keys), or component props and events. A redesign that breaks a filter is a regression, however nice it looks.
- **Every feature stays reachable.** Compare the final sidebar and top bar against the audit list.
- **The project's rules win.** Its CLAUDE.md overrides this skill's defaults: palette, comment style, required subagents.
- **Comment the non-obvious.** Grid sizing, the sticky header wrapper, z-index choices and the exact match on `/` each deserve a one-line comment saying why. Don't carry this skill's template comments into the project's files.
- **No new dependencies.** Everything here is plain CSS and Vue.
- **Pre-existing problems stay out of scope.** That includes hard-coded English in a whole view, Options API views in a Composition API codebase, index keys and dead CSS. Report them; don't fix them as part of the redesign.

## Summary to give the user

End with:
- What changed: shell, tokens, components, and which views were swept.
- What moved, for example "filters now sit under the top bar".
- Decisions they might want to revisit: base font size, warning hue, rounded type sizes.
- What you noticed but deliberately left alone.
- How you verified it, stating plainly which checklist items were checked and which were not.
