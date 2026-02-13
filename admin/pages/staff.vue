<template>
    <div v-if="isLoadingSession" class="flex-center py-20">
        <div class="text-center text-tertiary">
            <p>{{ $t('auth.checkingAccess') }}</p>
        </div>
    </div>
    <div v-else-if="!hasRole('admin')" class="flex-center py-20">
        <div class="text-center">
            <h2 class="text-thin">{{ $t('auth.accessDenied') }}</h2>
            <p class="text-secondary">{{ $t('auth.noPermission') }}</p>
            <NuxtLink to="/dashboard" class="btn btn-primary btn-sm mt-4">{{ $t('nav.dashboard') }}</NuxtLink>
        </div>
    </div>
    <div v-else class="users-page animate-fade-in">
        <header class="page-header">
            <div class="container">
                <div class="flex-between">
                    <div>
                        <h1 class="text-thin">{{ $t('staff.title') }}</h1>
                        <p class="text-secondary text-light">{{ $t('staff.subtitle') }}</p>
                    </div>
                    <div class="header-actions">
                        <button class="btn btn-primary btn-sm" @click="openModal()">
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor"
                                stroke-width="2" style="margin-right: 8px;">
                                <path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
                                <circle cx="8.5" cy="7" r="4" />
                                <line x1="20" y1="8" x2="20" y2="14" />
                                <line x1="23" y1="11" x2="17" y2="11" />
                            </svg>
                            {{ $t('staff.addUser') }}
                        </button>
                    </div>
                </div>
            </div>
        </header>

        <div class="container">
            <!-- Minimal Search Bar -->
            <div class="search-filter-row mb-8">
                <div class="flex gap-4">
                    <div class="search-wrap">
                        <input v-model="searchQuery" type="text" :placeholder="$t('common.searchPlaceholder')"
                            class="input input-minimal">
                    </div>
                    <select v-model="roleFilter" class="input input-minimal" style="width: 160px;">
                        <option value="all">{{ $t('common.allRoles') }}</option>
                        <option v-for="role in roles" :key="role.key" :value="role.key">
                            {{ role.label }}
                        </option>
                    </select>
                </div>
            </div>

            <!-- Clean Table -->
            <div class="card no-padding overflow-hidden border-light shadow-sm">
                <div class="table-responsive">
                    <table class="admin-table">
                        <thead>
                            <tr>
                                <th class="pl-8">{{ $t('staff.user') }}</th>
                                <th>{{ $t('staff.role') }}</th>
                                <th>{{ $t('staff.phone') }}</th>
                                <th>{{ $t('staff.status') }}</th>
                                <th class="text-right pr-8">{{ $t('common.actions') }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-if="loading" v-for="i in 3" :key="i">
                                <td colspan="5" class="py-12 text-center text-tertiary">{{ $t('common.loading') }}</td>
                            </tr>
                            <tr v-else v-for="user in filteredUsers" :key="user.id" class="premium-row clickable-row"
                                @click="openModal(user)">
                                <td class="pl-8 py-5">
                                    <div class="flex items-center gap-4">
                                        <div class="user-id-circle">{{ user.first_name?.charAt(0) }}</div>
                                        <div>
                                            <div class="font-medium text-primary">{{ user.first_name }} {{
                                                user.last_name }}</div>
                                            <div class="smaller-text text-tertiary">{{ user.email || $t('staff.noEmail')
                                                }}
                                            </div>
                                        </div>
                                    </div>
                                </td>
                                <td><span class="badge" :class="user.role">{{ translateRole(user.role) }}</span></td>
                                <td class="text-secondary">{{ user.phone || '—' }}</td>
                                <td>
                                    <div class="flex items-center gap-2">
                                        <span class="status-dot" :class="{ active: user.is_active }"></span>
                                        <span class="text-secondary smaller-text">{{ user.is_active ? $t('staff.active')
                                            :
                                            $t('staff.blocked') }}</span>
                                    </div>
                                </td>
                                <td class="text-right pr-8">
                                    <div class="flex justify-end gap-2" @click.stop>
                                        <button @click="toggleStatus(user)" class="btn btn-sm btn-outline btn-minimal"
                                            :class="user.is_active ? 'text-error' : 'text-success'">
                                            {{ user.is_active ? $t('staff.block') : $t('staff.activate') }}
                                        </button>
                                        <button @click="openModal(user)" class="btn btn-icon-only btn-ghost">
                                            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor"
                                                fill="none" stroke-width="2">
                                                <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
                                                <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                                            </svg>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="spacer"></div>
        </div>

        <!-- User Modal -->
        <Teleport to="body">
            <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
                <div class="modal-card animate-scale-in" :class="{ 'modal-wide': editingId }">
                    <div class="modal-header-premium mb-6">
                        <div class="flex-between items-center mb-4">
                            <h2 class="text-xl font-bold m-0">{{ modalTitle }}</h2>
                            <button v-if="editingId" class="btn btn-icon-only btn-ghost"
                                @click="showModal = false">✕</button>
                        </div>

                        <div v-if="editingId" class="tabs-minimal mt-4">
                            <button class="tab-btn" :class="{ active: activeTab === 'profile' }"
                                @click="activeTab = 'profile'">
                                {{ $t('common.profile') }}
                            </button>
                            <button class="tab-btn" :class="{ active: activeTab === 'performance' }"
                                @click="activeTab = 'performance'">
                                {{ $t('dashboard.quickStats') }}
                            </button>
                        </div>
                    </div>

                    <!-- Profile Tab -->
                    <div v-if="activeTab === 'profile'" class="tab-content animate-fade-in">
                        <div class="grid grid-2 gap-4">
                            <div class="form-group">
                                <label class="micro-label mb-2">{{ $t('staff.firstName') }}</label>
                                <input v-model="form.first_name" type="text" class="input input-sm">
                            </div>
                            <div class="form-group">
                                <label class="micro-label mb-2">{{ $t('staff.lastName') }}</label>
                                <input v-model="form.last_name" type="text" class="input input-sm">
                            </div>
                        </div>
                        <div class="form-group mt-4">
                            <label class="micro-label mb-2">{{ $t('common.email') }}</label>
                            <input v-model="form.email" type="email" class="input input-sm">
                        </div>
                        <div class="form-group mt-4">
                            <label class="micro-label mb-2">{{ $t('staff.phone') }}</label>
                            <div class="phone-input-wrapper">
                                <span class="phone-prefix">+998</span>
                                <input v-model="phoneNumber" @input="formatPhoneInput" type="tel"
                                    class="input input-sm phone-input" :placeholder="$t('auth.phonePlaceholder')"
                                    maxlength="15">
                            </div>
                        </div>
                        <div class="form-group mt-4">
                            <label class="micro-label mb-2">{{ $t('staff.role') }}</label>
                            <select v-model="form.role" class="input input-sm">
                                <option v-for="role in roles" :key="role.key" :value="role.key">
                                    {{ role.label }}
                                </option>
                            </select>
                        </div>
                        <div class="form-group mt-4" v-if="!editingId">
                            <label class="micro-label mb-2">{{ $t('auth.password') }}</label>
                            <input v-model="form.password" type="password" class="input input-sm">
                        </div>
                        <div class="form-group mt-4" v-else>
                            <label class="micro-label mb-2">{{ $t('settings.newPassword') }} ({{ $t('common.optional')
                                }})</label>
                            <input v-model="form.password" type="password" class="input input-sm"
                                :placeholder="$t('settings.leaveBlank')">
                        </div>
                        <div class="flex gap-3 mt-8">
                            <button class="btn btn-sm flex-grow" @click="showModal = false">{{ $t('common.close')
                                }}</button>
                            <button class="btn btn-primary btn-sm flex-grow font-bold" @click="saveUser"
                                :disabled="saving">
                                {{ saving ? $t('common.loading') : $t('common.save') }}
                            </button>
                        </div>
                    </div>

                    <!-- Performance Tab -->
                    <div v-if="activeTab === 'performance' && editingId" class="tab-content animate-fade-in">
                        <div class="performance-overview-grid mb-8">
                            <div class="stat-card-premium">
                                <label class="micro-label uppercase tracking-widest text-tertiary mb-2 block">{{
                                    $t('common.period') }}</label>
                                <div class="select-fancy-wrapper">
                                    <select v-model="selectedPeriod" class="select-fancy">
                                        <option value="day">{{ $t('common.today') }}</option>
                                        <option value="week">{{ $t('common.thisWeek') }}</option>
                                        <option value="month">{{ $t('common.thisMonth') }}</option>
                                        <option value="all">{{ $t('common.allTime') }}</option>
                                    </select>
                                    <span class="select-icon">
                                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
                                            stroke="currentColor" stroke-width="3">
                                            <path d="M6 9l6 6 6-6" />
                                        </svg>
                                    </span>
                                </div>
                            </div>
                            <div v-if="performanceData" class="stat-card-premium highlight-success">
                                <label class="micro-label uppercase tracking-widest text-tertiary mb-2 block">
                                    {{ performanceData.label === 'processed' ? $t('dashboard.processed') :
                                        $t('dashboard.delivered') }}
                                </label>
                                <div class="flex items-center justify-between">
                                    <div class="text-3xl font-black text-primary tracking-tight">
                                        {{ performanceData.success_count }}
                                    </div>

                                </div>
                            </div>
                        </div>

                        <div v-if="performanceLoading" class="py-12 flex-center">
                            <div class="loading-spinner-fancy"></div>
                        </div>

                        <div v-else-if="performanceData?.applications?.length"
                            class="performance-history-container custom-scrollbar">
                            <h3 class="micro-label uppercase tracking-widest text-tertiary mb-4">
                                {{ $t('dashboard.recentActivity') }}
                            </h3>
                            <div class="activity-feed">
                                <div v-for="app in performanceData.applications" :key="app.id"
                                    class="activity-item-card-premium" @click="openAppDetails(app)">
                                    <div class="activity-status-indicator">
                                        <div class="activity-dot-fancy" :class="app.status"></div>
                                        <div class="activity-line"></div>
                                    </div>
                                    <div class="activity-content-premium">
                                        <div class="flex-between items-start mb-2">
                                            <div>
                                                <div class="activity-title">
                                                    {{ $t('applications.application') }} #{{
                                                        app.id.toString().substring(0, 8).toUpperCase() }}
                                                </div>
                                                <div class="activity-time">
                                                    {{ new Date(app.created_at).toLocaleDateString(locale, {
                                                        day: '2-digit',
                                                        month: 'short',
                                                        year: 'numeric',
                                                        hour: '2-digit',
                                                        minute: '2-digit'
                                                    }) }}
                                                </div>
                                            </div>
                                            <span class="badge-premium-pill" :class="app.status">
                                                {{ $t(`applications.status.${app.status}`) || app.status }}
                                            </span>
                                        </div>
                                        <div class="activity-details">
                                            <div class="car-tag-mini">{{ app.car_brand }} {{ app.car_model }}</div>
                                            <div class="client-tag-mini">{{ app.client_first_name }}</div>
                                        </div>
                                    </div>
                                    <div class="activity-arrow">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                                            stroke="currentColor" stroke-width="2.5">
                                            <path d="M9 18l6-6-6-6" />
                                        </svg>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div v-else class="py-16 text-center text-tertiary animate-fade-in">
                            <div class="empty-state-icon mb-4">
                                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="1" class="opacity-20">
                                    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
                                    <polyline points="13 2 13 9 20 9" />
                                </svg>
                            </div>
                            <p class="small-text font-medium">{{ $t('common.noData') }}</p>
                        </div>
                    </div>
                </div>
            </div>
        </Teleport>

        <!-- Application Quick Detail Sub-modal -->
        <Teleport to="body">
            <div v-if="selectedApp" class="modal-overlay" @click.self="selectedApp = null" style="z-index: 3000;">
                <div class="modal-card modal-compact animate-scale-in border-accent-light shadow-2xl">
                    <div class="flex-between mb-6">
                        <h2 class="text-xl font-black m-0 tracking-tight">{{ $t('applications.detail.title') }}</h2>
                        <button class="btn btn-icon-only btn-ghost" @click="selectedApp = null">✕</button>
                    </div>

                    <div class="bg-secondary/20 p-5 rounded-2xl border border-light mb-6">
                        <div class="flex-between mb-4">
                            <span class="micro-label">{{ $t('common.status') }}</span>
                            <span class="badge" :class="selectedApp.status">{{ selectedApp.status }}</span>
                        </div>
                        <div class="flex-between mb-4">
                            <span class="micro-label">{{ $t('applications.finalPrice') }}</span>
                            <span class="text-xl font-bold text-primary">${{ selectedApp.final_price?.toLocaleString()
                                }}</span>
                        </div>
                        <div class="flex-between">
                            <span class="micro-label">{{ $t('common.created') }}</span>
                            <span class="text-secondary smaller-text">{{ new
                                Date(selectedApp.created_at).toLocaleString() }}</span>
                        </div>
                    </div>

                    <div class="grid gap-3">
                        <NuxtLink :to="`/applications?id=${selectedApp.id}`"
                            class="btn btn-primary btn-sm w-full font-bold shadow-sm">
                            {{ $t('applications.fullCrmDetails') }}
                        </NuxtLink>
                        <button class="btn btn-ghost btn-sm w-full" @click="selectedApp = null">
                            {{ $t('common.close') }}
                        </button>
                    </div>
                </div>
            </div>
        </Teleport>

        <!-- Confirmation Modal -->
        <Teleport to="body">
            <div v-if="showConfirmModal" class="modal-overlay" @click.self="closeConfirm">
                <div class="modal-card modal-compact animate-scale-in">
                    <div class="text-center mb-6">
                        <div class="icon-circle mb-4 mx-auto" :class="confirmType">
                            <svg v-if="confirmType === 'danger'" width="24" height="24" viewBox="0 0 24 24" fill="none"
                                stroke="currentColor" stroke-width="2">
                                <path
                                    d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                            </svg>
                            <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
                                <polyline points="22 4 12 14.01 9 11.01" />
                            </svg>
                        </div>
                        <h3 class="text-lg font-bold mb-2">{{ confirmTitle }}</h3>
                        <p class="text-secondary text-sm">{{ confirmMessage }}</p>
                    </div>

                    <div class="flex gap-3">
                        <button class="btn btn-sm flex-grow" @click="closeConfirm">{{ $t('common.cancel') }}</button>
                        <button class="btn btn-sm flex-grow font-bold"
                            :class="confirmType === 'danger' ? 'btn-error' : 'btn-primary'" @click="executeConfirm"
                            :disabled="processingConfirm">
                            {{ processingConfirm ? $t('common.loading') : confirmButtonText }}
                        </button>
                    </div>
                </div>
            </div>
        </Teleport>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'

