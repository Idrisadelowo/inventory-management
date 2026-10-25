# Redesign QA checklist

Work through this after the build passes. Fix failures before reporting. Items marked (visual) need a rendered page: with no browser automation and no user to open pages for, report them as unverified rather than skipping them silently.

## Nothing lost
- [ ] Every route from the audit has a sidebar item, in the original order, and each link navigates correctly.
- [ ] Every control from the old header (logo/brand, filters, search, language switcher, profile/user menu, notifications) is present and still works.
- [ ] Modals and dropdowns opened from the shell still open, sit above the sidebar and top bar, and close.
- [ ] If the app has i18n: switching language updates sidebar labels too, and no raw keys like `nav.reports` appear.

## Navigation
- [ ] Exactly one sidebar item is active on each route; `/` is not active on other pages.
- [ ] Active item has `aria-current="page"`; nav has an accessible label.
- [ ] Keyboard: Tab reaches every nav item and top bar control with a visible focus ring.

## Layout and spacing
- [ ] (visual) At ~1280px wide: no horizontal page scroll; wide tables scroll inside their own container; multi-column chart grids still have room beside the sidebar.
- [ ] (visual) At ~400px wide: sidebar is a horizontal strip, content is single column, no horizontal page scroll.
- [ ] (visual) On desktop the header (top bar plus any filter row) stays pinned together while scrolling, and the sidebar stays put; on phones the header scrolls away.
- [ ] No leftover `top: Npx` offsets tied to the old header height.
- [ ] Every width risk from the audit is fixed (no fixed px minimums above ~280px in grids).
- [ ] The existing reset still applies (headings and paragraphs didn't gain browser default margins).
- [ ] Gaps between cards are uniform across views; card padding is the same everywhere.
- [ ] Page titles, card titles and table headers use the same sizes on every view.

## Visual consistency
- [ ] Hard-coded greys/borders/radii in view styles are replaced by tokens where equivalent (search for `#e2e8f0`, `#64748b`, `#0f172a`, `border-radius:` with raw px).
- [ ] Status colors keep their meaning (success = green, warning = amber, danger = red, info = blue) and badges look identical across views.
- [ ] Chart and data colors were left as they were.
- [ ] Every `var(--x)` used is defined in tokens.css.
- [ ] Hover and active states still differ from their base state (no pair collapsed onto one token).
- [ ] Shell components (filters, language switcher, profile menu) match the top bar; top-bar buttons share one height.
- [ ] No emojis or symbol glyphs (▶ ✓ ★ ⚠) used as icons or decoration; all icons are inline SVG using `currentColor`.
- [ ] Text contrast: body text on surfaces uses `--color-text` or `--color-text-secondary`; muted text is only used for labels and captions.

## Behaviour unchanged
- [ ] Filters still change the data on each view that used them.
- [ ] Forms and actions (submit buttons, toggles, modals) behave exactly as before.
- [ ] (visual) Browser console shows no new errors or Vue warnings on any route.
- [ ] Every affected automated test suite still passes (frontend unit tests if present; backend only if shared code changed).
