<!--
  TEMPLATE NOTES (delete this block when copying):
  Copy to src/components/AppSidebar.vue and adapt:
  - Fill NAV_ITEMS from the audit: nav order, same label source.
  - If the app has no i18n, replace `t(...)` calls with plain strings.
  - Script style: follow the project's CLAUDE.md, then the dominant style in existing views.
  - Use <h1> for the brand only if the old header's brand was the page's <h1>; otherwise a <span>.
  Depends on tokens from design-tokens.css.
-->
<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <!-- Brand text (or logo <img>) moved here from the old top header -->
      <!-- t() is called in the template, not setup(), so labels re-render when the locale changes -->
      <h1 class="brand-name">{{ t('nav.companyName') }}</h1>
      <span class="brand-subtitle">{{ t('nav.subtitle') }}</span>
    </div>

    <nav class="sidebar-nav" aria-label="Main">
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

    <div v-if="$slots.footer" class="sidebar-footer">
      <slot name="footer" />
    </div>
  </aside>
</template>

<script>
import { useI18n } from '../composables/useI18n'

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

// Fill from the audit: same routes and order as the old nav
const NAV_ITEMS = [
  { to: '/', labelKey: 'nav.overview', icon: 'home' }
  // { to: '/inventory', labelKey: 'nav.inventory', icon: 'box' },
]

export default {
  name: 'AppSidebar',
  setup() {
    const { t } = useI18n()
    return {
      t,
      ICONS,
      NAV_ITEMS
    }
  }
}
</script>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  padding: var(--space-5) var(--space-3);
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  /* Sticky + full height so the nav stays put while the content column scrolls */
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
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
  font-weight: var(--weight-bold);
  color: var(--color-text);
  line-height: var(--leading-tight);
}

.brand-subtitle {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  text-decoration: none;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.nav-item:hover {
  background: var(--color-surface-muted);
  color: var(--color-text);
}

.nav-item:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--color-focus-ring);
}

.nav-item--active,
.nav-item--active:hover {
  background: var(--color-accent-soft);
  color: var(--color-accent-text);
}

.nav-icon {
  flex-shrink: 0;
}

.sidebar-footer {
  margin-top: auto;
  padding: 0 var(--space-3);
}

/* Narrow screens: sidebar becomes a horizontal scrolling strip (no drawer, no JS) */
@media (max-width: 900px) {
  .sidebar {
    position: static;
    height: auto;
    flex-direction: row;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-2) var(--space-4);
    border-right: none;
    border-bottom: 1px solid var(--color-border);
    overflow-x: auto;
  }

  .sidebar-brand {
    padding: 0;
    flex-shrink: 0;
  }

  .brand-subtitle,
  .sidebar-footer {
    display: none;
  }

  .sidebar-nav {
    flex-direction: row;
  }

  .nav-item {
    white-space: nowrap;
  }
}
</style>
