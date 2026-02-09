<template>
    <div class="dashboard-page animate-fade-in">
        <header class="page-header">
            <div class="container">
                <div class="flex-between dashboard-header">
                    <div class="header-info">
                        <h1 class="text-thin">Обзор операций</h1>
                        <p class="text-secondary text-light">Мониторинг показателей в реальном времени</p>
                    </div>
                    <div class="header-actions flex gap-3">
                        <button class="btn btn-outline btn-sm hover-accent flex-grow" @click="fetchData">
                            <span class="mr-2">↻</span> Обновить
                        </button>
                        <NuxtLink to="/applications"
                            class="btn btn-primary btn-sm shadow-lg flex-grow flex items-center justify-center text-white no-underline">
                            <span class="mr-2">+</span> Новая заявка
                        </NuxtLink>
                    </div>
                </div>
            </div>
        </header>

        <div class="container">
            <!-- Priority Metrics Cards -->
            <section class="metrics-grid mb-10">
                <div class="grid grid-4 gap-6">
                    <!-- Revenue Pulse -->
                    <div class="metric-card glass-card shadow-sm">
                        <div class="flex-between mb-4">
                            <label class="section-label">Общий объем</label>
                            <span class="trend-tag success">USD</span>
                        </div>
                        <div class="metric-value text-primary font-bold">
                            {{ formatMoney(stats.total_volume_usd) }}
                        </div>
                        <div class="metric-footer mt-4 flex items-center gap-2">
                            <div class="text-secondary smaller-text">
                                ≈ {{ formatMoneyUZS(stats.total_volume_uzs) }} UZS
                            </div>
                        </div>
                    </div>

                    <!-- Pipeline Health -->
                    <div class="metric-card glass-card shadow-sm">
                        <div class="flex-between mb-4">
                            <label class="section-label">В работе</label>
                            <div class="status-indicator active"></div>
                        </div>
                        <div class="metric-value text-primary font-bold">
                            {{ stats.in_pipeline }} <span class="smaller-text text-tertiary">Заявок</span>
                        </div>
                        <div class="metric-footer mt-4">
                            <div class="progress-mini">
                                <div class="progress-fill accent" style="width: 65%;"></div>
                            </div>
                            <div class="flex-between mt-2">
                                <span class="smaller-text text-tertiary">Активные сделки</span>
                                <span class="smaller-text text-accent font-bold">Приоритет</span>
                            </div>
                        </div>
                    </div>

                    <!-- Inventory Flow -->
                    <div class="metric-card glass-card shadow-sm">
                        <div class="flex-between mb-4">
                            <label class="section-label">Автопарк</label>
                            <span class="trend-tag neutral">Каталог</span>
                        </div>
                        <div class="metric-value text-primary font-bold">
                            {{ stats.fleet_count }} <span class="smaller-text text-tertiary">Машин</span>
                        </div>
                        <div class="metric-footer mt-4">
                            <div class="flex items-center gap-2 mb-1">
                                <div class="status-dot-mini success"></div>
                                <span class="smaller-text text-secondary">Доступно к заказу</span>
                            </div>
                        </div>
                    </div>

                    <!-- Conversion Impact -->
                    <div class="metric-card glass-card shadow-sm">
                        <div class="flex-between mb-4">
                            <label class="section-label">Конверсия</label>
                        </div>
                        <div class="metric-value text-primary font-bold">
                            {{ stats.conversion_rate }} <span class="smaller-text text-tertiary">%</span>
                        </div>
                        <div class="metric-footer mt-4 flex items-center justify-between">
                            <span class="smaller-text text-tertiary">Процент успешных сделок</span>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Operational Insights Section -->
            <div class="insights-layout">
                <!-- Left: Detailed Activity & Tables -->
                <div class="insights-main">
                    <div class="flex-between mb-4 px-2">
                        <h3 class="m-0 text-thin">Последние операции</h3>
                        <NuxtLink to="/applications"
                            class="btn btn-ghost smaller-text font-bold text-accent hover-accent">ВСЕ ЗАЯВКИ ↗
                        </NuxtLink>
                    </div>

                    <div class="card no-padding overflow-hidden border-light shadow-sm">
                        <table class="admin-table">
                            <thead>
                                <tr>
                                    <th class="pl-8">ID</th>
                                    <th>Клиент</th>
                                    <th>Автомобиль</th>
                                    <th>Сумма</th>
                                    <th class="pr-8">Статус</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-if="loading" v-for="i in 3" :key="i">
                                    <td colspan="5" class="py-12 text-center text-tertiary smaller-text">
                                        Загрузка данных...
                                    </td>
                                </tr>
                                <tr v-else-if="recentApplications.length === 0">
                                    <td colspan="5" class="py-12 text-center text-tertiary smaller-text">
                                        Нет активных операций.
                                    </td>
                                </tr>
                                <tr v-else v-for="app in recentApplications" :key="app.id"
                                    class="premium-row clickable-row"
                                    @click="$router.push(`/applications/${app.fullId}`)">
                                    <td class="pl-8 py-5">
                                        <code class="id-badge-minimal">#{{ app.id }}</code>
                                    </td>
                                    <td>
                                        <div class="font-bold text-primary">{{ app.client }}</div>
                                    </td>
                                    <td>
                                        <div class="text-secondary font-medium">{{ app.car }}</div>
                                    </td>
                                    <td>
                                        <div class="font-bold">{{ formatMoney(app.amount) }}</div>
                                        <div class="smaller-text text-tertiary">USD</div>
                                    </td>
                                    <td class="pr-8">
                                        <span class="badge" :class="app.status.toLowerCase()">{{
                                            translateStatus(app.status) }}</span>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Right: Pie Chart Stats -->
                <div class="insights-side">
                    <div class="card glass-card shadow-sm featured-insight">
                        <label class="section-label mb-6">Структура заявок</label>

                        <!-- Pie Chart Container -->
                        <div class="chart-container flex justify-center mb-6">
                            <div class="pie-chart" :style="pieChartStyle">
                                <div class="chart-center">
                                    <span class="chart-total">{{ stats.total_applications }}</span>
                                    <span class="chart-label">Всего</span>
                                </div>
                            </div>
                        </div>

                        <!-- Legend -->
                        <div class="chart-legend grid gap-3">
                            <div class="legend-item">
                                <div class="flex items-center gap-2">
                                    <div class="dot active-dot"></div>
                                    <span class="smaller-text font-bold">В работе</span>
                                </div>
                                <span class="smaller-text text-tertiary">{{ stats.in_pipeline }} шт.</span>
                            </div>
                            <div class="legend-item">
                                <div class="flex items-center gap-2">
                                    <div class="dot success-dot"></div>
                                    <span class="smaller-text font-bold">Завершено</span>
                                </div>
                                <span class="smaller-text text-tertiary">{{ stats.sold_count }} шт.</span>
                            </div>
                            <div class="legend-item">
                                <div class="flex items-center gap-2">
                                    <div class="dot cancel-dot"></div>
                                    <span class="smaller-text font-bold">Отменено</span>
                                </div>
                                <span class="smaller-text text-tertiary">{{ stats.canceled_count }} шт.</span>
                            </div>
                        </div>

                        <div class="mt-6 p-4 rounded bg-bg-secondary border border-light">
                            <p class="smaller-text m-0 text-secondary italic">
                                "Статистика обновляется в реальном времени."
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="spacer"></div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

