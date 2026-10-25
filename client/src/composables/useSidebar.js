import { ref, computed, getCurrentScope, onScopeDispose } from 'vue'

// Shared sidebar state (singleton pattern, like useFilters): App.vue sizes the grid
// column and AppSidebar.vue renders the rail, so both must read the same values.

const STORAGE_KEY = 'sidebar-collapsed'

// Breakpoints. Keep in sync with the CSS media queries in App.vue and AppSidebar.vue:
// <= 600px the sidebar is a horizontal strip (collapse does not apply),
// 601-1200px it defaults to the icon rail, > 1200px it defaults to expanded.
const PHONE_QUERY = '(max-width: 600px)'
const RAIL_QUERY = '(max-width: 1200px)'

const hasWindow = typeof window !== 'undefined' && typeof window.matchMedia === 'function'

// localStorage can throw (Safari private mode, storage disabled by policy), so every
// access is wrapped and failure just means "no remembered choice"
const readStoredPreference = () => {
  try {
    const value = window.localStorage.getItem(STORAGE_KEY)
    if (value === 'true') return true
    if (value === 'false') return false
  } catch (err) {
    // Ignore: fall back to the width-based default
  }
  return null
}

const writeStoredPreference = (value) => {
  try {
    window.localStorage.setItem(STORAGE_KEY, String(value))
  } catch (err) {
    // Ignore: the choice still applies for this session, it just isn't remembered
  }
}

const phoneMql = hasWindow ? window.matchMedia(PHONE_QUERY) : null
const railMql = hasWindow ? window.matchMedia(RAIL_QUERY) : null

// Read the media queries synchronously at module load (before the first render) so
// the shell paints at the right width straight away instead of animating into place
const isPhone = ref(phoneMql ? phoneMql.matches : false)
const isRailWidth = ref(railMql ? railMql.matches : false)

// null = the user has never clicked the toggle
const userPreference = ref(hasWindow ? readStoredPreference() : null)

const onPhoneChange = (event) => { isPhone.value = event.matches }
const onRailChange = (event) => { isRailWidth.value = event.matches }

// Old Safari (< 14) only has the deprecated addListener/removeListener on MediaQueryList
const listen = (mql, handler) => {
  if (mql.addEventListener) mql.addEventListener('change', handler)
  else mql.addListener(handler)
}
const unlisten = (mql, handler) => {
  if (mql.removeEventListener) mql.removeEventListener('change', handler)
  else mql.removeListener(handler)
}

// Several components call useSidebar(); the listeners are shared, so they are
// attached on the first user and removed when the last one is unmounted
let subscribers = 0

const subscribe = () => {
  if (!hasWindow) return
  if (subscribers === 0) {
    // Re-sync in case the viewport changed while nothing was listening
    isPhone.value = phoneMql.matches
    isRailWidth.value = railMql.matches
    listen(phoneMql, onPhoneChange)
    listen(railMql, onRailChange)
  }
  subscribers++
}

const unsubscribe = () => {
  if (!hasWindow || subscribers === 0) return
  subscribers--
  if (subscribers === 0) {
    unlisten(phoneMql, onPhoneChange)
    unlisten(railMql, onRailChange)
  }
}

// Precedence:
//   1. Phones (<= 600px): never collapsed - the strip layout has its own labels.
//   2. An explicit toggle click (remembered in localStorage) wins over the width default,
//      on any non-phone width, until the user clicks again.
//   3. Otherwise the width decides: icon rail at 601-1200px, expanded above 1200px.
const isCollapsed = computed(() => {
  if (isPhone.value) return false
  if (userPreference.value !== null) return userPreference.value
  return isRailWidth.value
})

// The toggle is meaningless in the strip layout, so the UI can hide it
const canCollapse = computed(() => !isPhone.value)

const toggleSidebar = () => {
  // Flip what the user currently sees (which may be the width default), then pin it
  const next = !isCollapsed.value
  userPreference.value = next
  writeStoredPreference(next)
}

export function useSidebar() {
  // Tie listener lifetime to the calling component's setup scope; outside a
  // component (no scope) there is nothing to clean up against, so don't attach
  if (getCurrentScope()) {
    subscribe()
    onScopeDispose(unsubscribe)
  }

  return {
    // Computed
    isCollapsed,
    canCollapse,

    // Methods
    toggleSidebar
  }
}
