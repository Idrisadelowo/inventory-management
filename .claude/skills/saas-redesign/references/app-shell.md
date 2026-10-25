# App shell pattern

The shell is a two-column CSS grid: a fixed-width sidebar, and a main column that holds a sticky top bar and the routed content. Only the main column's content changes between routes.

```
+-----------+--------------------------------------------+
|  Brand    |  Top bar: [filters / search]   [lang][user] |
|           +--------------------------------------------+
|  Nav      |                                            |
|  - item   |  <router-view />  (max-width, padded)      |
|  - item   |                                            |
|           |                                            |
|  footer   |                                            |
+-----------+--------------------------------------------+
```

## App.vue template

Adapt names to the project; keep every component the old header rendered.

```vue
<template>
  <div class="app-shell">
    <AppSidebar />

    <div class="app-main">
      <!-- One sticky wrapper for the top bar and filter row, so they stay
           together without hard-coded top offsets -->
      <div class="app-header">
        <header class="app-topbar">
          <div class="topbar-start">
            <!-- filters/search only if they fit beside topbar-end at 1280px;
                 otherwise leave this empty -->
          </div>
          <div class="topbar-end">
            <!-- language switcher, notifications, profile menu -->
          </div>
        </header>
        <!-- Filters that don't fit the top bar go here as their own row -->
      </div>

      <main class="app-content">
        <router-view />
      </main>
    </div>

    <!-- Modals stay outside the grid so their fixed positioning and z-index are unaffected -->
  </div>
</template>
```

## Global shell CSS (unscoped, in App.vue or a global stylesheet)

Merge this with the app's existing reset rather than replacing it. If the old reset zeroed `margin`/`padding` on `*`, keep that: views were written assuming it. Keep the existing base font size too (shown here as `--text-base`).

```css
*,
*::before,
*::after {
  box-sizing: border-box;
  /* keep margin: 0; padding: 0; here if the old reset had them */
}

body {
  margin: 0;
  font-family: var(--font-sans);
  font-size: var(--text-base); /* match the app's previous base size */
  line-height: var(--leading-normal);
  color: var(--color-text);
  background: var(--color-bg);
  -webkit-font-smoothing: antialiased;
}

.app-shell {
  display: grid;
  grid-template-columns: var(--sidebar-width) minmax(0, 1fr);
  min-height: 100vh;
}

/* minmax(0, 1fr) above and min-width: 0 here stop wide tables from
   stretching the main column past the viewport */
.app-main {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* The wrapper is sticky, not the top bar, so a filter row below it stays attached */
.app-header {
  position: sticky;
  top: 0;
  z-index: var(--z-topbar);
}

.app-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  min-height: var(--topbar-height);
  padding: var(--space-2) var(--content-padding);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.topbar-start,
.topbar-end {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 0;
}

.app-content {
  width: 100%;
  max-width: var(--content-max);
  margin: 0 auto;
  padding: var(--space-8) var(--content-padding);
}

@media (max-width: 900px) {
  .app-shell {
    grid-template-columns: minmax(0, 1fr);
  }

  :root {
    --content-padding: var(--space-4);
  }

  /* Wrapped filters become a tall block on phones; pinning it would cover the content */
  .app-header {
    position: static;
  }

  .app-topbar {
    flex-wrap: wrap;
  }
}

/* Tables inside padded cards: bleed to the card edges so the header band and
   row borders run full width */
.card > .table-container {
  margin: 0 calc(-1 * var(--space-6)) calc(-1 * var(--space-6));
}
```

## Shared component styles to rewrite with tokens

Rewrite whatever the project already has under these roles; don't introduce new class names unless nothing exists for the role.

| Role | Typical classes | Token guidance |
|---|---|---|
| Page header | `.page-header h2`, `p` | `--text-xl` semibold title, `--color-text-muted` description, `--space-6` below |
| Card | `.card` | `--color-surface`, 1px `--color-border`, `--radius-lg`, `--shadow-sm`, padding `--space-6`, gap between cards `--space-6` |
| Card header | `.card-header`, `.card-title` | flex, space-between, `--text-lg` semibold, `--space-4` below |
| KPI / stat card | `.stat-card`, `.stat-label`, `.stat-value` | label `--text-xs` uppercase muted, value `--text-2xl` bold; status variants keep any existing colored value and may add a 3px left border in the same status color; avoid full colored backgrounds |
| Grid of cards | `.stats-grid` | `repeat(auto-fit, minmax(min(220px, 100%), 1fr))`, gap `--space-4` |
| Table | `table`, `th`, `td`, `.table-container` | container `overflow-x: auto`; `th` `--text-xs` uppercase muted on `--color-surface-muted`; cells `--space-3` `--space-4`; row border `--color-border`; hover `--color-surface-muted` |
| Badge | `.badge.success/.info/.warning/.danger`, plus domain variants (trend, priority, stock) | one shape everywhere: `--radius-full`, `--text-xs` medium; color each variant by meaning with the soft background + matching text token |
| Button | `button`, `.btn` | primary uses `--color-accent`; `--radius-md`; focus ring `--color-focus-ring`; disabled 50% opacity |
| Inputs / selects | `input`, `select` | 1px `--color-border-strong`, `--radius-sm`, focus ring, height ~36px |
| Loading / error / empty | `.loading`, `.error`, `.empty-state` | centered muted text; error uses `--color-danger-soft` background with `--color-danger-text` |
| Disclosure carets | `details > summary` markers | draw with a CSS border triangle or inline SVG, never a ▶ character |
