<!--
  Primary navigation for the app shell. Replaces the old top-nav tabs in App.vue:
  same routes, same order, same i18n label keys. Brand text moved here from the
  old header. Depends on tokens from src/styles/tokens.css.
-->
<template>
  <aside :class="['sidebar', { 'sidebar--collapsed': isCollapsed }]">
    <div class="sidebar-brand">
      <!-- Kept as the page's only <h1>, as it was in the old header. t() is called in the
           template, not setup(), so labels re-render when the locale changes.
           In the rail the full name is visually hidden (still read by screen readers)
           and the monogram is shown instead; the monogram is aria-hidden so the
           heading isn't announced as "Catalyst Components CC" -->
      <h1 class="brand-name">
        <span class="brand-full">{{ t('nav.companyName') }}</span>
        <span class="brand-monogram" aria-hidden="true">{{ monogram(t('nav.companyName')) }}</span>
      </h1>
      <span class="brand-subtitle">{{ t('nav.subtitle') }}</span>
    </div>

    <nav id="sidebar-nav" class="sidebar-nav" aria-label="Main">
      <!-- Vue Router 4 has no `exact` prop; the custom slot lets '/' use exact matching
           (otherwise it is active on every page) while other items match nested paths -->
      <router-link
        v-for="item in NAV_ITEMS"
        :key="item.to"
        :to="item.to"
        v-slot="{ href, navigate, isActive, isExactActive }"
        custom
      >
        <a
          :href="href"
          :class="['nav-item', { 'nav-item--active': item.to === '/' ? isExactActive : isActive }]"
          :aria-current="(item.to === '/' ? isExactActive : isActive) ? 'page' : undefined"
          :title="isCollapsed ? t(item.labelKey) : undefined"
          @click="navigate"
        >
          <svg
            class="nav-icon"
            viewBox="0 0 24 24"
            width="20"
            height="20"
            fill="none"
            stroke="currentColor"
            stroke-width="1.75"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
            v-html="ICONS[item.icon] || ICONS.grid"
          />
          <span class="nav-label">{{ t(item.labelKey) }}</span>
        </a>
      </router-link>
    </nav>

    <!-- Footer: the collapse toggle, plus the optional footer slot (version text,
         help link). The slot is dropped in the rail, which has no room for text -->
    <div class="sidebar-footer">
      <div v-if="$slots.footer && !isCollapsed" class="sidebar-footer-slot">
        <slot name="footer" />
      </div>

      <!-- The visible/visually-hidden label is the button's accessible name (no
           aria-label needed); title adds a hover tooltip only when the text is hidden.
           v-if on canCollapse matches the CSS hiding at <= 600px, where the strip
           layout has no collapsed state to toggle -->
      <button
        v-if="canCollapse"
        type="button"
        class="sidebar-toggle"
        :aria-expanded="isCollapsed ? 'false' : 'true'"
        aria-controls="sidebar-nav"
        :title="isCollapsed ? t('nav.expandSidebar') : undefined"
        @click="toggleSidebar"
      >
        <svg
          class="nav-icon"
          viewBox="0 0 24 24"
          width="20"
          height="20"
          fill="none"
          stroke="currentColor"
          stroke-width="1.75"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <!-- Panel outline with a divider for the sidebar; the chevron points the
               way the sidebar will move: left to collapse, right to expand -->
          <rect x="3" y="4" width="18" height="16" rx="2" />
          <path d="M9 4v16" />
          <path v-if="isCollapsed" d="m14 9 3 3-3 3" />
          <path v-else d="m17 9-3 3 3 3" />
        </svg>
        <span class="nav-label">{{ isCollapsed ? t('nav.expandSidebar') : t('nav.collapseSidebar') }}</span>
      </button>
    </div>
  </aside>
</template>

<script>
import { useI18n } from '../composables/useI18n'
import { useSidebar } from '../composables/useSidebar'