const { t, locale } = useI18n()
const toast = useToast()

const {
    getUsers,
    createStaffUser,
    updateUserStatus,
    addToBlacklist,
    removeFromBlacklistByPhone,
    hasRole,
    authToken,
    currentUser,
    getStaffPerformance,
    getApplication
} = useApi()

const isLoadingSession = computed(() => !!authToken.value && !currentUser.value)

const users = ref<any[]>([])
const loading = ref(true)
const saving = ref(false)
// User Modal
const showModal = ref(false)
const editingId = ref<string | null>(null)
const modalTitle = computed(() => editingId.value ? t('staff.editUser') : t('staff.addUser'))

// Confirmation Modal
const showConfirmModal = ref(false)
const confirmTitle = ref('')
const confirmMessage = ref('')
const confirmButtonText = ref('Подтвердить')
const confirmType = ref('primary') // or 'danger'
const processingConfirm = ref(false)
let pendingConfirmAction: (() => Promise<void>) | null = null

const searchQuery = ref('')
const roleFilter = ref('all')

const roles = computed(() => [
    { key: 'operator', label: t('users.roles.operator') },
    { key: 'manager', label: t('users.roles.manager') },
    { key: 'admin', label: t('users.roles.admin') }
])

const activeTab = ref('profile')
const performanceData = ref<any>(null)
const performanceLoading = ref(false)
const selectedPeriod = ref('all')
const selectedApp = ref<any>(null)

