<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && backlogItem" class="modal-overlay" @click="close">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">
              {{ mode === 'view' ? t('purchaseOrder.viewTitle') : t('purchaseOrder.createTitle') }}
            </h3>
            <button type="button" class="close-button" :aria-label="t('common.close')" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <!-- Create mode -->
          <form v-if="mode !== 'view'" class="po-form" @submit.prevent="submit">
            <div class="modal-body">
              <div class="item-summary">
                <div class="item-name">{{ translateProductName(backlogItem.item_name) }}</div>
                <div class="item-meta">
                  <span>{{ t('purchaseOrder.sku') }}: <span class="figure">{{ backlogItem.item_sku }}</span></span>
                  <span>{{ t('purchaseOrder.shortage') }}: <span class="figure">{{ shortage }} {{ t('purchaseOrder.units') }}</span></span>
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label for="po-supplier">{{ t('purchaseOrder.supplier') }}</label>
                  <input
                    id="po-supplier"
                    v-model="form.supplier_name"
                    type="text"
                    class="po-input"
                    :placeholder="t('purchaseOrder.supplierPlaceholder')"
                    required
                  />
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label for="po-quantity">{{ t('purchaseOrder.quantity') }}</label>
                  <input
                    id="po-quantity"
                    v-model="form.quantity"
                    type="number"
                    min="1"
                    step="1"
                    class="po-input"
                    required
                  />
                </div>
                <div class="form-group">
                  <label for="po-unit-cost">{{ t('purchaseOrder.unitCost') }}</label>
                  <input
                    id="po-unit-cost"
                    v-model="form.unit_cost"
                    type="number"
                    min="0"
                    step="0.01"
                    class="po-input"
                    required
                  />
                </div>
                <div class="form-group">
                  <label for="po-delivery">{{ t('purchaseOrder.expectedDelivery') }}</label>
                  <input
                    id="po-delivery"
                    v-model="form.expected_delivery_date"
                    type="date"
                    class="po-input"
                    required
                  />
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label for="po-notes">{{ t('purchaseOrder.notes') }}</label>
                  <textarea
                    id="po-notes"
                    v-model="form.notes"
                    rows="3"
                    class="po-input"
                    :placeholder="t('purchaseOrder.notesPlaceholder')"
                  ></textarea>
                </div>
              </div>

              <div class="line-total">
                <span class="line-total-label">{{ t('purchaseOrder.lineTotal') }}</span>
                <span class="line-total-value">{{ formatMoney(lineTotal) }}</span>
              </div>

              <div v-if="errorMessage" class="error-message" role="alert">{{ errorMessage }}</div>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-secondary" @click="close">{{ t('common.cancel') }}</button>
              <button type="submit" class="btn-primary" :disabled="saving">
                {{ saving ? t('purchaseOrder.saving') : t('purchaseOrder.submit') }}
              </button>
            </div>
          </form>

          <!-- View mode -->
          <template v-else>
            <div class="modal-body">
              <div v-if="loadingPO" class="state-message">{{ t('purchaseOrder.loading') }}</div>
              <div v-else-if="errorMessage" class="error-message" role="alert">{{ errorMessage }}</div>
              <div v-else-if="po" class="info-grid">
                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrder.poNumber') }}</div>
                  <div class="info-value figure">{{ po.id }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrder.status') }}</div>
                  <div class="info-value">
                    <span class="badge" :class="statusClass">{{ statusLabel }}</span>
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrder.supplier') }}</div>
                  <div class="info-value">{{ po.supplier_name }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrder.sku') }}</div>
                  <div class="info-value figure">{{ backlogItem.item_sku }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrder.quantity') }}</div>
                  <div class="info-value figure">{{ po.quantity }} {{ t('purchaseOrder.units') }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrder.unitCost') }}</div>
                  <div class="info-value figure">{{ formatMoney(po.unit_cost) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrder.lineTotal') }}</div>
                  <div class="info-value figure">{{ formatMoney(po.quantity * po.unit_cost) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrder.expectedDelivery') }}</div>
                  <div class="info-value">{{ formatDate(po.expected_delivery_date) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrder.createdDate') }}</div>
                  <div class="info-value">{{ formatDate(po.created_date) }}</div>
                </div>
                <div class="info-item info-item-wide">
                  <div class="info-label">{{ t('purchaseOrder.notes') }}</div>
                  <div class="info-value notes">{{ po.notes || t('purchaseOrder.noNotes') }}</div>
                </div>
              </div>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-secondary" @click="close">{{ t('common.close') }}</button>
            </div>
          </template>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrencyWithDecimals } from '../utils/currency'

const emptyForm = (defaultQuantity) => ({
  supplier_name: '',
  quantity: defaultQuantity > 0 ? defaultQuantity : 1,
  unit_cost: '',
  expected_delivery_date: '',
  notes: ''
})

export default {
  name: 'PurchaseOrderModal',
  props: {
    isOpen: {
      type: Boolean,
      default: false
    },
    backlogItem: {
      type: Object,
      default: null
    },
    mode: {
      type: String,
      default: 'create',
      validator: (value) => ['create', 'view'].includes(value)
    }
  },
  emits: ['close', 'po-created'],
  setup(props, { emit }) {
    const { t, currentLocale, currentCurrency, translateProductName } = useI18n()

    const form = ref(emptyForm(1))
    const saving = ref(false)
    const loadingPO = ref(false)
    const errorMessage = ref(null)
    const fetchedPO = ref(null)

    const shortage = computed(() => {
      if (!props.backlogItem) return 0
      return props.backlogItem.quantity_needed - props.backlogItem.quantity_available
    })

    const lineTotal = computed(() => {
      const qty = Number(form.value.quantity)
      const cost = Number(form.value.unit_cost)
      if (!Number.isFinite(qty) || !Number.isFinite(cost)) return 0
      return qty * cost
    })

    const po = computed(() => props.backlogItem?.purchase_order || fetchedPO.value)

    const statusClass = computed(() => {
      const map = { pending: 'info', ordered: 'info', shipped: 'warning', received: 'success', cancelled: 'danger' }
      return map[po.value?.status?.toLowerCase()] || 'info'
    })

    const statusLabel = computed(() => {
      const status = po.value?.status
      if (!status) return ''
      // API returns capitalised statuses ("Pending"); locale keys are lowercase
      const key = `purchaseOrder.statuses.${status.toLowerCase()}`
      const label = t(key)
      return label === key ? status : label
    })

    const formatMoney = (amount) => {
      const value = Number(amount)
      if (!Number.isFinite(value)) return '-'
      return formatCurrencyWithDecimals(value, currentCurrency.value, 2)
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      // Date-only strings parse as UTC; anchor them to local time to avoid off-by-one days
      const date = new Date(/^\d{4}-\d{2}-\d{2}$/.test(dateString) ? `${dateString}T00:00:00` : dateString)
      if (isNaN(date.getTime())) return 'N/A'
      return date.toLocaleDateString(currentLocale.value === 'ja' ? 'ja-JP' : 'en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    const loadPO = async () => {
      fetchedPO.value = null
      errorMessage.value = null
      const item = props.backlogItem
      if (!item || item.purchase_order || !item.purchase_order_id) {
        if (item && !item.purchase_order) errorMessage.value = t('purchaseOrder.loadFailed')
        return
      }
      loadingPO.value = true
      try {
        fetchedPO.value = await api.getPurchaseOrder(item.purchase_order_id)
      } catch (err) {
        console.error('Failed to load purchase order:', err)
        errorMessage.value = t('purchaseOrder.loadFailed')
      } finally {
        loadingPO.value = false
      }
    }

    // Reset or load whenever the modal opens or targets a different item/mode
    watch(
      () => [props.isOpen, props.backlogItem, props.mode],
      () => {
        if (!props.isOpen || !props.backlogItem) return
        errorMessage.value = null
        saving.value = false
        if (props.mode === 'view') {
          loadPO()
        } else {
          form.value = emptyForm(shortage.value)
        }
      },
      { immediate: true }
    )

    const validate = () => {
      const f = form.value
      const qty = Number(f.quantity)
      const cost = Number(f.unit_cost)
      if (!f.supplier_name.trim()) return t('purchaseOrder.errSupplier')
      if (!Number.isInteger(qty) || qty <= 0) return t('purchaseOrder.errQuantity')
      if (f.unit_cost === '' || !Number.isFinite(cost) || cost < 0) return t('purchaseOrder.errUnitCost')
      if (!f.expected_delivery_date || isNaN(new Date(f.expected_delivery_date).getTime())) {
        return t('purchaseOrder.errDate')
      }
      return null
    }

    const submit = async () => {
      if (saving.value) return
      const validationError = validate()
      if (validationError) {
        errorMessage.value = validationError
        return
      }
      saving.value = true
      errorMessage.value = null
      try {
        const created = await api.createPurchaseOrder({
          backlog_item_id: props.backlogItem.id,
          supplier_name: form.value.supplier_name.trim(),
          quantity: Number(form.value.quantity),
          unit_cost: Number(form.value.unit_cost),
          expected_delivery_date: form.value.expected_delivery_date,
          notes: form.value.notes.trim() || null
        })
        emit('po-created', created)
      } catch (err) {
        console.error('Failed to create purchase order:', err)
        errorMessage.value = t('purchaseOrder.createFailed')
      } finally {
        saving.value = false
      }
    }

    const close = () => {
      emit('close')
    }

    return {
      t,
      translateProductName,
      form,
      saving,
      loadingPO,
      errorMessage,
      shortage,
      lineTotal,
      po,
      statusClass,
      statusLabel,
      formatMoney,
      formatDate,
      submit,
      close
    }
  }
}
</script>

<style scoped>
/* Colors, radii and the overlay shadow come from tokens. Weights top out at 600
   because Plex is only loaded up to 600 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 1rem;
}

.modal-container {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  max-width: 700px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.po-form {
  display: flex;
  flex-direction: column;
  min-height: 0;
  flex: 1;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-title {
  font-size: 1.25rem;
  font-weight: var(--weight-semibold);
  color: var(--color-text);
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  transition: all 0.15s ease;
}

.close-button:hover {
  background: var(--color-surface-muted);
  color: var(--color-text);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.figure {
  font-family: var(--font-figures);
  font-variant-numeric: tabular-nums;
}

.item-summary {
  padding: 1rem 1.25rem;
  background: var(--color-surface-muted);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  margin-bottom: 1.5rem;
}

.item-name {
  font-size: 1.125rem;
  font-weight: var(--weight-semibold);
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.item-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.5rem;
  font-size: 0.875rem;
  color: var(--color-text-muted);
}

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
  min-width: 0;
}

label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.po-input {
  padding: 0.75rem;
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  font-size: 0.95rem;
  font-family: inherit;
  background: var(--color-surface);
  color: var(--color-text);
  transition: border-color 0.2s ease;
}

.po-input:focus {
  outline: none;
  border-color: var(--color-accent);
}

textarea.po-input {
  resize: vertical;
}

.line-total {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: 1rem 0;
  border-top: 1px solid var(--color-border);
}

.line-total-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-muted);
}

.line-total-value {
  font-family: var(--font-figures);
  font-variant-numeric: tabular-nums;
  font-size: 1.5rem;
  font-weight: var(--weight-semibold);
  color: var(--color-text);
}

.error-message {
  padding: 0.75rem 1rem;
  background: var(--color-danger-soft);
  color: var(--color-danger-text);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
}

.state-message {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-muted);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-item-wide {
  grid-column: 1 / -1;
}

.info-label {
  font-size: 0.813rem;
  font-weight: 600;
  color: var(--color-text-muted);
}

.info-value {
  font-size: 0.938rem;
  color: var(--color-text);
  font-weight: 500;
}

.info-value.notes {
  white-space: pre-wrap;
  font-weight: 400;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
}

.badge.info {
  background: var(--color-info-soft);
  color: var(--color-info-text);
}

.badge.warning {
  background: var(--color-warning-soft);
  color: var(--color-warning-text);
}

.badge.success {
  background: var(--color-success-soft);
  color: var(--color-success-text);
}

.badge.danger {
  background: var(--color-danger-soft);
  color: var(--color-danger-text);
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-secondary,
.btn-primary {
  padding: 0.625rem 1.25rem;
  border-radius: var(--radius-md);
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.btn-secondary {
  background: var(--color-surface-muted);
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
}

.btn-secondary:hover {
  background: var(--color-border);
  border-color: var(--color-border-strong);
}

.btn-primary {
  background: var(--color-accent);
  border: 1px solid var(--color-accent);
  color: var(--color-surface);
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-accent-hover);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 600px) {
  .form-row {
    flex-direction: column;
  }
}

/* Modal transition animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}
</style>