// Inline SVG path data (24x24, stroke-based, Lucide-style). Static strings, so v-html is safe here.
const ICONS = {
  home: '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V20a1 1 0 0 0 1 1h4v-6h4v6h4a1 1 0 0 0 1-1V9.5"/>',
  grid: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
  box: '<path d="M21 8 12 3 3 8v8l9 5 9-5V8z"/><path d="m3 8 9 5 9-5"/><path d="M12 13v8"/>',
  cart: '<circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.6 12.2a1.5 1.5 0 0 0 1.5 1.2h8.8a1.5 1.5 0 0 0 1.5-1.2L21 7H6"/>',
  receipt: '<path d="M5 3h14v18l-3-2-2 2-2-2-2 2-2-2-3 2V3z"/><path d="M9 8h6M9 12h6"/>',
  wallet: '<path d="M3 7a2 2 0 0 1 2-2h13v4"/><path d="M3 7v11a2 2 0 0 0 2 2h15V9H5a2 2 0 0 1-2-2z"/><circle cx="16" cy="14.5" r="1.25"/>',
  trend: '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
  chart: '<path d="M3 3v18h18"/><path d="M7 15v3M12 10v8M17 6v12"/>',
  truck: '<path d="M2 6h11v10H2z"/><path d="M13 9h4l4 4v3h-8"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
  file: '<path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8l-5-5z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
  users: '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M18 14a6 6 0 0 1 3.5 6"/>',
  settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>'
}

// Same routes and order as the old top-nav tabs (note: the old nav listed
// Finance before Demand, which differs from the route order in main.js; the nav order wins).
// 'nav.reports' is new: the old Reports tab was hard-coded English text.
const NAV_ITEMS = [
  { to: '/', labelKey: 'nav.overview', icon: 'home' },
  { to: '/inventory', labelKey: 'nav.inventory', icon: 'box' },
  { to: '/orders', labelKey: 'nav.orders', icon: 'cart' },
  { to: '/spending', labelKey: 'nav.finance', icon: 'wallet' },
  { to: '/demand', labelKey: 'nav.demandForecast', icon: 'trend' },
  { to: '/restocking', labelKey: 'nav.restocking', icon: 'truck' },
  { to: '/reports', labelKey: 'nav.reports', icon: 'file' }
]

// Rail monogram from the translated company name: first letter of the first two
// words ("Catalyst Components" -> "CC"). Names without spaces (e.g. Japanese
// "触媒コンポーネンツ") fall back to the first character, since two glyphs of a
// CJK word aren't initials. Array.from splits by code point, not UTF-16 unit.
const monogram = (name) => {
  const words = String(name || '').trim().split(/\s+/).filter(Boolean)
  if (words.length === 0) return ''
  if (words.length === 1) return Array.from(words[0])[0]
  return words.slice(0, 2).map(word => Array.from(word)[0]).join('').toUpperCase()
}

export default {
  name: 'AppSidebar',
  setup() {
    const { t } = useI18n()
    const { isCollapsed, canCollapse, toggleSidebar } = useSidebar()
    return {
      t,
      ICONS,
      NAV_ITEMS,
      monogram,
      isCollapsed,
      canCollapse,
      toggleSidebar
    }
  }
}
</script>

<style scoped>
/* Graphite chrome: the one dark surface in the app, so the nav reads as the
   frame around the work rather than part of it */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  padding: var(--space-5) var(--space-3);
  background: var(--color-sidebar-bg);
  border-right: 1px solid var(--color-sidebar-border);
  /* Sticky + full height so the nav stays put while the content column scrolls */
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  /* Clip sideways: while the grid column animates between 232px and the 64px rail
     the content is briefly wider than the column, and must not spill or scroll */
  overflow-x: hidden;
  z-index: var(--z-sidebar);
}

.sidebar-brand {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: 0 var(--space-3);
}

.brand-name {
  margin: 0;
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  color: var(--color-sidebar-text-active);
  line-height: var(--leading-tight);
}

/* Brand text, nav labels and the toggle label stay on one line so nothing re-wraps
   (and changes height) mid-animation; the ellipsis is only a safety net, both
   locales fit the expanded width */