const fetchPerformance = async () => {
    if (!editingId.value) return
    performanceLoading.value = true
    try {
        performanceData.value = await getStaffPerformance(editingId.value, { period: selectedPeriod.value })
    } catch (err) {
        console.error('Failed to fetch performance', err)
    } finally {
        performanceLoading.value = false
    }
}

watch(selectedPeriod, () => {
    if (activeTab.value === 'performance') fetchPerformance()
})

watch(activeTab, (newTab) => {
    if (newTab === 'performance' && !performanceData.value) {
        fetchPerformance()
    }
})

const openAppDetails = async (app: any) => {
    try {
        const fullApp = await getApplication((app.id || app).toString())
        selectedApp.value = fullApp
    } catch (err) {
        toast.error(t('common.error'), t('common.loadError'))
    }
}

const form = ref({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    role: 'operator',
    password: ''
})

const phoneNumber = ref('')

const formatPhoneInput = () => {
    let cleaned = phoneNumber.value.replace(/\D/g, '').slice(0, 9)
    let formatted = cleaned
    if (cleaned.length > 2) formatted = cleaned.slice(0, 2) + ' ' + cleaned.slice(2)
    if (cleaned.length > 5) formatted = cleaned.slice(0, 2) + ' ' + cleaned.slice(2, 5) + ' ' + cleaned.slice(5)
    if (cleaned.length > 7) formatted = cleaned.slice(0, 2) + ' ' + cleaned.slice(2, 5) + ' ' + cleaned.slice(5, 7) + ' ' + cleaned.slice(7, 9)
    phoneNumber.value = formatted
    form.value.phone = '+998' + cleaned
}

