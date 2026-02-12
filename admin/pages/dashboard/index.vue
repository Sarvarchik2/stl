<template>
    <div class="dashboard-page animate-fade-in">
        <header class="page-header">
            <div class="container">
                <div class="flex-between dashboard-header">
                    <div class="header-info">
                        <h1 class="text-thin">{{ $t('dashboard.title') }}</h1>
                        <p class="text-secondary text-light">{{ $t('dashboard.subtitle') }}</p>
                    </div>
                    <div class="header-actions flex gap-3 items-center">
                        <div class="filter-group">
                            <select v-model="selectedPeriod" @change="fetchData" class="select-filter">
                                <option value="all">{{ $t('common.allTime') }}</option>
                                <option value="month">{{ $t('common.thisMonth') }}</option>
                                <option value="week">{{ $t('common.thisWeek') }}</option>
                                <option value="day">{{ $t('common.today') }}</option>
                            </select>
                        </div>
                        <button class="btn btn-outline btn-sm hover-accent" @click="fetchData">
                            <span class="mr-2">↻</span>
                        </button>
                        <NuxtLink to="/applications"
                            class="btn btn-primary btn-sm shadow-lg flex items-center justify-center text-white no-underline">
                            <span class="mr-2">+</span> {{ $t('applications.newApplication') }}
                        </NuxtLink>
                    </div>
                </div>
            </div>
        </header>

        <div class="container">
            <!-- Priority Metrics Cards -->
            <div class="metrics-row mb-10">
                <div class="metrics-grid-flexible">
                    <!-- Turnover (Volume) -->
                    <div v-if="showFinancials" class="metric-card glass-card shadow-sm">
                        <div class="flex-between mb-4">
                            <label class="section-label">{{ $t('dashboard.turnover') }}</label>
                            <span class="trend-tag success">USD</span>
                        </div>
                        <div class="metric-value text-primary font-bold">
                            {{ formatMoney(stats.total_volume_usd) }}
                        </div>
                        <div class="metric-footer mt-2">
                            <span class="smaller-text text-tertiary">Gross Sales</span>
                        </div>
                    </div>

                    <!-- Profit (Income) -->
                    <div v-if="showFinancials" class="metric-card glass-card shadow-sm">
                        <div class="flex-between mb-4">
                            <label class="section-label">{{ $t('dashboard.income') }}</label>
                            <span class="trend-tag success">USD</span>
                        </div>
                        <div class="metric-value text-success font-bold">
                            +{{ formatMoney(stats.total_profit_usd || 0) }}
                        </div>
                        <div class="metric-footer mt-2">
                            <span class="smaller-text text-tertiary">Net Margin</span>
                        </div>
                    </div>

                    <!-- Staff-Specific Status Highlights (Replacement for financials) -->
                    <div v-if="!hasRole('admin') && hasRole('operator')"
                        class="metric-card glass-card shadow-sm border-accent-light">
                        <div class="flex-between mb-4">
                            <label class="section-label">{{ $t('applications.status.new') }}</label>
                            <span class="status-dot-mini accent animate-pulse"></span>
                        </div>
                        <div class="metric-value text-accent font-bold">
                            {{ getStatusCount('new') }}
                        </div>
                        <div class="metric-footer mt-2">
                            <span class="smaller-text text-tertiary">Waiting for contact</span>
                        </div>
                    </div>

                    <div v-if="!hasRole('admin') && hasRole('manager')" class="metric-card glass-card shadow-sm">
                        <div class="flex-between mb-4">
                            <label class="section-label font-bold text-accent">{{ $t('applications.filters.confirmed')
                            }}</label>
                            <span class="badge badge-sm badge-outline">Ready</span>
                        </div>
                        <div class="metric-value text-primary font-bold">
                            {{ getStatusCount('confirmed') }}
                        </div>
                        <div class="metric-footer mt-2">
                            <span class="smaller-text text-tertiary">Needs processing</span>
                        </div>
                    </div>

                    <div v-if="!hasRole('admin') && hasRole('manager')" class="metric-card glass-card shadow-sm">
                        <div class="flex-between mb-4">
                            <label class="section-label">{{ $t('applications.status.contract_signed') }}</label>
                            <span class="trend-tag info">Doc</span>
                        </div>
                        <div class="metric-value text-primary font-bold">
                            {{ getStatusCount('contract_signed') }}
                        </div>
                        <div class="metric-footer mt-2">
                            <span class="smaller-text text-tertiary">{{ $t('dashboard.requireAttention') }}</span>
                        </div>
                    </div>

                    <!-- Personal Performance (Backend Driven) -->
                    <div v-if="stats.personal_performance && stats.personal_performance.count > 0 && !hasRole('admin')"
                        class="metric-card glass-card shadow-sm border-accent-light">
                        <div class="flex-between mb-4">
                            <label class="section-label font-bold text-accent">
                                {{ stats.personal_performance.label === 'processed' ?
                                    $t('applications.filters.confirmed') : $t('applications.status.delivered') }}
                            </label>
                            <span class="trend-tag success">★</span>
                        </div>
                        <div class="metric-value text-success font-bold">
                            {{ stats.personal_performance.count }}
                        </div>
                        <div class="metric-footer mt-2">
                            <span class="smaller-text text-tertiary">
                                {{ stats.personal_performance.label === 'processed' ? $t('dashboard.processed') :
                                $t('dashboard.delivered') }}
                                ({{ selectedPeriod === 'all' ? $t('common.allTime') : selectedPeriod }})
                            </span>
                        </div>
                    </div>

                    <div v-if="!hasRole('admin') && hasRole('manager')" class="metric-card glass-card shadow-sm">
                        <div class="flex-between mb-4">
                            <label class="section-label">{{ $t('applications.status.paid') }}</label>
                            <span class="trend-tag success">$</span>
                        </div>
                        <div class="metric-value text-success font-bold">
                            {{ getStatusCount('paid') }}
                        </div>
                        <div class="metric-footer mt-2">
                            <span class="smaller-text text-tertiary">Ready for logistics</span>
                        </div>
                    </div>

                    <div v-if="!hasRole('admin') && hasRole('manager')" class="metric-card glass-card shadow-sm">
                        <div class="flex-between mb-4">
                            <label class="section-label">{{ $t('applications.status.delivered') }}</label>
                            <span class="trend-tag success">Done</span>
                        </div>
                        <div class="metric-value text-primary font-bold">
                            {{ getStatusCount('delivered') + getStatusCount('completed') }}
                        </div>
                        <div class="metric-footer mt-2">
                            <span class="smaller-text text-tertiary">Completed deals</span>
                        </div>
                    </div>

                    <div v-if="!hasRole('admin') && hasRole('operator')" class="metric-card glass-card shadow-sm">
                        <div class="flex-between mb-4">
                            <label class="section-label">{{ $t('applications.contactStatus') }}: {{
                                $t('applications.contactStatuses.not_touched') }}</label>
                            <span class="status-dot-mini warning"></span>
                        </div>
                        <div class="metric-value text-primary font-bold">
                            {{ getContactCount('not_touched') }}
                        </div>
                        <div class="metric-footer mt-2">
                            <span class="smaller-text text-tertiary">New leads</span>
                        </div>
                    </div>

                    <div v-if="!hasRole('admin') && hasRole('operator')" class="metric-card glass-card shadow-sm">
                        <div class="flex-between mb-4">
                            <label class="section-label">{{ $t('applications.contactStatuses.callback') }}</label>
                            <span class="trend-tag info">Call</span>
                        </div>
                        <div class="metric-value text-primary font-bold">
                            {{ getContactCount('callback') }}
                        </div>
                        <div class="metric-footer mt-2">
                            <span class="smaller-text text-tertiary">Schedule calls</span>
                        </div>
                    </div>

                    <!-- Pipeline Health -->
                    <div class="metric-card glass-card shadow-sm">
                        <div class="flex-between mb-4">
                            <label class="section-label">{{ $t('applications.filters.inProgress') }}</label>
                            <div class="status-indicator active"></div>
                        </div>
                        <div class="metric-value text-primary font-bold">
                            {{ stats.in_pipeline }}
                            <span class="smaller-text text-tertiary">
                                {{ ($t('dashboard.totalApplications') || '').split(' ').pop() }}
                            </span>
                        </div>
                        <div class="metric-footer mt-4">
                            <div class="progress-mini">
                                <div class="progress-fill accent"
                                    :style="{ width: stats.total_applications ? (stats.in_pipeline / stats.total_applications * 100) + '%' : '0%' }">
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Inventory Flow -->
                    <div v-if="!hasRole('operator')" class="metric-card glass-card shadow-sm">
                        <div class="flex-between mb-4">
                            <label class="section-label">{{ $t('nav.cars') }}</label>
                            <span class="trend-tag neutral">{{ $t('cars.statuses.available') }}</span>
                        </div>
                        <div class="metric-value text-primary font-bold">
                            {{ stats.fleet_count }}
                        </div>
                        <div class="metric-footer mt-4">
                            <div class="flex items-center gap-2 mb-1">
                                <div class="status-dot-mini success"></div>
                                <span class="smaller-text text-secondary">{{ $t('cars.statuses.available') }}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Conversion Impact -->
                    <div class="metric-card glass-card shadow-sm">
                        <div class="flex-between mb-4">
                            <label class="section-label">{{ $t('dashboard.quickStats') }}</label>
                        </div>
                        <div class="metric-value text-primary font-bold">
                            {{ stats.conversion_rate }} <span class="smaller-text text-tertiary">%</span>
                        </div>
                        <div class="metric-footer mt-4 flex items-center justify-between">
                            <span class="smaller-text text-tertiary">{{ $t('dashboard.completedDeals') }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Operational Insights Section -->
        <div class="insights-layout">
            <!-- Left: Detailed Activity & Tables -->
            <div class="insights-main">
                <div class="flex-between mb-4 px-2">
                    <h3 class="m-0 text-thin">{{ $t('dashboard.recentActivity') }}</h3>
                    <NuxtLink to="/applications" class="btn btn-ghost smaller-text font-bold text-accent hover-accent">
                        {{
                            ($t('common.all') || '').toString().toUpperCase() }} ↗
                    </NuxtLink>
                </div>

                <div class="card no-padding overflow-hidden border-light shadow-sm">
                    <table class="admin-table">
                        <thead>
                            <tr>
                                <th class="pl-8">{{ $t('common.user') }}</th>
                                <th>{{ $t('common.action') }}</th>
                                <th>{{ $t('common.target') }}</th>
                                <th class="pr-8 text-right">{{ $t('common.date') }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-if="loading" v-for="i in 3" :key="i">
                                <td colspan="4" class="py-12 text-center text-tertiary smaller-text">
                                    {{ $t('common.loading') }}
                                </td>
                            </tr>
                            <tr v-else-if="!stats.recent_activity || stats.recent_activity.length === 0">
                                <td colspan="4" class="py-12 text-center text-tertiary smaller-text">
                                    {{ $t('common.noData') }}
                                </td>
                            </tr>
                            <tr v-else v-for="log in stats.recent_activity" :key="log.id" class="premium-row">
                                <td class="pl-8 py-4">
                                    <div class="font-bold text-primary">{{ log.user_id ? $t('users.roles.admin') :
                                        'System' }}</div>
                                    <div class="smaller-text text-tertiary monospace">#{{ log.user_id ?
                                        log.user_id.substring(0, 6) : 'SYS' }}</div>
                                </td>
                                <td>
                                    <span class="badge neutral">{{ formatAction(log.action) }}</span>
                                </td>
                                <td>
                                    <div class="text-secondary font-medium">{{ formatEntity(log.entity_type) }}
                                    </div>
                                    <div class="smaller-text text-tertiary">#{{ log.entity_id ?
                                        log.entity_id.substring(0, 8) : '-' }}</div>
                                </td>
                                <td class="pr-8 text-right">
                                    <div class="text-secondary">{{ new Date(log.created_at).toLocaleTimeString() }}
                                    </div>
                                    <div class="smaller-text text-tertiary">{{ new
                                        Date(log.created_at).toLocaleDateString() }}</div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Right: Pie Chart Stats -->
            <div class="insights-side">
                <div class="card glass-card shadow-sm featured-insight">
                    <label class="section-label mb-6">{{ $t('dashboard.quickStats') }}</label>

                    <!-- Pie Chart Container -->
                    <div class="chart-container flex justify-center mb-6">
                        <div class="pie-chart" :style="pieChartStyle">
                            <div class="chart-center">
                                <span class="chart-total">{{ stats.total_applications }}</span>
                                <span class="chart-label">{{ $t('common.all') }}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Legend -->
                    <div class="chart-legend grid gap-3">
                        <div class="legend-item">
                            <div class="flex items-center gap-2">
                                <div class="dot active-dot"></div>
                                <span class="smaller-text font-bold">{{ $t('applications.filters.inProgress')
                                    }}</span>
                            </div>
                            <span class="smaller-text text-tertiary">{{ stats.in_pipeline }}</span>
                        </div>
                        <div class="legend-item">
                            <div class="flex items-center gap-2">
                                <div class="dot success-dot"></div>
                                <span class="smaller-text font-bold">{{ $t('applications.filters.completed')
                                    }}</span>
                            </div>
                            <span class="smaller-text text-tertiary">{{ stats.sold_count }}</span>
                        </div>
                        <div class="legend-item">
                            <div class="flex items-center gap-2">
                                <div class="dot cancel-dot"></div>
                                <span class="smaller-text font-bold">{{ $t('applications.status.cancelled')
                                    }}</span>
                            </div>
                            <span class="smaller-text text-tertiary">{{ stats.canceled_count }}</span>
                        </div>
                    </div>

                    <div class="mt-6 p-4 rounded bg-bg-secondary border border-light">
                        <p class="smaller-text m-0 text-secondary italic">
                            "{{ $t('dashboard.realTime') }}"
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <div class="spacer"></div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

