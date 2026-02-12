<template>
    <div class="payments-page animate-fade-in">
        <header class="page-header">
            <div class="container">
                <h1 class="text-thin">{{ $t('payments.title') }}</h1>
                <p class="text-secondary text-light">{{ $t('payments.subtitle') }}</p>
            </div>
        </header>

        <div class="container">
            <!-- Stats Summary -->
            <div class="grid grid-3 mb-12">
                <div class="detail-card">
                    <p class="section-label mb-2">{{ $t('payments.stats.revenue') }}</p>
                    <div class="number-medium text-primary">
                        {{ stats.total_revenue.toLocaleString() }} <span class="smaller-text text-tertiary">USD</span>
                    </div>
                    <p class="smaller-text text-success mt-3 font-medium">↑ 12.5% {{ $t('payments.stats.fromLastMonth')
                        }}</p>
                </div>
                <div class="detail-card">
                    <p class="section-label mb-2">{{ $t('payments.stats.loans') }}</p>
                    <div class="number-medium text-primary">{{ stats.active_loans }}</div>
                    <p class="smaller-text text-tertiary mt-3">{{ $t('payments.stats.repaid') }}</p>
                </div>
                <div class="detail-card">
                    <p class="section-label mb-2">{{ $t('payments.stats.pending') }}</p>
                    <div class="number-medium text-error">
                        {{ stats.pending_payments.toLocaleString() }} <span
                            class="smaller-text text-tertiary">USD</span>
                    </div>
                    <p class="smaller-text text-tertiary mt-3">{{ $t('payments.stats.endOfWeek') }}</p>
                </div>
            </div>

            <!-- Transaction List -->
            <div class="card no-padding overflow-hidden border-light shadow-sm">
                <div class="table-responsive">
                    <table class="admin-table">
                        <thead>
                            <tr>
                                <th class="pl-8">{{ $t('payments.table.id') }}</th>
                                <th>{{ $t('payments.table.client') }}</th>
                                <th>{{ $t('payments.table.vehicle') }}</th>
                                <th>{{ $t('payments.table.amount') }}</th>
                                <th>{{ $t('payments.table.type') }}</th>
                                <th>{{ $t('payments.table.status') }}</th>
                                <th class="text-right pr-8">{{ $t('payments.table.date') }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-if="loading" v-for="i in 5" :key="i">
                                <td colspan="7" class="py-12 text-center text-tertiary">{{ $t('payments.updating') }}
                                </td>
                            </tr>
                            <tr v-else v-for="item in payments" :key="item.id" class="premium-row clickable-row">
                                <td class="pl-8 py-5">
                                    <code class="id-badge-minimal">#{{ item.id.substring(0, 8) }}</code>
                                </td>
                                <td>
                                    <div class="font-medium text-primary">{{ item.client_name }}</div>
                                </td>
                                <td class="text-secondary smaller-text font-medium">{{ item.car_name }}</td>
                                <td>
                                    <div class="font-bold"
                                        :class="item.type === 'income' ? 'text-success' : 'text-primary'">
                                        {{ item.type === 'income' ? '+' : '' }}{{ item.amount.toLocaleString() }}
                                        <span class="smaller-text text-tertiary font-normal ml-1">USD</span>
                                    </div>
                                </td>
                                <td><span class="type-badge" :class="item.type">{{ formatType(item.type) }}</span></td>
                                <td><span class="badge" :class="item.status">{{ formatStatus(item.status) }}</span></td>
                                <td class="text-right pr-8 text-secondary smaller-text font-medium">{{
                                    formatDate(item.date) }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="spacer"></div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const { t, locale } = useI18n()
const { getPayments, getPaymentStats } = useApi()

const payments = ref<any[]>([])
const stats = ref({
    total_revenue: 450000000,
    active_loans: 24,
    pending_payments: 15200000
})
const loading = ref(true)

const fetchData = async () => {
    loading.value = true
    try {
        const [payRes, statRes]: any = await Promise.all([
            getPayments({ limit: 100 }),
            getPaymentStats()
        ])
        payments.value = payRes.items || []
        if (statRes) {
            stats.value = {
                total_revenue: statRes.total_revenue || 0,
                active_loans: statRes.active_loans_count || 0,
                pending_payments: statRes.pending_total || 0
            }
        }
    } catch (err) {
        payments.value = []
    } finally {
        loading.value = false
    }
}

const formatDate = (d: string) => new Date(d).toLocaleDateString(locale.value, { day: '2-digit', month: '2-digit', year: 'numeric' })
const formatType = (type: string) => t(`payments.type.${type?.toLowerCase() || 'income'}`)
const formatStatus = (status: string) => t(`payments.status.${status?.toLowerCase() || 'pending'}`)

onMounted(fetchData)

definePageMeta({ layout: false })
</script>

<style scoped>
.page-header {
    padding: var(--spacing-xl) 0 var(--spacing-lg);
}

.detail-card {
    background: var(--color-bg-primary);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: 2rem;
    transition: var(--transition);
}

.detail-card:hover {
    border-color: var(--color-text-tertiary);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.02);
}

.section-label {
    text-transform: uppercase;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: var(--color-text-tertiary);
    display: block;
}

.id-badge-minimal {
    font-family: monospace;
    font-size: 0.75rem;
    color: var(--color-text-tertiary);
    background: var(--color-bg-secondary);
    padding: 2px 6px;
    border-radius: 4px;
}

.type-badge {
    font-size: 0.65rem;
    padding: 2px 8px;
    border-radius: 4px;
    text-transform: uppercase;
    font-weight: 800;
    letter-spacing: 0.05em;
    border: 1px solid transparent;
}

.type-badge.income {
    background: rgba(16, 185, 129, 0.05);
    color: var(--color-success);
    border-color: rgba(16, 185, 129, 0.1);
}

.type-badge.refund {
    background: rgba(239, 68, 68, 0.05);
    color: var(--color-error);
    border-color: rgba(239, 68, 68, 0.1);
}

.badge.completed {
    background: rgba(16, 185, 129, 0.08);
    color: var(--color-success);
    border-color: var(--color-success);
}

.badge.failed {
    background: rgba(239, 68, 68, 0.08);
    color: var(--color-error);
    border-color: var(--color-error);
}

.border-light {
    border-color: var(--color-border-light);
}

.pl-8 {
    padding-left: 2.5rem;
}

.pr-8 {
    padding-right: 2.5rem;
}

.py-5 {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
}

.mb-12 {
    margin-bottom: 3rem;
}

.spacer {
    height: 8rem;
}

@media (max-width: 768px) {
    .header-actions {
        width: 100%;
    }

    .header-actions .btn {
        flex-grow: 1;
    }

    .grid-3 {
        grid-template-columns: 1fr;
    }

    .metric-card {
        padding: 1.25rem;
    }
}
</style>