const fetchUsers = async () => {
    loading.value = true
    try {
        const response: any = await getUsers()
        users.value = response.items || response || []
    } catch (err) {
        users.value = []
    } finally {
        loading.value = false
    }
}

const openModal = (user?: any) => {
    activeTab.value = 'profile'
    performanceData.value = null
    if (user) {
        editingId.value = user.id
        form.value = { ...user, password: '' }
        if (user.phone && user.phone.startsWith('+998')) {
            const cleaned = user.phone.replace('+998', '').replace(/\D/g, '')
            let formatted = cleaned
            if (cleaned.length > 2) formatted = cleaned.slice(0, 2) + ' ' + cleaned.slice(2)
            if (cleaned.length > 5) formatted = cleaned.slice(0, 2) + ' ' + cleaned.slice(2, 5) + ' ' + cleaned.slice(5)
            if (cleaned.length > 7) formatted = cleaned.slice(0, 2) + ' ' + cleaned.slice(2, 5) + ' ' + cleaned.slice(5, 7) + ' ' + cleaned.slice(7, 9)
            phoneNumber.value = formatted
        } else {
            phoneNumber.value = ''
        }
    } else {
        editingId.value = null
        form.value = { first_name: '', last_name: '', email: '', phone: '', role: 'operator', password: '' }
        phoneNumber.value = ''
    }
    showModal.value = true
}

