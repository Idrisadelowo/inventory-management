<template>
  <!-- The modifier class only swaps the sidebar column width; the rail itself is
       styled inside AppSidebar from the same shared useSidebar state -->
  <div :class="['app-shell', { 'app-shell--sidebar-collapsed': isCollapsed }]">
    <AppSidebar />

    <div class="app-main">
      <!-- Top bar and filter row share one sticky wrapper so the filters stay pinned
           directly under the top bar without a hard-coded offset (the old FilterBar
           used top: 70px, tied to the old header height) -->
      <div class="app-header">
        <header class="app-topbar">
          <!-- Left side intentionally empty: the four global filters are too wide for
               the top bar, so they get their own row below (FilterBar) -->
          <div class="topbar-start"></div>
          <div class="topbar-end">
            <LanguageSwitcher />
            <ProfileMenu
              @show-profile-details="showProfileDetails = true"
              @show-tasks="showTasks = true"
            />
          </div>
        </header>
        <FilterBar />
      </div>

      <main class="app-content">
        <router-view />
      </main>
    </div>

    <!-- Modals stay outside the grid (and teleport to body), so their fixed
         positioning and z-index are unaffected by the shell -->
    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useSidebar } from './composables/useSidebar'
import AppSidebar from './components/AppSidebar.vue'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

export default {
  name: 'App',
  components: {
    AppSidebar,
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher
  },
  setup() {
    const { currentUser } = useAuth()
    const { isCollapsed } = useSidebar()
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    onMounted(loadTasks)

    return {
      isCollapsed,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask
    }
  }
}
</script>

<style>
/*
 * Global styles: app shell plus the shared classes every view relies on
 * (.page-header, .card, .stat-card, tables, .badge, .loading, .error).
 * All values come from src/styles/tokens.css.
 */

/* Keep the old margin/padding reset: views were written against it, and
   dropping it would bring back browser default margins on every h2/h3/p/ul */
*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-sans);
  font-size: var(--text-sm);
  line-height: var(--leading-normal);
  color: var(--color-text);
  background: var(--color-bg);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Form controls don't inherit the page font by default */
button,
input,
select,
textarea {
  font-family: inherit;
}

/* ---- App shell ---- */

/* Two columns: fixed sidebar + flexible main. minmax(0, 1fr) instead of 1fr
   so a wide table can't force the main column wider than the viewport */
.app-shell {
  display: grid;
  grid-template-columns: var(--sidebar-width) minmax(0, 1fr);
  min-height: 100vh;
  /* Only the column width animates on collapse/expand, so the main content slides
     rather than jumps. Uses the shared fast duration; tokens.css switches it off
     under prefers-reduced-motion */
  transition: grid-template-columns var(--transition-fast);
}

/* Icon rail. Scoped to above the strip breakpoint so this (more specific) selector
   can never override the single-column phone layout below */
@media (min-width: 601px) {
  .app-shell--sidebar-collapsed {
    grid-template-columns: var(--sidebar-width-collapsed) minmax(0, 1fr);
  }
}

/* min-width: 0 pairs with minmax(0, 1fr) above for the same reason */
.app-main {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* Top bar + filter row stick together as one block. Its z-index (above the
   sidebar's) also lifts the language/profile dropdowns, which live inside it */
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

/* 600px and below: single column, sidebar becomes a strip above (see AppSidebar).
   601-1200px keeps two columns with the icon rail instead (see useSidebar).
   The header stops being sticky because the wrapped filter row would otherwise
   pin a tall block over the content on phones */
@media (max-width: 600px) {
  :root {
    --content-padding: var(--space-4);
  }

  .app-shell {
    grid-template-columns: minmax(0, 1fr);
  }

  .app-header {
    position: static;
  }

  .app-topbar {
    flex-wrap: wrap;
  }

  .app-content {
    padding-top: var(--space-6);
  }
}

/* ---- Page header ---- */

.page-header {
  margin-bottom: var(--space-6);
}

.page-header h2 {
  font-size: var(--text-xl);
  font-weight: var(--weight-semibold);
  line-height: var(--leading-tight);
  color: var(--color-text);
  margin-bottom: var(--space-1);
}

.page-header p {
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

/* ---- Stat / KPI cards ---- */

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

/* Flat like every other panel: stat cards aren't interactive, so the old
   hover lift implied a click that does nothing */
.stat-card {
  background: var(--color-surface);
  padding: var(--space-4) var(--space-5);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
}

/* Sentence case, no tracking: labels read as plain words, not chrome */
.stat-label {
  color: var(--color-text-muted);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  margin-bottom: var(--space-1);
}

/* Figures use the condensed cut with fixed-width digits, matching the KPI strip */
.stat-value {
  font-family: var(--font-figures);
  font-size: var(--text-2xl);
  font-weight: var(--weight-semibold);
  line-height: var(--leading-tight);
  color: var(--color-text);
  font-variant-numeric: tabular-nums;
}

/* Status variants: a 3px left accent marks the status (amber only on warning,
   i.e. only when something needs attention). The value keeps its
   status color because views use it to signal meaning (e.g. negative budget) */
.stat-card.success { border-left: 3px solid var(--color-success); }
.stat-card.info { border-left: 3px solid var(--color-info); }
.stat-card.warning { border-left: 3px solid var(--color-warning); }
.stat-card.danger { border-left: 3px solid var(--color-danger); }

.stat-card.success .stat-value { color: var(--color-success); }
.stat-card.info .stat-value { color: var(--color-info); }
/* Warning text uses ochre: raw amber on white fails contrast for a figure */
.stat-card.warning .stat-value { color: var(--color-warning-text); }
.stat-card.danger .stat-value { color: var(--color-danger); }

/* ---- Cards ---- */

.card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  border: 1px solid var(--color-border);
  /* No shadow: panels sit flat on the paper, separated by the rule alone */
  margin-bottom: var(--space-6);
}

/* Wraps so a title plus search box / button / legend never overflows on narrow screens */
.card-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-3) var(--space-4);
  margin-bottom: var(--space-4);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  line-height: var(--leading-tight);
  color: var(--color-text);
}