.brand-full,
.brand-subtitle,
.nav-label {
  display: block;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.brand-subtitle {
  font-size: var(--text-xs);
  color: var(--color-sidebar-text-muted);
}

/* Monogram only exists for the rail; hidden in every other layout */
.brand-monogram {
  display: none;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.nav-item {
  /* Anchors the active marker below */
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  color: var(--color-sidebar-text);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  text-decoration: none;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.nav-item:hover {
  background: var(--color-sidebar-hover);
  color: var(--color-sidebar-text-active);
}

.nav-item:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--color-focus-ring);
}

.nav-item--active,
.nav-item--active:hover {
  background: var(--color-sidebar-active);
  color: var(--color-sidebar-text-active);
}

/* Active marker: a 3px amber bar flush with the sidebar's left edge (offset
   by the sidebar's horizontal padding). Amber here means "you are here" -
   the one attention signal the chrome carries */
.nav-item--active::before {
  content: "";
  position: absolute;
  top: 0;
  bottom: 0;
  left: calc(-1 * var(--space-3));
  width: 3px;
  background: var(--color-attention);
}

.nav-icon {
  flex-shrink: 0;
}

/* margin-top: auto pins the footer (and the toggle) to the bottom of the sidebar */
.sidebar-footer {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.sidebar-footer-slot {
  padding: 0 var(--space-3);
  color: var(--color-sidebar-text-muted);
}

/* Same box as a nav item so the icon sits in the same column as the nav icons,
   but muted: it's a utility control, not a destination */
.sidebar-toggle {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  padding: var(--space-2) var(--space-3);
  border: none;
  border-radius: var(--radius-md);
  background: none;
  color: var(--color-sidebar-text-muted);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  text-align: left;
  cursor: pointer;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.sidebar-toggle:hover {
  background: var(--color-sidebar-hover);
  color: var(--color-sidebar-text-active);
}

.sidebar-toggle:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--color-focus-ring);
}

/* ---- Icon rail (601px and up, when collapsed) ----
   Scoped to above the strip breakpoint so a stale collapsed class can never
   fight the phone strip layout below */
@media (min-width: 601px) {
  .sidebar--collapsed .sidebar-brand {
    align-items: center;
    padding: 0;
  }

  .sidebar--collapsed .brand-monogram {
    /* 40px square = the rail's inner width (64px minus 12px padding each side),
       so it lines up with the nav item boxes below */
    display: flex;
    align-items: center;
    justify-content: center;
    width: var(--space-10);
    height: var(--space-10);
    border: 1px solid var(--color-sidebar-border);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
  }

  .sidebar--collapsed .brand-subtitle {
    display: none;
  }

  /* Containing blocks for the absolutely positioned visually-hidden text below,
     so the 1px boxes stay inside their own element rather than the sidebar */
  .sidebar--collapsed .brand-name,
  .sidebar--collapsed .sidebar-toggle {
    position: relative;
  }

  /* Visually-hidden pattern (not display: none) so screen readers still read the
     heading, link names and toggle name; the links also carry a title tooltip */
  .sidebar--collapsed .brand-full,
  .sidebar--collapsed .nav-label {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }

  /* Centre the 20px icon in the 40px item: no gap (the label is out of flow) and
     8px padding instead of 12px, which would leave too little room. The amber
     ::before bar is unaffected: it is still offset by the sidebar's own padding,
     so it stays flush with the rail's left edge */
  .sidebar--collapsed .nav-item,
  .sidebar--collapsed .sidebar-toggle {
    justify-content: center;
    gap: 0;
    padding: var(--space-2);
  }
}

/* Phones (600px and below): sidebar becomes a horizontal scrolling strip (no drawer,
   no JS). 601-1200px uses the icon rail by default instead (see useSidebar) */
@media (max-width: 600px) {
  .sidebar {
    position: static;
    height: auto;
    flex-direction: row;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-2) var(--space-4);
    border-right: none;
    border-bottom: 1px solid var(--color-sidebar-border);
    overflow-x: auto;
  }

  .sidebar-brand {
    padding: 0;
    flex-shrink: 0;
    /* Keep the brand on one line so the strip stays a single row */
    white-space: nowrap;
  }

  /* The footer holds the collapse toggle, which doesn't apply to the strip */
  .brand-subtitle,
  .sidebar-footer {
    display: none;
  }

  .sidebar-nav {
    flex-direction: row;
  }

  /* flex-shrink: 0 because .nav-label has min-width: 0 (for the rail animation);
     without it the items would shrink and ellipsize instead of the strip scrolling */
  .nav-item {
    flex-shrink: 0;
    white-space: nowrap;
  }

  /* In the strip the marker moves to the bottom edge, flush with the strip's
     bottom (offset by its vertical padding) */
  .nav-item--active::before {
    top: auto;
    bottom: calc(-1 * var(--space-2));
    left: 0;
    right: 0;
    width: auto;
    height: 3px;
  }
}
</style>