const saveUser = async () => {
    saving.value = true
    try {
        if (!editingId.value) {
            const newUser = await createStaffUser(form.value)
            users.value.unshift(newUser)
        }
        showModal.value = false
        fetchUsers()
    } catch (err: any) {
        toast.error(t('common.error'), err?.data?.detail || t('common.saveError'))
    } finally {
        saving.value = false
    }
}

const openConfirm = (title: string, message: string, type: 'primary' | 'danger', action: () => Promise<void>) => {
    confirmTitle.value = title
    confirmMessage.value = message
    confirmType.value = type
    confirmButtonText.value = type === 'danger' ? t('staff.block') : t('staff.activate')
    pendingConfirmAction = action
    showConfirmModal.value = true
}

const closeConfirm = () => {
    showConfirmModal.value = false
    pendingConfirmAction = null
}

const executeConfirm = async () => {
    if (!pendingConfirmAction) return
    processingConfirm.value = true
    try {
        await pendingConfirmAction()
        closeConfirm()
    } catch (e) {
        console.error(e)
    } finally {
        processingConfirm.value = false
    }
}

const toggleStatus = (user: any) => {
    const isBlocking = user.is_active
    const title = isBlocking ? t('users.confirmBlock.title') : t('users.confirmActivate.title')
    const message = isBlocking
        ? t('users.confirmBlock.message', { name: user.first_name })
        : t('users.confirmActivate.message', { name: user.first_name })

    openConfirm(title, message, isBlocking ? 'danger' : 'primary', async () => {
        try {
            await updateUserStatus(user.id, !user.is_active)
            user.is_active = !user.is_active
            if (isBlocking) {
                await addToBlacklist({
                    phone: user.phone,
                    reason: 'other',
                    reason_note: `Staff Block: ${user.first_name} ${user.last_name}`,
                    block_type: 'permanent'
                }).catch(() => { })
            } else {
                await removeFromBlacklistByPhone(user.phone).catch(() => { })
            }
        } catch (err: any) {
            toast.error(t('common.error'), err?.data?.detail || t('users.statusError'))
        }
    })
}