/* ---- Tables ---- */

/* Wide tables scroll inside their card instead of widening the page */
.table-container {
  overflow-x: auto;
}

/* Bleed tables to the card's left/right edges so the rules span the full
   card width; the cell padding below restores the visual inset */
.card > .table-container {
  margin: 0 calc(-1 * var(--space-6));
}

table {
  width: 100%;
  border-collapse: collapse;
}

/* Header is quiet steel text on the panel white, closed by a single rule;
   no fill band, so the data rows carry the visual weight */
th {
  text-align: left;
  padding: var(--space-2) var(--space-4);
  font-weight: var(--weight-medium);
  color: var(--color-text-muted);
  font-size: var(--text-xs);
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

/* 10px vertical padding: dense enough to scan many rows, still clickable */
td {
  padding: 10px var(--space-4);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
}

/* No border under the last row: the card's bottom padding closes the table */
tbody tr:last-child td {
  border-bottom: none;
}

/* Numeric columns: condensed figures, fixed-width digits, right-aligned so
   place values line up down the column */
th.num,
th.text-right,
td.num,
td.text-right {
  text-align: right;
}

td.num,
td.text-right {
  font-family: var(--font-figures);
  font-variant-numeric: tabular-nums;
}

td strong {
  color: var(--color-text);
  font-weight: var(--weight-semibold);
}

tbody tr {
  transition: background-color var(--transition-fast);
}

tbody tr:hover {
  background: var(--color-surface-muted);
}

/* ---- Badges ---- */

/* One badge shape everywhere (small 4px rectangle, not a pill); only the
   color changes, and it always encodes meaning */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 1px var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  line-height: var(--leading-normal);
  white-space: nowrap;
}

/* Trend and priority badges reuse the status palette with their existing
   meanings: increasing = green, decreasing/high = red, medium = amber,
   stable/low = blue (stable was indigo before; blue keeps "neutral/info") */
.badge.success,
.badge.increasing {
  background: var(--color-success-soft);
  color: var(--color-success-text);
}

.badge.warning,
.badge.medium {
  background: var(--color-warning-soft);
  color: var(--color-warning-text);
}

.badge.danger,
.badge.decreasing,
.badge.high {
  background: var(--color-danger-soft);
  color: var(--color-danger-text);
}

.badge.info,
.badge.stable,
.badge.low {
  background: var(--color-info-soft);
  color: var(--color-info-text);
}

/* ---- Shared focus ring for keyboard users (mouse clicks don't trigger :focus-visible) ---- */

button:focus-visible,
a:focus-visible,
select:focus-visible,
input:focus-visible,
summary:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--color-focus-ring);
}

/* ---- Loading / error / empty ---- */

.loading {
  text-align: center;
  padding: var(--space-12) var(--space-4);
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

.error {
  background: var(--color-danger-soft);
  color: var(--color-danger-text);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  margin: var(--space-4) 0;
  font-size: var(--text-sm);
}

.empty-state {
  text-align: center;
  padding: var(--space-10) var(--space-4);
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}
</style>