const { getStats, getApplications, hasRole } = useApi()
const { t } = useI18n()

const showFinancials = computed(() => hasRole('admin'))
const showStaffMetrics = computed(() => hasRole(['manager', 'operator', 'admin']))

const getStatusCount = (s: string) => (stats.value as any).status_counts?.[s] || 0
const getContactCount = (s: string) => (stats.value as any).contact_counts?.[s] || 0

const selectedPeriod = ref('all')

const stats = ref({
    total_volume_uzs: 0,
    total_volume_usd: 0,
    total_profit_usd: 0,
    in_pipeline: 0,
    fleet_count: 0,
    conversion_rate: 0,
    total_applications: 0,
    sold_count: 0,
    canceled_count: 0,
    status_counts: {} as Record<string, number>,
    contact_counts: {} as Record<string, number>,
    recent_activity: [] as any[],
    personal_performance: {
        count: 0,
        label: ''
    }
})

const recentApplications = ref<any[]>([])
const loading = ref(true)

const formatMoney = (amount: number) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(amount || 0)
}

const formatAction = (action: string) => {
    if (!action) return '-'
    return action.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const formatEntity = (type: string) => {
    if (!type) return '-'
    return type.charAt(0).toUpperCase() + type.slice(1)
}



// Compute Pie Chart Segments
const pieChartStyle = computed(() => {
    const total = stats.value.total_applications || 1
    const active = (stats.value.in_pipeline / total) * 100
    const sold = (stats.value.sold_count / total) * 100
    const canceled = (stats.value.canceled_count / total) * 100

    // Colors: Active (Accent), Sold (Success), Canceled (Gray/Error)
    const colorActive = 'var(--color-accent)'
    const colorSold = 'var(--color-success)'
    const colorCanceled = '#e5e7eb'

    return {
        background: `conic-gradient(
            ${colorActive} 0% ${active}%,
            ${colorSold} ${active}% ${active + sold}%,
            ${colorCanceled} ${active + sold}% 100%
        )`
    }
})



const fetchData = async () => {
    loading.value = true
    try {
        const [statsData, appsRes]: any = await Promise.all([
            getStats({ period: selectedPeriod.value }),
            getApplications({ limit: 5 })
        ])

        stats.value = statsData

        // If user wants "Recent Actions" to be actual Audit Logs, we should switch the UI.
        // For now, based on screenshot, they are showing Applications table.
        // We will stick to Applications but maybe they want it filtered?
        // Let's reload applications if they change date filter?
        // Usually "Recent Applications" means just latest created, regardless of stats filter.
        // But "Recent Actions" (Audit Logs) should be filtered. 

        recentApplications.value = (appsRes.items || []).map((a: any) => ({
            id: a.id.substring(0, 8),
            fullId: a.id,
            client: `${a.client_first_name} ${a.client_last_name}`,
            car: `${a.car_brand} ${a.car_model}`,
            amount: a.final_price || 0,
            status: a.status
        }))

    } catch (err) {
        console.error('Dashboard fetch failed', err)
    } finally {
        loading.value = false
    }
}

onMounted(fetchData)

definePageMeta({ layout: false })

useHead({
    title: computed(() => `${t('dashboard.title')} - STL Admin`)
})
</script>

<style scoped>
.dashboard-page {
    padding-top: var(--spacing-lg);
}

.page-header {
    margin-bottom: var(--spacing-xl);
}

.metrics-grid-flexible {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
}

.metrics-grid-flexible>* {
    flex: 1;
    min-width: 220px;
    max-width: calc(25% - 1.2rem);
}

@media (max-width: 1400px) {
    .metrics-grid-flexible>* {
        max-width: calc(33.33% - 1rem);
    }
}

@media (max-width: 1024px) {
    .metrics-grid-flexible>* {
        max-width: calc(50% - 0.75rem);
    }
}

@media (max-width: 640px) {
    .metrics-grid-flexible>* {
        max-width: 100%;
    }
}

.grid-5 {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1.5rem;
}

@media (max-width: 900px) {
    .grid-5 {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 600px) {
    .grid-5 {
        grid-template-columns: 1fr;
    }
}

/* Metric Cards */
.metric-card {
    padding: 1.5rem;
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    transition: all var(--transition);
    position: relative;
    overflow: hidden;
}

.metric-card::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: var(--color-accent);
    opacity: 0.1;
}

.metric-card:hover {
    transform: translateY(-4px);
    border-color: var(--color-accent);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.metric-card:hover::after {
    opacity: 1;
}

.metric-value {
    font-size: 1.5rem;
    letter-spacing: -0.02em;
    margin: 0.5rem 0;
}

.metric-value.text-success {
    color: var(--color-success);
}

.badge.neutral {
    background: var(--color-bg-secondary);
    color: var(--color-text-secondary);
    border-color: var(--color-border);
}

.monospace {
    font-family: 'Courier New', Courier, monospace;
}

.section-label {
    text-transform: uppercase;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: var(--color-text-tertiary);
}

.trend-tag {
    font-size: 0.65rem;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 800;
}

.trend-tag.success {
    background: rgba(16, 185, 129, 0.1);
    color: var(--color-success);
}

.trend-tag.neutral {
    background: var(--color-bg-secondary);
    color: var(--color-text-tertiary);
}

/* Progress Mini */
.progress-mini {
    height: 4px;
    background: var(--color-bg-secondary);
    border-radius: 2px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    transition: width 1s ease;
}

.progress-fill.accent {
    background: var(--color-accent);
}

.status-dot-mini {
    width: 6px;
    height: 6px;
    border-radius: 50%;
}

.status-dot-mini.success {
    background: var(--color-success);
}

/* Insights Layout */
.insights-layout {
    display: grid;
    gap: 2.5rem;
    grid-template-columns: 1fr 320px;
}

@media (max-width: 1200px) {
    .insights-layout {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 768px) {
    .metrics-grid {
        margin-bottom: var(--spacing-lg);
    }

    .metric-card {
        padding: 1.25rem;
    }

    .dashboard-header {
        margin-bottom: var(--spacing-lg);
    }
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

.id-badge-minimal {
    font-family: monospace;
    font-size: 0.75rem;
    color: var(--color-text-tertiary);
    background: var(--color-bg-secondary);
    padding: 2px 6px;
    border-radius: 4px;
}

.featured-insight {
    padding: 2rem;
    background: var(--color-bg-card);
}

.spacer {
    height: 8rem;
}

.mb-10 {
    margin-bottom: 2.5rem;
}

.btn-ghost {
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 0.4rem 0.8rem;
    border-radius: 4px;
    transition: var(--transition);
}

.btn-ghost:hover {
    background: var(--color-bg-hover);
}

/* Pie Chart Styles */
.pie-chart {
    width: 160px;
    height: 160px;
    border-radius: 50%;
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
}

.chart-center {
    width: 100px;
    height: 100px;
    background: var(--color-bg-primary);
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.chart-total {
    font-size: 1.75rem;
    font-weight: 800;
    color: var(--color-text-primary);
    line-height: 1;
}

.chart-label {
    font-size: 0.75rem;
    color: var(--color-text-tertiary);
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 0.05em;
    margin-top: 4px;
}

.legend-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid var(--color-border-light);
}

.legend-item:last-child {
    border-bottom: none;
}

.dot {
    width: 10px;
    height: 10px;
    border-radius: 2px;
}

.active-dot {
    background: var(--color-accent);
}

.success-dot {
    background: var(--color-success);
}

.cancel-dot {
    background: var(--color-border);
}

.select-filter {
    padding: 0.4rem 0.8rem;
    border: 1px solid var(--color-border);
    border-radius: 4px;
    background: var(--color-bg-primary);
    color: var(--color-text-primary);
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    min-width: 140px;
}

.select-filter:focus {
    outline: none;
    border-color: var(--color-primary);
}
</style>