const filteredUsers = computed(() => {
    return users.value.filter(u => {
        // Exclude clients for Staff page
        if (u.role === 'client') return false

        const fullName = `${u.first_name || ''} ${u.last_name || ''}`.toLowerCase()
        const matchesSearch = !searchQuery.value ||
            fullName.includes(searchQuery.value.toLowerCase()) ||
            u.phone?.includes(searchQuery.value)
        const matchesRole = roleFilter.value === 'all' || u.role === roleFilter.value
        return matchesSearch && matchesRole
    })
})

const translateRole = (r: string) => {
    return t(`users.roles.${r?.toLowerCase()}`) || r
}

onMounted(() => {
    if (hasRole('admin')) {
        fetchUsers()
    }
})
definePageMeta({ layout: false })
</script>

<style scoped>
.page-header {
    padding: var(--spacing-xl) 0 var(--spacing-lg);
}

.search-wrap {
    flex-grow: 1;
    max-width: 400px;
}

.input-minimal {
    background: transparent;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
}

.input-minimal:focus {
    border-color: var(--color-text-primary);
    background: var(--color-bg-secondary);
}

.border-light {
    border-color: var(--color-border-light);
}

.user-id-circle {
    width: 36px;
    height: 36px;
    background: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--color-text-primary);
}

.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--color-border);
}

.status-dot.active {
    background: var(--color-success);
}

.btn-ghost {
    background: transparent;
    border: none;
    opacity: 0.4;
}

.btn-ghost:hover {
    opacity: 1;
    background: var(--color-bg-hover);
}

.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
    height: 100vh;
}

.modal-card {
    background: var(--color-bg-card);
    color: var(--color-text-primary);
    width: 100%;
    max-width: 450px;
    padding: 2.5rem;
    border-radius: var(--radius-lg);
    border: 1px solid var(--color-border);
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.3);
}

.modal-compact {
    max-width: 400px;
    padding: 2.5rem 2rem;
    text-align: center;
}

.icon-circle {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    margin: 0 auto 1.5rem auto;
}

.icon-circle.danger {
    color: var(--color-error);
    background: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.2);
}

.icon-circle.primary {
    color: var(--color-success);
    background: rgba(16, 185, 129, 0.1);
    border-color: rgba(16, 185, 129, 0.2);
}

.btn-error {
    background: var(--color-error);
    color: #ffffff;
    border: 1px solid var(--color-error);
}

.btn-error:hover {
    opacity: 0.9;
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

.section-label {
    display: block;
    text-transform: uppercase;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    color: var(--color-text-tertiary);
    margin-bottom: 0.5rem;
}

.pl-8 {
    padding-left: 2rem;
}

.pr-8 {
    padding-right: 2rem;
}

.py-5 {
    padding-top: 1.25rem;
    padding-bottom: 1.25rem;
}

@keyframes scaleIn {
    from {
        opacity: 0;
        transform: scale(0.95);
    }

    to {
        opacity: 1;
        transform: scale(1);
    }
}

.animate-scale-in {
    animation: scaleIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.spacer {
    height: 8rem;
}

.phone-input-wrapper {
    display: flex;
    align-items: center;
    position: relative;
    width: 100%;
}

.phone-prefix {
    position: absolute;
    left: 1rem;
    color: var(--color-text-primary);
    font-weight: 500;
    pointer-events: none;
    z-index: 1;
}

.phone-input {
    padding-left: 4rem !important;
}

@media (max-width: 640px) {
    .search-filter-row .flex {
        flex-direction: column;
    }

    .search-filter-row .input {
        width: 100% !important;
    }

    .header-actions,
    .header-actions .btn {
        width: 100%;
    }
}

.modal-wide {
    max-width: 650px !important;
}

.tabs-minimal {
    display: flex;
    gap: 1.5rem;
    border-bottom: 1px solid var(--color-border);
}

.tab-btn {
    background: none;
    border: none;
    padding: 0.75rem 0;
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--color-text-tertiary);
    cursor: pointer;
    position: relative;
    transition: all var(--transition);
}

.tab-btn.active {
    color: var(--color-text-primary);
}

.tab-btn.active::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--color-text-primary);
}