const { getStats, getApplications } = useApi()

const stats = ref({
    total_volume_uzs: 0,
    total_volume_usd: 0,
    in_pipeline: 0,
    fleet_count: 0,
    conversion_rate: 0,
    total_applications: 0,
    sold_count: 0,
    canceled_count: 0
})

const recentApplications = ref<any[]>([])
const loading = ref(true)

const formatMoney = (amount: number) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(amount)
}

const formatMoneyUZS = (amount: number) => {
    if (amount >= 1000000000) {
        return (amount / 1000000000).toFixed(1) + ' Млрд'
    }
    if (amount >= 1000000) {
        return (amount / 1000000).toFixed(1) + ' Млн'
    }
    return amount.toLocaleString()
}

const translateStatus = (status: string) => {
    const map: Record<string, string> = {
        'new': 'Новая',
        'contacted': 'В работе',
        'visit_scheduled': 'Визит',
        'test_drive': 'Тест-драйв',
        'offer_sent': 'КП',
        'contract_signed': 'Контракт',
        'paid': 'Оплачено',
        'completed': 'Выдано',
        'cancelled': 'Отмена'
    }
    return map[status?.toLowerCase()] || status
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
            getStats(),
            getApplications({ limit: 5 })
        ])

        stats.value = statsData

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
    title: 'Дашборд - STL Admin'
})
</script>

<style scoped>
.dashboard-page {
    padding-top: var(--spacing-lg);
}

.page-header {
    margin-bottom: var(--spacing-xl);
}

/* Metric Cards */
.metric-card {
    padding: 1.75rem;
    background: var(--color-bg-primary);
    border: 1px solid var(--color-border);
    transition: var(--transition);
}

.metric-card:hover {
    transform: translateY(-2px);
    border-color: var(--color-text-tertiary);
}

.metric-value {
    font-size: 1.75rem;
    letter-spacing: -0.02em;
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
</style>
