<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div class="card budget-card">
      <div class="budget-header">
        <label for="restock-budget" class="budget-label">{{ t('restocking.budget') }}</label>
        <div class="budget-value">{{ formatCurrency(budget, currentCurrency) }}</div>
      </div>
      <input
        id="restock-budget"
        v-model.number="budget"
        type="range"
        class="budget-slider"
        :min="BUDGET_MIN"
        :max="BUDGET_MAX"
        :step="BUDGET_STEP"
        :aria-valuetext="formatCurrency(budget, currentCurrency)"
      />
      <div class="budget-scale">
        <span>{{ formatCurrency(BUDGET_MIN, currentCurrency) }}</span>
        <span>{{ formatCurrency(BUDGET_MAX, currentCurrency) }}</span>
      </div>
      <p class="budget-hint">{{ t('restocking.budgetHint') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="loadError && !recommendations" class="error">{{ loadError }}</div>
    <div v-else-if="recommendations">
      <div v-if="successOrder" class="banner banner-success" role="status">
        <span>{{ t('restocking.orderPlaced', { orderNumber: successOrder.order_number, days: successOrder.lead_time_days }) }}</span>
        <router-link to="/orders" class="banner-link">{{ t('restocking.viewOrders') }}</router-link>
      </div>
      <div v-if="submitError" class="error" role="alert">{{ submitError }}</div>
      <!-- A failed re-fetch keeps the last good table on screen, so surface the error above it -->
      <div v-if="loadError" class="error" role="alert">{{ loadError }}</div>

      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.selectedTotal') }}</div>
          <div class="stat-value">{{ formatCurrency(selectedTotal, currentCurrency) }}</div>
          <div class="stat-sub">{{ t('restocking.itemsSelected', { count: selectedItems.length }) }}</div>
        </div>
        <div :class="['stat-card', remainingBudget < 0 ? 'danger' : 'success']">
          <div class="stat-label">{{ t('restocking.remainingBudget') }}</div>
          <div class="stat-value">{{ formatCurrency(remainingBudget, currentCurrency) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.estimatedLeadTime') }}</div>
          <div class="stat-value">
            {{ selectedItems.length ? t('restocking.days', { count: estimatedLeadTime }) : '-' }}
          </div>
        </div>
      </div>

      <div :class="['card', { refreshing }]" :aria-busy="refreshing">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendations') }} ({{ items.length }})</h3>
          <button
            type="button"
            class="place-order-btn"
            :disabled="!canSubmit"
            @click="placeOrder"
          >
            {{ submitting ? t('restocking.placingOrder') : t('restocking.placeOrder') }}
          </button>
        </div>

        <div v-if="items.length === 0" class="empty-state">{{ t('restocking.noRecommendations') }}</div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th class="col-select">{{ t('restocking.table.select') }}</th>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.itemName') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
                <th class="num">{{ t('restocking.table.forecastedDemand') }}</th>
                <th class="num">{{ t('restocking.table.quantity') }}</th>
                <th class="num">{{ t('restocking.table.unitCost') }}</th>
                <th class="num">{{ t('restocking.table.lineTotal') }}</th>
                <th class="num">{{ t('restocking.table.leadTime') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in items"
                :key="item.item_sku"
                :class="{ unselected: !selectedSkus.has(item.item_sku) }"
              >
                <td class="col-select">
                  <input
                    type="checkbox"
                    :checked="selectedSkus.has(item.item_sku)"
                    :aria-label="`${t('restocking.table.select')} ${item.item_name}`"
                    @change="toggleItem(item.item_sku)"
                  />
                </td>
                <td><strong>{{ item.item_sku }}</strong></td>
                <td>{{ translateProductName(item.item_name) }}</td>
                <td>
                  <span :class="['badge', item.trend]">{{ t(`trends.${item.trend}`) }}</span>
                </td>
                <td class="num">{{ item.forecasted_demand }}</td>
                <td class="num"><strong>{{ item.recommended_quantity }}</strong></td>
                <td class="num">{{ formatCurrencyWithDecimals(item.unit_cost, currentCurrency, 2) }}</td>
                <td class="num"><strong>{{ formatCurrencyWithDecimals(item.line_total, currentCurrency, 2) }}</strong></td>
                <td class="num">{{ t('restocking.days', { count: item.lead_time_days }) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrency, formatCurrencyWithDecimals } from '../utils/currency'

// A full restock of every forecast item costs roughly $65K, so the slider tops out just above that
const BUDGET_MIN = 0
const BUDGET_MAX = 70000
const BUDGET_STEP = 500
const DEFAULT_BUDGET = 25000
const FETCH_DEBOUNCE_MS = 300

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency, translateProductName } = useI18n()

    const budget = ref(DEFAULT_BUDGET)
    const recommendations = ref(null)
    // Full-page loading only for the first fetch; later fetches set `refreshing` and keep the table visible
    const loading = ref(true)
    const refreshing = ref(false)
    const loadError = ref(null)
    const selectedSkus = ref(new Set())

    const submitting = ref(false)
    const submitError = ref(null)
    const successOrder = ref(null)

    let debounceTimer = null
    // Each fetch takes a ticket; only the latest ticket may write results. Without this, a slow
    // response for an old slider position could land after a newer one and show stale items.
    let latestRequestId = 0

    const items = computed(() => recommendations.value?.items ?? [])

    const selectedItems = computed(() => {
      return items.value.filter(item => selectedSkus.value.has(item.item_sku))
    })

    const selectedTotal = computed(() => {
      return selectedItems.value.reduce((sum, item) => sum + item.line_total, 0)
    })

    // Measured against the budget the recommendations were computed for, so the figure stays
    // consistent with the table while a newer fetch is still in flight
    const remainingBudget = computed(() => {
      const appliedBudget = recommendations.value?.budget ?? budget.value
      return appliedBudget - selectedTotal.value
    })

    // Items ship together as one order, so the slowest supplier sets the delivery estimate
    const estimatedLeadTime = computed(() => {
      return selectedItems.value.reduce((max, item) => Math.max(max, item.lead_time_days), 0)
    })

    // Blocked while refreshing so we never submit rows that belong to a budget the user has moved away from
    const canSubmit = computed(() => {
      return selectedItems.value.length > 0 && !submitting.value && !refreshing.value
    })

    const loadRecommendations = async () => {
      const requestId = ++latestRequestId
      if (recommendations.value) {
        refreshing.value = true
      }
      try {
        const data = await api.getRestockRecommendations(budget.value)
        if (requestId !== latestRequestId) return
        recommendations.value = data
        // New recommendations replace the previous selection; everything starts ticked
        selectedSkus.value = new Set(data.items.map(item => item.item_sku))
        loadError.value = null
      } catch (err) {
        if (requestId !== latestRequestId) return
        loadError.value = t('restocking.loadError')
        console.error('Load restock recommendations error:', err)
      } finally {
        // Leave the flags alone if a newer request now owns them
        if (requestId === latestRequestId) {
          loading.value = false
          refreshing.value = false
        }
      }
    }

    const toggleItem = (sku) => {
      // Replace the Set rather than mutating it so the change is obvious to dependent computeds
      const next = new Set(selectedSkus.value)
      if (next.has(sku)) {
        next.delete(sku)
      } else {
        next.add(sku)
      }
      selectedSkus.value = next
    }

    const clearBanners = () => {
      submitError.value = null
      successOrder.value = null
    }

    const placeOrder = async () => {
      if (!canSubmit.value) return
      clearBanners()
      submitting.value = true
      try {
        const order = await api.createRestockOrder({
          budget: recommendations.value.budget,
          items: selectedItems.value.map(item => ({
            item_sku: item.item_sku,
            quantity: item.recommended_quantity
          }))
        })
        successOrder.value = order
        loadRecommendations()
      } catch (err) {
        submitError.value = err.response?.data?.detail || t('restocking.submitError')
        console.error('Create restock order error:', err)
      } finally {
        submitting.value = false
      }
    }

    // Dragging the slider fires many input events; wait for it to settle before hitting the API
    watch(budget, () => {
      clearBanners()
      clearTimeout(debounceTimer)
      debounceTimer = setTimeout(loadRecommendations, FETCH_DEBOUNCE_MS)
    })

    onMounted(loadRecommendations)

    onBeforeUnmount(() => {
      clearTimeout(debounceTimer)
    })

    return {
      t,
      currentCurrency,
      translateProductName,
      formatCurrency,
      formatCurrencyWithDecimals,
      BUDGET_MIN,
      BUDGET_MAX,
      BUDGET_STEP,
      budget,
      recommendations,
      loading,
      refreshing,
      loadError,
      items,
      selectedSkus,
      selectedItems,
      selectedTotal,
      remainingBudget,
      estimatedLeadTime,
      canSubmit,
      submitting,
      submitError,
      successOrder,
      toggleItem,
      placeOrder
    }
  }
}
</script>

<style scoped>
.budget-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: var(--space-4);
}

.budget-label {
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  color: var(--color-text-muted);
}

/* Condensed readout with fixed-width digits so the figure doesn't jitter
   while the slider moves */
.budget-value {
  font-family: var(--font-figures);
  font-size: var(--text-2xl);
  font-weight: var(--weight-semibold);
  line-height: var(--leading-tight);
  color: var(--color-text);
  font-variant-numeric: tabular-nums;
}

.budget-slider {
  width: 100%;
  height: 6px;
  margin: var(--space-2) 0;
  accent-color: var(--color-accent);
  cursor: pointer;
}

/* Outline (not the global box-shadow ring) because a range input's box is only 6px tall */
.budget-slider:focus-visible {
  box-shadow: none;
  outline: 2px solid var(--color-focus-ring);
  outline-offset: 4px;
}

.budget-scale {
  display: flex;
  justify-content: space-between;
  font-variant-numeric: tabular-nums;
  font-size: var(--text-xs);
  color: var(--color-text-subtle);
}

.budget-hint {
  margin-top: var(--space-3);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.stat-sub {
  margin-top: 0.375rem;
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4);
  margin: var(--space-4) 0;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
}

.banner-success {
  background: var(--color-success-soft);
  color: var(--color-success-text);
}

.banner-link {
  color: var(--color-success-text);
  font-weight: var(--weight-semibold);
  white-space: nowrap;
}

.banner-link:hover {
  text-decoration: none;
}

/* Dim rather than hide while re-fetching so the layout doesn't jump on every slider move */
.card.refreshing .table-container,
.card.refreshing .empty-state {
  opacity: 0.5;
  transition: opacity 0.15s ease;
}

.place-order-btn {
  height: 36px;
  padding: 0 var(--space-4);
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  cursor: pointer;
  transition: background var(--transition-fast), opacity var(--transition-fast);
}

.place-order-btn:hover:not(:disabled) {
  background: var(--color-accent-hover);
}

.place-order-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.col-select {
  width: 70px;
  text-align: center;
}

.col-select input {
  width: 16px;
  height: 16px;
  accent-color: var(--color-accent);
  cursor: pointer;
}

/* Alignment repeated here for the header cells; the condensed face for
   numeric cells comes from the global td.num rule in App.vue */
.num {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

tr.unselected td:not(.col-select) {
  color: var(--color-text-subtle);
}

</style>