/* Performance Tab Enhanced Styles */
.performance-overview-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
}

.stat-card-premium {
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: 1.25rem;
    padding: 1.5rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.stat-card-premium.highlight-success {
    background: linear-gradient(135deg, #ffffff 0%, rgba(16, 185, 129, 0.03) 100%);
    border-color: rgba(16, 185, 129, 0.15);
}

.stat-badge-icon {
    width: 44px;
    height: 44px;
    background: rgba(16, 185, 129, 0.1);
    color: var(--color-success);
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.select-fancy-wrapper {
    position: relative;
    width: 100%;
}

.select-fancy {
    width: 100%;
    appearance: none;
    background: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 0.75rem 2.5rem 0.75rem 1rem;
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--color-text-primary);
    cursor: pointer;
    transition: all 0.2s ease;
}

.select-fancy:hover {
    border-color: var(--color-text-tertiary);
    background: var(--color-bg-hover);
}

.select-icon {
    position: absolute;
    right: 1rem;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    opacity: 0.6;
}

.performance-history-container {
    max-height: 450px;
    overflow-y: auto;
    padding-right: 8px;
    margin-top: 2rem;
}

.activity-feed {
    display: flex;
    flex-direction: column;
}

.activity-item-card-premium {
    display: flex;
    gap: 1.25rem;
    padding: 1rem 0;
    cursor: pointer;
    transition: all 0.2s ease;
    border-bottom: 1px solid var(--color-border-light);
}

.activity-item-card-premium:last-child {
    border-bottom: none;
}

.activity-item-card-premium:hover {
    padding-left: 0.5rem;
}

.activity-item-card-premium:hover .activity-title {
    color: var(--color-accent);
}

.activity-status-indicator {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 0.5rem;
}

.activity-dot-fancy {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--color-border);
    flex-shrink: 0;
    position: relative;
    z-index: 2;
}

.activity-dot-fancy.delivered,
.activity-dot-fancy.completed,
.activity-dot-fancy.paid {
    background: var(--color-success);
    box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
}

.activity-dot-fancy.new,
.activity-dot-fancy.confirmed {
    background: var(--color-accent);
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.activity-line {
    width: 1px;
    flex-grow: 1;
    background: var(--color-border-light);
    margin-top: 4px;
}

.activity-content-premium {
    flex-grow: 1;
}

.activity-title {
    font-size: 0.9rem;
    font-weight: 800;
    color: var(--color-text-primary);
    margin-bottom: 2px;
    transition: color 0.2s ease;
}

.activity-time {
    font-size: 0.75rem;
    color: var(--color-text-tertiary);
    font-weight: 500;
}

.badge-premium-pill {
    padding: 4px 12px;
    border-radius: 100px;
    font-size: 0.65rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    background: var(--color-bg-secondary);
    color: var(--color-text-secondary);
}

.badge-premium-pill.delivered,
.badge-premium-pill.paid {
    background: rgba(16, 185, 129, 0.1);
    color: var(--color-success);
}

.badge-premium-pill.cancelled {
    background: rgba(239, 68, 68, 0.1);
    color: var(--color-error);
}

.activity-details {
    display: flex;
    gap: 8px;
    margin-top: 8px;
}

.car-tag-mini,
.client-tag-mini {
    font-size: 0.7rem;
    font-weight: 600;
    padding: 2px 8px;
    background: var(--color-bg-secondary);
    border-radius: 6px;
    color: var(--color-text-secondary);
}

.activity-arrow {
    display: flex;
    align-items: center;
    opacity: 0;
    transition: all 0.2s ease;
    transform: translateX(-10px);
}

.activity-item-card-premium:hover .activity-arrow {
    opacity: 0.3;
    transform: translateX(0);
}

.loading-spinner-fancy {
    width: 32px;
    height: 32px;
    border: 3px solid var(--color-border-light);
    border-top-color: var(--color-text-primary);
    border-radius: 50%;
    animation: spin 1s cubic-bezier(0.76, 0, 0.24, 1) infinite;
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}

.custom-scrollbar::-webkit-scrollbar {
    width: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background: var(--color-border);
    border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: var(--color-text-tertiary);
}

@media (max-width: 640px) {
    .performance-overview-grid {
        grid-template-columns: 1fr;
    }
}
</style>
